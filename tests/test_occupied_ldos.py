#!/usr/bin/env python3
"""SAE の fdLDOS_color.py に基づく占有 LDOS 描画を検証する。"""

import numpy as np

from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos


class SampleSd:
    """描画テスト用に固定の LDOS データを提供する。"""

    def get_eng(self):
        """テスト用のエネルギー軸を返す。"""
        return np.array([-2.0, -1.0, 0.0, 1.0])

    def get_ldos(self, orbital):
        """指定軌道に対するテスト用密度を返す。

        Args:
            orbital: 対象の軌道名。

        Returns:
            numpy.ndarray: テスト用の LDOS。
        """
        assert orbital == "p"
        return np.array([0.1, 0.4, 0.8, 0.2])


def test_occupied_ldos_writes_pdf(tmp_path):
    """フェルミ準位とエネルギー移動量を指定して図を保存することを検証する。"""
    output = tmp_path / "occupied.pdf"
    plotter = PlotFdmDos()
    result = plotter.plot_occupied_ldos(
        SampleSd(),
        output,
        orbital="p",
        edge_offset=10.0,
        fermi_position=10.0,
    )
    assert result == output
    assert output.is_file()
    assert output.stat().st_size > 0
