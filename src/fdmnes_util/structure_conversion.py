#!/usr/bin/env python3
"""Structure input conversion. POSCAR is read by the installed vasp_util module."""
from pathlib import Path
class StructureConversion:
    """StructureConversionに関する処理を提供する。"""
    @staticmethod
    def poscar_to_atoms(filename):
        """poscar_to_atomsの処理を実行する。
        
        Args:
            filename: filenameを指定する。
        
        Returns:
            処理結果。
        
        """
        from vasp_util.vasp_poscar import VaspPoscar
        from ase import Atoms
        poscar=VaspPoscar(str(filename))
        return Atoms(symbols=poscar.get_atom_indices(),
                     scaled_positions=poscar.get_coords_direct(),
                     cell=poscar.get_lattice_vectors(),pbc=True)
    @staticmethod
    def other_to_atoms(filename,format):
        """other_to_atomsの処理を実行する。
        
        Args:
            filename: filenameを指定する。
            format: formatを指定する。
        
        Returns:
            処理結果。
        
        """
        from ase.io import read
        return read(str(filename),format=format)
