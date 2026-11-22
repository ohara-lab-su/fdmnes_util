#!/usr/bin/env python3
# SAE original: sae/commands/FDconv_e2photoe.py
# Copyright Kengo NAKADA; SAE class library.
# K.NAKADA, kengo.nakada@gmail.com
#
# FEconv_e2photow.py
#   *_conv.txt ---> *_conv_photoe.txt
#   EF からの相対単位を Photon Energy 単位に変換して出力するプログラム
#
# 2018.08.17
#   Python2/3 両対応
#
# This class is a new file-format writer extracted from the original command.
"""光子エネルギーへ変換済みの畳み込み XAS を ``*_conv_photoe.txt`` に保存する。

FdmPhotoenergy は変換済みの数値配列を検証して二列で書き出す。元の ``*_conv.txt`` の読み取りとエネルギー変換は別のクラスが担当する。
"""
from pathlib import Path

import numpy as np


class FdmPhotoenergy:
    """解析の派生出力 `*_conv_photoe.txt` に光子エネルギーと吸収強度を保存する。

    軸の変換は AnalyzeFdmXas が担当する。このクラスでは変換後のエネルギー列と吸収強度列を検証して保存する。
    """

    def write(self, energy, intensity, filename):
        """変換済みのエネルギーと吸収強度をテキストに保存する。

        Args:
            energy: エネルギー値の配列（eV）。
            intensity: エネルギー各点に対応する一次元の吸収強度。
            filename: 対象ファイルのパス。

        Returns:
            pathlib.Path: 保存したファイルのパス。

        Raises:
            ValueError: 配列の長さまたは次元が一致しない場合。
        """
        energy_values = np.asarray(energy)
        intensity_values = np.asarray(intensity)

        if energy_values.ndim != 1:
            raise ValueError("Energy values must be one-dimensional")

        if intensity_values.ndim != 1:
            raise ValueError("Intensity values must be one-dimensional")

        if len(energy_values) != len(intensity_values):
            raise ValueError("Energy and intensity lengths differ")

        output_path = Path(filename)
        # ---> convert to PhotoEnergy (EF0 + E_edge)
        with output_path.open("w", encoding="utf-8") as convout:
            print("", file=convout)
            # 畳み込み強度には、同じ畳み込みスペクトルのエネルギー軸を使う。
            for i in range(len(energy_values)):
                print(
                    f" {energy_values[i]:13.5f}  {intensity_values[i]:14.10f}",
                    file=convout,
                )
        return output_path
