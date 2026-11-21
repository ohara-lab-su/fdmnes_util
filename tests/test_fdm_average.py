#!/usr/bin/env python3
"""Regression tests for averaged FDMNES spectra."""

import numpy as np
import pytest

from fdmnes_util.analyze_fdm_average import AnalyzeFdmAverage


class FakeSd:
    """Provide the small SD interface used by the averaging class."""

    def __init__(self, energy, values):
        """Store a synthetic energy grid and orbital data."""
        self.energy = np.asarray(energy)
        self.values = np.asarray(values)

    def get_eng(self):
        """Return the synthetic energy grid."""
        return self.energy

    def get_pdos(self, lm=None, spin=0):
        """Return synthetic orbital data."""
        return self.values


def test_average_pdos():
    """Average corresponding orbital columns point by point."""
    readers = [FakeSd([1, 2], [2, 4]), FakeSd([1, 2], [4, 8])]
    energy, density = AnalyzeFdmAverage().average(readers, "get_pdos", lm="p_z")
    np.testing.assert_allclose(energy, [1, 2])
    np.testing.assert_allclose(density, [3, 6])


def test_mismatched_energy_grids():
    """Reject averaging spectra sampled at different energies."""
    readers = [FakeSd([1, 2], [2, 4]), FakeSd([1, 3], [4, 8])]
    with pytest.raises(ValueError, match="Energy grids"):
        AnalyzeFdmAverage().average(readers, "get_pdos")


class FakeConv:
    """Provide the FdmConv interface for convolved XAS averaging tests."""

    def __init__(self, energy, absorption):
        """Store a synthetic convolved spectrum.

        Args:
            energy: Photon-energy or relative-energy samples.
            absorption: Absorption values at those samples.
        """
        self.energy = np.asarray(energy, dtype=float)
        self.absorption = np.asarray(absorption, dtype=float)

    def get_eng(self):
        """Return the energy samples."""
        return self.energy

    def get_xas(self, spin=0):
        """Return the absorption channel requested by the example."""
        return self.absorption


def test_average_convolved_xas():
    """Check the XAS averaging path used by fdPDOS_XAS_av.py."""
    readers = [
        FakeConv([0.0, 0.5, 1.0], [2.0, 4.0, 6.0]),
        FakeConv([0.0, 0.5, 1.0], [4.0, 8.0, 12.0]),
    ]

    energy, absorption = AnalyzeFdmAverage().average(
        readers,
        "get_xas",
        spin=0,
    )

    np.testing.assert_allclose(energy, [0.0, 0.5, 1.0])
    np.testing.assert_allclose(absorption, [3.0, 6.0, 9.0])


def test_average_convolved_xas_rejects_mismatched_grid():
    """Prevent averaging spectra with different XAS energy samples."""
    readers = [
        FakeConv([0.0, 0.5], [1.0, 2.0]),
        FakeConv([0.0, 0.6], [3.0, 4.0]),
    ]

    with pytest.raises(ValueError, match="Energy grids"):
        AnalyzeFdmAverage().average(readers, "get_xas", spin=0)


@pytest.mark.parametrize("invalid_value", [float("nan"), float("inf")])
def test_average_rejects_non_finite_xas(invalid_value):
    """Reject undefined and infinite absorption values before averaging."""
    readers = [FakeConv([0.0, 1.0], [1.0, invalid_value])]

    with pytest.raises(ValueError, match="non-finite"):
        AnalyzeFdmAverage().average(readers, "get_xas")


def test_average_rejects_empty_energy_grid():
    """Reject empty inputs rather than returning a meaningless mean."""
    readers = [FakeConv([], [])]

    with pytest.raises(ValueError, match="empty"):
        AnalyzeFdmAverage().average(readers, "get_xas")
