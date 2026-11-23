"""FDMNES の計算・畳み込み入力 ``*.inp`` を読み書きする共通の入口。

FdmInp は明示した形式年で処理を選び、指定がなければ2016年形式を使う。ブロック編集と POSCAR からの入力作成は2026年形式の実装に委譲する。
"""
from collections.abc import Sequence
from pathlib import Path

from .fdm_inp_2016 import FdmInp2016
from .fdm_inp_2026 import FdmInp2026


class FdmInp:
    """FDMNES の計算・畳み込み入力ファイル（`*.inp`）を読み書きする。

    入力の読み取りは既定で2016年形式を使う。設定を編集する場合は
    `format_year=2026` を選び、`set_structure()` で構造節を、
    `set_absorber()` と `set_edge()` で吸収サイトと吸収端を指定する。
    `set_range()` は計算するエネルギー格子、`set_filout()` は出力の接頭辞を設定する。
    """
    KEYWORDS = FdmInp2016.KEYWORDS

    def __init__(self, filename="read_pdb.inp", *, format_year=2016):
        """指定した計算入力を開く。

        Args:
            filename: FDMNES 計算入力のパス。
            format_year: 読み書きに使う実装の年。入力を編集するときは 2026 を指定する。

        Raises:
            ValueError: 対応していない形式年を指定した場合。
            FileNotFoundError: 指定した入力ファイルが存在しない場合。
        """
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
        """入力本文を編集可能な2026形式の計算入力として開く。

        Args:
            text: FDMNES キーワードとデータ行を記述した文字列。
                最初から組み立てる場合は終端の `End` だけでもよい。

        Returns:
            FdmInp: 編集可能な入力。ファイルにするには save() を呼ぶ。
        """
        inp = cls(None, format_year=2026)
        inp._reader._set_text(text)
        return inp

    @classmethod
    def from_poscar(cls, filename, *, molecule=False):
        """vasp_util で POSCAR を読み、FDMNES の構造節を作る。

        Args:
            filename: POSCAR のパス。
            molecule: True の場合は Molecule 節、False の場合は Crystal 節を作る。

        Returns:
            FdmInp: 構造節が入った編集可能な2026形式の入力。
                吸収端やエネルギー範囲は set_edge() や set_range() で指定する。
        """
        inp = cls(None, format_year=2026)
        inp._reader._set_poscar(filename, molecule=molecule)
        return inp

    def _editable_reader(self):
        """編集メソッドの委譲先である2026年形式の入力リーダーを返す。"""
        if self.format_year != 2026:
            raise ValueError("Editing the input requires format_year=2026")
        return self._reader

    def set_keyword(self, keyword, *rows, old_rows=None):
        """2026形式の入力にキーワードブロックを追加または置換する。

        Args:
            keyword: FDMNES のキーワード名。例は `Filout`、`Range`、`Calculation`。
            *rows: キーワードに続くデータ行。文字列や数値は1行として扱い、
                タプルなどの並びは空白区切りの1行にする。
                `Green` のような値のないキーワードは、行を渡さずに指定する。
            old_rows: 置換前のデータ行数。`Calculation` など、行数が可変の
                既存キーワードの値を置換する場合に指定する。

        Returns:
            FdmInp: 更新した入力。

        Raises:
            ValueError: 形式年が2026以外、またはブロックの指定が不正な場合。
        """
        self._editable_reader()._set_block(keyword, *rows, old_rows=old_rows)
        return self

    def set_block(self, keyword, *rows, old_rows=None):
        """既存の呼び出しとの互換用。引数と戻り値は set_keyword() と同じ。"""
        return self.set_keyword(keyword, *rows, old_rows=old_rows)

    def set_structure(self, cell, *atoms, molecule=False, old_rows=None):
        """2026形式の入力に Crystal または Molecule の構造節を設定する。

        Args:
            cell: FDMNES の構造節の先頭に書く格子長と格子角などのデータ行。
            *atoms: FDMNES の書式で指定した原子行。
                Crystal では各行に原子番号と分率座標を渡す。
            molecule: True で Molecule 節を指定する。既定は Crystal 節。
            old_rows: 同じ構造節を置換するときの、格子行を含む元のデータ行数。

        Returns:
            FdmInp: 更新した入力。

        Raises:
            ValueError: 形式年が2026以外、または構造節の行指定が不正な場合。
        """
        self._editable_reader()._set_structure(
            cell,
            *atoms,
            molecule=molecule,
            old_rows=old_rows,
        )
        return self

    def set_range(self, *grid):
        """フェルミ準位を基準とする光電子エネルギーの計算格子を設定する。

        Args:
            *grid: 下限、刻み幅、上限の順の値（eV）。刻み幅を途中で変える場合は、
                上限の前に切替エネルギーと次の刻み幅の組を挿入する。
                例えば `set_range(-5, 0.2, 10, 0.5, 60)` は 10 eV で刻み幅を変える。

        Returns:
            FdmInp: 更新した入力。

        Raises:
            ValueError: 形式年が2026以外、値の数が不正、エネルギーが昇順でない、
                刻み幅が正でない、または値が有限でない場合。
        """
        self._editable_reader()._set_range(grid)
        return self

    def get_range(self):
        """2026形式の Range の値を入力順のタプル（eV）で返す。

        Range が省略されていれば None を返す。Rangel は別のキーワード。
        出力軸を光子エネルギーに変える Energpho も、指定された Range の値は変えない。
        """
        return self._editable_reader()._get_numeric_row("range")

    def set_edge(self, edge):
        """吸収端を設定する。例は K、L3、L23（L2 と L3 の同時計算）。

        Args:
            edge: FDMNES が解釈する吸収端のラベル。

        Returns:
            FdmInp: 更新した入力。
        """
        self._editable_reader()._set_edge(edge)
        return self

    def get_edge(self):
        """2026形式で指定された吸収端を返す。未指定時は既定値 K。"""
        return self._editable_reader()._get_keyword_value("edge", default="K").upper()

    def set_absorber(self, absorber):
        """Crystal または Molecule の原子行から吸収サイトを選ぶ。

        Args:
            absorber: 1始まりの原子行番号、または複数サイトの番号の並び。
                元素の原子番号による指定は FDMNES の Z_absorber を使う。

        Returns:
            FdmInp: 更新した入力。
        """
        self._editable_reader()._set_absorber(absorber)
        return self

    def set_filout(self, prefix):
        """計算結果の出力接頭辞を拡張子なしで設定する。

        Args:
            prefix: 出力ファイルの接頭辞。ディレクトリを含められる。
                相対パスは FDMNES の作業ディレクトリを基準とする。

        Returns:
            FdmInp: 更新した入力。
        """
        self._editable_reader()._set_block("Filout", prefix)
        return self

    def set_green(self, enabled=True):
        """Green を設定し、マフィンティンポテンシャルの多重散乱法を選ぶ。

        False を指定すると Green を取り除く。更新した入力を返す。
        """
        self._editable_reader()._set_flag("Green", enabled)
        return self

    def get_green(self):
        """2026形式の入力に Green が指定されているかを返す。"""
        return "green" in self._editable_reader().tags

    def set_convolution(self, enabled=True):
        """アークタンジェントモデルによるスペクトルの幅付けを指定する。

        False を指定すると Convolution を取り除く。更新した入力を返す。
        """
        self._editable_reader()._set_flag("Convolution", enabled)
        return self

    def set_spgroup(self, space_group):
        """非磁性計算で、非等価原子行から構造を展開するための空間群を指定する。

        Args:
            space_group: 空間群記号または番号。原点の選択も指定できる。
                例えば Fd-3m:1 または 227:1。

        Returns:
            FdmInp: 更新した入力。
        """
        self._editable_reader()._set_block("Spgroup", space_group)
        return self

    def get_spgroup(self):
        """2026形式で指定された空間群を入力表記のまま返す。未指定なら空文字列。"""
        return self._editable_reader()._get_keyword_value("spgroup", default="")

    def remove_block(self, keyword, *, old_rows=None):
        """指定した入力ブロックを取り除く。"""
        self._editable_reader()._remove_block(keyword, old_rows=old_rows)
        return self

    def set_radius(self, radius, *changes):
        """2026形式の入力に計算クラスタの半径を設定する。

        Args:
            radius: 最初に使う半径（Å）。正の有限値を指定する。
            *changes: 切替エネルギー（eV）と切替後の半径（Å）の組。
                複数の組を指定する場合は、切替エネルギーを昇順に並べる。

        Returns:
            FdmInp: 更新した入力。

        Raises:
            ValueError: 形式年が2026以外、または半径や切替エネルギーが不正な場合。
        """
        self._editable_reader()._set_radius(radius, *changes)
        return self

    def get_radius(self):
        """2026形式の Radius の値を入力順で返す。未指定なら None。

        最初の値は半径（Å）。後続は切替エネルギー（eV）、切替後の半径（Å）の順。
        """
        return self._editable_reader()._get_numeric_row("radius")

    def render_input(self):
        """編集中の2026形式の入力を文字列で確認する。

        Returns:
            str: 終端の `End` を含む入力本文。
        """
        return self._editable_reader()._render_input()

    def save(self, filename, *, overwrite=False):
        """編集中の2026形式の入力を UTF-8 で保存する。

        Args:
            filename: 保存先のパス。
            overwrite: True の場合は既存のファイルを上書きする。

        Returns:
            pathlib.Path: 保存した入力のパス。FdmRun.run() に渡せる。

        Raises:
            FileExistsError: 保存先がすでに存在し、overwrite が False の場合。
            OSError: 保存先に書き込めない場合。
        """
        return self._editable_reader()._save_input(filename, overwrite=overwrite)

    def get_absorber(self) -> int:
        """Absorber の先頭の1始まりの原子行番号を返す。

        未指定時の返り値は1。本体は既定で構造節の先頭原子と同じ原子番号の
        全原子の寄与を計算する。
        """
        return self._reader.get_absorber()

    def get_absorbers(self) -> list[int]:
        """Absorber の1始まりの原子行番号を入力順に返す。未指定時の返り値は [1]。"""
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
        """指定された出力接頭辞を返す。

        未指定時の返り値は空文字列。本体は既定の接頭辞 fdmnes_out を使う。
        """
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
