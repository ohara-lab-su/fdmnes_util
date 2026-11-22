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

from __future__ import annotations

import re
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .fdm_bav_2016 import FdmBav2016
    from .fdm_bav_2020 import FdmBav2020
    from .fdm_bav_2026 import FdmBav2026


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
            if re.search(r"FDMNES.*program,", line):
                self.revision = line.strip()
                break
        if self.revision is None:
            raise ValueError("Missing FDMNES revision line")
        years = re.findall(r"\b(?:19|20)\d{2}\b", self.revision)
        if years:
            self.year = int(years[-1])
        elif self.revision == "FDMNES II program, Revision 1st of September 20":
            # 2016年9月1日版の main.f90 は50文字固定長で、年の末尾を切り落とす。
            self.year = 2016
        else:
            raise ValueError(f"Unknown FDMNES version: {self.revision}")

    def select_reader(self) -> FdmBav2016 | FdmBav2020 | FdmBav2026:
        """Return the implementation selected by the revision year.

        Returns:
            FdmBav2016 | FdmBav2020 | FdmBav2026: Reader for the revision.

        Raises:
            ValueError: For an unverified revision from 2022 onwards.
        """
        if self.year >= 2022:
            from .fdm_bav_2026 import FdmBav2026

            if self.revision == FdmBav2026.REVISION:
                return FdmBav2026(self.path, _lines=self.lines)
            raise ValueError(f"Unverified BAV layout for revision {self.year}")

        # SAE と同様、版の判定に使った本文を選択先に渡す。
        if self.year <= 2016:
            from .fdm_bav_2016 import FdmBav2016

            return FdmBav2016(self.path, _lines=self.lines)
        from .fdm_bav_2020 import FdmBav2020

        return FdmBav2020(self.path, _lines=self.lines)

    @cached_property
    def _reader(self) -> FdmBav2016 | FdmBav2020 | FdmBav2026:
        return self.select_reader()

    def get_edge(self):
        """ログに記録された吸収端のラベルを返す。"""
        return self._reader.get_edge()

    def get_nspin(self):
        """スピン数を返す。"""
        return self._reader.get_nspin()

    def is_self_consistent(self) -> bool:
        """自己無撞着計算の記録があるか返す。"""
        return self._reader.is_self_consistent()

    def get_max_scf_iterations(self) -> int | None:
        """SCF の反復上限を返す。"""
        return self._reader.get_max_scf_iterations()

    def get_n_scf_loop(self) -> int:
        """最後の SCF サイクル番号を返す。"""
        return self._reader.get_n_scf_loop()

    def get_scf_toten(self):
        """記録された SCF 全エネルギーを返す。"""
        return self._reader.get_scf_toten()

    def get_scf_history(self) -> list[tuple[int, float | None]]:
        """対応する版の SCF サイクル番号と全エネルギー（eV）を返す。"""
        read_history = getattr(self._reader, "_get_scf_history", None)
        if read_history is None:
            return []
        return read_history()

    def get_position(self):
        """クラスタの直交座標を返す。"""
        return self._reader.get_position()

    def get_atoms_index_j(self):
        """クラスタの原子順に元素記号を返す。"""
        return self._reader.get_atoms_index_j()

    def get_natom(self):
        """クラスタの原子数を返す。"""
        return self._reader.get_natom()

    def get_e_edge(self):
        """吸収端エネルギーを返す。"""
        return self._reader.get_e_edge()

    def get_ngroup(self):
        """原子グループ数を返す。"""
        return self._reader.get_ngroup()

    def get_t(self):
        """結晶基底の変換行列を返す。"""
        return self._reader.get_t()

    def get_lmax(self):
        """原子リストにある軌道角運動量の最大値を返す。"""
        return self._reader.get_lmax()
