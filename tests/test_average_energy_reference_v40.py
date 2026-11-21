#!/usr/bin/env python3
"""Regression tests for the SAE averaged-plot energy reference."""

import pytest

from fdmnes_util.analyze_fdm_average import AnalyzeFdmAverage


class ExampleInput:
    """Provide the calculation-mode accessor used by FdmInp."""

    def __init__(self, photon_mode):
        """Store whether the example calculation uses photon energy."""
        self.photon_mode = photon_mode

    def get_energygpho(self):
        """Return the example input calculation mode."""
        return self.photon_mode


class ExampleSpectrum:
    """Provide the metadata accessors used by FdmTxt."""

    def get_eedge(self):
        """Return the absorption-edge energy in eV."""
        return 100.0

    def get_efermi(self):
        """Return the Fermi energy relative to the edge in eV."""
        return 5.0


@pytest.mark.parametrize(
    ("photon_mode", "fermi", "expected_shift"),
    [
        (False, False, 100.0),
        (False, True, -5.0),
        (True, False, 0.0),
        (True, True, -105.0),
    ],
)
def test_sae_energy_reference_modes(photon_mode, fermi, expected_shift):
    """Check all four combinations of calculation and display modes."""
    analyzer = AnalyzeFdmAverage()
    shift, absolute_fermi = analyzer.energy_reference(
        ExampleInput(photon_mode),
        ExampleSpectrum(),
        fermi=fermi,
    )
    assert shift == expected_shift
    assert absolute_fermi == 105.0
