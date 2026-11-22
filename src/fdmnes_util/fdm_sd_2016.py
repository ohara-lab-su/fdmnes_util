#!/usr/bin/env python3
#
# SAE原本: sae/fdmnes/sd_2016.py
# 以下はSAE原本の冒頭コメントを原文のまま保存したものです。
# 原本に記された旧仕様・旧クラス名は現在のAPI仕様を意味しません。
# fmt: off
# ---- SAE original header (verbatim) ----
# -*- coding: utf-8 -*
###############################################################################
# K.NAKADA, kengo.nakada@gmail.com
#  〜 2016.01.08 までのバージョンのsdファイルの解析
#  +
#  〜 新しいバージョンの sdファイル形式に対応
#
# FDMNES
#   *_sd*.txt ファイル( pw.x 入力ファイル 読み込み)
#   Ver_0.0.2 以降 FDMNS のバージョンの違いによるログの違いを吸収
#
# Energy
# Int_t
# n(0, 0)
# Intn(0, 0)
# n_l(0)
# Intn_l(0)
# n(1, -1)
# Intn(1, -1)
# n(1, 0)
# Intn(1, 0)
# n(1, 1)
# Intn(1, 1)
# n_l(1)
# Intn_l(1)
# n(2, -2)
# Intn(2, -2)
# n(2, -1)
# Intn(2, -1)
# n(2, 0)
# Intn(2, 0)
# n(2, 1)
# Intn(2, 1)
# n(2, 2)
# Intn(2, 2)
# n_l(2)
# Intn_l(2)
#
###############################################################################
#
# 2020.07.17 (Ver_0.0.2)
#  2016.08.01 以降に sd? のナンバリングルールが変わったのでそれに対する対応
#  - バージョンチェック(ReadFdmBav.py) を用いる
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
"""Read the column-ordered FDMNES 2016 SD output format."""
# fmt: on

import re
from pathlib import Path

import numpy as np


