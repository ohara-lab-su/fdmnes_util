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
"""Read an Athena normalized XAFS spectrum from a ``*.nor`` file."""

from pathlib import Path
import re

import numpy as np


class AthenaNor:
    """Read the energy axis and normalized absorption from an Athena file.

    Attributes:
        path: Path to the source file.
        energy: Photon energies in eV.
        normalized: Normalized absorption values.
        e0: Optional absorption-edge energy from the header.
    """

    def __init__(self, filename):
        """Load an Athena normalized spectrum.

        Args:
            filename: Path to a ``*.nor`` text file.

        Raises:
            ValueError: If a data row has fewer than two numeric columns.
        """
        self.path = Path(filename)
        energies = []
        normalized = []
        self.e0 = None

        with self.path.open(encoding="utf-8", errors="replace") as stream:
            for line in stream:
                stripped = line.strip()
                if not stripped:
                    continue

                if stripped.startswith("#"):
                    self._read_e0_comment(stripped)
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

    def _read_e0_comment(self, comment):
        """Extract the optional ``E0=`` field from an Athena comment.

        Args:
            comment: One comment line from the source file.
        """
        match = re.search(r"\bE0\s*=\s*([-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)", comment)
        if match is not None:
            self.e0 = float(match.group(1))

    def get_eng(self):
        """Return the photon-energy axis.

        Returns:
            numpy.ndarray: Photon-energy values.
        """
        return self.energy

    def get_nor(self):
        """Return the normalized absorption spectrum.

        Returns:
            numpy.ndarray: Normalized absorption values.
        """
        return self.normalized
