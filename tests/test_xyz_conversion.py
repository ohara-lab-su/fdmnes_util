#!/usr/bin/env python3
"""Regression tests for the editable XYZ conversion example."""

from fdmnes_util.fdm_structure import FdmStructure
from fdmnes_util.xyz import Xyz


def test_xyz_to_molecule(tmp_path):
    """Preserve Cartesian coordinates and chemical atomic numbers."""
    source = tmp_path / "water.xyz"
    source.write_text("3\nwater\nO 0 0 0\nH 0 0 1\nH 0 1 0\n")
    xyz = Xyz(source)
    content = FdmStructure.render_xyz_molecule(xyz.symbols, xyz.positions)
    assert "molecule" in content
    assert "! O" in content
    assert "! H" in content
    assert "1.000000" in content


def test_xyz_rejects_short_file(tmp_path):
    """Reject truncated XYZ data rather than silently omitting atoms."""
    source = tmp_path / "bad.xyz"
    source.write_text("2\ncomment\nH 0 0 0\n")
    try:
        Xyz(source)
    except ValueError:
        return
    raise AssertionError("Truncated XYZ file must raise ValueError")
