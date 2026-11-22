#!/usr/bin/env python3
#
# SAE原本: sae/fdmnes/sd_2020.py
# 以下はSAE原本の冒頭コメントを原文のまま保存したものです。
# 原本に記された旧仕様・旧クラス名は現在のAPI仕様を意味しません。
# fmt: off
# ---- SAE original header (verbatim) ----
# -*- coding: utf-8 -*
###############################################################################
# K.NAKADA, kengo.nakada@gmail.com
# FDMNES 2020.06.16-2 を解析できるように修正したバージョン
# それ以前特に 2016.01.08 などとは大きく異なるので注意
# データ読み込み整理に Pandas を使って大幅に簡略化
#
# FDMNES
#   *_sd*.txt ファイル( pw.x 入力ファイル 読み込み)
#   Ver_0.0.2 以降 FDMNS のバージョンの違いによるログの違いを吸収
#
# 2016,2019 までと異なっていて、積算部分状態密度の情報がごっそり消されている。
#
# Energy
# (0, 0)  s
#        Int(s)
# (1, 1) px
# (1,-1) py
# (1, 0) pz
#        p
#        Int(p)
# (2, 2) dx2 - y2
# (2, 0) dz2
# (2,-1) dyz
# (2, 1) dxz
# (2,-2) dxy
#        d
#        Int(d)
# total
# Int(total)
#
###############################################################################
#
# 2020.07.17-19 (Ver_0.0.2)
#  2016.08.01 以降に sd? のナンバリングルールが変わったのでそれに対する対応
#  - バージョンチェック(ReadFdmBav.py) を用いる
#  - sd0 ファイルそれ自体のフォーマットが2020では大きく変わっている
#  - pandas 利用に全面書き換え
#
# 2018.08.15
#  Python2/3 両対応
#
# 2015.09.11
#   lmax 判定の新バージョン(2015.08.18)が
#   spin に対して動作が不完全だったので修正
#
# 2015.09.09
#   TDOS および INTTDOS が未完成だったので修正した
#
# 2015.09.08
#   DOS の最大レンジ自動取得
#
# 2015.09.08
#   非平均化もーどで DOS の Weight の計算が出来るようにした
#
# 2015.09.08
#  sd 平均化情報の出力（ファイル出力）を修正
#  それにあせて sd ファイルのヘッダー出力なども追加
#
# 2015.09.07
#  pdos を軌道成分名 or l,m の指定でゲットできるようにした
#
# 2015.08.18
#  lmax の抽出を _bav.txt ファイルではなくて 実際に計算している _sd*.txt
#  のヘッダから行うように変更。それに伴って _bav.txt の利用を前面停止
#  ただし、内部的には bavname はそのまま用いる(averageなどで使う)
#  --> 明示的に指定しない限り bavname は自動で sdname となる
#
# 2015.07.02
#  spin,ylm,intt,等の全出力の対応を含めた一般化
#
# 2015.07.01
#  spin対応版 startup
#
# 2015.07.01
#  平均化ルーチンで重み(平均する際に割る数)を引数に追加
#  --> 平均化ルーチンはコンストラクタで処理
#
# 2015.07.01
#   absorber 複数のファイル結合モードを追加
#
# 2015.05.21
#   startup (スピン未対応)
#
###############################################################################
# トップディレクトリ関係のエラーは ImportError ではキャッチ出来ない
###############################################################################
# import gzip
# sys.path.append('../..')
# import SpaceGroupEnvironment as SGE
###############################################################################
#   name = 'Fe'
###############################################################################
#tmp = sd.get_pdos(l=0,lm='s', spin=0)
#print(tmp)
#   eng = conv.get_eng()
#   xas = conv.get_xas()
#   print "NAME",name
# Copyright Kengo NAKADA; SAE class library.
# ---- End of SAE original header ----
"""Read the 2020 FDMNES SD layout with named DOS columns."""
# fmt: on

from pathlib import Path

import numpy as np


