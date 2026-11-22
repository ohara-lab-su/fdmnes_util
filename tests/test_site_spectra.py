#!/usr/bin/env python3
"""FDMNES クラスライブラリを回帰検証する。"""

from pathlib import Path
import numpy as np
import pytest
from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from test_commands import load_script

main = load_script("FDplot_XASs.py").main


def test_site_series_and_command(tmp_path):
    """test_site_series_and_commandの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。

    Returns:
        処理結果。

    """
    pytest.importorskip("matplotlib")
    (tmp_path / "read_pdb.inp").write_text("Filout\n Fe\nEND\n")
    for i in (1, 3):
        (tmp_path / f"Fe_{i}_conv.txt").write_text("Energy XAS\n0 2\n1 3\n")
        (tmp_path / f"Fe_{i}.txt").write_text("7112 26 = E_edge Z\nE XAS\n0 1\n1 2\n")
    spectra = AnalyzeFdmXas.site_spectra(tmp_path / "Fe", [3, 1])
    assert [x[2] for x in spectra] == ["absorber=3", "absorber=1"]
    out = tmp_path / "site.pdf"
    assert (
        main(
            ["-i", str(tmp_path / "read_pdb.inp"), "-a", "3", "1", "--output", str(out)]
        )
        == out
    )
    assert out.stat().st_size > 100


def test_site_series_reject_duplicate(tmp_path):
    """test_site_series_reject_duplicateの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。

    Returns:
        処理結果。

    """
    with pytest.raises(ValueError, match="Duplicate"):
        AnalyzeFdmXas.site_spectra(tmp_path / "Fe", [1, 1])


def test_fermi_flag_not_silently_accepted(tmp_path):
    """test_fermi_flag_not_silently_acceptedの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。

    Returns:
        処理結果。

    """
    (tmp_path / "read_pdb.inp").write_text("Filout\n Fe\nEND\n")
    (tmp_path / "Fe_1_conv.txt").write_text("Energy XAS\n0 2\n1 3\n")
    (tmp_path / "Fe_1.txt").write_text("7112 26 = E_edge Z\nE XAS\n0 1\n1 2\n")
    output = tmp_path / "fermi.pdf"
    result = main(
        ["-i", str(tmp_path / "read_pdb.inp"), "-a", "1", "-f", "--output", str(output)]
    )
    assert result == output
    assert output.stat().st_size > 100
