#!/usr/bin/env python3
# SAE source: sae/commands/FDcif2fdm.py.
# ---- Original SAE header (verbatim, comment text) ----
# VASP to FDMNES crystal 情報
#
# using ASE version
#
# (注意)
#  1) ASE のルーチン(cellconst) を使っている
#  2) ASE のmodule を呼び出している
#
# 2018.08.17
#  Python2/3 両対応
#
# 2015.05.18 startup
# ---- End of original SAE header ----
# Original author: Kengo NAKADA; Copyright 2015, MIT.
"""Represent a CIF crystal structure using ASE.

The SAE command ``FDcif2fdm.py`` reads CIF with ASE but terminates with
``bug version``. This class provides the missing structure accessors without
copying ASE's CIF parser.
"""

from pathlib import Path


class Cif:
    """Provide FDMNES structure conversion with CIF-backed atomic data.

    Attributes:
        path: Input CIF file path.
        atoms: Atomic structure returned by ASE.
    """

    def __init__(self, path: str | Path) -> None:
        """Load a CIF file.

        Args:
            path: Input CIF file path.

        Raises:
            FileNotFoundError: If the input file is absent.
            ImportError: If ASE is not installed.
        """
        self.path = Path(path)
        if not self.path.is_file():
            raise FileNotFoundError(self.path)

        # CIF interpretation belongs to ASE, not to fdmnes_util.
        from ase.io import read

        self.atoms = read(str(self.path), format="cif")

    def get_symbols(self) -> list[str]:
        """Return atomic symbols in the order supplied by ASE.

        Returns:
            list[str]: Atomic symbols.
        """
        return list(self.atoms.get_chemical_symbols())

    def get_lattice_vectors(self):
        """Return the three cell vectors in angstroms.

        Returns:
            numpy.ndarray: A 3-by-3 array of lattice vectors.
        """
        return self.atoms.cell.array

    def get_direct_positions(self):
        """Return fractional coordinates in the CIF unit cell.

        Returns:
            numpy.ndarray: Atomic positions in fractional coordinates.
        """
        return self.atoms.get_scaled_positions()

    def get_cartesian_positions(self):
        """Return Cartesian coordinates in angstroms.

        Returns:
            numpy.ndarray: Cartesian atomic positions.
        """
        return self.atoms.get_positions()
