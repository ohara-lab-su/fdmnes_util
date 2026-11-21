#!/usr/bin/env python3
"""Tests for the occupied-LDOS plot based on SAE fdLDOS_color.py."""

import numpy as np

from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos


class SampleSd:
    """Provide deterministic LDOS data for plotting tests."""

    def get_eng(self):
        """Return the sample energy axis."""
        return np.array([-2.0, -1.0, 0.0, 1.0])

    def get_ldos(self, orbital):
        """Return the sample density for the requested orbital.

        Args:
            orbital: Orbital label.

        Returns:
            numpy.ndarray: Sample LDOS.
        """
        assert orbital == "p"
        return np.array([0.1, 0.4, 0.8, 0.2])


def test_occupied_ldos_writes_pdf(tmp_path):
    """Save a plot with an explicit Fermi level and energy offset."""
    output = tmp_path / "occupied.pdf"
    plotter = PlotFdmDos()
    result = plotter.plot_occupied_ldos(
        SampleSd(),
        output,
        orbital="p",
        edge_offset=10.0,
        fermi_position=10.0,
    )
    assert result == output
    assert output.is_file()
    assert output.stat().st_size > 0
