#!/usr/bin/env python3
# SAE source: sae/athena/nor.py
# ---- SAE original header ----
# -*- coding: utf-8 -*-
###############################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# Read Athena Normalize Data ( *.txt.nor )
#
# コメントアウトを除いて energy, XANES 形式に並んだだけのファイル
# Athena の Normlized Data の読み込みプロット
#
###############################################################################
#
# 2020.08.10: カプセル化
#
# 2018.08.15
#  Python2/3 両対応
#
# 2015.06.30
#   == Noneo --> is None
#
# 2015.05.21
#  ファイル名の自動取得&基本プロットのサンプル追加
#
# 2015.03.30
#  startup
#
###############################################################################
###############################################################################
# import gzip
# import optparse
# sys.path.append('../..')
# import SpaceGroupEnvironment as SGE
###############################################################################
###############################################################################
# ラベル等のフォントサイズ
# レジェンドのフォントサイズ
# 軸の太さを設定。目盛りは変わらない
# for portrait
#   plt.axvline(x=0,color='black',linewidth=1)
###############################################################################
###############################################################################
#   plot_athena_nor(spec.eng,spec.nor)
#   for i in range(ndata):
#       print eng[i],nor[i]
# Copyright Kengo NAKADA; SAE class library.
# ---- End of SAE original header ----
"""Athena の実験スペクトル ``*.nor`` を読み取る。

AthenaNor は光子エネルギー、規格化吸収強度、および見出しにあれば E0 を取り出す。
"""
from pathlib import Path
import re

import numpy as np


class AthenaNor:
    """実験入力の Athena `*.nor` からエネルギー軸と規格化吸収強度を読む。

    Attributes:
        path: 対象ファイルのパス。
        energy: エネルギー値の配列（eV）。
        normalized: 規格化した吸収強度。
        e0: 見出しに記録された吸収端エネルギー。記録がなければ None。
    """

    def __init__(self, filename):
        """Athena の規格化スペクトルを読み込む。

        Args:
            filename: Athena が出力した規格化スペクトルのパス。

        Raises:
            ValueError: データ行の数値列が2列未満の場合。
        """
        self.path = Path(filename)
        energies = []
        normalized = []
        self.e0 = None
        e0_field = re.compile(r"\bE0\s*=\s*([-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)")

        with self.path.open(encoding="utf-8", errors="replace") as stream:
            for line in stream:
                stripped = line.strip()
                if not stripped:
                    continue

                if stripped.startswith("#"):
                    match = e0_field.search(stripped)
                    if match is not None:
                        self.e0 = float(match.group(1))
                    continue

                values = stripped.split()
                if len(values) < 2:
                    raise ValueError(
                        f"Invalid Athena data row in {self.path}: {stripped}"
                    )

                # SAE uses the first two columns as photon energy and
                # normalized absorption. Athena may append other quantities.
                energies.append(float(values[0]))
                normalized.append(float(values[1]))

        self.energy = np.asarray(energies, dtype=float)
        self.normalized = np.asarray(normalized, dtype=float)

    def get_eng(self):
        """光子エネルギー軸を返す。

        Returns:
            numpy.ndarray: 光子エネルギーの配列。
        """
        return self.energy

    def get_nor(self):
        """規格化吸収スペクトルを返す。

        Returns:
            numpy.ndarray: 規格化した吸収強度。
        """
        return self.normalized
