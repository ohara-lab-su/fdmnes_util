#!/usr/bin/env python3
"""SAE の二段の実験・計算比較図を回帰検証する。"""

import numpy as np
import pytest

from fdmnes_util.plot.plot_fdm_xas_ldos import PlotFdmXasLdos


def test_plot_experiment_ldos(tmp_path):
    """独立したエネルギー格子で二段の PDF を保存することを検証する。"""
    pytest.importorskip("matplotlib")
    output = tmp_path / "comparison.pdf"
    plotter = PlotFdmXasLdos()
    result = plotter.plot_experiment_ldos(
        calculated_energy=np.array([1.0, 2.0]),
        calculated_absorption=np.array([0.1, 0.2]),
        raw_energy=np.array([1.0, 1.5, 2.0]),
        raw_absorption=np.array([0.1, 0.15, 0.2]),
        observed_energy=np.array([1.0, 2.0]),
        observed_absorption=np.array([0.2, 0.3]),
        ldos_energy=np.array([1.0, 1.5, 2.0]),
        ldos_density=np.array([0.3, 0.4, 0.5]),
        fermi_energy=1.5,
        output=output,
    )
    assert result == output
    assert output.stat().st_size > 0


def test_plot_experiment_ldos_rejects_mismatched_grid(tmp_path):
    """エネルギー軸の長さが合わない場合に拒否することを検証する。"""
    pytest.importorskip("matplotlib")
    plotter = PlotFdmXasLdos()
    values = np.array([1.0, 2.0])
    with pytest.raises(ValueError, match="different lengths"):
        plotter.plot_experiment_ldos(
            calculated_energy=values,
            calculated_absorption=np.array([0.5]),
            raw_energy=values,
            raw_absorption=values,
            observed_energy=values,
            observed_absorption=values,
            ldos_energy=values,
            ldos_density=values,
            fermi_energy=1.5,
            output=tmp_path / "bad.pdf",
        )
