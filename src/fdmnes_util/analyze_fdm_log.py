#!/usr/bin/env python3
"""Extract cluster coordinates from FDMNES calculation logs."""

from functools import cached_property

import numpy as np

from ._elements import SYMBOLS_BY_NUMBER


class AnalyzeFdmLog:
    """Analyze the cluster block of a year-specific FDMNES BAV reader."""

    def __init__(self, reader):
        """Store the parsed log.

        Args:
            reader: BAV reader exposing the source lines in file order.
        """
        self.reader = reader

    def positions(self):
        """Read the atomic symbols and Cartesian positions of the cluster.

        Returns:
            A list of chemical symbols and an array of XYZ coordinates.

        Raises:
            ValueError: If the cluster section is absent or has no atom rows.
        """
        # SAE と同様に座標表を一度だけ解析する。返した値の変更は内部に反映しない。
        symbols, positions = self._cluster
        return symbols.copy(), positions.copy()

    @cached_property
    def _cluster(self):
        lines = self.reader.lines
        # SAE replaces the stored cluster whenever another table is found.
        for index in range(len(lines) - 1, -1, -1):
            if "Cluster: atom positions in order" in lines[index]:
                break
        else:
            raise ValueError("Cluster: atom positions section is missing")

        # The first four columns contain Z, x, y, and z. Some revisions use
        # Fortran D exponents. Skip headings and stop after the final atom row.
        symbols = []
        positions = []
        for line in lines[index + 1 :]:
            parts = line.split()
            try:
                if len(parts) < 4:
                    raise ValueError("Incomplete cluster row")
                symbol = SYMBOLS_BY_NUMBER[int(parts[0])]
                point = [float(value.replace("D", "E")) for value in parts[1:4]]
            except (ValueError, KeyError):
                if symbols:
                    break
                continue
            symbols.append(symbol)
            positions.append(point)
        if not symbols:
            raise ValueError("No atom positions in log cluster")
        return symbols, np.asarray(positions, dtype=float)
