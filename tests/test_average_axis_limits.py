#!/usr/bin/env python3
"""SAE の描画軸範囲オプションを回帰検証する。"""

import pytest

from fdmnes_util.plot.plot_fdm_average import PlotFdmAverage


def test_average_plot_rejects_nonpositive_dos_limit(tmp_path):
    """非正の DOS 上限値を描画前に拒否することを検証する。"""
    plotter = PlotFdmAverage()
    with pytest.raises(ValueError, match="dmax"):
        plotter.plot([("s", [0.0], [1.0])], tmp_path / "out.pdf", dmax=0)


def test_average_plot_rejects_nonpositive_xas_limit(tmp_path):
    """非正の XAS 上限値を描画前に拒否することを検証する。"""
    plotter = PlotFdmAverage()
    with pytest.raises(ValueError, match="ymax"):
        plotter.plot([("s", [0.0], [1.0])], tmp_path / "out.pdf", ymax=-1)


def test_average_plot_saves_with_axis_limits(tmp_path):
    """DOS と XAS の独立した軸範囲で複合図を保存することを検証する。"""
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
