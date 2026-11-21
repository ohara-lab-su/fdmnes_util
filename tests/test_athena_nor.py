#!/usr/bin/env python3
"""Regression tests for Athena files and the original -o command option."""

from pathlib import Path

import numpy as np
import pytest

from fdmnes_util.read_athena_nor import ReadAthenaNor
from test_commands import load_script

main = load_script("FDplot_XASs.py").main


def test_read_athena_nor(tmp_path):
    """Read E0 and the first two columns of a normalized file."""
    source = tmp_path / "sample.nor"
    source.write_text("# Athena E0=7112.3\n7100 0.25\n7101 0.75\n")

    result = ReadAthenaNor(source)

    assert result.e0 == pytest.approx(7112.3)
    np.testing.assert_allclose(result.get_eng(), [7100, 7101])
    np.testing.assert_allclose(result.get_nor(), [0.25, 0.75])


def test_original_observed_option_creates_plot(tmp_path):
    """The original -o flag requests an observed spectrum overlay."""
    pytest.importorskip("matplotlib")

    input_file = tmp_path / "read_pdb.inp"
    input_file.write_text("Filout\n Fe\nEND\n")
    (tmp_path / "Fe_1.txt").write_text(
        "7112 26 = E_edge Z\nE XAS\n0 1\n1 2\n"
    )
    (tmp_path / "Fe_1_conv.txt").write_text("E XAS\n0 1\n1 2\n")
    (tmp_path / "Fe_1_obs.txt.nor").write_text(
        "# E0=7112\n7112 0.5\n7113 1.0\n"
    )
    output = tmp_path / "spectrum.pdf"

    result = main([
        "-i", str(input_file), "-a", "1", "-o",
        "--output", str(output),
    ])

    assert result == output
    assert output.stat().st_size > 100
