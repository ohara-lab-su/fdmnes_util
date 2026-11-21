#!/usr/bin/env python3
"""Check that VASP parsing is delegated to the installed vasp_util module."""

import sys
import types

import numpy as np

from fdmnes_util.vasp_poscar import VaspPoscarFile


def test_vasp_reader_uses_external_module(monkeypatch, tmp_path):
    """Verify that the public VaspPoscar API supplies conversion data."""
    class FakeVaspPoscar:
        """Implement the subset of the provided vasp_util public API."""

        def __init__(self, filename):
            """Remember the path supplied by the bridge."""
            self.filename = filename

        def get_lattice_vectors(self):
            """Return an orthorhombic test cell."""
            return np.diag([3.0, 4.0, 5.0])

        def get_coords_direct(self):
            """Return fractional positions."""
            return np.array([[0.0, 0.0, 0.0]])

        def get_atom_indices(self):
            """Return the chemical symbols."""
            return ["Fe"]

    package = types.ModuleType("vasp_util")
    module = types.ModuleType("vasp_util.vasp_poscar")
    module.VaspPoscar = FakeVaspPoscar
    monkeypatch.setitem(sys.modules, "vasp_util", package)
    monkeypatch.setitem(sys.modules, "vasp_util.vasp_poscar", module)

    structure = VaspPoscarFile(str(tmp_path / "POSCAR"))
    assert structure.get_symbols() == ["Fe"]
    np.testing.assert_allclose(structure.get_lattice_vectors(), np.diag([3, 4, 5]))


def test_fdmnes_writer_uses_read_vasp_poscar(monkeypatch, tmp_path):
    """Check FDMNES output without introducing a second VASP parser."""
    class FakeStructure:
        """Provide the public interface of VaspPoscarFile."""

        def get_lattice_vectors(self):
            """Return the test lattice."""
            return np.diag([3.0, 4.0, 5.0])

        def get_direct_positions(self):
            """Return the test fractional position."""
            return np.array([[0.25, 0.5, 0.75]])

        def get_symbols(self):
            """Return the test element."""
            return ["Fe"]

    from fdmnes_util.fdm_structure import FdmStructure

    writer = FdmStructure(FakeStructure())
    output = writer.write(tmp_path / "POSCAR.fdmnes")
    content = output.read_text(encoding="utf-8")
    assert "Crystal" in content
    assert "26" in content
    assert "0.2500" in content
    assert "90.0000" in content
