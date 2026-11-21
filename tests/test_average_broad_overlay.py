#!/usr/bin/env python3
"""Regression tests for the SAE averaged-XAS broadening overlay."""

import matplotlib
import numpy as np
import pytest

from fdmnes_util.plot.plot_fdm_average import PlotFdmAverage


matplotlib.use("Agg")


def test_average_plot_overlays_distinct_energy_grids(tmp_path):
    """Plot raw and broadened XAS on their respective energy grids."""
    orbital_data = [
        ("s", np.array([0.0, 1.0]), np.array([1.0, 2.0])),
    ]
    broadened = (
        np.array([0.0, 0.5, 1.0]),
        np.array([1.0, 1.5, 2.0]),
    )
    unbroadened = (
        np.array([0.0, 1.0]),
        np.array([2.0, 3.0]),
    )
    output = tmp_path / "overlay.pdf"

    result = PlotFdmAverage().plot(
        orbital_data,
        output,
        xas_data=broadened,
        raw_xas_data=unbroadened,
    )

    assert result == output
    assert output.is_file()
    assert output.stat().st_size > 0


def test_raw_overlay_requires_convolved_xas(tmp_path):
    """Reject raw-XAS overlays when the XAS panel is absent."""
    orbital_data = [
        ("s", np.array([0.0, 1.0]), np.array([1.0, 2.0])),
    ]
    unbroadened = (
        np.array([0.0, 1.0]),
        np.array([2.0, 3.0]),
    )

    with pytest.raises(ValueError, match="requires convolved"):
        PlotFdmAverage().plot(
            orbital_data,
            tmp_path / "invalid.pdf",
            raw_xas_data=unbroadened,
        )
