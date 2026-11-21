#!/usr/bin/env python3
#
# SAE原本: sae/fdmnes/bav.py
# 以下はSAE原本の冒頭コメントを原文のまま保存したものです。
# 原本に記された旧仕様・旧クラス名は現在のAPI仕様を意味しません。
# ---- SAE original header (verbatim) ----
# -*- coding: utf-8 -*-
###############################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
# FDMNES
# *_bav.txt ファイル
#
###############################################################################
#
# 2020.08.11: バージョン切り替えのバグフィックス
#
# 2020.07.17
#  2016.08.01 以降に sd? のナンバリングルールが変わったのでそれに対する対応
#  - バージョンチェック(ReadFdmBav.py) のための改修
#  - バージョン切り替えのために ReadFdmBav2016()
#  - バージョン切り替えのために ReadFdmBav2020() 切り替え
#
# 2018.08.15
#  Python2/3 両対応
#
# 2015.09.11
#  scf ループ関係の情報吸い出しを追加
#
# 2015.06.25
#  R2 bases に対応した cluster: atom positions 吸い出しに対応
#
# 2015.06.23 startup
#
###############################################################################
# トップディレクトリ関係のエラーは ImportError ではキャッチ出来ない
###############################################################################
# import gzip
# import StructureAnalysisEnvironment as SAE
# import SpaceGroupEnvironment as SGE
###############################################################################
#   name = 'POSCAR.txt'
###############################################################################
#   for i in range(natom):
#       print "%s %10.6f %10.6f %10.6f" \
#         % (atoms_index_j[i], position[i, 0], position[i, 1], position[i, 2])
#       print position[i][0],position[i][1],position[i][2]
# Copyright Kengo NAKADA; SAE class library.
# ---- End of SAE original header ----
"""Select a version-specific reader for an FDMNES calculation log."""

import re
from pathlib import Path


class FdmBav:
    """Inspect a ``_bav.txt`` header and select its version-specific parser."""

    def __init__(self, filename):
        """Read the revision marker from a calculation log.

        Args:
            filename: Calculation-log filename.

        Raises:
            ValueError: If the revision marker or its year cannot be found.
        """
        self.path = Path(filename)
        self.lines = self.path.read_text(errors="replace").splitlines()
        self.revision = None
        for line in self.lines:
            if "FDMNES program," in line:
                self.revision = line.strip()
                break
        if self.revision is None:
            raise ValueError("Missing FDMNES revision line")
        years = re.findall(r"\b(?:19|20)\d{2}\b", self.revision)
        if not years:
            raise ValueError(f"Unknown FDMNES version: {self.revision}")
        self.year = int(years[-1])

    def select_reader(self):
        """Return the implementation selected by the revision year.

        Returns:
            FdmBav2016 | FdmBav2020: Reader for the supported revision.

        Raises:
            ValueError: For revision 2022 or later until those BAV variants
                have a verified parser.
        """
        if self.year >= 2022:
            raise ValueError(f"Unverified BAV layout for revision {self.year}")

        if self.year <= 2016:
            from .fdm_bav_2016 import FdmBav2016

            return FdmBav2016(self.path)
        from .fdm_bav_2020 import FdmBav2020

        return FdmBav2020(self.path)
