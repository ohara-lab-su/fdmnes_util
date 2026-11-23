"""FDMNES の計算・畳み込み入力 ``*.inp`` を2026年形式で読み、作成・編集する。

FdmInp2026 は複数の吸収サイト、畳み込み条件、拡張 SD 設定を扱う。POSCAR を使う場合は vasp_util と FdmStructure で入力の構造節を作る。
"""
import re
from collections.abc import Iterable, Sequence
from math import isfinite
from pathlib import Path

from .fdm_inp_2016 import FdmInp2016
from .fdm_structure import FdmStructure


class FdmInp2026:
    """FDMNES の計算入力 `*.inp` の2026年形式を読み書きし、入力ブロックを編集する。"""
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

    _ALIASES = {"file_out": "filout", "fileout": "filout", "fil_out": "filout"}
    _SINGLE_ROW = {
        "absorber",
        "conv_out",
        "edge",
        "filout",
        "lmax_dosout",
        "n_self",
        "r_self",
        "radius",
        "range",
        "spgroup",
        "z_absorber",
    }
    _FLAGS = {"convolution", "density_comp", "green", "scf"}
    _BLOCK_HEADERS = (
        _SINGLE_ROW
        | _FLAGS
        | {
            "atom",
            "calculation",
            "cif_file",
            "crystal",
            "density",
            "molecule",
            "polarise",
            "polarisation",
            "surface",
            "tddft",
        }
    )

    def __init__(self, filename="read_pdb.inp"):
        """既存の計算入力を読み込む。ファイル名が None の場合は空の入力から始める。"""
        self.path = None
        text = ""
        if filename is not None:
            self.path = Path(filename)
            with self.path.open(
                encoding="utf-8", errors="replace", newline=""
            ) as stream:
                text = stream.read()

        # ファイルを読み直さず、既存の取得メソッドに編集中の行と索引を渡す。
        self._reader = object.__new__(FdmInp2016)
        self._reader.path = self.path
        self._reader.lines = self.lines = []
        self._reader.tags = self.tags = {}
        self._reader._last_record_offsets = {}
        self._set_text(text)

    def _set_text(self, text):
        """入力の行末を保持し、キーワードの索引を作り直す。"""
        self._lines = text.splitlines(keepends=True)
        self._newline = "\n"
        if any(line.endswith("\r\n") for line in self._lines):
            self._newline = "\r\n"
        if self._lines and not self._lines[-1].endswith(("\n", "\r")):
            self._lines[-1] += self._newline
        self._index_input()

    def _index_input(self):
        """編集中の入力から、参照を共有する行一覧とキーワード索引を更新する。"""
        self.lines[:] = [line.rstrip("\r\n") for line in self._lines]
        self.tags.clear()
        offsets = self._reader._last_record_offsets
        offsets.clear()
        current_keyword = None
        for line in self.lines:
            content = self._content(line)
            if not content:
                continue
            words = content.split()
            keyword = words[0].lower()
            keyword = self._ALIASES.get(keyword, keyword)
            if keyword == "end":
                break
            if keyword in self.KEYWORDS or keyword in self._BLOCK_HEADERS:
                current_keyword = keyword
                records = self.tags.setdefault(keyword, [])
                offsets[keyword] = len(records)
                if len(words) > 1:
                    records.append(" ".join(words[1:]))
            elif current_keyword is not None:
                self.tags[current_keyword].append(content)

    def _set_poscar(self, filename, *, molecule=False):
        """vasp_util で POSCAR を読み、計算入力に使う構造節を生成する。"""
        from vasp_util.vasp_poscar import VaspPoscar

        structure = FdmStructure(VaspPoscar(str(filename)))
        self._set_text(structure.render(molecule=molecule))

    def get_absorber(self) -> int:
        """先頭の吸収サイトを返す。"""
        return self._get_absorbers()[0]

    def _get_absorbers(self):
        """最後の Absorber ブロックを読み、吸収原子インデックスのリストを返す。"""
        if "absorber" not in self.tags:
            return [1]
        return self._read_absorbers(self._reader._last_record("absorber"))

    def _get_calculations(self):
        """最後の Calculation ブロックからファイル名と畳み込み条件を返す。"""
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
            list[tuple]: (ファイル名, 重み, シフト, カットオフ) の並び。 省略された数値は None。
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
        """複数の吸収サイトと SD 出力設定を含む計算入力を生成する。"""
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
            calculations: (生 XAS ファイル, 重み, シフト) の順序付きデータ。 相対パスは FDMNES の実行フォルダ基準。シフトは eV。
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

    @staticmethod
    def _content(line):
        """コメントと前後の空白を除いた入力行の内容を返す。"""
        return line.partition("!")[0].partition("#")[0].strip()

    def _end_index(self):
        """計算入力の終端 End の行番号を返す。なければ行数を返す。"""
        for index, line in enumerate(self._lines):
            if self._content(line).lower() == "end":
                return index
        return len(self._lines)

    def _set_block(self, keyword, *rows, old_rows=None):
        """ブロックを追加するか、既存のブロックを置き換える。

        Args:
            keyword: FDMNES のキーワード。大文字・小文字は不問。
            *rows: 値を一行ずつ指定する。文字列は一行、そのほかの イテラブルは空白区切りの一行として出力する。
            old_rows: 既存ブロックのデータ行数。既知の1行型とフラグは 省略可。可変長・任意のブロックを置換するときは指定する。

        Returns:
            FdmInp2026: 更新した入力。
        """
        self._edit_block(keyword, rows, old_rows)
        self._index_input()
        return self

    def _set_structure(self, cell, *atoms, molecule=False, old_rows=None):
        """格子行と原子行を、指定された種類の構造節に書く。"""
        keyword = "Crystal"
        if molecule:
            keyword = "Molecule"
        self._set_block(keyword, cell, *atoms, old_rows=old_rows)

    def _remove_block(self, keyword, *, old_rows=None):
        """指定のブロックを取り除く。行数の規則は set_block と同じ。"""
        self._edit_block(keyword, None, old_rows)
        self._index_input()
        return self

    def _edit_block(self, keyword, rows, old_rows):
        """指定ブロックを編集し、他のブロックと End 以降の行を保持する。"""
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", keyword):
            raise ValueError(f"Invalid FDMNES keyword: {keyword}")
        key = self._ALIASES.get(keyword.lower(), keyword.lower())
        if key == "end":
            raise ValueError("End is managed by the input document")

        rendered = []
        for row in rows or ():
            if isinstance(row, Iterable) and not isinstance(row, str):
                value = " ".join(str(token) for token in row)
            else:
                value = str(row)
            if "\n" in value or "\r" in value or not self._content(value):
                raise ValueError("Each value must occupy a single nonempty record")
            if self._content(value).lower() == "end":
                raise ValueError("End is managed by the input document")
            rendered.append(f"  {value}{self._newline}")

        end = self._end_index()
        matches = []
        for index, line in enumerate(self._lines[:end]):
            current = self._content(line).lower()
            if self._ALIASES.get(current, current) == key:
                matches.append(index)
            elif current and key in self._SINGLE_ROW:
                first = current.split()[0]
                if self._ALIASES.get(first, first) == key:
                    raise ValueError(f"Use a separate keyword line for {keyword}")
        if len(matches) > 1:
            raise ValueError(f"Multiple {keyword} blocks in input")
        if not matches:
            if rows is not None:
                self._lines[end:end] = [
                    keyword + self._newline,
                    *rendered,
                    self._newline,
                ]
            return self

        if old_rows is None:
            # 認識できる固定長ブロック以外は、置換範囲を呼び出し側に指定してもらう。
            if key in self._SINGLE_ROW:
                old_rows = 1
            elif key in self._FLAGS:
                old_rows = 0
            else:
                raise ValueError(f"Specify old_rows to replace {keyword}")
        if type(old_rows) is not int or old_rows < 0:
            raise ValueError("old_rows must be a nonnegative integer")
        start = matches[0] + 1
        record_indices = []
        for index in range(start, end):
            if len(record_indices) == old_rows:
                break
            content = self._content(self._lines[index]).lower()
            if not content:
                continue
            if self._ALIASES.get(content, content) in self._BLOCK_HEADERS:
                raise ValueError(f"Incomplete {keyword} block before {content}")
            record_indices.append(index)
        if len(record_indices) != old_rows:
            raise ValueError(f"Incomplete {keyword} block")

        # 対応する行をその場で置換する。間にある空行やコメント行は残す。
        common = min(len(rendered), len(record_indices))
        for offset in range(common):
            self._lines[record_indices[offset]] = rendered[offset]
        for index in reversed(record_indices[common:]):
            del self._lines[index]
        if rows is None:
            del self._lines[matches[0]]
            return self
        if common:
            start = record_indices[common - 1] + 1
        self._lines[start:start] = rendered[common:]
        return self

    def _set_radius(self, radius, *changes):
        """半径（Å）と、切替エネルギー（eV）・次の半径（Å）の組を設定する。"""
        radius = float(radius)
        if not isfinite(radius) or radius <= 0:
            raise ValueError("Radius must be positive and finite")
        values = [radius]
        previous_energy = float("-inf")
        for energy, next_radius in changes:
            energy, next_radius = float(energy), float(next_radius)
            if not isfinite(energy) or energy <= previous_energy:
                raise ValueError("Radius transition energies must increase")
            if not isfinite(next_radius) or next_radius <= 0:
                raise ValueError("Radius must be positive and finite")
            values.extend((energy, next_radius))
            previous_energy = energy
        return self._set_block("Radius", values)

    def _render_input(self):
        """入力テキストを返し、必要な場合に終端の End を補う。"""
        content = "".join(self._lines)
        if self._end_index() == len(self._lines):
            return content + "End" + self._newline
        return content

    def _save_input(self, filename, *, overwrite=False):
        """入力を保存してパスを返す。上書きは明示指定する。"""
        path = Path(filename)
        mode = "x"
        if overwrite:
            mode = "w"
        with path.open(mode, encoding="utf-8", newline="") as stream:
            stream.write(self._render_input())
        return path
