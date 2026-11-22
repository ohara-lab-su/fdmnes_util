#!/usr/bin/env python3
"""Regression tests for the FDMNES class library."""

from pathlib import Path
import numpy as np
import pytest
from fdmnes_util.fdm_sd_2020 import FdmSd2020
from fdmnes_util.fdm_sd_2016 import FdmSd2016
from fdmnes_util.fdm_sd import FdmSd
from fdmnes_util.fdm_bav import FdmBav
from fdmnes_util.fdm_txt import FdmTxt
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from fdmnes_util.fdm_photoenergy import FdmPhotoenergy
from fdmnes_util.fdm_inp import FdmInp

F = Path(__file__).parent / "fixtures"


def test_2020_sd_orbitals():
    """test_2020_sd_orbitalsの処理を実行する。

    Returns:
        処理結果。

    """
    sd = FdmSd2020(F / "Fe_sd0.txt")
    assert sd.get_lmax() == 2
    assert np.allclose(
        sd.get_tdos(), sd.get_ldos("s") + sd.get_ldos("p") + sd.get_ldos("d")
    )
    assert np.allclose(sd.get_pdos(lm="dxy"), sd.get_pdos(l=2, m=-2))
    assert len(sd.get_inttdos()) == len(sd.get_eng())


def test_2020_reject_old_header(tmp_path):
    """test_2020_reject_old_headerの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。

    Returns:
        処理結果。

    """
    p = tmp_path / "old_sd.txt"
    p.write_text("Energy Int_t n(0,0) Intn(0,0) n_l(0) Intn_l(0)\n0 1 2 3 4 5\n")
    with pytest.raises(ValueError):
        FdmSd2020(p)


def test_2016_separate_layout(tmp_path):
    """test_2016_separate_layoutの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。

    Returns:
        処理結果。

    """
    p = tmp_path / "old_sd.txt"
    p.write_text(
        "Energy Int_t n(0,0) Intn(0,0) n_l(0) Intn_l(0)\n0 1 2 3 4 5\n1 1 3 4 5 6\n"
    )
    sd = FdmSd2016(p)
    assert np.array_equal(sd.get_eng(), [0.0, 1.0])
    assert sd.get_pdos(lm="s")[0] == 2
    assert sd.get_tdos()[0] == 4
    assert sd.get_inttdos()[0] == 6


def test_unverified_2022_not_silently_mapped():
    """test_unverified_2022_not_silently_mappedの処理を実行する。

    Returns:
        処理結果。

    """
    with pytest.raises(ValueError, match="Unverified"):
        FdmSd(F / "Fe_sd0.txt", format_year=2022).select_reader()


def test_2020_bav_version():
    """test_2020_bav_versionの処理を実行する。

    Returns:
        処理結果。

    """
    log = FdmBav(F / "Fe_bav.txt")
    assert log.year == 2020
    assert type(log.select_reader()).__name__ == "FdmBav2020"


def test_bav_recognizes_truncated_september_2016_revision(tmp_path):
    """The September 2016 binary writes its revision into 50 characters."""
    path = tmp_path / "old_bav.txt"
    path.write_text("   FDMNES II program, Revision 1st of September 20\n")
    log = FdmBav(path)
    assert log.year == 2016
    assert type(log.select_reader()).__name__ == "FdmBav2016"


def test_xas_and_conversion(tmp_path):
    """test_xas_and_conversionの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。

    Returns:
        処理結果。

    """
    x = FdmTxt(F / "Fe.txt")
    c = FdmConv(F / "Fe_conv.txt")
    energy, y = AnalyzeFdmXas.photon_energy(c, x)
    assert np.isclose(energy[0], x.edge_energy + c.get_eng()[0])
    out = FdmPhotoenergy().write(energy, y, tmp_path / "Fe_conv_photoe.txt")
    assert np.loadtxt(out).shape[0] == len(energy)


