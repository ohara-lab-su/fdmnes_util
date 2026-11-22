#!/usr/bin/env python3
"""3サイトの LDOS の描画例を検証する。"""

from pathlib import Path

import numpy as np
import pytest

from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos


class ExampleSd:
    """描画処理が受け取る最小限の SD リーダーを提供する。"""

    def get_eng(self):
        """短いエネルギー軸を返す。"""
        return np.array([-1.0, 0.0, 1.0])

    def get_ldos(self, orbital):
        """軌道別の密度配列を返す。"""
        if orbital != "p":
            raise ValueError("This fixture only supplies p orbitals")
        return np.array([0.1, 0.5, 0.2])


def test_plot_three_sites(tmp_path):
    """共通の光子エネルギー軸で三段の PDF を保存することを検証する。"""
    pytest.importorskip("matplotlib")
    readers = [ExampleSd(), ExampleSd(), ExampleSd()]
    labels = ["sd0", "sd1", "sd2"]
    destination = tmp_path / "LDOSmulti.pdf"

    result = PlotFdmDos().plot_multiple_sites(
        readers,
        labels,
        destination,
        edge_energy=7100.0,
        fermi_energy=2.0,
        emin=7098.0,
        emax=7102.0,
    )

    assert result == destination
    assert destination.stat().st_size > 100


def test_plot_requires_three_sites(tmp_path):
    """SD のサイトが不足する場合に拒否することを検証する。"""
    with pytest.raises(ValueError):
        PlotFdmDos().plot_multiple_sites(
            [ExampleSd()],
            ["sd0"],
            tmp_path / "bad.pdf",
            edge_energy=7100.0,
            fermi_energy=2.0,
        )


def test_plot_three_sites_all_formats(tmp_path):
    """SAE の描画スクリプトが使う3種類の図を保存することを検証する。"""
    pytest.importorskip("matplotlib")
    readers = [ExampleSd(), ExampleSd(), ExampleSd()]
    labels = ["sd0", "sd1", "sd2"]
    prefix = tmp_path / "LDOSmulti"

    paths = PlotFdmDos().save_multiple_formats(
        readers,
        labels,
        prefix,
        edge_energy=7100.0,
        fermi_energy=2.0,
    )

    assert [path.suffix for path in paths] == [".eps", ".pdf", ".png"]
    for path in paths:
        assert path.is_file()
        assert path.stat().st_size > 100


def test_plot_rejects_unsupported_format(tmp_path):
    """ファイル生成前に不正な形式を拒否することを検証する。"""
    with pytest.raises(ValueError, match="Unsupported format"):
        PlotFdmDos().save_multiple_formats(
            [ExampleSd(), ExampleSd(), ExampleSd()],
            ["sd0", "sd1", "sd2"],
            tmp_path / "LDOSmulti",
            formats=("svg",),
            edge_energy=7100.0,
            fermi_energy=2.0,
        )
