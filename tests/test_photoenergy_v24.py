#!/usr/bin/env python3
"""Regression tests for the original SAE photon-energy conversion command."""

import numpy as np
import pytest

from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from fdmnes_util.fdm_photoenergy import FdmPhotoenergy


class Spectrum:
    """Provide a minimal spectrum with an independently sampled energy grid."""

    def __init__(self):
        """Initialize raw-XAS metadata used by the conversion."""
        self.edge_energy = 7100.0
        self.energy = np.array([-1.0, 0.0])


class Convolution:
    """Provide convolution values with a different grid length."""

    def __init__(self):
        """Initialize three energy points and their absorption values."""
        self.energy = np.array([-2.0, 0.0, 2.0])
        self.xas = np.array([[0.1], [0.5], [0.9]])


def test_photon_energy_uses_convolution_grid(tmp_path):
    """Keep energy and intensity aligned when raw and conv grids differ."""
    energy, intensity = AnalyzeFdmXas.photon_energy(
        Convolution(),
        Spectrum(),
    )
    output = FdmPhotoenergy().write(
        energy,
        intensity,
        tmp_path / "sample_conv_photoe.txt",
    )
    values = np.loadtxt(output)
    np.testing.assert_allclose(values[:, 0], [7098.0, 7100.0, 7102.0])
    np.testing.assert_allclose(values[:, 1], [0.1, 0.5, 0.9])


def test_photoenergy_rejects_mismatched_arrays(tmp_path):
    """Reject energy and intensity arrays of different lengths."""
    with pytest.raises(ValueError, match="lengths differ"):
        FdmPhotoenergy().write(
            [1.0, 2.0],
            [0.5],
            tmp_path / "invalid.txt",
        )