def test_convolution_header_keeps_parameters_and_column_names(tmp_path):
    path = tmp_path / "Fe_conv.txt"
    path.write_text(
        "# FDMNES program, Revision 5th of November 2026\n"
        "# 7112.0 1.25 10.0 -0.66631 = E_edge, Gamma_hole, Gamma_max, E_cut\n"
        "# 0.76830 -0.2 = Shifts\n"
        "    Energy    <xanes>\n"
        " -2.00000  3.4835903E-04\n"
    )
    reader = FdmConv(path)
    assert reader.format_year == 2026
    assert reader.header == "Energy    <xanes>"
    assert reader.parameters["E_edge"] == 7112.0
    assert reader.shifts == (0.76830, -0.2)
    assert reader.get_eng().tolist() == [-2]
    assert reader.get_xas().tolist() == [3.4835903e-4]

    ordinary = FdmConv(F / "Fe_conv.txt")
    assert ordinary.format_year == 2016
    np.testing.assert_array_equal(
        ordinary.get_eng(), ordinary.select_reader().get_eng()
    )


def test_combined_input_round_trip(tmp_path):
    path = FdmInp.write_convolution(
        tmp_path / "conv.inp",
        [("Fe_sites_1", 1, 0.2), ("Fe_sites_2", 1, -0.2)],
        output="weighted_conv.txt",
        format_year=2026,
        header=True,
        energy_step=0.25,
        per_atom=True,
    )
    reader = FdmInp(path, format_year=2026)
    assert reader.get_calculation() == "Fe_sites_1"
    assert reader.get_calculations() == [
        ("Fe_sites_1", 1.0, 0.2, None),
        ("Fe_sites_2", 1.0, -0.2, None),
    ]
    assert reader.get_conv_out() == "weighted_conv.txt"
    assert "header" in reader.tags
    assert reader.tags["e_step_conv"] == ["0.25"]
    assert "per_atom" in reader.tags


def test_read_multi_absorber_last_record(tmp_path):
    path = tmp_path / "sites.inp"
    path.write_text("Absorber 4\nAbsorber\n2 5\nDensity\nEND\n")
    reader = FdmInp(path, format_year=2026)
    assert reader.get_absorber() == 2
    assert reader.get_absorbers() == [2, 5]
    with pytest.raises(ValueError):
        FdmInp(path).get_absorber()


def test_input_missing_crystal(tmp_path):
    """test_input_missing_crystalの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。

    Returns:
        処理結果。

    """
    p = tmp_path / "a.inp"
    p.write_text("Filout\n  Fe\nConvolution\nEND\n")
    r = FdmInp(p)
    assert r.get_filout() == "Fe" and r.get_convolution()
    assert r.get_cellparam() is None


def test_plot(tmp_path):
    """test_plotの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。

    Returns:
        処理結果。

    """
    pytest.importorskip("matplotlib")
    from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas
    from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos

    x = FdmTxt(F / "Fe.txt")
    s = FdmSd2020(F / "Fe_sd0.txt")
    assert (
        PlotFdmXas()
        .plot([(x.energy, x.get_xas(), "Fe")], tmp_path / "x.pdf")
        .stat()
        .st_size
        > 100
    )
    assert PlotFdmDos().plot(s, tmp_path / "d.pdf").stat().st_size > 100


def test_fdmfile_write_and_read(tmp_path):
    """test_fdmfile_write_and_readの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。

    Returns:
        処理結果。

    """
    from fdmnes_util.fdmfile import Fdmfile

    path = tmp_path / "fdmfile.txt"
    Fdmfile.write(["a.inp", "b.inp"], path)
    assert Fdmfile(path).filenames == ["a.inp", "b.inp"]


