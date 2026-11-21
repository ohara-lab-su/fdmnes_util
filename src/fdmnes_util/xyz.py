#!/usr/bin/env python3
# SAE provenance: sae/commands/FDxyz2fdm.py.
# Original author: Kengo NAKADA; Copyright 2015, Kengo NAKADA; MIT.
# Original development history (verbatim):
# 2018.08.21
#  Python2/3 両対応
# 2015.06.30
#  == None --> is None
# 2015.05.18 startup
"""Read XYZ coordinates for the FDMNES molecule conversion example.

SAE used ``ReadMd`` and ``AseInputOperations`` for the conversion. This
module handles standard XYZ files only; OpenMX MD input is not interpreted.
"""

from pathlib import Path


class Xyz:
    """Represent atomic symbols and Cartesian coordinates in an XYZ file."""

    def __init__(self, filename: str | Path) -> None:
        """Read an XYZ file.

        Args:
            filename: Path to a standard XYZ coordinate file.

        Raises:
            ValueError: If the atom count or coordinate records are invalid.
        """
        self.filename = Path(filename)
        self.symbols: list[str] = []
        self.positions: list[tuple[float, float, float]] = []
        self.read()

    def read(self) -> None:
        """Parse the atom count and Cartesian coordinate records.

        Raises:
            ValueError: If the input is not a valid standard XYZ file.
        """
        lines = self.filename.read_text(encoding="utf-8").splitlines()
        if len(lines) < 2:
            raise ValueError("XYZ input must contain a count and a comment line")

        try:
            atom_count = int(lines[0].strip())
        except ValueError as error:
            raise ValueError("Invalid XYZ atom count") from error

        if atom_count < 0:
            raise ValueError("XYZ atom count cannot be negative")
        if len(lines) < atom_count + 2:
            raise ValueError("XYZ file contains fewer atoms than declared")

        symbols: list[str] = []
        positions: list[tuple[float, float, float]] = []
        for index in range(atom_count):
            fields = lines[index + 2].split()
            if len(fields) < 4:
                raise ValueError(f"Invalid XYZ coordinate at atom {index + 1}")
            symbol = fields[0]
            try:
                coordinates = (
                    float(fields[1]),
                    float(fields[2]),
                    float(fields[3]),
                )
            except ValueError as error:
                raise ValueError(
                    f"Invalid XYZ coordinate at atom {index + 1}"
                ) from error
            symbols.append(symbol)
            positions.append(coordinates)

        self.symbols = symbols
        self.positions = positions
