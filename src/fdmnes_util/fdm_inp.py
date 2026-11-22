"""FDMNES の計算・畳み込み入力 ``*.inp`` を読み書きする共通の入口。

FdmInp は明示した形式年で処理を選び、指定がなければ2016年形式を使う。ブロック編集と POSCAR からの入力作成は2026年形式の実装に委譲する。
"""
from collections.abc import Sequence
from pathlib import Path

from .fdm_inp_2016 import FdmInp2016
from .fdm_inp_2026 import FdmInp2026


class FdmInp:
    """FDMNES の計算入力 `*.inp` を読み書きし、指定された形式の実装へ委譲する。"""
    KEYWORDS = FdmInp2016.KEYWORDS

    def __init__(self, filename="read_pdb.inp", *, format_year=2016):
        """通常入力は2016、拡張入力は明示的に2026を指定する。"""
        self._reader = self._reader_class(format_year)(filename)
        self.format_year = format_year
        self.path = self._reader.path
        self.lines = self._reader.lines
        self.tags = self._reader.tags

    @staticmethod
    def _reader_class(format_year):
        """指定された入力形式を担当する年別クラスを返す。"""
        if format_year == 2016:
            return FdmInp2016
        if format_year == 2026:
            return FdmInp2026
        raise ValueError(f"Unverified FDMNES input layout: {format_year}")

    def select_reader(self):
        """選んだ年別リーダーを返す。"""
        return self._reader

    @classmethod
    def from_text(cls, text):
        """テキストを編集可能な2026形式の計算入力として開く。"""
        inp = cls(None, format_year=2026)
        inp._reader._set_text(text)
        return inp

    @classmethod
    def from_poscar(cls, filename, *, molecule=False):
        """POSCAR の構造を使って2026形式の計算入力を作る。"""
        inp = cls(None, format_year=2026)
        inp._reader._set_poscar(filename, molecule=molecule)
        return inp

    def _editable_reader(self):
        """編集メソッドの委譲先である2026年形式の入力リーダーを返す。"""
        if self.format_year != 2026:
            raise ValueError("Editing the input requires format_year=2026")
        return self._reader

    def set_block(self, keyword, *rows, old_rows=None):
        """データ行を追加または置換する。可変長の置換では old_rows を指定する。"""
        self._editable_reader()._set_block(keyword, *rows, old_rows=old_rows)
        return self

    def remove_block(self, keyword, *, old_rows=None):
        """指定した入力ブロックを取り除く。"""
        self._editable_reader()._remove_block(keyword, old_rows=old_rows)
        return self

    def set_radius(self, radius, *changes):
        """半径（Å）と、切替エネルギー（eV）・切替後の半径の組を指定する。"""
        self._editable_reader()._set_radius(radius, *changes)
        return self

    def render_input(self):
        """現在の入力本文を返す。"""
        return self._editable_reader()._render_input()

    def save(self, filename, *, overwrite=False):
        """編集中の入力を保存する。既存ファイルの上書きは明示指定する。"""
        return self._editable_reader()._save_input(filename, overwrite=overwrite)

    def get_absorber(self) -> int:
        """先頭の吸収サイトを返す。"""
        return self._reader.get_absorber()

    def get_absorbers(self) -> list[int]:
        """吸収サイトを入力順に返す。"""
        read_absorbers = getattr(self._reader, "_get_absorbers", None)
        if read_absorbers is None:
            return [self.get_absorber()]
        return read_absorbers()

    def get_calculations(self):
        """各計算のファイル名、重み、シフト、カットオフを返す。"""
        read_calculations = getattr(self._reader, "_get_calculations", None)
        if read_calculations is not None:
            return read_calculations()
        filename = self.get_calculation()
        if filename:
            return [(filename, None, None, None)]
        return []

    def get_filout(self):
        """出力の接頭辞を返す。"""
        return self._reader.get_filout()

    def get_ispin(self):
        """スピン数を返す。"""
        return self._reader.get_ispin()

    def get_allsite(self):
        """全サイト計算の指定を返す。"""
        return self._reader.get_allsite()

    def get_energygpho(self):
        """光子エネルギーの指定を返す。"""
        return self._reader.get_energygpho()

    def get_nonexc(self):
        """非励起計算の指定を返す。"""
        return self._reader.get_nonexc()

    def get_convolution(self):
        """畳み込みの指定を返す。"""
        return self._reader.get_convolution()

    def get_conv_out(self):
        """畳み込みの出力ファイル名を返す。"""
        return self._reader.get_conv_out()

    def get_calculation(self):
        """先頭の計算ファイル名を返す。"""
        return self._reader.get_calculation()

    def get_cellparam(self):
        """格子定数を返す。"""
        return self._reader.get_cellparam()

    def get_crystal_atoms(self):
        """周期構造を返す。"""
        return self._reader.get_crystal_atoms()

    def get_molecule_atoms(self):
        """分子構造を返す。"""
        return self._reader.get_molecule_atoms()

    @staticmethod
    def render(
        absorber: int | Sequence[int] = 1,
        fileout: str = "Cu",
        energy_range: str = "-15. 0.2  0. 0.5 10. 1. 45.",
        edge: str = "K",
        radius: float = 5,
        molecule: bool = False,
        structure_writer=None,
        *,
        format_year=2016,
        density_complex=False,
        lmax_dosout=None,
    ) -> str:
        """選んだ形式で計算入力を生成する。"""
        reader = FdmInp._reader_class(format_year)
        settings = dict(
            absorber=absorber,
            fileout=fileout,
            energy_range=energy_range,
            edge=edge,
            radius=radius,
            molecule=molecule,
            structure_writer=structure_writer,
        )
        if format_year == 2026:
            return reader._render_extended(
                density_complex=density_complex,
                lmax_dosout=lmax_dosout,
                **settings,
            )
        if (
            density_complex
            or lmax_dosout is not None
            or (isinstance(absorber, Sequence) and not isinstance(absorber, str))
        ):
            raise ValueError("Extended input options require format_year=2026")
        return reader.render(**settings)

    @staticmethod
    def write(filename: str | Path = "read_pdb.inp", **kwargs) -> Path:
        """計算入力を保存する。"""
        destination = Path(filename)
        destination.write_text(FdmInp.render(**kwargs), encoding="utf-8")
        return destination

    @staticmethod
    def write_convolution(
        filename,
        calculations,
        *,
        output,
        format_year,
        header=False,
        energy_step=None,
        per_atom=False,
    ):
        """複数サイトを合わせる2026年形式の畳み込み入力を書く。"""
        if format_year != 2026:
            raise ValueError("Combined convolution input requires format_year=2026")
        return FdmInp2026._write_convolution(
            filename,
            calculations,
            output=output,
            header=header,
            energy_step=energy_step,
            per_atom=per_atom,
        )
