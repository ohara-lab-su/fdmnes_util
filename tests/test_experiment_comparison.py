#!/usr/bin/env python3
"""Regression tests for the experimental XAS comparison plot."""

import matplotlib
import numpy as np

from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas


def test_comparison_plot_creates_pdf(tmp_path):
    """Save calculated and experimental spectra to one PDF figure."""
    matplotlib.use("Agg")
    energies = np.array([11900.0, 11910.0, 11920.0])
    calculated = np.array([0.1, 0.4, 0.8])
    observed = np.array([0.2, 0.5, 0.7])
    output = tmp_path / "comparison.pdf"

    plotter = PlotFdmXas()
    result = plotter.plot_experiment_comparison(
        calculated_energy=energies,
        calculated_absorption=calculated,
        observed_energy=energies,
        observed_absorption=observed,
        output=output,
        xmin=11900.0,
        xmax=11920.0,
    )

    assert result == output
    assert output.read_bytes().startswith(b"%PDF")
