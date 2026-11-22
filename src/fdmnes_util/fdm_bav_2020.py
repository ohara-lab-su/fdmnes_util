#!/usr/bin/env python3
#
# SAE原本: sae/fdmnes/bav_2020.py
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
# 2020.08.11: lmax 関係の 2020対応が場合寄っては機能しなかったのを修正
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
# sys.path.append('../..')
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
"""Read the FDMNES 2020 calculation-log format."""

from .fdm_bav import _FdmBavReader


class FdmBav2020(_FdmBavReader):
    """Extract calculation information from a 2020-format ``_bav.txt`` file."""

    def get_lmax(self):
        """Return the maximum angular-momentum index in the atom listing."""
        for begin in range(len(self.lines) - 1, -1, -1):
            if self.lines[begin].lstrip().startswith("Excited atom,"):
                break
        else:
            return None
        levels = []
        for line in self.lines[begin + 2 :]:
            if line.lstrip().startswith("Excited atom total energy"):
                break
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                levels.append(int(parts[1]))
            except ValueError:
                continue
        if levels:
            return max(levels)
        return None
