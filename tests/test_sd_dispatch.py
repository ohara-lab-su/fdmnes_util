#!/usr/bin/env python3
"""Check explicit dispatch to year-specific FDMNES SD parsers."""

from unittest.mock import patch

import pytest

from fdmnes_util.fdm_sd import FdmSd
from fdmnes_util.fdm_sd_2016 import FdmSd2016
from fdmnes_util.fdm_sd_2020 import FdmSd2020


def test_2016_dispatch_preserves_spin_and_weight():
    """Forward 2016-specific arguments to the 2016 parser."""
    with patch("fdmnes_util.fdm_sd.FdmSd2016") as reader_class:
        selector = FdmSd("example_sd0.txt", format_year=2016, ispin=2, weight=3)
        result = selector.select_reader()

    reader_class.assert_called_once_with(
        selector.path,
        ispin=2,
        weight=3,
    )
    assert result is reader_class.return_value


def test_2020_dispatch_uses_2020_parser():
    """Use the 2020 layout without passing unsupported spin arguments."""
    with patch("fdmnes_util.fdm_sd.FdmSd2020") as reader_class:
        selector = FdmSd("example_sd0.txt", format_year=2020, weight=2)
        result = selector.select_reader()

    reader_class.assert_called_once_with(selector.path, weight=2)
    assert result is reader_class.return_value


def test_unverified_format_is_rejected():
    """Do not silently treat 2022 output as the 2020 layout."""
    with pytest.raises(ValueError, match="Unverified SD layout"):
        FdmSd("example_sd0.txt", format_year=2022)


@pytest.mark.parametrize(
    ("header", "row", "reader_type"),
    [
        ("Energy Int_t n(0,0) Intn(0,0) n_l(0) Intn_l(0)", "0 1 2 3 4 5", FdmSd2016),
        ("Energy s Int(s) total Int(total)", "0 2 3 2 3", FdmSd2020),
    ],
)
def test_auto_dispatch_uses_sd_header(tmp_path, header, row, reader_type):
    """Determine the format without a companion BAV or a revision year."""
    path = tmp_path / "example_sd0.txt"
    path.write_text(f"{header}\n{row}\n", encoding="utf-8")
    reader = FdmSd(path, format_year=None).select_reader()
    assert isinstance(reader, reader_type)
