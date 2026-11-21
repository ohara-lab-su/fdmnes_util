#!/usr/bin/env python3
"""Extract cluster coordinates from FDMNES calculation logs."""

from importlib.resources import files

import numpy as np


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
        table = files("fdmnes_util").joinpath("atomic_symbols.list")
        periodic = {}
        for row in table.read_text(encoding="utf-8").splitlines():
            atomic_number, symbol = row.split()[:2]
            periodic[int(atomic_number)] = symbol

        source = iter(self.reader.lines)
        for line in source:
            if "Cluster: atom positions in order" in line:
                break
        else:
            raise ValueError("Cluster: atom positions section is missing")

        # The first four columns contain Z, x, y, and z. Some revisions use
        # Fortran D exponents. Skip headings and stop after the final atom row.
        symbols = []
        positions = []
        for line in source:
            parts = line.split()
            try:
                if len(parts) < 4:
                    raise ValueError("Incomplete cluster row")
                symbol = periodic[int(parts[0])]
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
