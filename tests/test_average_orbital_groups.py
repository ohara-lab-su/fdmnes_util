#!/usr/bin/env python3
"""SAE の軌道グループ指定を回帰検証する。"""

import matplotlib
import numpy as np
import pytest

from fdmnes_util.plot.plot_fdm_average import PlotFdmAverage

matplotlib.use("Agg")


def test_grouped_orbitals_share_a_panel(tmp_path, monkeypatch):
    """s・p 軌道を三段ではなく二段へ割り当てることを検証する。"""
    from matplotlib.figure import Figure

    savefig = Figure.savefig
    panel_labels = []

    def record_panels(figure, *args, **kwargs):
        for axis in figure.axes:
            panel_labels.append([line.get_label() for line in axis.lines])
        return savefig(figure, *args, **kwargs)

    monkeypatch.setattr(Figure, "savefig", record_panels)
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
    assert panel_labels == [["0-p_z", "0-p_x"], ["0-s"]]


def test_overlapping_orbital_groups_are_rejected(tmp_path):
    """同じ軌道を二度描く指定を拒否することを検証する。"""
    energy = np.array([0.0, 1.0])
    curves = [("0-s", energy, energy)]
    with pytest.raises(ValueError, match="overlap"):
        PlotFdmAverage().plot(
            curves,
            tmp_path / "invalid.pdf",
            orbital_groups=[["s"], ["s"]],
        )
