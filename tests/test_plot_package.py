#!/usr/bin/env python3
"""Regression checks for the plotting package location and combined plot."""

from pathlib import Path
import shutil

import pytest

from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos
from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas
from fdmnes_util.plot.plot_fdm_xas_ldos import PlotFdmXasLdos
from test_commands import load_script

fd_plot_xas_ldos = load_script("FDplot_XAS_LDOS.py")


FIXTURES = Path(__file__).parent / "fixtures"


def test_plot_classes_live_under_plot_package():
    """Check that all public plotting classes are in the plot package."""
    assert PlotFdmDos.__module__ == "fdmnes_util.plot.plot_fdm_dos"
    assert PlotFdmXas.__module__ == "fdmnes_util.plot.plot_fdm_xas"
    assert PlotFdmXasLdos.__module__ == "fdmnes_util.plot.plot_fdm_xas_ldos"


def test_combined_xas_ldos_cli(tmp_path):
    """Generate a combined plot from real SAE Fe sample output files."""
    pytest.importorskip("matplotlib")
    for name in ("Fe.txt", "Fe_conv.txt", "Fe_sd0.txt"):
        shutil.copy(FIXTURES / name, tmp_path / name)

    inp_path = tmp_path / "read_pdb.inp"
    inp_path.write_text("Filout\n Fe\nEnd\n", encoding="utf-8")
    output = tmp_path / "combined.pdf"
    result = fd_plot_xas_ldos.main(
        [
            "-i",
            str(inp_path),
            "--year",
            "2020",
            "--output",
            str(output),
        ]
    )
    assert result == output
    assert output.stat().st_size > 100