class FdmSd2016:
    """Read DOS projections and spin channels from a 2016 SD file."""

    def __init__(self, filename, *, ispin=1, weight=None):
        """Load a 2016-format SD output.

        Args:
            filename: Path to an SD output file.
            ispin: Number of spin channels (one or two).
            weight: Optional normalization divisor.

        Raises:
            ValueError: If the input header or number of columns is invalid.
        """
        self.path = Path(filename)
        lines = self.path.read_text(errors="replace").splitlines()
        if len(lines) < 2:
            raise ValueError("Incomplete SD file")

        self.header = lines[0].split()
        found_orbital_header = False
        for token in self.header:
            if "n(" in token:
                found_orbital_header = True
                break
        if not found_orbital_header:
            raise ValueError("Not 2016 SD format")

        self.ispin = int(ispin)
        if self.ispin not in (1, 2):
            raise ValueError("ispin must be 1 or 2")

        tmp = self.header[-1]
        tmp = re.sub(r".*\(", "", tmp)
        try:
            # nonmag 版
            self.lmax = int(re.sub(r"\).*", "", tmp))
        except ValueError:
            # spin 版
            try:
                self.lmax = int(re.sub(r",.*\).*", "", tmp))
            except ValueError as error:
                raise ValueError("Cannot detect 2016 lmax") from error
        if self.lmax < 0:
            raise ValueError("Cannot detect 2016 lmax")

        # 列名と同じ読込みから数値行を解析する。
        self.values = np.loadtxt(lines[1:], ndmin=2)
        tmmax = 0
        for l in range(self.lmax + 1):
            tmmax += (2 * l + 1) * self.ispin
        total_orbit = tmmax
        total_row = 1 + self.ispin + total_orbit * 2 + (l + 1) * 2 * self.ispin
        if len(self.header) != total_row or self.values.shape[1] != total_row:
            raise ValueError(
                f"2016 SD column mismatch: header has {len(self.header)} columns, "
                f"data has {self.values.shape[1]}, expected {total_row}"
            )

        if weight is not None:
            divisor = float(weight)
            if divisor == 0:
                raise ValueError("weight must be nonzero")
            # Energy は除く
            self.values[:, 1:] /= divisor

        self.energy = self.values[:, 0].copy()
        self._partial = {}
        self._ldos = {}
        self._intldos = {}
        self._total = {}
        self._integrated_total = {}
        # INTTDOS  Int_t(u), Int_t(d)
        row = 1
        for s in range(self.ispin):
            self._total[s] = np.zeros_like(self.energy)
            self._integrated_total[s] = self.values[:, row].copy()
            row += 1
        # PDOS & INTPDOS
        for ll in range(self.lmax + 1):
            # m,spin成分分解 n(0,0),,,
            for m in range(-ll, ll + 1):
                for s in range(self.ispin):
                    self._partial[ll, m, s] = self.values[:, row]
                    # 個別軌道の積分列は数値表に保持する。
                    row += 2
            # l軌道のsum n_l(0,0),,,
            for s in range(self.ispin):
                self._ldos[ll, s] = self.values[:, row]
                self._total[s] += self.values[:, row]
                row += 1
                self._intldos[ll, s] = self.values[:, row]
                self._integrated_total[s] += self.values[:, row]
                row += 1

    def get_densities(self):
        """Return all density and integral columns in file order."""
        return self.values[:, 1:]

    def get_eng(self):
        """Return the energy axis."""
        return self.energy

    def get_lmax(self):
        """Return the highest angular-momentum channel."""
        return self.lmax

    def get_ispin(self):
        """Return the number of spin channels."""
        return self.ispin

    @staticmethod
    def _spin_index(spin):
        """Translate the spin names accepted by the original SAE SD reader.

        Args:
            spin: Zero-based spin index or its SAE alias.

        Returns:
            int: Zero-based spin index.

        Raises:
            KeyError: If the spin name is unrecognized.
        """
        if isinstance(spin, str):
            indices = {"up": 0, "non": 0, "nonmag": 0, "dn": 1, "down": 1}
            return indices[spin]
        return spin

    def get_ldos(self, l=0, spin=0):
        """Return the stored angular-momentum DOS channel.

        Args:
            l: Angular momentum index or the orbital group name s, p, d, or f.
            spin: Zero-based spin index or an SAE spin name, such as up or down.

        Returns:
            numpy.ndarray: One value per energy point.

        Raises:
            ValueError: If the orbital group name is invalid.
            KeyError: If the requested orbital group or spin is unavailable.
        """
        if isinstance(l, str):
            l = "spdf".index(l)
        return self._ldos[(l, self._spin_index(spin))]

    def get_intldos(self, l=0, spin=0):
        """Return the stored integral of an angular-momentum DOS channel.

        Args:
            l: Angular momentum index or the orbital group name s, p, d, or f.
            spin: Zero-based spin index or an SAE spin name, such as up or down.

        Returns:
            numpy.ndarray: One value per energy point.

        Raises:
            ValueError: If the orbital group name is invalid.
            KeyError: If the requested orbital group or spin is unavailable.
        """
        if isinstance(l, str):
            l = "spdf".index(l)
        return self._intldos[(l, self._spin_index(spin))]

    def get_pdos(self, l=0, m=0, lm=None, spin=0):
        """Return the density projected onto a single orbital and spin.

        Args:
            l: Angular momentum index.
            m: Magnetic quantum number.
            lm: Optional orbital name overriding l and m.
            spin: Zero-based spin index or an SAE spin name.

        Returns:
            numpy.ndarray: Orbital densities on the file's energy grid.

        Raises:
            KeyError: If the orbital or spin channel is unavailable.
        """
        orbitals = {
            "s": (0, 0),
            "px": (1, 1),
            "py": (1, -1),
            "pz": (1, 0),
            "dxy": (2, -2),
            "dyz": (2, -1),
            "dz2": (2, 0),
            "d3z2-r2": (2, 0),
            "dxz": (2, 1),
            "dx2-y2": (2, 2),
        }
        if lm is not None:
            key = lm.lower().replace("_", "")
            l, m = orbitals[key]
        return self._partial[(l, m, self._spin_index(spin))]

    def get_tdos(self, spin=0):
        """Return the sum of angular-momentum DOS channels for one spin.

        Args:
            spin: Zero-based spin index or an SAE spin name.

        Returns:
            numpy.ndarray: Total or integrated total at each energy point.

        Raises:
            KeyError: If the requested spin channel is unavailable.
        """
        return self._total[self._spin_index(spin)]

    def get_inttdos(self, spin=0):
        """Return the SAE sum of the leading integral and per-group integrals.

        Args:
            spin: Zero-based spin index or an SAE spin name.

        Returns:
            numpy.ndarray: Total or integrated total at each energy point.

        Raises:
            KeyError: If the requested spin channel is unavailable.
        """
        return self._integrated_total[self._spin_index(spin)]
