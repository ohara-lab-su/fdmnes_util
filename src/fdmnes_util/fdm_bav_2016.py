#!/usr/bin/env python3
#
# SAE原本: sae/fdmnes/bav_2016.py
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
#   for i in range(natom):
#       print "%s %10.6f %10.6f %10.6f" \
#         % (atoms_index_j[i], position[i, 0], position[i, 1], position[i, 2])
#       print position[i][0],position[i][1],position[i][2]
# Copyright Kengo NAKADA; SAE class library.
# ---- End of SAE original header ----
"""Read the FDMNES 2016 calculation-log format."""

import re
from functools import cached_property
from pathlib import Path

import numpy as np

from .fdm_structure import ElementTable


class FdmBav2016:
    """Extract calculation information from a 2016-format ``_bav.txt`` file."""

    def __init__(self, filename, *, _lines=None):
        """Load the log file.

        Args:
            filename: Path to the FDMNES calculation log.
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
        """Return the absorption-edge label in the log."""
        for line in reversed(self.lines):
            if "Threshold:" in line:
                return line.partition("Threshold:")[2].strip()
        return ""

    def get_nspin(self):
        """Return the number of spin channels reported by FDMNES."""
        for line in self.lines:
            if "Magnetic calculation" in line and "Non-" not in line:
                return 2
        return 1

    def is_self_consistent(self) -> bool:
        """Return whether the log announces a self-consistent calculation."""
        return any("Self consistent calculation" in line for line in self.lines)

    def get_max_scf_iterations(self) -> int | None:
        """Return the reported SCF iteration limit, or None when absent."""
        for line in reversed(self.lines):
            match = re.search(r"Maximum number of iterations?\s*[:=]?\s*(\d+)", line)
            if match:
                return int(match.group(1))
        return None

    def get_n_scf_loop(self) -> int:
        """Return the last reported SCF cycle number, or zero when absent."""
        cycle = 0
        # FDMNES output and the SAE readers use the spelling "Begining".
        pattern = r"Begin(?:n)?ing of cycle\s+(\d+)"
        for line in self.lines:
            match = re.search(pattern, line)
            if match:
                cycle = int(match.group(1))
        return cycle

    def get_scf_toten(self):
        """Return the numeric unit-cell energy for each reported SCF record."""
        energies = []
        pattern = r"[-+]?\d+(?:\.\d+)?(?:[EeDd][-+]?\d+)?"
        for line in self.lines:
            if "Unit cell energy" not in line:
                continue
            matches = re.findall(pattern, line)
            if matches:
                energy = float(matches[-1].replace("D", "E"))
                energies.append(energy)
        return energies

    def get_position(self):
        """Return Cartesian atomic positions from the log's cluster section."""
        return self._cluster[1].copy()

    def get_atoms_index_j(self):
        """Return chemical symbols in the order recorded in the cluster."""
        return self._cluster[0].copy()

    def get_natom(self):
        """Return the number of atoms in the cluster section."""
        return len(self._cluster[0])

    def get_e_edge(self):
        """Return the numeric absorption-edge energy, if present."""
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
        """Return the number of atom groups, if recorded."""
        for line in reversed(self.lines):
            if re.match(r"^\s*ngroup\s*=", line):
                match = re.search(r"ngroup\s*=\s*(\d+)", line)
                if match is not None:
                    return int(match.group(1))
        return None

    def get_t(self):
        """Return the 3-by-3 crystal-basis transformation matrix."""
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
        """Return the maximum angular-momentum index in the atom listing."""
        for begin in range(len(self.lines) - 1, -1, -1):
            if self.lines[begin].lstrip().startswith("Excited atom,"):
                break
        else:
            return None
        levels = []
        for line in self.lines[begin + 2 :]:
            if line.lstrip().startswith("Atom type"):
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
