#!/usr/bin/env python3
"""Regression tests for the independent-calculation LDOS comparison."""

import numpy as np
import pytest

from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos


class ExampleSd:
    """Supply a minimal SD reader for plotting tests."""

    def get_eng(self):
        """Return the energy grid."""
        return np.array([0.0, 1.0, 2.0])

    def get_ldos(self, orbital):
        """Return a sample LDOS channel."""
        if orbital != "p":
            raise ValueError("Only p is available")
        return np.array([0.0, 1.0, 0.0])


def test_three_calculations_saves_pdf(tmp_path, monkeypatch):
    """Generate a PDF from three independent Fermi references."""
    from matplotlib.figure import Figure

    grids = []
    savefig = Figure.savefig

    def record_grids(figure, *args, **kwargs):
        grids.extend(axis.lines[0].get_xdata().copy() for axis in figure.axes)
        return savefig(figure, *args, **kwargs)

    monkeypatch.setattr(Figure, "savefig", record_grids)
    readers = [ExampleSd(), ExampleSd(), ExampleSd()]
    destination = tmp_path / "three.pdf"
    result = PlotFdmDos().plot_three_calculations(
        readers,
        [0.0, 0.5, 1.0],
        ["one", "two", "three"],
        destination,
    )
    assert result == destination
    assert destination.stat().st_size > 0
    np.testing.assert_array_equal(
        grids,
        [[0.0, 1.0, 2.0], [-0.5, 0.5, 1.5], [-1.0, 0.0, 1.0]],
    )


def test_three_calculations_rejects_bad_inputs(tmp_path):
    """Reject an incomplete set of calculations."""
    with pytest.raises(ValueError, match="Three SD readers"):
        PlotFdmDos().plot_three_calculations(
            [ExampleSd()],
            [0.0],
            ["one"],
            tmp_path / "bad.pdf",
        )
