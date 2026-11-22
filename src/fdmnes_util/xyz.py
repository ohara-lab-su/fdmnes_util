#!/usr/bin/env python3
# SAE provenance: sae/commands/FDxyz2fdm.py.
# Original author: Kengo NAKADA; Copyright 2015, Kengo NAKADA; MIT.
# Original development history (verbatim):
# 2018.08.21
#  Python2/3 両対応
# 2015.06.30
#  == None --> is None
# 2015.05.18 startup
# SAE source for XYZ output: sae/commands/FDbav2xyz.py.
# 2015.06.24 startup
# 2018.08.21 Python2/3 両対応
"""Read and write standard XYZ atomic coordinates.

SAE used ``ReadMd`` and ``AseInputOperations`` for the conversion. This
module handles standard XYZ files only; OpenMX MD input is not interpreted.
"""

from pathlib import Path


class Xyz:
    """Read and write element symbols and Cartesian coordinates in XYZ format."""

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

    @staticmethod
    def render(symbols, positions) -> str:
        """Serialize Cartesian positions with the precision used by FDbav2xyz.

        The first line contains the number of atoms, followed by an empty
        comment line and one element/coordinate record for each atom.

        Args:
            symbols: Chemical symbols in the desired output order.
            positions: Cartesian positions in angstroms, each with three values.

        Returns:
            Complete XYZ text, including its trailing newline.

        Raises:
            ValueError: If the number of symbols and positions differs, or
                if any position does not contain three coordinates.
        """
        atom_symbols = list(symbols)
        atom_positions = list(positions)

        if len(atom_symbols) != len(atom_positions):
            raise ValueError("Atom/coordinate count mismatch")

        lines = [str(len(atom_symbols)), ""]

        for symbol, position in zip(atom_symbols, atom_positions):
            if len(position) != 3:
                raise ValueError("Each atom must have three coordinates")

            x_coordinate = float(position[0])
            y_coordinate = float(position[1])
            z_coordinate = float(position[2])

            # Preserve the ten-decimal-place coordinate representation.
            atom_line = (
                f" {symbol} {x_coordinate:14.10f} "
                f"{y_coordinate:14.10f} {z_coordinate:14.10f}"
            )
            lines.append(atom_line)

        return "\n".join(lines) + "\n"

    @classmethod
    def write(cls, symbols, positions, filename) -> Path:
        """Write an XYZ file containing the supplied atomic coordinates.

        Args:
            symbols: Chemical symbols in the desired output order.
            positions: Cartesian positions in angstroms, each with three values.
            filename: Destination filename or path.

        Returns:
            Path of the written XYZ file.

        Raises:
            ValueError: If the symbols and positions are inconsistent.
            OSError: If the destination cannot be written.
        """
        output_path = Path(filename)
        output_path.write_text(cls.render(symbols, positions), encoding="utf-8")
        return output_path
