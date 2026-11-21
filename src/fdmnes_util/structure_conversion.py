#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Related SAE source: sae/commands/FDvasp2fdm.py
# Original author: Kengo NAKADA (kengo.nakada@gmail.com)
# Copyright 2015, Kengo NAKADA. License: MIT.
#
# Original SAE development history:
#   2015.05.18 startup
#   2016.01.16 A standalone replacement for ASE was found to contain a
#              critical bug; the earlier ASE-backed implementation returned.
#   2016.01.16 Output format adapted to the newer FDMNES format.
#   2018.08.21 Python2/3 両対応
#
# This class is a new adapter, not an SAE class copied verbatim.
# POSCAR parsing is delegated to the external vasp_util package.
# =============================================================================
"""Convert supported structure-file data to ASE atomic structures."""

from .vasp_poscar import VaspPoscarFile


class StructureConversion:
    """Adapt structure readers to ASE without duplicating POSCAR parsing."""

    @staticmethod
    def poscar_to_atoms(filename):
        """Load a VASP POSCAR using vasp_util and construct an ASE structure.

        Args:
            filename: Path to the POSCAR file.

        Returns:
            ase.Atoms: Periodic structure in the POSCAR atom order.
        """
        from ase import Atoms

        poscar = VaspPoscarFile(filename)
        return Atoms(
            symbols=poscar.get_symbols(),
            scaled_positions=poscar.get_direct_positions(),
            cell=poscar.get_lattice_vectors(),
            pbc=True,
        )

    @staticmethod
    def other_to_atoms(filename, format):
        """Read a non-POSCAR structure using ASE's format-specific reader.

        Args:
            filename: Path to the structure file.
            format: ASE file-format identifier.

        Returns:
            ase.Atoms: Structure returned by ASE.
        """
        from ase.io import read

        atoms = read(str(filename), format=format)
        return atoms
