#!/usr/bin/env python3
#
# SAE原本: sae/fdmnes/sd.py
# 以下はSAE原本の冒頭コメントを原文のまま保存したものです。
# 原本に記された旧仕様・旧クラス名は現在のAPI仕様を意味しません。
# ---- SAE original header (verbatim) ----
# -*- coding: utf-8 -*
###############################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# FDMNES
#   *_sd*.txt ファイル( pw.x 入力ファイル 読み込み)
#   Ver_0.0.2 以降 FDMNS のバージョンの違いによるログの違いを吸収
#    - ReadFdmSd2016()
#    - ReadFdmSd2020() 切り替え
#
###############################################################################
#
# 2020.07.17 (Ver_0.0.2)
#  2016.08.01 以降に sd? のナンバリングルールが変わったのでそれに対する対応
#  - バージョンチェック(ReadFdmBav.py) を用いる
#    - ReadFdmSd2016()
#    - ReadFdmSd2020() 切り替え
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
#   eng = conv.get_eng()
#   xas = conv.get_xas()
#   print "NAME",name
# Copyright Kengo NAKADA; SAE class library.
# ---- End of SAE original header ----
"""FDMNES のサイト別状態密度 ``*_sdN.txt`` を列構成または明示指定で年別リーダーへ渡す。

FdmSd は2016・2020・2026の列形式を扱う。平均表を保存するときはエネルギー、状態密度、積分の元の列順を保持する。

SD の列構成は版によって異なる。改訂年だけでは書式を決められない。
"""

from functools import cached_property
from pathlib import Path

import numpy as np

from .fdm_sd_2016 import FdmSd2016
from .fdm_sd_2020 import FdmSd2020
from .fdm_sd_2026 import FdmSd2026


class FdmSd:
    """FDMNES の出力 `*_sdN.txt` を列構成に応じて年別リーダーへ委譲する。

    このクラスは形式を選ぶ。数値列の解釈は年別リーダーに委譲する。

    Attributes:
        path: 対象ファイルのパス。
        format_year: 対応する形式年。None なら列名で判定する。
        ispin: 2016年形式を読む場合のスピン数。
        weight: 密度列と積分列を規格化する除数。省略時は値を変更しない。
    """

    def __init__(self, filename, *, format_year, ispin=1, weight=None):
        """ファイル名を保持し、指定された SD 形式を検証する。

        Args:
            filename: サイト別状態密度の出力パス。
            format_year: 対応する形式年。None なら列名で判定する。
            ispin: 2016年形式を読む場合のスピン数。
            weight: 密度列と積分列を規格化する除数。省略時は値を変更しない。

        Raises:
            ValueError: 指定した SD 形式が未検証の場合。
        """
        if format_year not in (None, 2016, 2020, 2026):
            raise ValueError(
                f"Unverified SD layout for year {format_year}; "
                "explicitly choose a tested format"
            )

        self.path = Path(filename)
        self.format_year = format_year
        self.ispin = ispin
        self.weight = weight

    def select_reader(self):
        """指定または判定した SD 形式のリーダーを作る。

        Returns:
            FdmSd2016 | FdmSd2020 | FdmSd2026: 選択した SD 形式に対応するリーダー。
        """
        year = self.format_year
        if year is None:
            # FDMNES 本体の改訂年と SD の列形式は一致するとは限らない。
            with self.path.open(encoding="utf-8", errors="replace") as stream:
                columns = stream.readline().split()
            old_total = {"Int_t", "Int_t(u)", "Int_t(d)"}.intersection(columns)
            if (
                "Energy" in columns
                and old_total
                and any(name.startswith("n(0,0") for name in columns)
            ):
                year = 2016
            # f 軌道付きの実基底は通常の s・p・d 列も持つため、先に判定する。
            elif FdmSd2026._matches_header(columns):
                year = 2026
            elif {"Energy", "s", "Int(s)", "total", "Int(total)"}.issubset(columns):
                year = 2020
            elif FdmSd2020._magnetic_header(columns):
                year = 2020
            else:
                raise ValueError(f"Unverified SD layout: {self.path}")

        if year == 2016:
            return FdmSd2016(
                self.path,
                ispin=self.ispin,
                weight=self.weight,
            )

        if year == 2026:
            return FdmSd2026(self.path, weight=self.weight)
        return FdmSd2020(self.path, weight=self.weight)

    @cached_property
    def _reader(self):
        """直接呼び出された取得メソッドが共有する年別リーダーを返す。"""
        return self.select_reader()

    def get_densities(self):
        """出力順の密度列を返す。"""
        return self._reader.get_densities()

    def get_eng(self):
        """エネルギー軸を返す。"""
        return self._reader.get_eng()

    def get_lmax(self):
        """最大角運動量を返す。"""
        return self._reader.get_lmax()

    def get_ispin(self):
        """スピン数を返す。"""
        return self._reader.get_ispin()

    def get_tdos(self, spin=0):
        """全状態密度を返す。"""
        return self._reader.get_tdos(spin=spin)

    def get_inttdos(self, spin=0):
        """積分全状態密度を返す。"""
        return self._reader.get_inttdos(spin=spin)

    def get_ldos(self, l=0, spin=0):
        """軌道群の状態密度を返す。"""
        return self._reader.get_ldos(l=l, spin=spin)

    def get_intldos(self, l=0, spin=0):
        """軌道群の積分状態密度を返す。"""
        return self._reader.get_intldos(l=l, spin=spin)

    def get_pdos(self, l=0, m=0, lm=None, spin=0):
        """軌道射影の状態密度を返す。"""
        return self._reader.get_pdos(l=l, m=m, lm=lm, spin=spin)

    @staticmethod
    def format_from_bav(filename):
        """従来の BAV 改訂年による SD 形式の推定結果を返す。

        SD 自体の列名で判定するには FdmSd に format_year=None を渡す。

        Args:
            filename: 対応する BAV のパス。

        Returns:
            int: 対応する SD 形式年。

        Raises:
            ValueError: BAV の改訂行がないか、その版が未検証の場合。
        """
        from .fdm_bav import FdmBav

        year = FdmBav(filename).year
        if year <= 2016:
            return 2016
        if year < 2022:
            return 2020
        raise ValueError(f"Unverified SD layout for BAV revision {year}")

    @staticmethod
    def write_table(filename, columns, grid, densities):
        """元の密度列を全て保持した平均 SD 表を書き出す。

        Args:
            filename: 対象ファイルのパス。
            columns: 元の順序の列名。先頭はエネルギー列。
            grid: 元のエネルギー格子（eV）。
            densities: エネルギーを除いた密度・積分列。
        """
        np.savetxt(
            filename,
            np.column_stack((grid, densities)),
            header=" ".join(columns),
            comments="",
            fmt="%.10g",
        )
