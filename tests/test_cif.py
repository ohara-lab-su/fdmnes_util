#!/usr/bin/env python3
"""CIF の読み取りと FDMNES 構造への変換を検証する。"""

from pathlib import Path

import pytest

from fdmnes_util.cif import Cif
from fdmnes_util.fdm_structure import FdmStructure


def test_cif_missing_file(tmp_path: Path) -> None:
    """存在しない入力パスを拒否することを検証する。"""
    with pytest.raises(FileNotFoundError):
        Cif(tmp_path / "absent.cif")


def test_cif_crystal_and_molecule(tmp_path: Path) -> None:
    """最小の CIF から結晶用・分子用の構造節を生成することを検証する。"""
    pytest.importorskip("ase")
    from ase import Atoms
    from ase.io import write

    input_path = tmp_path / "test.cif"
    atoms = Atoms(
        "Si2",
        scaled_positions=[[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]],
        cell=[5.0, 5.0, 5.0],
        pbc=True,
    )
    write(input_path, atoms, format="cif")
    structure = Cif(input_path)
    crystal = FdmStructure(structure).render()
    molecule = FdmStructure.render_xyz_molecule(
        structure.get_symbols(),
        structure.get_cartesian_positions(),
    )
    assert "Crystal" in crystal
    assert "molecule" in molecule
    assert "Si" in crystal
