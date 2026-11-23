"""年別 BAV リーダーと2026年版の SCF 読み取りを検証する。"""

from inspect import signature
from unittest.mock import Mock

import pytest

from fdmnes_util.fdm_bav import FdmBav
from fdmnes_util.fdm_bav_2016 import FdmBav2016
from fdmnes_util.fdm_bav_2020 import FdmBav2020
from fdmnes_util.fdm_bav_2026 import FdmBav2026


@pytest.mark.parametrize("reader", [FdmBav2016, FdmBav2020, FdmBav2026])
def test_bav_readers_define_version_local_parsers(reader):
    """SAEと同じく、各版の解析をその版のクラスに置く。"""
    assert reader.__bases__ == (object,)
    methods = (
        "get_edge",
        "get_nspin",
        "is_self_consistent",
        "get_max_scf_iterations",
        "get_n_scf_loop",
        "get_scf_toten",
        "get_position",
        "get_atoms_index_j",
        "get_natom",
        "get_e_edge",
        "get_ngroup",
        "get_t",
        "get_lmax",
    )
    for name in methods:
        method = vars(reader)[name]
        assert method.__qualname__ == f"{reader.__name__}.{name}"
        assert signature(vars(FdmBav)[name], eval_str=True) == signature(method)
    public = {
        name
        for name in vars(reader)
        if name.startswith("get_") or name == "is_self_consistent"
    }
    assert public == set(methods)


@pytest.mark.parametrize(
    ("revision", "reader_class"),
    [
        ("FDMNES II program, Revision 1st of September 20", FdmBav2016),
        ("FDMNES program, Revision 1st of July 2020", FdmBav2020),
        ("FDMNES program, Revision 29th of June 2021", FdmBav2020),
        (FdmBav2026.REVISION, FdmBav2026),
    ],
)
def test_bav_facade_delegates_to_selected_reader(tmp_path, revision, reader_class):
    path = tmp_path / "Fe_bav.txt"
    path.write_text(f"{revision}\nThreshold: K\n")
    bav = FdmBav(path)
    assert type(bav.select_reader()) is reader_class
    assert bav.get_edge() == "K"
    assert bav.get_scf_history() == []

    delegate = Mock(spec=reader_class)
    bav._reader = delegate
    for name in vars(reader_class):
        if name.startswith("get_") or name == "is_self_consistent":
            assert getattr(bav, name)() is getattr(delegate, name).return_value
            getattr(delegate, name).assert_called_once_with()


def test_scf_cycle_and_energy(tmp_path):
    path = tmp_path / "Fe_bav.txt"
    path.write_text(
        f"{FdmBav2026.REVISION}\n"
        " Threshold: Iron K1 edge\n"
        " Self consistent calculation\n"
        " Cycle 1, Fermi energy = -9.371 eV\n"
        " Cycle 2, Fermi energy = -10.211 eV\n"
        " Excited atom total energy = -1000 eV\n"
        " Total energy = -4.38755D+04 eV, Delta energy = 1329.203 eV\n"
        " Last cycle, XANES calculation\n"
        " Total energy = -999 eV, Delta energy = 0.0 eV\n"
    )
    bav = FdmBav(path)
    assert type(bav.select_reader()) is FdmBav2026
    assert bav.get_edge() == "Iron K1 edge"
    assert bav.get_scf_history() == [(1, None), (2, -43875.5)]
    assert bav.get_n_scf_loop() == 2
    assert bav.get_scf_toten() == [-43875.5]


def test_fermi_cycle_without_scf(tmp_path):
    path = tmp_path / "Ni_bav.txt"
    path.write_text(
        f"{FdmBav2026.REVISION}\n"
        " Magnetic calculation without spin-orbit interaction\n"
        " Cycle 1, Fermi Energy = -11.054 eV\n"
    )
    bav = FdmBav(path)
    assert bav.get_nspin() == 2
    assert bav.get_scf_history() == []
    assert bav.get_n_scf_loop() == 0
    assert bav.get_scf_toten() == []


def test_unverified_november_2026_revision_is_rejected(tmp_path):
    path = tmp_path / "Fe_bav.txt"
    path.write_text("FDMNES program, Revision 6th of November 2026\n")
    with pytest.raises(ValueError, match="Unverified BAV layout"):
        FdmBav(path).select_reader()
