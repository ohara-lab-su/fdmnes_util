#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# SAE source: sae/commands/FDbav2xyz.py
# Original author: Kengo NAKADA (kengo.nakada@gmail.com)
# Copyright 2015, Kengo NAKADA. License: MIT.
#
# Original SAE development history:
#   2015.06.24 startup
#   2018.08.21 Python2/3 両対応
#
# The original script converted atomic positions from *_bav.txt to XYZ.
# This module contains only the XYZ file-format handling. The BAV parser
# and calculation-log analysis remain separate responsibilities.
# =============================================================================
"""Handle XYZ output files generated from FDMNES atomic positions."""

from pathlib import Path


class FdmXyz:
    """Serialize FDMNES atomic positions using the standard XYZ format."""

    def render(self, symbols, positions) -> str:
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
                f"{symbol} {x_coordinate:.10f} "
                f"{y_coordinate:.10f} {z_coordinate:.10f}"
            )
            lines.append(atom_line)

        return "\n".join(lines) + "\n"

    def write(self, symbols, positions, filename) -> Path:
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
        output_path.write_text(self.render(symbols, positions), encoding="utf-8")
        return output_path
