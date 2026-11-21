#!/usr/bin/env python3
"""Check consistent energy-axis shifts in the averaged DOS/XAS plot."""

import numpy as np
import pytest

from fdmnes_util.plot.plot_fdm_average import PlotFdmAverage


def test_energy_offset_applies_to_every_panel(tmp_path, monkeypatch):
    """Shift DOS, broadened XAS, and raw XAS by the same offset."""
    import matplotlib.axes

    recorded = []
    original_plot = matplotlib.axes.Axes.plot

    def capture_plot(self, x, y, *args, **kwargs):
        """Record the energy values passed to Matplotlib."""
        recorded.append(np.asarray(x).copy())
        return original_plot(self, x, y, *args, **kwargs)

    monkeypatch.setattr(matplotlib.axes.Axes, "plot", capture_plot)
    energy = np.array([0.0, 1.0, 2.0])
    density = np.array([1.0, 2.0, 1.0])
    raw_energy = np.array([0.5, 1.5])
    raw_density = np.array([0.5, 0.6])

    PlotFdmAverage().plot(
        [("p", energy, density)],
        tmp_path / "average.pdf",
        xas_data=(energy, density),
        raw_xas_data=(raw_energy, raw_density),
        energy_offset=3.5,
    )

    np.testing.assert_allclose(recorded[0], energy + 3.5)
    np.testing.assert_allclose(recorded[1], energy + 3.5)
    np.testing.assert_allclose(recorded[2], raw_energy + 3.5)


def test_energy_offset_rejects_nonfinite(tmp_path):
    """Reject undefined energy shifts before creating a figure."""
    with pytest.raises(ValueError, match="energy_offset"):
        PlotFdmAverage().plot(
            [("p", [0.0, 1.0], [1.0, 2.0])],
            tmp_path / "bad.pdf",
            energy_offset=float("nan"),
        )
