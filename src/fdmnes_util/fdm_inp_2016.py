#!/usr/bin/env python3
#
# SAE原本: sae/fdmnes/inp.py
# 以下はSAE原本の冒頭コメントを原文のまま保存したものです。
# 原本に記された旧仕様・旧クラス名は現在のAPI仕様を意味しません。
# ---- SAE original header (verbatim) ----
# -*- coding: utf-8 -*-
###############################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
#  Method --- ReadVaspPoscar
#  Method --- ReadFdmInp
#  Method --- ReaMxDatMethod -- ReadMxDat
#                            -- ReadMxDftscf
#                            -- ReadMxOut
#                            -- ReadMxPdos
#                            -- ReadMxTdos
#  Method --- ReadRmcpotCfg
#  Method --- ReadPwIn
#
###############################################################################
#
# FDMNES
# *.in ファイル
#
# 主に Crystal の部分の解析と読み込み
#
###############################################################################
#
# 2018.08.15
#  Python2/3 両対応
#
# 2015.11.20
#  convolution 用の結晶構造情報が無いファイルに対する対応
#
# 2015.08.25
#  統合化&Method でいろいろと分離
#
# 2015.08.20
#  Read.py との統合化のためのすりあわせ
#  position のソートルーチンの追加＆分離
#
# 2015.08.19
#  cellparam の基本並進ベクトル変換を ASE の coorsys を採用
#
# 2015.06.24
#  allsite 計算をしているか否かの判断を*.inp かおこなう
#
# 2015.06.19
#   読み込むタグをいくつか追加
#   コメントアウトの処理
#   タグ名とタグの内容が同一行でも対応可能に
#
# 2015.05.19 startup
#   cellpar(a,b,c,alpha,beta,gamma) --> cell(基本並進) への変換が意外に鬼門
#   ---> とりあえずこのルーチンの開発は一旦サスペンド
#
###############################################################################
# トップディレクトリ関係のエラーは ImportError ではキャッチ出来ない
###############################################################################
# import gzip
# import os
# import copy
# import SpaceGroupEnvironment as SGE
# for coorsys
# suing coorsys
###############################################################################
##########################################################################
#   name = 'POSCAR.inp'
##########################################################################
#   out = ReadFdmInp(name,sort=True)
#   cal = np.cos(alpha * np.pi / 180.0)
#   cbe = np.cos(beta * np.pi / 180.0)
#   cga = np.cos(gamma * np.pi /180.0)
#   sga = np.sin(gamma * np.pi /180.0)
#   t = np.array([
#                 [a, b * cga, c * cbe],\
#                 [0, b * sga, c * (cal - cbe * cga) / sga],\
#                 [0, 0, c * np.sqrt(1 - cal**2 -cbe**2 - cga**2 +\
#                                    2 * cal * cbe * cga) / sga],\
#                ]).transpose()
#   out.sort_atoms_index_j()
#   out.sort_atoms_number_j()
#   out.sort_fix()
#       print "NAME",name
# Copyright Kengo NAKADA; SAE class library.
# ---- End of SAE original header ----
# SAE source: sae/fdmnes/inp_writer.py
# ---- SAE original header ----
# -*- coding: utf-8 -*-
################################################################################
# VASP to FDMNES crystal 情報
#
# 構造ファイル & INPUT file
#
# (注意)
#  1) ASE のルーチン(cellconst) を使っている
#  2) ASE のmodule を呼び出している
#  3) atoms は ASE オブジェクトが前提
#
# FDvasp2fdm.py がベース --> class 化
#
################################################################################
################################################################################
#
################################################################################
## using cellconst
# from ase.io.xyz import *
################################################################################
# atoms.write('POSCAR.pdb',format='pdb')
# print atoms.positions
# print ""
# print atoms.cell
# print ""
# print atoms.get_scaled_positions()
# fdm.write_fdmnes(atoms=atoms, MOL=MOL)
# Copyright Kengo NAKADA; SAE class library.
# ---- End of SAE original header ----
"""FDMNES の計算入力 ``*.inp`` を2016年形式で読む。

FdmInp2016 はキーワードと結晶・分子などの構造節を読み、SAE のテンプレートで計算入力も書き出す。
"""
from pathlib import Path

from .fdm_structure import FdmStructure


