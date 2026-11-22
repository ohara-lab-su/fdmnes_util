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
"""FDMNES の畳み込み XAS 出力 ``*_conv.txt`` を2016年形式で読む。

FdmConv2016 は先頭行に続くエネルギーと吸収強度を読み、平均スペクトルを SAE の二列書式で保存できる。
"""
from pathlib import Path

import numpy as np


class FdmConv2016:
    """FDMNES の出力 `*_conv.txt` を2016年形式で読み、エネルギー軸と全吸収列を保持する。"""

    def __init__(self, filename):
        """畳み込み XAS ファイルを読み込む。

        Args:
            filename: 対象ファイルのパス。

        Raises:
            ValueError: 入力の数値列が不足している場合。
        """
        self.path = Path(filename)

        with self.path.open(encoding="utf-8", errors="replace") as file:
            self.header = file.readline().strip()
            self.values = np.loadtxt(file, ndmin=2)

        if self.values.shape[1] < 2:
            raise ValueError("FDMNES convolution output requires an XAS column")

        self.energy = self.values[:, 0]
        self.xas = self.values[:, 1:]

    def get_eng(self):
        """ファイルで定義された基準のエネルギー軸を返す。"""
        return self.energy

    def get_xas(self, spin=0):
        """指定した吸収強度列を返す。

        Args:
            spin: 0始まりの吸収強度列の番号。

        Returns:
            numpy.ndarray: 吸収強度の配列。
        """
        return self.xas[:, spin]

    @staticmethod
    def write_spectrum(filename, spectrum):
        """畳み込み XAS の平均を SAE の二列書式で保存する。

        Args:
            filename: 対象ファイルのパス。
            spectrum: ファイルのエネルギー基準でのエネルギーと強度の配列。
        """
        with Path(filename).open("w", encoding="utf-8") as stream:
            stream.write("\n")
            np.savetxt(stream, np.column_stack(spectrum), fmt="  %14.8f %14.8f")
