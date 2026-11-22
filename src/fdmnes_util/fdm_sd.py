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
"""Select the FDMNES SD parser for an explicitly specified format year.

The 2016 and 2020 layouts are separate formats. A numerical year is not
sufficient evidence that another FDMNES release uses the same layout.
"""

from pathlib import Path

import numpy as np

from .fdm_sd_2016 import FdmSd2016
from .fdm_sd_2020 import FdmSd2020


class FdmSd:
    """Select the format-specific parser for a site-resolved DOS file.

    This class is responsible for SD format selection. The actual file
    parsing remains the responsibility of the year-specific classes.

    Attributes:
        path: Path to the SD output file.
        format_year: Supported file format year, or None to inspect the header.
        ispin: Spin channel used for the 2016 layout.
        weight: Optional site-averaging weight.
    """

    def __init__(self, filename, *, format_year, ispin=1, weight=None):
        """Store the requested file and validate the SD format.

        Args:
            filename: Path to the FDMNES site-resolved DOS file.
            format_year: Supported SD layout year (2016 or 2020), or None to
                select by SD column names.
            ispin: Spin channel for the 2016 layout.
            weight: Optional weighting factor passed to the parser.

        Raises:
            ValueError: If the requested SD format is not verified.
        """
        if format_year not in (None, 2016, 2020):
            raise ValueError(
                f"Unverified SD layout for year {format_year}; "
                "explicitly choose a tested format"
            )

        self.path = Path(filename)
        self.format_year = format_year
        self.ispin = ispin
        self.weight = weight

    def select_reader(self):
        """Construct the parser corresponding to the requested layout.

        Returns:
            FdmSd2016 | FdmSd2020: Parser for the selected SD format.
        """
        year = self.format_year
        if year is None:
            with self.path.open(encoding="utf-8", errors="replace") as stream:
                columns = set(stream.readline().split())
            old_total = columns.intersection({"Int_t", "Int_t(u)", "Int_t(d)"})
            if "Energy" in columns and old_total and any(
                name.startswith("n(0,0") for name in columns
            ):
                year = 2016
            elif {"Energy", "s", "Int(s)", "total", "Int(total)"}.issubset(columns):
                year = 2020
            else:
                raise ValueError(f"Unverified SD layout: {self.path}")

        if year == 2016:
            return FdmSd2016(
                self.path,
                ispin=self.ispin,
                weight=self.weight,
            )

        return FdmSd2020(self.path, weight=self.weight)

    @staticmethod
    def format_from_bav(filename):
        """Return the historical SD layout estimate based on a BAV revision.

        Construct ``FdmSd`` with ``format_year=None`` to identify the layout
        from the actual SD columns instead.

        Args:
            filename: Path to the companion BAV file.

        Returns:
            int: Supported SD layout year.

        Raises:
            ValueError: If the BAV revision is missing or unverified.
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
        """Write an averaged SD file with all original density columns.

        Args:
            filename: Destination SD filename.
            columns: Column names, beginning with the energy label.
            grid: Original energy grid in eV.
            densities: Averaged density and integral columns, without energy.
        """
        np.savetxt(
            filename,
            np.column_stack((grid, densities)),
            header=" ".join(columns),
            comments="",
            fmt="%.10g",
        )
