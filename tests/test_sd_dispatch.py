#!/usr/bin/env python3
"""Check explicit dispatch to year-specific FDMNES SD parsers."""

from unittest.mock import patch

import numpy as np
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


def test_magnetic_2020_sd_columns(tmp_path):
    """Use the 31 columns recorded in the 2021 and 2026 Ni calculations."""
    header = (
        "Energy s_up Int(s)_up s_dn Int(s)_dn px_up px_dn py_up py_dn "
        "pz_up pz_dn p_up Int(p)_up p_dn Int(p)_dn dx2-y2_up dx2-y2_dn "
        "dz2_up dz2_dn dyz_up dyz_dn dxz_up dxz_dn dxy_up dxy_dn "
        "d_up Int(d)_up d_dn Int(d)_dn total Int(total)"
    )
    path = tmp_path / "Ni_mag_sd1.txt"
    row = " ".join(str(index) for index in range(1, 32))
    path.write_text(f"{header}\n{row}\n", encoding="utf-8")

    for year in (None, 2020):
        reader = FdmSd(path, format_year=year, weight=2).select_reader()
        assert reader.get_ispin() == 2
        assert reader.get_lmax() == 2
        np.testing.assert_array_equal(reader.get_eng(), [1])
        np.testing.assert_array_equal(reader.get_densities(), [np.arange(2, 32) / 2])
        assert reader.get_ldos("d", spin="down").tolist() == [14]
        assert reader.get_intldos("d", spin="up").tolist() == [13.5]
        assert reader.get_pdos(2, -2, spin="dn").tolist() == [12.5]
        assert reader.get_tdos(spin=0).tolist() == [15]
        assert reader.get_tdos(spin=1).tolist() == [15]
        assert reader.get_inttdos(spin=1).tolist() == [15.5]