class FdmSd2020:
    """Read orbital-resolved density of states from a 2020-format SD file.

    The first line contains orbital column names. The numerical columns are
    retained without reordering, so the integrated columns remain associated
    with the same orbitals as in the original output.

    Attributes:
        path: Path of the SD output file.
        columns: Column labels in their original order.
        values: Numerical data, including the energy column.
        energy: Energy axis in electronvolts.
        lmax: Largest available orbital angular momentum index.
        ispin: Number of spin channels in this format.
    """

    # total と Int(total) は磁性出力でも全スピン共通の一列。
    total_ispin = 1

    ORBITALS = {
        "s": (0, 0),
        # py (l=1, m=-1, spin=0)
        "py": (1, -1),
        # pz (l=1, m=0, spin=0)
        "pz": (1, 0),
        # px (l=1, m=1, spin=0)
        "px": (1, 1),
        # dxy (l=2, m=-2, spin=0)
        "dxy": (2, -2),
        # dyz (l=2, m=-1, spin=0)
        "dyz": (2, -1),
        # dz2 (l=2, m=0, spin=0)
        "dz2": (2, 0),
        # dxz (l=2, m=1, spin=0)
        "dxz": (2, 1),
        # dx2-y2 (l=2, m=2, spin=0)
        "dx2-y2": (2, 2),
    }
    ALIASES = {
        "p_y": "py",
        "p_z": "pz",
        "p_x": "px",
        "d_xy": "dxy",
        "d_yz": "dyz",
        "d_z2": "dz2",
        "d_3z2-r2": "dz2",
        "d_z^2": "dz2",
        "d_xz": "dxz",
        "d_x2-y2": "dx2-y2",
        "d_x^2-y^2": "dx2-y2",
    }

    def __init__(self, filename, *, weight=None):
        """Read a 2020-format density-of-states file.

        Args:
            filename: Path to the SD file, including its suffix.
            weight: Optional divisor for all density and integrated columns.

        Raises:
            ValueError: If the header or column count is inconsistent.
        """
        self.path = Path(filename)
        lines = self.path.read_text(errors="replace").splitlines()
        if len(lines) < 2:
            raise ValueError("Incomplete SD file")

        self.columns = lines[0].split()
        column_count = len(self.columns)
        if self._magnetic_header(self.columns):
            self.ispin = 2
            self.lmax = 2
        elif column_count == 5:
            self.ispin = 1
            self.lmax = 0
        elif column_count == 10:
            self.ispin = 1
            self.lmax = 1
        elif column_count == 17:
            self.ispin = 1
            self.lmax = 2
        else:
            raise ValueError(f"Not a 2020 SD header ({column_count} columns)")

        # 列名と同じ読込みから数値行を解析する。
        self.values = np.loadtxt(lines[1:], ndmin=2)
        if self.values.shape[1] != column_count:
            raise ValueError("SD column count mismatch")

        self._fields = dict(zip(self.columns, self.values.T))

        required = {"Energy", "total", "Int(total)"}
        orbitals = set()
        orbital_groups = ("s", "p", "d")
        for level in range(self.lmax + 1):
            group = orbital_groups[level]
            orbitals.update((group, f"Int({group})"))
        for orbital, (level, _) in self.ORBITALS.items():
            if level <= self.lmax:
                orbitals.add(orbital)
        if self.ispin == 2:
            for suffix in ("_up", "_dn"):
                required.update(f"{orbital}{suffix}" for orbital in orbitals)
        else:
            required.update(orbitals)
        missing = required.difference(self._fields)
        if missing or len(self._fields) != column_count:
            raise ValueError(f"Invalid 2020 SD columns; missing: {sorted(missing)}")

        if weight is not None:
            divisor = float(weight)
            if divisor == 0:
                raise ValueError("weight must be nonzero")
            # Energy は除く
            for name, column in self._fields.items():
                if name != "Energy":
                    column /= divisor

        self.energy = self._fields["Energy"].copy()

    @staticmethod
    def _magnetic_header(columns):
        return len(columns) == 31 and {"s_up", "s_dn"}.issubset(columns)

    def get_densities(self):
        """Return all density and integral columns in file order."""
        if self.columns[0] == "Energy":
            return self.values[:, 1:]
        return np.delete(self.values, self.columns.index("Energy"), axis=1)

    def get_eng(self):
        """Return the energy axis (eV)."""
        return self.energy

    def get_lmax(self):
        """Return the maximum available orbital angular momentum."""
        return self.lmax

    def get_ispin(self):
        """Return the number of spin channels."""
        return self.ispin

    def _spin_suffix(self, spin):
        """実ファイルの軌道列に付くスピンの接尾辞を返す。"""
        if spin in (0, "up", "non", "nonmag"):
            if self.ispin == 1:
                return ""
            return "_up"
        if self.ispin == 1:
            raise ValueError("The verified 2020 SD layout has one spin channel")
        if spin in (1, "dn", "down"):
            return "_dn"
        raise ValueError(f"Unknown SD spin channel: {spin}")

    def get_ldos(self, l=0, spin=0):
        """Return the l-resolved DOS for the requested orbital.

        Args:
            l: Orbital angular momentum index or the name s, p, or d.
            spin: スピン番号、または up・dn・down。

        Returns:
            numpy.ndarray: Density values for the requested orbital.

        Raises:
            ValueError: If spin selects an unavailable channel.
            IndexError: If a numerical angular momentum is out of range.
            KeyError: If the orbital column is absent.
        """
        suffix = self._spin_suffix(spin)
        if isinstance(l, int):
            key = ("s", "p", "d")[l]
        else:
            key = l
        return self._fields[f"{key}{suffix}"]

    def get_intldos(self, l=0, spin=0):
        """Return the stored integral of an angular-momentum DOS channel.

        Args:
            l: Angular momentum index or group name s, p, or d.
            spin: スピン番号、または up・dn・down。

        Returns:
            numpy.ndarray: Integrated densities on the file's energy grid.

        Raises:
            ValueError: If spin selects an unavailable channel.
            IndexError: If a numerical angular momentum is out of range.
            KeyError: If the integrated orbital column is absent.
        """
        suffix = self._spin_suffix(spin)
        if isinstance(l, int):
            key = ("s", "p", "d")[l]
        else:
            key = l
        return self._fields[f"Int({key}){suffix}"]

    def get_pdos(self, l=0, m=0, lm=None, spin=0):
        """Return an (l, m)-resolved orbital contribution.

        Args:
            l: Orbital angular momentum index.
            m: Magnetic quantum number.
            lm: Optional orbital name, such as ``dxy`` or ``p_x``.
            spin: スピン番号、または up・dn・down。

        Returns:
            numpy.ndarray: Partial density values.

        Raises:
            KeyError: If the orbital column does not exist.
            ValueError: If spin selects an unavailable channel.
        """
        suffix = self._spin_suffix(spin)
        if lm is not None:
            orbital_name = lm.lower()
            key = self.ALIASES.get(orbital_name, orbital_name)
        else:
            key = None
            for orbital_name, quantum_numbers in self.ORBITALS.items():
                if quantum_numbers == (l, m):
                    key = orbital_name
                    break

        if key not in self.ORBITALS:
            raise KeyError(f"Orbital absent: {key}")
        return self._fields[f"{key}{suffix}"]

    def get_tdos(self, spin=0):
        """Return the total DOS column written by FDMNES.

        Args:
            spin: スピン指定の有効性を検査する。戻り値は全スピン共通。

        Returns:
            numpy.ndarray: One value per energy point.

        Raises:
            ValueError: If spin selects an unavailable channel.
        """
        self._spin_suffix(spin)
        return self._fields["total"]

    def get_inttdos(self, spin=0):
        """Return the integrated total DOS column written by FDMNES.

        Args:
            spin: スピン指定の有効性を検査する。戻り値は全スピン共通。

        Returns:
            numpy.ndarray: One value per energy point.

        Raises:
            ValueError: If spin selects an unavailable channel.
        """
        self._spin_suffix(spin)
        return self._fields["Int(total)"]
