#!/usr/bin/env python3
"""SAE の光子エネルギー変換コマンドを回帰検証する。"""

import numpy as np
import pytest

from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from fdmnes_util.fdm_photoenergy import FdmPhotoenergy


class Spectrum:
    """独立したエネルギー格子を持つ最小限のスペクトルを提供する。"""

    def __init__(self):
        """変換に用いる生 XAS のメタデータを初期化する。"""
        self.edge_energy = 7100.0
        self.energy = np.array([-1.0, 0.0])


class Convolution:
    """異なる長さの格子で畳み込みの値を提供する。"""

    def __init__(self):
        """3点のエネルギーと対応する吸収強度を初期化する。"""
        self.energy = np.array([-2.0, 0.0, 2.0])
        self.xas = np.array([[0.1], [0.5], [0.9]])


def test_photon_energy_uses_convolution_grid(tmp_path):
    """生 XAS と畳み込みの格子が違ってもエネルギーと強度の対応を保つことを検証する。"""
    energy, intensity = AnalyzeFdmXas.photon_energy(
        Convolution(),
        Spectrum(),
    )
    output = FdmPhotoenergy().write(
        energy,
        intensity,
        tmp_path / "sample_conv_photoe.txt",
    )
    values = np.loadtxt(output)
    np.testing.assert_allclose(values[:, 0], [7098.0, 7100.0, 7102.0])
    np.testing.assert_allclose(values[:, 1], [0.1, 0.5, 0.9])
    assert output.read_text().splitlines()[:2] == [
        "",
        "    7098.00000    0.1000000000",
    ]


def test_photoenergy_rejects_mismatched_arrays(tmp_path):
    """エネルギーと強度の配列長が異なる場合に拒否することを検証する。"""
    with pytest.raises(ValueError, match="lengths differ"):
        FdmPhotoenergy().write(
            [1.0, 2.0],
            [0.5],
            tmp_path / "invalid.txt",
        )
