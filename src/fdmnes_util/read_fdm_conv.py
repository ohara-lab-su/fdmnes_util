#!/usr/bin/env python3
"""Read the convolved XAS spectrum written to ``*_conv.txt`` by FDMNES."""

from pathlib import Path

import numpy as np


class ReadFdmConv:
    """Retain the energy axis and all absorption columns of one output file."""

    def __init__(self, filename):
        self.path = Path(filename)

        with self.path.open(encoding="utf-8", errors="replace") as file:
            self.header = file.readline().strip()

        self.values = np.loadtxt(self.path, skiprows=1, ndmin=2)
        if self.values.shape[1] < 2:
            raise ValueError("FDMNES convolution output requires an XAS column")

        self.energy = self.values[:, 0]
        self.xas = self.values[:, 1:]

    def get_eng(self):
        return self.energy

    def get_xas(self, spin=0):
        return self.xas[:, spin]