def test_conv_allsite(tmp_path):
    """test_conv_allsiteの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。

    Returns:
        処理結果。

    """
    from fdmnes_util.fdm_convolution_inputs import FdmConvolutionInputs
    from fdmnes_util.fdmfile import Fdmfile

    for i in (1, 2):
        (tmp_path / f"Fe_{i}.txt").write_text("data")
    (tmp_path / "Fe_bav.txt").write_text("ignore")
    files = FdmConvolutionInputs().write(tmp_path / "Fe", tmp_path)
    assert len(files) == 2
    assert Fdmfile(tmp_path / "fdmfile.txt").filenames == files


def test_result_clean_and_move_different_sets(tmp_path):
    """test_result_clean_and_move_different_setsの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。

    Returns:
        処理結果。

    """
    from fdmnes_util.fdm_result_files import FdmResultFiles

    for name in ("Fe.txt", "Fe_bav.txt", "Fe_sd0.txt", "fdm.out"):
        (tmp_path / name).write_text("x")
    obj = FdmResultFiles(tmp_path / "Fe")
    moved = obj.move(tmp_path / "dest")
    assert len(moved) == 3 and (tmp_path / "fdm.out").exists()
    deleted = obj.clean()
    assert [x.name for x in deleted] == ["fdm.out"]


def test_fermi_metadata():
    """test_fermi_metadataの処理を実行する。

    Returns:
        処理結果。

    """
    reader = FdmTxt(F / "Fe.txt")
    assert reader.get_efermi() == 0.0
    assert reader.parameters["E_edge"] == reader.edge_energy


def test_xas_metadata_uses_parameter_names(tmp_path):
    """Use the original SAE value-to-name mapping for edge energy and Z."""
    path = tmp_path / "sample.txt"
    path.write_text(
        "26 7112.0 4.5 = Z, E_edge, E_Fermi\nEnergy <xanes>\n0 1\n",
        encoding="utf-8",
    )
    reader = FdmTxt(path)
    assert reader.atomic_number == 26
    assert reader.get_eedge() == 7112.0
    assert reader.get_efermi() == 4.5


def test_log_xyz_real_file():
    """test_log_xyz_real_fileの処理を実行する。

    Returns:
        処理結果。

    """
    log = FdmBav(F / "Fe_bav.txt").select_reader()
    symbols = log.get_atoms_index_j()
    positions = log.get_position()
    assert symbols[0] == "Fe" and symbols[1] == "O"
    assert np.allclose(positions[0], [0, 0, 0])
    assert np.isclose(positions[1, 0], -1.4245090371)
    assert log.get_lmax() == 2
    assert log.get_ngroup() == 56
    assert log.get_e_edge() == 7112


@pytest.mark.parametrize("year", [2016, 2020])
def test_bav_scf_records(tmp_path, year):
    """Read SAE's final cycle index, configured limit, and SCF energies."""
    log_path = tmp_path / "test_bav.txt"
    log_path.write_text(
        f"FDMNES program, Revision 1st of June {year}\n"
        "Self consistent calculation\n"
        "Maximum number of iteration = 25\n"
        "Begining of cycle 4\n"
        "Unit cell energy = -1.2D+03 eV\n"
        "Beginning of cycle 7\n"
        "Unit cell energy = -1.3D+03 eV\n",
        encoding="utf-8",
    )
    log = FdmBav(log_path).select_reader()
    assert log.is_self_consistent()
    assert log.get_max_scf_iterations() == 25
    assert log.get_n_scf_loop() == 7
    assert log.get_scf_toten() == [-1200, -1300]


@pytest.mark.parametrize("record", ["", "Absorber 3\n", "Absorber\n3\n"])
def test_absorber_index(tmp_path, record):
    """Read inline and multiline SAE absorber records with the default of one."""
    path = tmp_path / "test.inp"
    path.write_text(record + "End\n")
    expected = 1
    if record:
        expected = 3
    assert FdmInp(path).get_absorber() == expected


