#!/usr/bin/env python3
# SAE original: sae/commands/FDconv_e2photoe.py
# Copyright Kengo NAKADA; SAE class library.
# K.NAKADA, kengo.nakada@gmail.com
#
# FEconv_e2photow.py
#   *_conv.txt ---> *_conv_photoe.txt
#   EF からの相対単位を Photon Energy 単位に変換して出力するプログラム
#
# 2018.08.17
#   Python2/3 両対応
#
# This class is a new file-format writer extracted from the original command.
"""Write a two-column FDMNES convolution spectrum in photon-energy units."""

from pathlib import Path

import numpy as np


class FdmPhotoenergy:
    """Represent the ``*_conv_photoe.txt`` output file format.

    The energy conversion itself belongs to ``AnalyzeFdmXas``. This class
    only validates and writes the converted energy and absorption columns.
    """

    def write(self, energy, intensity, filename):
        """Write converted energy and absorption values to a text file.

        Args:
            energy: One-dimensional photon-energy values in eV.
            intensity: One-dimensional absorption values at those energies.
            filename: Destination path for the converted spectrum.

        Returns:
            pathlib.Path: Path to the generated text file.

        Raises:
            ValueError: If arrays have different lengths or dimensions.
        """
        energy_values = np.asarray(energy)
        intensity_values = np.asarray(intensity)

        if energy_values.ndim != 1:
            raise ValueError("Energy values must be one-dimensional")

        if intensity_values.ndim != 1:
            raise ValueError("Intensity values must be one-dimensional")

        if len(energy_values) != len(intensity_values):
            raise ValueError("Energy and intensity lengths differ")

        output_path = Path(filename)
        # ---> convert to PhotoEnergy (EF0 + E_edge)
        with output_path.open("w", encoding="utf-8") as convout:
            print("", file=convout)
            # 畳み込み強度には、同じ畳み込みスペクトルのエネルギー軸を使う。
            for i in range(len(energy_values)):
                print(
                    f" {energy_values[i]:13.5f}  {intensity_values[i]:14.10f}",
                    file=convout,
                )
        return output_path
