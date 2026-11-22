#!/usr/bin/env python3
"""独立した計算の LDOS 比較を回帰検証する。"""

import numpy as np
import pytest

from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos


class ExampleSd:
    """描画テスト用の最小限の SD リーダーを提供する。"""

    def get_eng(self):
        """エネルギー格子を返す。"""
        return np.array([0.0, 1.0, 2.0])

    def get_ldos(self, orbital):
        """テスト用の LDOS 列を返す。"""
        if orbital != "p":
            raise ValueError("Only p is available")
        return np.array([0.0, 1.0, 0.0])


def test_three_calculations_saves_pdf(tmp_path, monkeypatch):
    """独立した三つのフェルミ準位を基準に PDF を作ることを検証する。"""
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
    """計算結果が必要数に満たないときに拒否することを検証する。"""
    with pytest.raises(ValueError, match="Three SD readers"):
        PlotFdmDos().plot_three_calculations(
            [ExampleSd()],
            [0.0],
            ["one"],
            tmp_path / "bad.pdf",
        )
