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
"""FDMNES 2026年11月5日版の計算ログ ``*_bav.txt`` を読む。

FdmBav2026 はクラスタ座標や吸収端に加え、SCF のサイクル番号と記録された全エネルギーを取得する。
"""
import re
from functools import cached_property
from pathlib import Path

import numpy as np

from .fdm_structure import ElementTable


class FdmBav2026:
    """FDMNES の出力 `*_bav.txt` を2026年形式で読み、SCF 履歴を取得する。"""
    REVISION = "FDMNES program, Revision 5th of November 2026"

    def __init__(self, filename, *, _lines=None):
        """計算ログを読み込む。

        Args:
            filename: FDMNES 計算ログのパス。
        """
        self.path = Path(filename)
        if _lines is None:
            self.lines = self.path.read_text(errors="replace").splitlines()
        else:
            self.lines = _lines.copy()
        self.revision = ""
        for line in self.lines:
            if re.search(r"FDMNES.*program,", line):
                self.revision = line.strip()
                break

    def get_edge(self):
        """ログにある吸収端のラベルを返す。"""
        for line in reversed(self.lines):
            if "Threshold:" in line:
                return line.partition("Threshold:")[2].strip()
        return ""

    def get_nspin(self):
        """FDMNES が報告したスピン数を返す。"""
        for line in self.lines:
            if "Magnetic calculation" in line and "Non-" not in line:
                return 2
        return 1

    def is_self_consistent(self) -> bool:
        """自己無撞着計算の記録があるかを返す。"""
        return any("Self consistent calculation" in line for line in self.lines)

    def get_max_scf_iterations(self) -> int | None:
        """記録された SCF の反復上限を返す。記録がなければ None。"""
        for line in reversed(self.lines):
            match = re.search(r"Maximum number of iterations?\s*[:=]?\s*(\d+)", line)
            if match:
                return int(match.group(1))
        return None

    def get_n_scf_loop(self) -> int:
        """最後の SCF サイクル番号を返す。"""
        if self._scf_history:
            return self._scf_history[-1][0]
        return 0

    def get_scf_toten(self):
        """記録されている SCF 全エネルギーを順に返す。"""
        if self._scf_history:
            return [energy for _, energy in self._scf_history if energy is not None]
        return []

    def _get_scf_history(self) -> list[tuple[int, float | None]]:
        """サイクル番号と全エネルギー（eV）の組を返す。未記録の値は None。"""
        return self._scf_history.copy()

    @cached_property
    def _scf_history(self):
        """XANES 計算開始までの各 SCF サイクルを、未記録のエネルギーも含めて保持する。"""
        if not self.is_self_consistent():
            return []

        # この版の実出力では、Fermi energy 行の次に全エネルギーが続く。
        # 初回など、全エネルギーが書かれないサイクルも履歴では保持する。
        cycle_pattern = re.compile(r"\s*Cycle\s+(\d+),\s*Fermi energy\s*=", re.I)
        energy_pattern = re.compile(
            r"\s*Total energy\s*=\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?)"
            r"\s+eV,\s*Delta energy\s*="
        )
        history = []
        in_cycle = False
        for line in self.lines:
            if line.lstrip().startswith("Last cycle, XANES calculation"):
                in_cycle = False
                continue
            cycle = cycle_pattern.match(line)
            if cycle:
                history.append((int(cycle.group(1)), None))
                in_cycle = True
                continue
            if in_cycle:
                energy = energy_pattern.match(line)
                if energy:
                    value = float(energy.group(1).upper().replace("D", "E"))
                    history[-1] = (history[-1][0], value)
        return history

    def get_position(self):
        """ログのクラスタ節から原子の直交座標を返す。"""
        return self._cluster[1].copy()

    def get_atoms_index_j(self):
        """ログに記録された原子順で元素記号を返す。"""
        return self._cluster[0].copy()

    def get_natom(self):
        """クラスタ節の原子数を返す。"""
        return len(self._cluster[0])

    def get_e_edge(self):
        """記録があれば吸収端のエネルギーを返す。"""
        for line in reversed(self.lines):
            if not line.lstrip().startswith("E_edge"):
                continue
            parts = line.split()
            if len(parts) < 3:
                return None
            try:
                return float(parts[2])
            except ValueError:
                return None
        return None

    def get_ngroup(self):
        """記録があれば原子グループ数を返す。"""
        for line in reversed(self.lines):
            if re.match(r"^\s*ngroup\s*=", line):
                match = re.search(r"ngroup\s*=\s*(\d+)", line)
                if match is not None:
                    return int(match.group(1))
        return None

    def get_t(self):
        """結晶基底の 3×3 変換行列を返す。"""
        lines = self.lines
        # absorber を原点とした時の基本並進ベクトル
        r2_reg = re.compile(".*Transformation Crystal Bases.*Bases R2.*")
        for i in range(len(lines) - 1, -1, -1):
            if r2_reg.match(lines[i]):
                break
        else:
            return None

        t1_x = float(lines[i + 1].split()[0])
        t1_y = float(lines[i + 1].split()[1])
        t1_z = float(lines[i + 1].split()[2])
        t2_x = float(lines[i + 2].split()[0])
        t2_y = float(lines[i + 2].split()[1])
        t2_z = float(lines[i + 2].split()[2])
        t3_x = float(lines[i + 3].split()[0])
        t3_y = float(lines[i + 3].split()[1])
        t3_z = float(lines[i + 3].split()[2])
        t = np.zeros((3, 3))
        t[0, 0] = t1_x
        t[1, 0] = t1_y
        t[2, 0] = t1_z
        t[0, 1] = t2_x
        t[1, 1] = t2_y
        t[2, 1] = t2_z
        t[0, 2] = t3_x
        t[1, 2] = t3_y
        t[2, 2] = t3_z
        return t

    @cached_property
    def _cluster(self):
        """最後のクラスタ座標表から元素記号と直交座標を読み、再利用する。"""
        lines = self.lines
        # SAE は座標表を読むたびに上書きするため、最後の表を使う。
        for index in range(len(lines) - 1, -1, -1):
            if "Cluster: atom positions in order" in lines[index]:
                break
        else:
            raise ValueError("Cluster: atom positions section is missing")

        # positon (絶対座標系)
        # SAE は見出しと列名に続く行から、次の空行までを座標表として読む。
        position = []
        atoms_index_j = []
        for line in lines[index + 2 :]:
            columns = line.split()
            if not columns:
                break
            if len(columns) < 4:
                raise ValueError(f"Incomplete atom position: {line}")
            zz = int(columns[0])
            atoms_index_j.append(ElementTable.get_atomic_symbol0(zz))
            px = float(columns[1].replace("D", "E"))
            py = float(columns[2].replace("D", "E"))
            pz = float(columns[3].replace("D", "E"))
            position.append([px, py, pz])
        if not atoms_index_j:
            raise ValueError("No atom positions in log cluster")
        return atoms_index_j, np.array(position)

    def get_lmax(self):
        """原子リストの最大軌道角運動量を返す。"""
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
