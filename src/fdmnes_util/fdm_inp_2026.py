"""2026年版で使用する計算入力の拡張項目を扱う。"""

from collections.abc import Sequence
from math import isfinite
from pathlib import Path

from .fdm_inp_2016 import FdmInp2016


class FdmInp2026:
    """複数サイト、畳み込みの指定、SD 出力オプションを扱う。"""

    KEYWORDS = FdmInp2016.KEYWORDS | {
        "density",
        "density_all",
        "density_comp",
        "lmax_dosout",
        "range",
        "radius",
        "edge",
        "green",
        "header",
        "scf",
        "n_self",
        "directory",
        "all_conv",
        "e_cut",
        "e_step_conv",
        "per_atom",
    }

    def __init__(self, filename="read_pdb.inp"):
        self._reader = FdmInp2016(filename, _keywords=self.KEYWORDS)
        self.path = self._reader.path
        self.lines = self._reader.lines
        self.tags = self._reader.tags

    def get_absorber(self) -> int:
        """先頭の吸収サイトを返す。"""
        return self._get_absorbers()[0]

    def _get_absorbers(self):
        if "absorber" not in self.tags:
            return [1]
        return self._read_absorbers(self._reader._last_record("absorber"))

    def _get_calculations(self):
        return self._read_calculations(self._reader._last_record("calculation"))

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
        absorber: int = 1,
        fileout: str = "Cu",
        energy_range: str = "-15. 0.2  0. 0.5 10. 1. 45.",
        edge: str = "K",
        radius: float = 5,
        molecule: bool = False,
        structure_writer=None,
    ) -> str:
        """共通テンプレートで計算入力を生成する。"""
        return FdmInp2016.render(
            absorber=absorber,
            fileout=fileout,
            energy_range=energy_range,
            edge=edge,
            radius=radius,
            molecule=molecule,
            structure_writer=structure_writer,
        )

    @staticmethod
    def write(filename: str | Path = "read_pdb.inp", **kwargs) -> Path:
        """計算入力を保存する。"""
        destination = Path(filename)
        destination.write_text(FdmInp2026.render(**kwargs), encoding="utf-8")
        return destination

    @staticmethod
    def _read_absorbers(values):
        """吸収サイトの行から、1始まりの原子インデックスを読む。"""
        if not values:
            raise ValueError("Absorber requires a positive atom index")
        try:
            indices = [int(word) for word in values[0].split()]
        except ValueError as error:
            raise ValueError("Absorber requires a positive atom index") from error
        if any(index < 1 for index in indices):
            raise ValueError("Absorber requires a positive atom index")
        return indices

    @staticmethod
    def _read_calculations(
        lines,
    ) -> list[tuple[str, float | None, float | None, float | None]]:
        """計算ファイル名と、次行の重み・シフト・カットオフを入力順に返す。

        Returns:
            list[tuple]: (ファイル名, 重み, シフト, カットオフ) の並び。
                省略された数値は None。
        """
        records = []
        i = 0
        while i < len(lines):
            filename, *inline = lines[i].split()
            i += 1
            parameters: list[float | None] = [
                float(word.upper().replace("D", "E")) for word in inline
            ]
            if not inline and i < len(lines):
                try:
                    parameters = [
                        float(word.upper().replace("D", "E"))
                        for word in lines[i].split()
                    ]
                except ValueError:
                    pass
                else:
                    i += 1
            if len(parameters) > 3:
                raise ValueError("Calculation accepts at most three numeric parameters")
            parameters.extend([None] * (3 - len(parameters)))
            records.append((filename, parameters[0], parameters[1], parameters[2]))
        return records

    @staticmethod
    def _render_extended(*, absorber, density_complex, lmax_dosout, **settings):
        absorber_line = FdmInp2026._render_absorbers(absorber)
        content = FdmInp2026.render(absorber=absorber_line, **settings)
        return FdmInp2026._render_output_keywords(
            content,
            density_complex=density_complex,
            lmax_dosout=lmax_dosout,
        )

    @staticmethod
    def _render_absorbers(absorber: int | Sequence[int]) -> str:
        """入力テンプレートに渡す吸収サイトの行を作る。"""
        indices = absorber
        if isinstance(absorber, int):
            indices = (absorber,)
        if not indices or any(type(index) is not int or index < 1 for index in indices):
            raise ValueError("Absorber requires positive atom indices")

        return " ".join(str(index) for index in indices)

    @staticmethod
    def _render_output_keywords(content, *, density_complex, lmax_dosout):
        """計算入力の末尾に SD 出力設定を加える。"""
        keywords = []
        if density_complex:
            keywords.append(" Density_comp\n\n")
        if lmax_dosout is not None:
            if type(lmax_dosout) is not int or lmax_dosout < 0:
                raise ValueError("lmax_dosout must be a nonnegative integer")
            keywords.append(f" Lmax_DOSout\n  {lmax_dosout}\n\n")
        end = " End\n\n"
        return content.removesuffix(end) + "".join(keywords) + end

    @staticmethod
    def _write_convolution(
        filename,
        calculations,
        *,
        output,
        header=False,
        energy_step=None,
        per_atom=False,
    ):
        """複数サイトを一つのスペクトルにする畳み込み入力を書く。

        Args:
            filename: 畳み込み入力の保存先。
            calculations: (生 XAS ファイル, 重み, シフト) の順序付きデータ。
                相対パスは FDMNES の実行フォルダ基準。シフトは eV。
            output: Conv_out の出力ファイル名。
            header: 畳み込み条件を出力する Header キーワードを加える。
            energy_step: E_step_conv に渡す出力間隔（eV）。省略時は本体の既定値。
            per_atom: Per_atom で吸収原子一個あたりの強度にする。

        Returns:
            Path: 書き出した入力ファイル。
        """
        lines = ["Calculation"]
        for spectrum, weight, shift in calculations:
            lines.extend((f"  {spectrum}", f"  {float(weight)} {float(shift)}"))
        if len(lines) == 1:
            raise ValueError("Calculation requires at least one spectrum")
        lines.extend(("Conv_out", f"  {output}", "Convolution"))
        if header:
            lines.append("Header")
        if energy_step is not None:
            energy_step = float(energy_step)
            if not isfinite(energy_step) or energy_step <= 0:
                raise ValueError("energy_step must be positive and finite")
            lines.extend(("E_step_conv", f"  {energy_step}"))
        if per_atom:
            lines.append("Per_atom")
        lines.append("End")
        path = Path(filename)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path
