#!/usr/bin/env python3
"""Read the non-convolved XANES spectrum written to ``*.txt`` by FDMNES."""

from pathlib import Path

import numpy as np


class ReadFdmTxt:
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

        self.parameters = {}
        tokens = lines[0].replace(",", " ").split()
        if "=" in tokens:
            separator = tokens.index("=")
            values = tokens[:separator]
            names = tokens[separator + 1:]

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
        """get_xas_allの処理を実行する。
        
        Returns:
            処理結果。
        
        """
        return self.xas

    def get_eedge(self):
        """get_eedgeの処理を実行する。
        
        Returns:
            処理結果。
        
        """
        return self.edge_energy

    def get_efermi(self):
        """get_efermiの処理を実行する。
        
        Returns:
            処理結果。
        
        """
        return self.fermi_energy
