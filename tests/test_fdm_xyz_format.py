#!/usr/bin/env python3
"""Test XYZ output generated from FDMNES coordinates."""

import pytest

from fdmnes_util.xyz import Xyz


def test_xyz_serialization(tmp_path):
    """Verify XYZ record count, order, and Cartesian coordinate precision."""
    output_path = tmp_path / "atoms.xyz"
    symbols = ["Fe", "O"]
    positions = [(0.0, 1.25, -2.0), (3.0, 4.0, 5.0)]

    Xyz.write(symbols, positions, output_path)

    lines = output_path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "2"
    assert lines[1] == ""
    assert lines[2] == " Fe   0.0000000000   1.2500000000  -2.0000000000"
    assert lines[3] == " O   3.0000000000   4.0000000000   5.0000000000"
    xyz = Xyz(output_path)
    assert xyz.symbols == symbols
    assert xyz.positions == positions


def test_xyz_rejects_mismatched_atom_counts(tmp_path):
    """Reject mismatched element and coordinate sequences."""
    output_path = tmp_path / "invalid.xyz"

    with pytest.raises(ValueError, match="count mismatch"):
        Xyz.write(["Fe"], [], output_path)

    assert not output_path.exists()


def test_xyz_rejects_incomplete_coordinates(tmp_path):
    """Reject incomplete Cartesian coordinates before writing the file."""
    output_path = tmp_path / "invalid.xyz"

    with pytest.raises(ValueError, match="three coordinates"):
        Xyz.write(["Fe"], [(0.0, 1.0)], output_path)

    assert not output_path.exists()
