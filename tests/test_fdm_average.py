#!/usr/bin/env python3
"""FDMNES スペクトルの平均処理を回帰検証する。"""

import numpy as np
import pytest

from fdmnes_util.analyze_fdm_average import AnalyzeFdmAverage


class FakeSd:
    """平均化クラスが使う最小限の SD I/F を提供する。"""

    def __init__(self, energy, values):
        """テスト用のエネルギー格子と軌道データを保持する。"""
        self.energy = np.asarray(energy)
        self.values = np.asarray(values)

    def get_eng(self):
        """テスト用のエネルギー格子を返す。"""
        return self.energy

    def get_pdos(self, lm=None, spin=0):
        """テスト用の軌道データを返す。"""
        return self.values


def test_average_pdos():
    """対応する軌道列をエネルギー点ごとに平均することを検証する。"""
    readers = [FakeSd([1, 2], [2, 4]), FakeSd([1, 2], [4, 8])]
    energy, density = AnalyzeFdmAverage().average(readers, "get_pdos", lm="p_z")
    np.testing.assert_allclose(energy, [1, 2])
    np.testing.assert_allclose(density, [3, 6])


def test_mismatched_energy_grids():
    """異なるエネルギー格子を持つスペクトルの平均を拒否することを検証する。"""
    readers = [FakeSd([1, 2], [2, 4]), FakeSd([1, 3], [4, 8])]
    with pytest.raises(ValueError, match="Energy grids"):
        AnalyzeFdmAverage().average(readers, "get_pdos")


class FakeConv:
    """畳み込み XAS の平均テストに FdmConv と同じ I/F を提供する。"""

    def __init__(self, energy, absorption):
        """テスト用の畳み込みスペクトルを保持する。

        Args:
            energy: エネルギー値の配列（eV）。
            absorption: 対応するエネルギー点の吸収強度。
        """
        self.energy = np.asarray(energy, dtype=float)
        self.absorption = np.asarray(absorption, dtype=float)

    def get_eng(self):
        """エネルギー点を返す。"""
        return self.energy

    def get_xas(self, spin=0):
        """サンプルが要求した吸収強度列を返す。"""
        return self.absorption


def test_average_convolved_xas():
    """fdPDOS_XAS_av.py が使う XAS 平均処理を検証する。"""
    readers = [
        FakeConv([0.0, 0.5, 1.0], [2.0, 4.0, 6.0]),
        FakeConv([0.0, 0.5, 1.0], [4.0, 8.0, 12.0]),
    ]

    energy, absorption = AnalyzeFdmAverage().average(
        readers,
        "get_xas",
        spin=0,
    )

    np.testing.assert_allclose(energy, [0.0, 0.5, 1.0])
    np.testing.assert_allclose(absorption, [3.0, 6.0, 9.0])


def test_average_convolved_xas_rejects_mismatched_grid():
    """XAS のエネルギー点が異なる場合に平均を拒否することを検証する。"""
    readers = [
        FakeConv([0.0, 0.5], [1.0, 2.0]),
        FakeConv([0.0, 0.6], [3.0, 4.0]),
    ]

    with pytest.raises(ValueError, match="Energy grids"):
        AnalyzeFdmAverage().average(readers, "get_xas", spin=0)


@pytest.mark.parametrize("invalid_value", [float("nan"), float("inf")])
def test_average_rejects_non_finite_xas(invalid_value):
    """平均化の前に非有限の吸収強度を拒否することを検証する。"""
    readers = [FakeConv([0.0, 1.0], [1.0, invalid_value])]

    with pytest.raises(ValueError, match="non-finite"):
        AnalyzeFdmAverage().average(readers, "get_xas")


def test_average_rejects_empty_energy_grid():
    """空の入力で平均化を拒否することを検証する。"""
    readers = [FakeConv([], [])]

    with pytest.raises(ValueError, match="empty"):
        AnalyzeFdmAverage().average(readers, "get_xas")
