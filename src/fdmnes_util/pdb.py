#!/usr/bin/env python3
# SAE source: sae/commands/FDpbd2fdm.py.
# ---- Original SAE header (verbatim) ----
# PDB to FDMNES crystal 情報
#
#  using ASE version
#
# 2015.08.20
#  関数分離(ごく一部だけASE分離)
#
# 2015.05.18 startup
# ---- End of original SAE header ----
# Original author: Kengo NAKADA; Copyright 2015, MIT.
"""Read a PDB structure for conversion to a FDMNES structure section."""

from pathlib import Path


class Pdb:
    """Represent the atomic structure and cell information in a PDB file.

    SAE distinguished molecular and crystal PDB input by the presence of a
    CRYST1 record. Atomic coordinates are loaded with ASE, as in the original.

    Attributes:
        path: Path to the PDB input file.
        molecule: Whether the PDB has no CRYST1 record.
    """

    def __init__(self, path: str | Path) -> None:
        """Read the input file and classify its structural representation.

        Args:
            path: Input PDB filename.

        Raises:
            FileNotFoundError: If the input file does not exist.
            ImportError: If the optional ASE package is unavailable.
        """
        self.path = Path(path)
        if not self.path.is_file():
            raise FileNotFoundError(self.path)

        self.molecule = True
        with self.path.open(encoding="utf-8") as source:
            for line in source:
                if line.startswith("CRYST1"):
                    self.molecule = False
                    break

        # Import ASE only when a PDB file is actually opened.
        from ase.io import read

        self.atoms = read(str(self.path), format="proteindatabank")

    def get_symbols(self) -> list[str]:
        """Return atomic symbols in the input order.

        Returns:
            list[str]: Chemical symbols.
        """
        return list(self.atoms.get_chemical_symbols())

    def get_cartesian_positions(self) -> list[tuple[float, float, float]]:
        """Return atomic positions in angstroms.

        Returns:
            list[tuple[float, float, float]]: Cartesian coordinates.
        """
        positions = []
        for row in self.atoms.get_positions():
            positions.append((float(row[0]), float(row[1]), float(row[2])))
        return positions

    def get_lattice_vectors(self):
        """Return the lattice vectors used for crystalline structures.

        Returns:
            numpy.ndarray: Three lattice vectors in angstroms.
        """
        return self.atoms.cell.array

    def get_direct_positions(self):
        """Return fractional atomic coordinates for a crystal.

        Returns:
            numpy.ndarray: Fractional atomic coordinates.
        """
        return self.atoms.get_scaled_positions()