class FdmInp2016:
    """FDMNES の計算入力 `*.inp` を2016年形式で読み書きする。

    Crystal 節のない入力にも対応する。元の行とキーワードごとの値を保持する。

    Attributes:
        path: 対象ファイルのパス。
        lines: 改行を除いた元の入力行。
        tags: 認識したキーワードと各キーワードの値。
    """

    KEYWORDS = {
        "filout",
        "spin",
        "magnetism",
        "allsite",
        "energpho",
        "energygpho",
        "convolution",
        "conv_out",
        "calculation",
        "nonexc",
        "crystal",
        "molecule",
        "absorber",
    }

    def __init__(self, filename="read_pdb.inp", *, _keywords=None):
        """計算入力から対応するキーワードと値を読む。

        Args:
            filename: FDMNES 計算入力のパス。
        """
        self.path = Path(filename)
        self.lines = self.path.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines()

        keywords = self.KEYWORDS
        if _keywords is not None:
            keywords = _keywords
        self.tags = {}
        self._last_record_offsets = {}
        current_keyword = None

        for line in self.lines:
            # FDMNES input files may contain inline explanations.
            content = line.split("!", 1)[0]
            content = content.split("#", 1)[0]
            content = content.strip()

            if not content:
                continue

            words = content.split()
            keyword = words[0].lower()
            if keyword in ("fileout", "file_out", "fil_out"):
                keyword = "filout"

            if keyword == "end":
                break

            if keyword in keywords:
                current_keyword = keyword
                values = self.tags.setdefault(keyword, [])
                self._last_record_offsets[keyword] = len(values)

                if len(words) > 1:
                    value = " ".join(words[1:])
                    values.append(value)
                continue

            # Values on subsequent lines belong to the preceding keyword.
            if current_keyword is not None:
                self.tags[current_keyword].append(content)

    def _last_record(self, keyword):
        # SAE replaces the previous scalar value when a keyword is repeated.
        """同じキーワードが複数ある場合に、最後の出現に対応するデータ行を返す。"""
        offset = self._last_record_offsets.get(keyword, 0)
        return self.tags.get(keyword, [])[offset:]

    def get_filout(self):
        """`Filout` の出力接頭辞を返す。

        Returns:
            str: 出力接頭辞。指定がなければ空文字列。
        """
        values = self._last_record("filout")
        if values:
            return values[0]
        return ""

    def get_absorber(self) -> int:
        """1始まりの吸収原子インデックスを返す。省略時は1。

        Returns:
            Absorber で指定した原子インデックス。省略時は1。

        Raises:
            ValueError: Absorber の値に正の整数が指定されていない場合。
        """
        if "absorber" not in self.tags:
            return 1
        values = self._last_record("absorber")
        if not values:
            raise ValueError("Absorber requires a positive atom index")
        try:
            index = int(values[0])
        except ValueError as error:
            raise ValueError("Absorber requires a positive atom index") from error
        if index < 1:
            raise ValueError("Absorber requires a positive atom index")
        return index

    def get_ispin(self):
        """入力で指定したスピン数を返す。

        Returns:
            int: Spin または Magnetism があれば2、なければ1。
        """
        if "spin" in self.tags or "magnetism" in self.tags:
            return 2
        return 1

    def get_allsite(self):
        """全サイト計算の指定があるかを返す。

        Returns:
            bool: Allsite があれば True。
        """
        return "allsite" in self.tags

    def get_energygpho(self):
        """光子エネルギー基準で計算する指定があるかを返す。

        Returns:
            bool: Energpho または Energygpho があれば True。
        """
        return "energpho" in self.tags or "energygpho" in self.tags

    def get_nonexc(self):
        """`Nonexc` が指定されているかを返す。

        Returns:
            bool: 対象のキーワードがあれば True。
        """
        return "nonexc" in self.tags

    def get_convolution(self):
        """畳み込みの指定があるかを返す。

        Returns:
            bool: Convolution があれば True。
        """
        return "convolution" in self.tags

    def get_conv_out(self):
        """`Conv_out` に指定されたファイル名を返す。

        Returns:
            str: 畳み込み出力の指定値。なければ空文字列。
        """
        values = self._last_record("conv_out")
        if values:
            return values[0].split()[0]
        return ""

    def get_calculation(self):
        """最後の `Calculation` ブロックの先頭ファイル名を返す。

        Returns:
            str: Calculation の値。なければ空文字列。
        """
        values = self._last_record("calculation")
        if values:
            return values[0].split()[0]
        return ""

    def get_cellparam(self):
        """結晶格子の数値があれば先頭6値を返す。

        Returns:
            list[float] | None: 格子の6パラメーター。記録がなければ None。
        """
        entries = self.tags.get("crystal", [])
        for row in entries:
            tokens = row.split()[:6]
            try:
                numbers = []
                for token in tokens:
                    numbers.append(float(token))
            except ValueError:
                continue

            if len(numbers) == 6:
                return numbers

        return None

    def get_crystal_atoms(self):
        """FDMNES の `Crystal` 節から ASE の周期構造を作る。

        Crystal の次の6値は格子長と格子角。後続行は原子番号と分率座標3成分で、次のキーワードまでが構造節となる。

        Returns:
            ase.Atoms: 分率座標を持つ周期構造。

        Raises:
            ValueError: Crystal 節がないか書式が不正な場合。
            ImportError: ASE がインストールされていない場合。
        """
        crystal_lines = self._get_structure_lines("crystal")
        if not crystal_lines:
            raise ValueError("No Crystal section was found")

        cell_values = self.get_cellparam()
        if cell_values is None:
            raise ValueError("Crystal cell parameters are missing")

        return FdmStructure.crystal_atoms(cell_values, crystal_lines[1:])

    def get_molecule_atoms(self):
        """FDMNES の `Molecule` 節から ASE の孤立構造を作る。

        FDMNES マニュアルに従い、尺度の値が1個なら球座標、2個なら円筒座標、6個なら分率座標として読む。

        Returns:
            ase.Atoms: Å 単位の原子位置を持つ非周期構造。

        Raises:
            ValueError: 尺度または原子座標の記録が不正な場合。
            ImportError: ASE がインストールされていない場合。
        """
        return FdmStructure.molecule_atoms(self._get_structure_lines("molecule"))

    def _get_structure_lines(self, section: str) -> list[str]:
        """構造キーワードの後に続く格子・原子座標の行を取り出す。

        Args:
            section: 小文字で指定する FDMNES の構造キーワード。

        Returns:
            list[str]: 格子と原子座標の記録行。
        """
        lines = []
        in_section = False
        for original_line in self.lines:
            line = original_line.split("!", 1)[0]
            line = line.split("#", 1)[0]
            # The FDMNES examples annotate structure rows with "= a, b, c…".
            line = line.partition("=")[0]
            line = line.strip()
            if not line:
                continue

            fields = line.split()
            keyword = fields[0].lower()
            if not in_section:
                if keyword == "end":
                    break
                if keyword == section:
                    in_section = True
                    if len(fields) > 1:
                        lines.append(" ".join(fields[1:]))
                continue

            if keyword in self.KEYWORDS or keyword == "end":
                break

            # Stop when an unrelated alphabetic keyword starts a new block.
            if fields[0][0].isalpha():
                break

            lines.append(line)
        return lines

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
        """構造節を含む FDMNES 計算入力を組み立てる。

        Args:
            absorber: 1始まりの吸収原子インデックス。
            fileout: 計算出力のファイル名の接頭辞。
            energy_range: エネルギー格子の指定（eV）。
            edge: K や L3 など、出力見出しで使う吸収端ラベル。
            radius: 計算クラスタの半径（Å）。
            molecule: True の場合は Crystal の代わりに Molecule を使う。
            structure_writer: FDMNES 形式の構造節を生成するオブジェクト。

        Returns:
            str: 構造節を含む FDMNES 入力の本文。

        Raises:
            ValueError: 構造ライターが指定されていない場合。
        """
        if structure_writer is None:
            raise ValueError("A structure writer is required")

        # Keep the keyword sequence and defaults of SAE's FDvasp2fdm.py.
        lines = [
            "! FDMNES indata file",
            "",
            "!Nonexc",
            "",
            " Absorber",
            f"  {absorber}",
            "! allsite",
            "",
            " Filout",
            f"  {fileout}",
            "",
            " Range                        ! Energy range of calculation (eV)",
            (
                f"  {energy_range}  ! first energy, step, intermediary "
                "energy, step ..., last energy "
            ),
            "! -15. 0.1 50. 1. 200.        !",
            "",
            "!Energpho",
            "",
            " Edge",
            f"  {edge}",
            "! L23",
            "",
            "!Quadrupole",
            "",
            " Relativism",
            "",
            " Convolution",
            "",
            "!No_Fermi",
            "!Efermi",
            "!  -6.0",
            "!Estart",
            "! -10.0",
            "",
            "!SCF",
            "!R_self",
            "! 5.0",
            "!N_self",
            "! 100",
            "!P_self",
            "! 0.05",
            "!Delta_E_conv",
            "! 0.01",
            "",
            "!Magnetism",
            "!SCF_mag_free",
            "",
            "!Hubbard",
            "! 0.0 6.3 0.0",
            "",
            "!TDDFT",
            "",
            "!Green",
            "",
            (
                " Radius                       ! Radius of the cluster "
                "where final state calculation is performed"
            ),
            (
                f"   {radius}  ! For a good calculation, this radius "
                "must be increased up to 6 or 7 Angstroems"
            ),
            "",
            " Memory_save",
            "",
        ]
        # The structure section is produced by its own file-format writer.
        structure_content = structure_writer.render(molecule=molecule)
        lines.extend(structure_content.rstrip("\n").splitlines())
        lines.extend(
            [
                "",
                "!Cif_file",
                "!  POSCAR.cif",
                "",
                " Density",
                "  state_all",
                "",
                "!Adimp",
                "! 0.20",
                "",
                " End",
                "",
            ]
        )
        return "\n".join(lines) + "\n"

    @staticmethod
    def write(filename: str | Path = "read_pdb.inp", **kwargs) -> Path:
        """FDMNES の計算入力を書き出す。

        Args:
            filename: 対象ファイルのパス。
            **kwargs: 対象のメソッドに渡す追加のキーワード引数。

        Returns:
            Path: 計算入力の保存先。
        """
        destination = Path(filename)
        content = FdmInp2016.render(**kwargs)
        destination.write_text(content, encoding="utf-8")
        return destination
