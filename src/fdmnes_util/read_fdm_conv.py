#!/usr/bin/env python3
# Original SAE source: conv.py
# SAE: K.NAKADA, kengo.nakada@gmail.com
# SAE: 2018.08.15
# SAE: 2015.07.22
# SAE: 2015.07.01
# SAE: 2015.06.30
# SAE: 2015.05.21 startup
# SAE: Copyright Kengo NAKADA; SAE class library.
"""Read the convolved XAS spectrum written to ``*_conv.txt`` by FDMNES."""

from pathlib import Path

import numpy as np


class ReadFdmConv:
    """Retain the energy axis and all absorption columns of one output file."""

    def __init__(self, filename):
        """Read a convolved XAS file.

        Args:
            filename: Path to the FDMNES output file.

        Raises:
            ValueError: If the input has too few numerical columns.
        """
        self.path = Path(filename)

        with self.path.open(encoding="utf-8", errors="replace") as file:
            self.header = file.readline().strip()

        self.values = np.loadtxt(self.path, skiprows=1, ndmin=2)
        if self.values.shape[1] < 2:
            raise ValueError("FDMNES convolution output requires an XAS column")

        self.energy = self.values[:, 0]
        self.xas = self.values[:, 1:]

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
