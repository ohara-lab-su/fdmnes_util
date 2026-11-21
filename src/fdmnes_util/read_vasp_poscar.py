#!/usr/bin/env python3
# Original SAE source: FDvasp2fdm.py
# SAE: Copyright Kengo NAKADA; SAE class library.
# SAE: 2018.08.21
# SAE: 2016.01.16
# SAE: 2015.05.18 startup
"""Read VASP POSCAR structures through the external vasp_util package."""

from pathlib import Path


class ReadVaspPoscar:
    """Provide FDMNES conversion data using vasp_util's POSCAR reader.

    This class does not implement a VASP parser. All POSCAR interpretation,
    including scaling and Cartesian-to-direct conversion, belongs to vasp_util.
    """

    def __init__(self, filename: str = "POSCAR") -> None:
        """Load a POSCAR file.

        Args:
            filename: POSCAR filename.
        """
        from vasp_util.vasp_poscar import VaspPoscar

        self.path = Path(filename)
        self.poscar = VaspPoscar(str(self.path))

    def get_lattice_vectors(self):
        """Return the 3-by-3 lattice matrix in angstroms.

        Returns:
            numpy.ndarray: Lattice vectors stored by rows.
        """
        return self.poscar.get_lattice_vectors()

    def get_direct_positions(self):
        """Return fractional positions in POSCAR atom order.

        Returns:
            numpy.ndarray: Array of fractional atomic positions.
        """
        return self.poscar.get_coords_direct()

    def get_symbols(self) -> list[str]:
        """Return one chemical symbol per atom.

        Returns:
            list[str]: Chemical symbols in POSCAR atom order.
        """
        return self.poscar.get_atom_indices()
