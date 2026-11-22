#!/usr/bin/env python3
"""SAE の平均図のエネルギー基準を回帰検証する。"""

import pytest

from fdmnes_util.analyze_fdm_average import AnalyzeFdmAverage


class ExampleInput:
    """FdmInp の計算モード取得メソッドを模擬する。"""

    def __init__(self, photon_mode):
        """テスト計算が光子エネルギーを使うかを保持する。"""
        self.photon_mode = photon_mode

    def get_energygpho(self):
        """テスト入力の計算モードを返す。"""
        return self.photon_mode


class ExampleSpectrum:
    """FdmTxt のメタデータ取得メソッドを模擬する。"""

    def get_eedge(self):
        """吸収端エネルギーを eV 単位で返す。"""
        return 100.0

    def get_efermi(self):
        """吸収端に対するフェルミエネルギーを eV 単位で返す。"""
        return 5.0


@pytest.mark.parametrize(
    ("photon_mode", "fermi", "expected_shift"),
    [
        (False, False, 100.0),
        (False, True, -5.0),
        (True, False, 0.0),
        (True, True, -105.0),
    ],
)
def test_sae_energy_reference_modes(photon_mode, fermi, expected_shift):
    """計算と表示のエネルギー基準の4通りの組み合わせを検証する。"""
    analyzer = AnalyzeFdmAverage()
    shift, absolute_fermi = analyzer.energy_reference(
        ExampleInput(photon_mode),
        ExampleSpectrum(),
        fermi=fermi,
    )
    assert shift == expected_shift
    assert absolute_fermi == 105.0
