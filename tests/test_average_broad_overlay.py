#!/usr/bin/env python3
"""SAE の平均 XAS 図での畳み込みスペクトルの重ね描きを回帰検証する。"""

import matplotlib
import numpy as np
import pytest

from fdmnes_util.plot.plot_fdm_average import PlotFdmAverage

matplotlib.use("Agg")


def test_average_plot_overlays_distinct_energy_grids(tmp_path):
    """生 XAS と畳み込み XAS がそれぞれのエネルギー格子を使うことを検証する。"""
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
    """XAS パネルがない場合に生 XAS の重ね描きを拒否することを検証する。"""
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
