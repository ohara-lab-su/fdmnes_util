#!/usr/bin/env python3
#
# SAE原本: sae/fdmnes/conv.py
# 以下はSAE原本の冒頭コメントを原文のまま保存したものです。
# 原本に記された旧仕様・旧クラス名は現在のAPI仕様を意味しません。
# ---- SAE original header (verbatim) ----
# -*- coding: utf-8 -*-
###############################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# FDMNES
# *_conv.txt ファイル( pw.x 入力ファイル 読み込み)
#
###############################################################################
#
# 2018.08.15
#  Python2/3 両対応
#
# 2015.07.22
#  入力ファイル名にsuffixを付けても、つけなくても(別オプションでsuffix指定)
#  どちらでも動作するように変更。
#
# 2015.07.01
#  平均化ルーチンで重み(平均する際に割る数)を引数に追加
#
# 2015.06.30
#   == Noneo --> is None
#
# 2015.05.21 startup
#
###############################################################################
# トップディレクトリ関係のエラーは ImportError ではキャッチ出来ない
###############################################################################
# import gzip
# import re
# sys.path.append('../..')
# import SpaceGroupEnvironment as SGE
###############################################################################
###############################################################################
# ラベル等のフォントサイズ
# レジェンドのフォントサイズ
# 軸の太さを設定。目盛りは変わらない
# for portrait
###############################################################################
###############################################################################
#   print name,suffix
#   plot_fdm_xas(eng,xas)
#   print "NAME",name
# Copyright Kengo NAKADA; SAE class library.
# ---- End of SAE original header ----
"""Read the convolved XAS spectrum written to ``*_conv.txt`` by FDMNES."""

from pathlib import Path

import numpy as np


class FdmConv:
    """Retain the energy axis and all absorption columns of one output file."""

    def __init__(self, filename):
        """Read a convolved XAS file.

        Args:
            filename: Path to the FDMNES output file.

        Raises:
            ValueError: If the input has too few numerical columns.
        """
        self.path = Path(filename)

        with self.path.open(encoding="utf-8", errors="replace") as file:
            self.header = file.readline().strip()

        self.values = np.loadtxt(self.path, skiprows=1, ndmin=2)
        if self.values.shape[1] < 2:
            raise ValueError("FDMNES convolution output requires an XAS column")

        self.energy = self.values[:, 0]
        self.xas = self.values[:, 1:]

    def get_eng(self):
        """Return the energy axis in the file-defined reference frame."""
        return self.energy

    def get_xas(self, spin=0):
        """Return the requested absorption column.

        Args:
            spin: Zero-based index of the absorption column.

        Returns:
            numpy.ndarray: Absorption intensity values.
        """
        return self.xas[:, spin]

    @staticmethod
    def write_spectrum(filename, spectrum):
        """Write the SAE two-column convolved average.

        Args:
            filename: Destination convolution filename.
            spectrum: Energy and intensity arrays in the original reference.
        """
        np.savetxt(
            filename,
            np.column_stack(spectrum),
            fmt="  %14.8f %14.8f",
            header=" ",
            comments="",
        )
