#!/usr/bin/env python3
"""Regression tests for the FDMNES class library."""

from pathlib import Path
import shutil
import numpy as np
import pytest
import importlib.util


def load_script(filename):
    """Import an editable example by its published script filename."""
    path = Path(__file__).resolve().parents[1] / "scripts" / filename
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fd_clean = load_script("FDclean.py")
fd_move = load_script("FDmove.py")
fd_conv_e2photoe = load_script("FDconv_e2photoe.py")
fd_getfermi = load_script("FDgetfermi.py")
fd_make_conv_allsite = load_script("FDmakeCconvAllsite.py")
fd_bav2xyz = load_script("FDbav2xyz.py")
fd_xas = load_script("fdXAS.py")
fd_ldos = load_script("fdLDOS.py")

F = Path(__file__).parent / "fixtures"


def prepare(tmp_path):
    """prepareの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。

    Returns:
        処理結果。

    """
    for name in ("Fe.txt", "Fe_conv.txt", "Fe_sd0.txt", "Fe_bav.txt"):
        shutil.copy(F / name, tmp_path / name)
    (tmp_path / "read_pdb.inp").write_text("Filout\n  Fe\nEND\n")


def test_getfermi_and_conversion(tmp_path, monkeypatch, capsys):
    """test_getfermi_and_conversionの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。
        monkeypatch: monkeypatchを指定する。
        capsys: capsysを指定する。

    Returns:
        処理結果。

    """
    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    fd_getfermi.main([])
    assert "7112.0" in capsys.readouterr().out
    fd_conv_e2photoe.main([])
    data = np.loadtxt("Fe_conv_photoe.txt")
    assert np.isclose(data[0, 0], 7097.0)


