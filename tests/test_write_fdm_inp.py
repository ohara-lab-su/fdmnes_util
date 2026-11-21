#!/usr/bin/env python3
"""Verify full FDMNES input generation with an isolated structure provider."""

import numpy as np

from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_structure import FdmStructure


class ExampleStructure:
    """Provide structural data through the same public reader interface."""

    def get_lattice_vectors(self):
        """Return a cubic cell."""
        return np.diag([3.0, 3.0, 3.0])

    def get_direct_positions(self):
        """Return one fractional atomic position."""
        return np.array([[0.0, 0.0, 0.0]])

    def get_symbols(self):
        """Return the atomic symbol."""
        return ["Fe"]


def test_full_input_contains_calculation_keywords_and_structure(tmp_path):
    """Check that the calculation template and structure are both written."""
    structure_writer = FdmStructure(ExampleStructure())
    input_writer = FdmInp
    destination = tmp_path / "read_pdb.inp"
    input_writer.write(
        destination,
        absorber=2,
        fileout="Fe",
        edge="L3",
        structure_writer=structure_writer,
    )
    content = destination.read_text(encoding="utf-8")
    assert " Absorber\n  2" in content
    assert " Filout\n  Fe" in content
    assert " Edge\n  L3" in content
    assert " Crystal" in content
    assert "   26" in content
    assert " Density\n  state_all" in content
    assert " End" in content


def test_molecule_keyword(tmp_path):
    """Confirm that the structure writer receives the molecule option."""
    content = FdmInp.render(
        molecule=True, structure_writer=FdmStructure(ExampleStructure())
    )
    assert " Molecule" in content
    assert " Crystal" not in content
