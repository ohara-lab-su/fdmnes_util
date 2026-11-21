#!/usr/bin/env python3
"""Regression tests for the SAE orbital grouping modes."""

import matplotlib
import numpy as np
import pytest

from fdmnes_util.plot.plot_fdm_average import PlotFdmAverage

matplotlib.use("Agg")


def test_grouped_orbitals_share_a_panel(tmp_path, monkeypatch):
    """Group s and p orbitals into two panels instead of three."""
    import matplotlib.pyplot as plt

    original_subplots = plt.subplots
    panel_counts = []

    def record_subplots(*args, **kwargs):
        """Record the requested panel count before creating the figure."""
        panel_counts.append(args[0])
        return original_subplots(*args, **kwargs)

    monkeypatch.setattr(plt, "subplots", record_subplots)
    energy = np.array([0.0, 1.0, 2.0])
    curves = [
        ("0-s", energy, energy),
        ("0-p_z", energy, energy),
        ("0-p_x", energy, energy),
    ]
    output = tmp_path / "grouped.pdf"
    PlotFdmAverage().plot(
        curves,
        output,
        orbital_groups=[["s"], ["p_z", "p_x"]],
    )
    assert output.is_file()
    assert panel_counts == [2]


def test_overlapping_orbital_groups_are_rejected(tmp_path):
    """Reject a grouping that would display the same orbital twice."""
    energy = np.array([0.0, 1.0])
    curves = [("0-s", energy, energy)]
    with pytest.raises(ValueError, match="overlap"):
        PlotFdmAverage().plot(
            curves,
            tmp_path / "invalid.pdf",
            orbital_groups=[["s"], ["s"]],
        )
