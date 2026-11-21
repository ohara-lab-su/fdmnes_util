#!/usr/bin/env python3
"""Regression tests for original SAE plot-limit options."""

import pytest

from fdmnes_util.plot.plot_fdm_average import PlotFdmAverage


def test_average_plot_rejects_nonpositive_dos_limit(tmp_path):
    """Reject a nonpositive DOS upper bound before drawing."""
    plotter = PlotFdmAverage()
    with pytest.raises(ValueError, match="dmax"):
        plotter.plot([("s", [0.0], [1.0])], tmp_path / "out.pdf", dmax=0)


def test_average_plot_rejects_nonpositive_xas_limit(tmp_path):
    """Reject a nonpositive XAS upper bound before drawing."""
    plotter = PlotFdmAverage()
    with pytest.raises(ValueError, match="ymax"):
        plotter.plot([("s", [0.0], [1.0])], tmp_path / "out.pdf", ymax=-1)


def test_average_plot_saves_with_axis_limits(tmp_path):
    """Write a combined plot with independent DOS and XAS limits."""
    pytest.importorskip("matplotlib")
    plotter = PlotFdmAverage()
    output = tmp_path / "average.pdf"
    result = plotter.plot(
        [("s", [0.0, 1.0], [1.0, 2.0])],
        output,
        xas_data=([0.0, 1.0], [2.0, 3.0]),
        dmax=4.0,
        ymax=5.0,
    )
    assert result == output
    assert output.stat().st_size > 0