def test_getfermi_selects_batch_input(tmp_path, monkeypatch, capsys):
    """Use the first batch job and let an explicit input take precedence."""
    prepare(tmp_path)
    (tmp_path / "read_pdb.inp").rename(tmp_path / "job.inp")
    (tmp_path / "fdmfile.txt").write_text("1\njob.inp\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    fd_getfermi.main([])
    assert "7112.0" in capsys.readouterr().out

    (tmp_path / "fdmfile.txt").write_text("1\nmissing.inp\n", encoding="utf-8")
    fd_getfermi.main(["-i", "job.inp"])
    assert "7112.0" in capsys.readouterr().out


def test_clean(tmp_path, monkeypatch):
    """test_cleanの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。
        monkeypatch: monkeypatchを指定する。

    Returns:
        処理結果。

    """
    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    fd_clean.main([])
    assert not (tmp_path / "Fe_sd0.txt").exists()
    assert not (tmp_path / "Fe.txt").exists()
    assert (tmp_path / "read_pdb.inp").exists()


def test_move(tmp_path, monkeypatch):
    """test_moveの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。
        monkeypatch: monkeypatchを指定する。

    Returns:
        処理結果。

    """
    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    fd_move.main(["-d", "archive"])
    assert (tmp_path / "archive/Fe_bav.txt").is_file()
    assert not (tmp_path / "Fe_bav.txt").exists()
    assert (tmp_path / "read_pdb.inp").exists()


def test_bav2xyz_real_data(tmp_path, capsys):
    """test_bav2xyz_real_dataの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。
        capsys: capsysを指定する。

    Returns:
        処理結果。

    """
    path = tmp_path / "Fe_bav.txt"
    shutil.copy(F / "Fe_bav.txt", path)
    fd_bav2xyz.main([str(path).removesuffix("_bav.txt")])
    xyz = tmp_path / "Fe.xyz"
    assert xyz.exists()
    lines = xyz.read_text().splitlines()
    assert lines[2].startswith(" Fe ")
    assert lines[3].startswith(" O ")


def test_convolution_allsite(tmp_path, monkeypatch):
    """test_convolution_allsiteの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。
        monkeypatch: monkeypatchを指定する。

    Returns:
        処理結果。

    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "conv.inp").write_text("Filout\n Fe\nEND\n")
    for i in (1, 2):
        (tmp_path / f"Fe_{i}.txt").write_text("data\n")
    fd_make_conv_allsite.main([])
    assert (tmp_path / "fdmfile.txt").exists()
    assert (tmp_path / "conv_2.inp").exists()


def test_plotting_cli(tmp_path, monkeypatch):
    """test_plotting_cliの処理を実行する。

    Args:
        tmp_path: tmp_pathを指定する。
        monkeypatch: monkeypatchを指定する。

    Returns:
        処理結果。

    """
    pytest.importorskip("matplotlib")
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure

    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    savefig = Figure.savefig
    shown = []

    def check_sae_figure(figure, filename, **kwargs):
        (axis,) = figure.axes
        np.testing.assert_allclose(
            axis.get_position().bounds,
            [0.17, 0.08, 0.75, 0.415],
        )
        assert len(axis.lines) == 2
        np.testing.assert_array_equal(axis.lines[1].get_xdata(), [0, 0])
        if Path(filename).name == "xas.pdf":
            assert axis.get_xlabel() == "Energy above Fermi [eV]"
            assert axis.get_ylabel() == "Absorption [arb. unit]"
        else:
            sd = np.loadtxt(F / "Fe_sd0.txt", skiprows=1)
            np.testing.assert_array_equal(axis.lines[0].get_ydata(), sd[:, 6])
        return savefig(figure, filename, **kwargs)

    monkeypatch.setattr(Figure, "savefig", check_sae_figure)
    monkeypatch.setattr(plt, "show", lambda: shown.append(plt.gcf()))
    fd_xas.main(["-o", "xas.pdf"])
    assert len(shown) == 1
    shutil.copyfile(F / "Fe_sd0.txt", tmp_path / "Fe_sd1.txt")
    fd_ldos.main(["-o", "ldos.pdf"])
    assert len(shown) == 2
    assert (tmp_path / "xas.pdf").stat().st_size > 100
    assert (tmp_path / "ldos.pdf").stat().st_size > 100


def test_move_renames_explicit_prefix(tmp_path, monkeypatch):
    """Apply the SAE source/destination syntax to spectra and site files."""
    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    fd_move.main(["Fe", "Fe-run2"])
    assert (tmp_path / "Fe-run2.txt").is_file()
    assert (tmp_path / "Fe-run2_sd0.txt").is_file()
    assert not (tmp_path / "Fe.txt").exists()
    assert (tmp_path / "read_pdb.inp").is_file()


def test_move_collision_preserves_results(tmp_path, monkeypatch):
    """Validate all target filenames before changing the first result."""
    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "Fe-run2_sd0.txt").write_text("existing output")
    with pytest.raises(FileExistsError):
        fd_move.main(["Fe", "Fe-run2"])
    assert (tmp_path / "Fe.txt").is_file()
    assert not (tmp_path / "Fe-run2.txt").exists()


def test_clean_uses_batch_input(tmp_path, monkeypatch):
    """Resolve the first batch job before cleaning its generated files."""
    prepare(tmp_path)
    (tmp_path / "read_pdb.inp").rename(tmp_path / "job.inp")
    (tmp_path / "fdmfile.txt").write_text("1\njob.inp\n")
    monkeypatch.chdir(tmp_path)
    fd_clean.main([])
    assert (tmp_path / "job.inp").is_file()
    assert not (tmp_path / "Fe.txt").exists()


def test_bav2xyz_stdout_matches_file(tmp_path, monkeypatch, capsys):
    """Preserve the XYZ precision in both output modes."""
    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    fd_bav2xyz.main(["-i", "Fe", "--std"])
    stdout = capsys.readouterr().out
    fd_bav2xyz.main([])
    assert stdout == (tmp_path / "Fe.xyz").read_text()


def test_plot_xas_uses_independent_grids(tmp_path, monkeypatch):
    """Capture the two reference-shifted spectra passed through the sample."""
    sample = load_script("FDplot_XAS.py")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "read_pdb.inp").write_text("Filout Fe\nEnd\n")
    (tmp_path / "Fe.txt").write_text(
        "7112 26 -5 = E_edge Z E_Fermi\nEnergy XAS\n-10 1\n0 2\n"
    )
    (tmp_path / "Fe_conv.txt").write_text("Energy XAS\n-4 1\n-2 2\n0 3\n")

    captured = {}

    def capture(plotter, spectra, output, **kwargs):
        """Record the arguments that would be passed to the renderer."""
        captured["spectra"] = spectra
        captured["fermi_position"] = kwargs["fermi_position"]

    monkeypatch.setattr(sample.PlotFdmXas, "plot_composite", capture)
    sample.main(["--fermi", "--nw"])
    raw, convolved = captured["spectra"]
    assert raw[0].tolist() == [-5, 5]
    assert convolved[0].tolist() == [1, 3, 5]
    assert captured["fermi_position"] == 0


def test_plot_xas_overlay_writes_pdf(tmp_path, monkeypatch):
    """Render the raw and broadened spectra from the supplied SAE Fe outputs."""
    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    output = load_script("FDplot_XAS.py").main(["--nonsubtract", "--nw"])
    assert output.read_bytes().startswith(b"%PDF-")
