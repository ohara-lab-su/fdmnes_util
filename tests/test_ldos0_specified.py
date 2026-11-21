#!/usr/bin/env python3
"""Test selected-orbital LDOS plotting from real FDMNES output."""

from pathlib import Path

import pytest

from test_commands import load_script

main = load_script("fdLDOS0_specified.py").main
from fdmnes_util.fdm_sd_2020 import FdmSd2020

FIXTURES = Path(__file__).parent / "fixtures"


def test_single_orbital_matches_reader(tmp_path):
    """Use the SD reader's p-channel without changing its values."""
    reader = FdmSd2020(FIXTURES / "Fe_sd0.txt")
    assert len(reader.get_eng()) == len(reader.get_ldos("p"))


def test_cli_uses_input_filout_and_writes_selected_format(tmp_path):
    """Resolve Fe_sd0.txt from Filout and save a selected plot."""
    pytest.importorskip("matplotlib")

    (tmp_path / "Fe_sd0.txt").write_bytes(
        (FIXTURES / "Fe_sd0.txt").read_bytes()
    )
    inp_path = tmp_path / "sample.inp"
    inp_path.write_text("Filout\n Fe\nEnd\n", encoding="utf-8")
    output_prefix = tmp_path / "LDOS"

    results = main(
        [
            "--input", str(inp_path),
            "--year", "2020",
            "--emin", "-10",
            "--emax", "20",
            "--dmax", "3",
            "--output-prefix", str(output_prefix),
            "--formats", "pdf",
        ]
    )
    assert len(results) == 1
    assert results[0] == tmp_path / "LDOS.pdf"
    assert results[0].stat().st_size > 100


def test_2022_format_is_not_automatically_assumed(tmp_path):
    """Do not interpret unverified 2022 output as a 2020 layout."""
    with pytest.raises(SystemExit):
        main(["--year", "2022"])
