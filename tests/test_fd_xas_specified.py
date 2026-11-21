#!/usr/bin/env python3
"""Regression tests for the SAE fdXAS_specified example."""

import importlib.util
from pathlib import Path

import numpy as np

from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from fdmnes_util.read_fdm_conv import ReadFdmConv
from fdmnes_util.read_fdm_txt import ReadFdmTxt


def test_fermi_relative_convolution(tmp_path):
    """Preserve the original subtraction of E_Fermi from convolved energy."""
    raw = tmp_path / "sample.txt"
    conv = tmp_path / "sample_conv.txt"
    raw.write_text("100 26\nEnergy XAS\n0 1\n1 2\n")
    conv.write_text("Energy XAS\n0 3\n1 4\n")

    raw_reader = ReadFdmTxt(raw)
    raw_reader.fermi_energy = 2.5
    conv_reader = ReadFdmConv(conv)
    energy, intensity = AnalyzeFdmXas.fermi_relative_convolution(
        conv_reader,
        raw_reader,
    )
    np.testing.assert_allclose(energy, [-2.5, -1.5])
    np.testing.assert_allclose(intensity, [3, 4])
    np.testing.assert_allclose(conv_reader.get_eng(), [0, 1])


def test_script_source_has_documented_main():
    """Ensure the installed example exposes an editable main function."""
    script = Path(__file__).resolve().parents[1] / "scripts/fdXAS_specified.py"
    source = script.read_text()
    assert source.startswith("#!/usr/bin/env python3")
    assert "def main(argv=None):" in source