def test_2020_does_not_return_up_dos_for_down_spin():
    """Apply channel validation to every DOS accessor."""
    sd = FdmSd2020(F / "Fe_sd0.txt")
    methods = [sd.get_ldos, sd.get_intldos, sd.get_pdos, sd.get_tdos, sd.get_inttdos]
    for method in methods:
        with pytest.raises(ValueError, match="one spin channel"):
            method(spin="down")


def test_2016_spin_aliases(tmp_path):
    """Compare the original SAE spin names against explicit column indices."""
    source = tmp_path / "spin_sd0.txt"
    source.write_text(
        "Energy Int_t(u) Int_t(d) n(0,0,u) Intn(0,0,u) "
        "n(0,0,d) Intn(0,0,d) n_l(0,u) Intn_l(0,u) n_l(0,d) Intn_l(0,d)\n"
        "0 1 2 3 4 5 6 7 8 9 10\n",
        encoding="utf-8",
    )
    sd = FdmSd2016(source, ispin=2)
    assert sd.get_ldos("s", spin="up").tolist() == [7]
    assert sd.get_pdos(lm="s", spin="down").tolist() == [5]
    assert sd.get_intldos("s", spin="dn").tolist() == [10]
    assert sd.get_inttdos(spin="down").tolist() == [12]


def test_batch_list_reads_original_sae_fixture():
    """Skip the original comment preamble and honor the declared job count."""
    from fdmnes_util.fdmfile import Fdmfile

    assert Fdmfile(F / "fdmfile.txt").filenames == ["read_pdb.inp"]


def test_magnetism_sets_spin_channels(tmp_path):
    """Recognize SAE's Magnetism keyword when selecting SD spin columns."""
    path = tmp_path / "test.inp"
    path.write_text("Magnetism\nEnd\n", encoding="utf-8")
    assert FdmInp(path).get_ispin() == 2


def test_bav_rejects_unverified_revision(tmp_path):
    """Keep the 2022 BAV format distinct until its layout can be verified."""
    path = tmp_path / "test_bav.txt"
    path.write_text("FDMNES program, Revision 1st of June 2022\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Unverified BAV layout"):
        FdmBav(path).select_reader()


def test_bav_ii_header_and_last_cluster(tmp_path):
    """Use SAE's revision recognition and last cluster in a multi-site log."""
    path = tmp_path / "sample_bav.txt"
    path.write_text(
        "FDMNES II program, Revision 29th of January 2019\n"
        "Cluster: atom positions in order, in the internal R2 bases\n"
        " Z posx posy posz\n"
        "29 0 0 0\n\n"
        "Transformation Crystal Bases, Bases R2\n"
        " 1 0 0\n 0 1 0\n 0 0 1\n"
        "Cluster: atom positions in order, in the internal R2 bases\n"
        " Z posx posy posz\n"
        " 8 1 2 3\n\n"
        "Transformation Crystal Bases, Bases R2\n"
        " 1 2 3\n 4 5 6\n 7 8 9\n",
        encoding="utf-8",
    )
    log = FdmBav(path)
    assert log.year == 2019
    reader = log.select_reader()
    assert reader.revision.startswith("FDMNES II program,")
    assert reader.get_atoms_index_j() == ["O"]
    np.testing.assert_array_equal(reader.get_position(), [[1, 2, 3]])
    np.testing.assert_array_equal(reader.get_t(), [[1, 4, 7], [2, 5, 8], [3, 6, 9]])


def test_input_scalar_getters_use_last_definition(tmp_path):
    """Keep all records while returning the last value as SAE does."""
    path = tmp_path / "sample.inp"
    path.write_text(
        "Filout first\nFile_out\n final\n"
        "Absorber 1\nAbsorber\n 3\n"
        "Calculation first_result\nCalculation\n last_result 0.5 1.25\nEnd\n",
        encoding="utf-8",
    )
    reader = FdmInp(path)
    assert reader.get_filout() == "final"
    assert reader.get_absorber() == 3
    assert reader.get_calculation() == "last_result"
    assert reader.tags["calculation"] == ["first_result", "last_result 0.5 1.25"]
