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
"""FDMNES の状態密度出力 ``*_sdN.txt`` を2020年形式で読む。

FdmSd2020 は列名から非磁性・磁性の形式を選び、元の列順を保ったまま軌道ごとの密度と積分値を取得する。
"""
# fmt: on

from pathlib import Path

import numpy as np


class FdmSd2020:
    """FDMNES の出力 `*_sdN.txt` を2020年形式で読み、軌道別の状態密度を取得する。

    先頭行は軌道列名。数値列の順序を保持して元の軌道と積分列の対応を保つ。

    Attributes:
        path: 対象ファイルのパス。
        columns: 元の順序の列名。先頭はエネルギー列。
        values: 数値データの配列。
        energy: エネルギー値の配列（eV）。
        lmax: 利用できる最大軌道角運動量。
        ispin: スピン数。
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
        """2020年形式の SD 出力を読み込む。

        Args:
            filename: 対象ファイルのパス。
            weight: 密度列と積分列を規格化する除数。省略時は値を変更しない。

        Raises:
            ValueError: 見出しと列数が一致しない場合。
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
        """確認済みの磁性 SD の列数と両スピンの s 軌道列を照合する。"""
        return len(columns) == 31 and {"s_up", "s_dn"}.issubset(columns)

    def get_densities(self):
        """密度と積分の列をファイルの順番で返す。"""
        if self.columns[0] == "Energy":
            return self.values[:, 1:]
        return np.delete(self.values, self.columns.index("Energy"), axis=1)

    def get_eng(self):
        """エネルギー軸を eV 単位で返す。"""
        return self.energy

    def get_lmax(self):
        """利用可能な最大軌道角運動量を返す。"""
        return self.lmax

    def get_ispin(self):
        """スピン数を返す。"""
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
        """指定軌道群の状態密度を返す。

        Args:
            l: 角運動量量子数、または軌道群名。
            spin: スピン番号、または up・dn・down。

        Returns:
            numpy.ndarray: 指定した軌道の状態密度。

        Raises:
            ValueError: 指定されたスピン列がない場合。
            IndexError: 数値で指定した角運動量が範囲外の場合。
            KeyError: 対象の軌道列が存在しない場合。
        """
        suffix = self._spin_suffix(spin)
        if isinstance(l, int):
            key = ("s", "p", "d")[l]
        else:
            key = l
        return self._fields[f"{key}{suffix}"]

    def get_intldos(self, l=0, spin=0):
        """指定した角運動量の状態密度の積分値を返す。

        Args:
            l: 角運動量量子数、または軌道群名。
            spin: スピン番号、または up・dn・down。

        Returns:
            numpy.ndarray: ファイルのエネルギー格子に対応する積分状態密度。

        Raises:
            ValueError: 指定されたスピン列がない場合。
            IndexError: 数値で指定した角運動量が範囲外の場合。
            KeyError: 対象の軌道の積分列が存在しない場合。
        """
        suffix = self._spin_suffix(spin)
        if isinstance(l, int):
            key = ("s", "p", "d")[l]
        else:
            key = l
        return self._fields[f"Int({key}){suffix}"]

    def get_pdos(self, l=0, m=0, lm=None, spin=0):
        """角運動量量子数 l と磁気量子数 m で指定した軌道の射影状態密度を返す。

        Args:
            l: 角運動量量子数、または軌道群名。
            m: 磁気量子数。
            lm: l と m に優先して指定する軌道名。省略可能。
            spin: スピン番号、または up・dn・down。

        Returns:
            numpy.ndarray: 射影状態密度の配列。

        Raises:
            KeyError: 対象の軌道列が存在しない場合。
            ValueError: 指定されたスピン列がない場合。
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
        """FDMNES が出力した全状態密度の列を返す。

        Args:
            spin: スピン指定の有効性を検査する。戻り値は全スピン共通。

        Returns:
            numpy.ndarray: 各エネルギー点につき一つの値。

        Raises:
            ValueError: 指定されたスピン列がない場合。
        """
        self._spin_suffix(spin)
        return self._fields["total"]

    def get_inttdos(self, spin=0):
        """FDMNES が出力した全状態密度の積分列を返す。

        Args:
            spin: スピン指定の有効性を検査する。戻り値は全スピン共通。

        Returns:
            numpy.ndarray: 各エネルギー点につき一つの値。

        Raises:
            ValueError: 指定されたスピン列がない場合。
        """
        self._spin_suffix(spin)
        return self._fields["Int(total)"]
