#!/usr/bin/env python3
"""SAE の fdXAS_specified サンプルを回帰検証する。"""

import importlib.util
from pathlib import Path

import numpy as np

from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.fdm_txt import FdmTxt


def test_fermi_relative_convolution(tmp_path):
    """畳み込みエネルギーから E_Fermi を引く SAE の処理を検証する。"""
    raw = tmp_path / "sample.txt"
    conv = tmp_path / "sample_conv.txt"
    raw.write_text("100 26\nEnergy XAS\n0 1\n1 2\n")
    conv.write_text("Energy XAS\n0 3\n1 4\n")

    raw_reader = FdmTxt(raw)
    raw_reader.fermi_energy = 2.5
    conv_reader = FdmConv(conv)
    energy, intensity = AnalyzeFdmXas.fermi_relative_convolution(
        conv_reader,
        raw_reader,
    )
    np.testing.assert_allclose(energy, [-2.5, -1.5])
    np.testing.assert_allclose(intensity, [3, 4])
    np.testing.assert_allclose(conv_reader.get_eng(), [0, 1])


def test_script_source_has_documented_main():
    """インストール用サンプルに編集可能な main 関数があることを検証する。"""
    script = Path(__file__).resolve().parents[1] / "scripts/fdXAS_specified.py"
    source = script.read_text()
    assert source.startswith("#!/usr/bin/env python3")
    assert "def main(argv=None):" in source
