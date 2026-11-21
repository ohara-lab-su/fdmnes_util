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
"""Read the non-convolved XANES spectrum written to ``*.txt`` by FDMNES."""

from pathlib import Path

import numpy as np


class FdmTxt:
    """Read one XAS output, including edge and Fermi-energy metadata."""

    def __init__(self, filename):
        """Read a non-convolved XAS file.

        Args:
            filename: Path to the FDMNES output file.

        Raises:
            ValueError: If the input has too few numerical columns.
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
        self.values = np.loadtxt(self.path, skiprows=2, ndmin=2)

        if self.values.shape[1] < 2:
            raise ValueError("FDMNES XAS output requires an absorption column")

        self.energy = self.values[:, 0]
        self.xas = self.values[:, 1:]
        self.edge_energy = None
        self.atomic_number = None

        metadata_fields = lines[0].split()
        if metadata_fields:
            try:
                self.edge_energy = float(metadata_fields[0])
            except ValueError:
                pass

        if len(metadata_fields) > 1:
            try:
                self.atomic_number = int(float(metadata_fields[1]))
            except ValueError:
                pass

        # The first line pairs values before "=" with names after it.
        self.parameters = {}
        tokens = lines[0].replace(",", " ").split()
        if "=" in tokens:
            separator = tokens.index("=")
            values = tokens[:separator]
            names = tokens[separator + 1 :]

            for key, value in zip(names, values):
                try:
                    self.parameters[key] = float(value)
                except ValueError:
                    continue

        self.fermi_energy = self.parameters.get("E_Fermi", 0.0)

    def get_eng(self):
        """Return the energy axis in the file-defined reference frame."""
        return self.energy

    def get_xas(self, spin=0):
        """Return the requested absorption column.

        Args:
            spin: Zero-based index of the absorption column.

        Returns:
            numpy.ndarray: Absorption intensity values.
        """
        return self.xas[:, spin]

    def get_xas_all(self):
        """Return the absorption matrix, with one row per energy point."""
        return self.xas

    def get_edge_xas(self, edge, spin=0):
        """Select the spin-indexed XAS column for a named absorption edge.

        Args:
            edge: Edge label as used in the output header, such as L2 or L3.
            spin: Zero-based index among columns for the selected edge.

        Returns:
            numpy.ndarray: The matching absorption intensities.

        Raises:
            ValueError: If the selected edge or spin column is absent.
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
        """Return the absorption-edge energy in eV, or None if unavailable."""
        return self.edge_energy

    def get_efermi(self):
        """Return the Fermi energy in eV, defaulting to zero as in SAE."""
        return self.fermi_energy

    @staticmethod
    def write_spectrum(filename, metadata, spectrum):
        """Write the SAE two-column average with the first site's metadata.

        Args:
            filename: Destination raw XAS filename.
            metadata: First-line parameters from the corresponding raw file.
            spectrum: Energy and intensity arrays in the original reference.
        """
        np.savetxt(
            filename,
            np.column_stack(spectrum),
            fmt="  %14.3f %14.8f",
            header=metadata + "\n    Energy    <xanes>",
            comments="",
        )
