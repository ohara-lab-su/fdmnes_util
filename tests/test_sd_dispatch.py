#!/usr/bin/env python3
"""Check explicit dispatch to year-specific FDMNES SD parsers."""

from unittest.mock import patch

import pytest

from fdmnes_util.fdm_sd import FdmSd


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
