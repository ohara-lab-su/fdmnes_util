#!/usr/bin/env python3
"""年別の FDMNES SD リーダーの選択を検証する。"""

from inspect import getmembers, isroutine, signature
from unittest.mock import patch

import numpy as np
import pytest

from fdmnes_util.fdm_sd import FdmSd
from fdmnes_util.fdm_sd_2016 import FdmSd2016
from fdmnes_util.fdm_sd_2020 import FdmSd2020
from fdmnes_util.fdm_sd_2026 import FdmSd2026


def test_sd_reader_public_methods_have_the_same_signatures(tmp_path):
    def interface(reader):
        return {
            name: signature(method)
            for name, method in getmembers(reader, isroutine)
            if name.startswith("get_")
        }

    assert interface(FdmSd2016) == interface(FdmSd2020) == interface(FdmSd2026)
    assert FdmSd2026.__bases__ == (object,)
    path = tmp_path / "sd.txt"
    path.write_text("Energy (0,0) Int(s) total Int(total)\n0 2 3 2 3\n")
    selector = FdmSd(path, format_year=None)
    reader = selector.select_reader()
    assert interface(selector) == interface(reader)
    np.testing.assert_array_equal(selector.get_ldos(), reader.get_ldos())


def test_2016_dispatch_preserves_spin_and_weight():
    """2016形式固有の引数を2016年リーダーに渡すことを検証する。"""
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
    """不要なスピン引数を渡さずに2020年リーダーを使うことを検証する。"""
    with patch("fdmnes_util.fdm_sd.FdmSd2020") as reader_class:
        selector = FdmSd("example_sd0.txt", format_year=2020, weight=2)
        result = selector.select_reader()

    reader_class.assert_called_once_with(selector.path, weight=2)
    assert result is reader_class.return_value


def test_unverified_format_is_rejected():
    """2022年形式を暗黙に2020年形式として扱わないことを検証する。"""
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
    """対応する BAV や改訂年を使わず SD の形式を選べることを検証する。"""
    path = tmp_path / "example_sd0.txt"
    path.write_text(f"{header}\n{row}\n", encoding="utf-8")
    reader = FdmSd(path, format_year=None).select_reader()
    assert isinstance(reader, reader_type)


def test_magnetic_2020_sd_columns(tmp_path):
    """2021年版と2026年版の Ni 出力で確認した31列の読み取りを検証する。"""
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


@pytest.mark.parametrize("year", [None, 2026])
def test_complex_sd_keeps_density_and_integral_interface(tmp_path, year):
    path = tmp_path / "Fe_sd0.txt"
    path.write_text(
        "Energy (0,0) Int(s) (1,-1) (1,0) (1,1) p Int(p) total Int(total)\n"
        "-1 2 3 4 5 6 15 7 17 10\n"
    )
    reader = FdmSd(path, format_year=year, weight=2).select_reader()
    assert type(reader) is FdmSd2026
    assert reader.get_ispin() == 1
    assert reader.get_ldos("s").tolist() == [1]
    assert reader.get_intldos("s").tolist() == [1.5]
    assert reader.get_pdos(1, -1).tolist() == [2]
    assert reader.get_pdos(lm="(1,0)").tolist() == [2.5]
    assert reader.get_inttdos().tolist() == [5]
    with pytest.raises(KeyError):
        reader.get_pdos(lm="px")


@pytest.mark.parametrize(
    ("f_columns", "tesseral"),
    [
        ("fxyz fx3 fy3 fz3 fx(y2-z2) fy(z2-x2) fz(x2-y2)", False),
        ("(3,-3) fxyz (3,-1) fz3 (3,1) fz(x2-y2) (3,3)", True),
    ],
)
def test_real_f_sd_uses_exact_orbital_names(tmp_path, f_columns, tesseral):
    columns = (
        "Energy s Int(s) px py pz p Int(p) dx2-y2 dz2 dyz dxz dxy d Int(d) "
        f"{f_columns} f Int(f) total Int(total)"
    ).split()
    path = tmp_path / "Au_sd0.txt"
    row = " ".join(str(index) for index in range(len(columns)))
    path.write_text(f"{' '.join(columns)}\n{row}\n")
    reader = FdmSd(path, format_year=None).select_reader()
    assert type(reader) is FdmSd2026
    assert reader.get_lmax() == 3
    assert reader.get_ldos(3).tolist() == [columns.index("f")]
    assert reader.get_intldos(3).tolist() == [columns.index("Int(f)")]
    assert reader.get_pdos(lm="fxyz").tolist() == [columns.index("fxyz")]
    if tesseral:
        assert reader.get_pdos(l=3, m=-2).tolist() == [columns.index("fxyz")]
