#!/usr/bin/env python3
#
# SAE原本: sae/fdmnes/txt.py
# 以下はSAE原本の冒頭コメントを原文のまま保存したものです。
# 原本に記された旧仕様・旧クラス名は現在のAPI仕様を意味しません。
# ---- SAE original header (verbatim) ----
# -*- coding: utf-8 -*-
###############################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# FDMNES
# *.txt ファイル
#
###############################################################################
#
# 2020.08.12: カプセル化推進
#
# 2019.01.08
#  新しい FDMNES における
#  Cu.txt などのログから E_Fermi が消えたことによる対応
#  （フェルミレベルが強制ゼロ、自動シフトに対する対応）
#
# 2018.08.15
#  Python2/3 両対応
#
# 2015.11.12
#  L2,3に対応
#
# 2015.09.11
#  .txt の生データーのスピン対応
#    XAS のデーター構造が変わるので注意
#
# 2015.09.08
#  .txt の平均化 Method を追加
#
# 2015.08.11
#  fdmnes_win64.exe を windows7 で動かした時と windows8 で動かしたときの
#  動作の違いを吸収するように重名に記述を変更しなおした。
#
# 2015.06.23 startup
#
###############################################################################
# トップディレクトリ関係のエラーは ImportError ではキャッチ出来ない
###############################################################################
# import gzip
# sys.path.append('../..')
# import SpaceGroupEnvironment as SGE
###############################################################################
# ラベル等のフォントサイズ
# レジェンドのフォントサイズ
# 軸の太さを設定。目盛りは変わらない
# for portrait
#   name = 'POSCAR.txt'
#   if not os.path.exists(name):
#       name0 = SAE.find_datfile1('_conv.txt')
#       if name0 is None:
#           name0 = name
#   name = name0
#   plot_fdm_xas(eng,xas)
#   print "NAME",name
# Copyright Kengo NAKADA; SAE class library.
# ---- End of SAE original header ----
"""FDMNES の生 XAS 出力 ``<Filout>.txt`` とサイト別の ``<Filout>_N.txt`` を読む。

FdmTxt は見出しの吸収端・フェルミ準位と数値列を保持する。生 XAS の平均を保存する場合は、最初のサイトのメタデータを使う。
"""
from pathlib import Path

import numpy as np


class FdmTxt:
    """生 XAS 出力 ``<Filout>.txt`` または ``<Filout>_N.txt`` を読み、吸収強度とエネルギーのメタデータを取り出す。"""
    def __init__(self, filename):
        """未畳み込みの XAS ファイルを読み込む。

        Args:
            filename: 対象ファイルのパス。

        Raises:
            ValueError: 入力の数値列が不足している場合。
        """
        self.path = Path(filename)
        lines = self.path.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines()

        if len(lines) < 3:
            raise ValueError("FDMNES XAS file is incomplete")

        self.metadata = lines[0]
        self.header = lines[1].split()
        # 吸収端などのメタデータと同じ読込みから数値行を解析する。
        self.values = np.loadtxt(lines[2:], ndmin=2)

        if self.values.shape[1] < 2:
            raise ValueError("FDMNES XAS output requires an absorption column")

        self.energy = self.values[:, 0]
        self.xas = self.values[:, 1:]

        # 一行目のイコールで結ばれたところまでの変数の数のカウント
        ###########################
        # 一行目のイコールで結ばれた値=変数名を、動的に変数＝値としてセット
        self.parameters = {}
        tokens = lines[0].replace(",", " ").split()
        if "=" in tokens:
            count = tokens.index("=") + 1
            # キーに対応する値がないときは、値が揃っている項目まで読む。
            for i in range(count, min(len(tokens), 2 * count - 1)):
                key = tokens[i]
                try:
                    value = float(tokens[i - count])
                except ValueError:
                    continue
                self.parameters[key] = value

        # SAE reads E_edge and Z by name. Keep the positional fallback for
        # headers without those keys.
        self.edge_energy = self.parameters.get("E_edge")
        atomic_number = self.parameters.get("Z")
        if atomic_number is None or self.edge_energy is None:
            metadata_fields = lines[0].split()
            if metadata_fields and self.edge_energy is None:
                try:
                    self.edge_energy = float(metadata_fields[0])
                except ValueError:
                    pass
            if len(metadata_fields) > 1 and atomic_number is None:
                try:
                    atomic_number = float(metadata_fields[1])
                except ValueError:
                    pass
        self.atomic_number = None
        if atomic_number is not None:
            try:
                self.atomic_number = int(atomic_number)
            except (ValueError, OverflowError):
                pass
        # 2020/2016 互換で、E_Fermi がないとき(2020)は互換値として 0.0 を入れる
        self.fermi_energy = self.parameters.get("E_Fermi", 0.0)

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

    def get_xas_all(self):
        """各行がエネルギー点に対応する吸収強度行列を返す。"""
        return self.xas

    def get_edge_xas(self, edge, spin=0):
        """吸収端ラベルとスピン順で生 XAS の吸収強度列を選ぶ。

        Args:
            edge: K や L3 など、出力見出しで使う吸収端ラベル。
            spin: 指定吸収端の吸収列内での0始まりの番号。

        Returns:
            numpy.ndarray: 選択した吸収強度。

        Raises:
            ValueError: 指定した吸収端またはスピンの列がない場合。
        """
        indices = []
        for index, column in enumerate(self.header[1:]):
            parts = column.upper().replace("-", "_").split("_")
            if edge.upper() in parts:
                indices.append(index)
        if spin < 0 or spin >= len(indices):
            raise ValueError(
                f"No XAS column for edge {edge}, spin {spin} in {self.path}"
            )
        return self.get_xas(indices[spin])

    def get_eedge(self):
        """吸収端エネルギーを eV 単位で返す。記録がなければ None。"""
        return self.edge_energy

    def get_efermi(self):
        """フェルミエネルギーを eV 単位で返す。記録がなければ SAE の既定値 0。"""
        return self.fermi_energy

    @staticmethod
    def write_spectrum(filename, metadata, spectrum):
        """最初のサイトのメタデータを付け、SAE の二列書式で平均を保存する。

        Args:
            filename: 対象ファイルのパス。
            metadata: 対応する生 XAS の1行目にあるパラメーター。
            spectrum: ファイルのエネルギー基準でのエネルギーと強度の配列。
        """
        np.savetxt(
            filename,
            np.column_stack(spectrum),
            fmt="  %14.3f %14.8f",
            header=metadata + "\n    Energy    <xanes>  ",
            comments="",
        )
