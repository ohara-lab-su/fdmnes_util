"""Structure input conversion. POSCAR is read by the installed vasp_util module."""
from pathlib import Path
class StructureConversion:
    @staticmethod
    def poscar_to_atoms(filename):
        from vasp_util.vasp_poscar import VaspPoscar
        from ase import Atoms
        poscar=VaspPoscar(str(filename))
        return Atoms(symbols=poscar.get_atom_indices(),
                     scaled_positions=poscar.get_coords_direct(),
                     cell=poscar.get_lattice_vectors(),pbc=True)
    @staticmethod
    def other_to_atoms(filename,format):
        from ase.io import read
        return read(str(filename),format=format)
