#!/usr/bin/env python3
"""Check SAE composite plotting through its editable sample entry points."""

from pathlib import Path

import numpy as np
import pytest

from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.fdm_sd_2020 import FdmSd2020
from fdmnes_util.fdm_txt import FdmTxt
from test_commands import load_script, prepare


@pytest.fixture
def capture_figures(monkeypatch):
    """Record live Matplotlib figures while still writing all requested files."""
    pytest.importorskip("matplotlib")
    from matplotlib.figure import Figure

    outputs = {}
    savefig = Figure.savefig

    def capture(figure, filename, *args, **kwargs):
        """Keep the figure and delegate to the real format writer."""
        outputs[Path(filename)] = figure
        return savefig(figure, filename, *args, **kwargs)

    monkeypatch.setattr(Figure, "savefig", capture)
    return outputs


def test_xas_experiment_and_site_average(tmp_path, monkeypatch, capture_figures):
    """Compare averaged XAS and DOS arrays, panel order, and three file formats."""
    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    for site, scale in ((1, 1), (3, 2)):
        Path(f"Fe_{site}.txt").write_text(
            f"7112 26 -5 = E_edge Z E_Fermi\nEnergy XAS\n-2 {scale}\n0 {2 * scale}\n"
        )
        Path(f"Fe_{site}_conv.txt").write_text(
            f"Energy XAS\n-1 {4 * scale}\n0 {5 * scale}\n1 {6 * scale}\n"
        )
        reader = FdmSd2020("Fe_sd0.txt")
        matrix = reader.values[:4].copy()
        matrix[:, 1:] *= scale
        np.savetxt(
            f"Fe_{site}_sd0.txt",
            matrix,
            header=" ".join(reader.columns),
            comments="",
        )
    Path("Fe_obs.txt.nor").write_text("7108 0.2\n7109 0.4\n")
    sample = load_script("FDplot_XAS.py")
    main_path = sample.main(
        [
            "-a",
            "1",
            "3",
            "-w",
            "6",
            "-x",
            "3",
            "-d",
            "-o",
            "Fe_obs.txt.nor",
            "--pdf",
            "--nw",
        ]
    )

    figure = capture_figures[main_path]
    calculated, observed, dos = figure.axes
    assert [axis.get_subplotspec().num1 for axis in (observed, calculated, dos)] == [
        0,
        1,
        2,
    ]
    assert list(calculated.lines[0].get_xdata()) == [7110, 7112]
    assert list(calculated.lines[1].get_xdata()) == [7111, 7112, 7113]
    np.testing.assert_allclose(calculated.lines[0].get_ydata(), [0.5, 1])
    np.testing.assert_allclose(calculated.lines[1].get_ydata(), [2, 2.5, 3])
    np.testing.assert_allclose(observed.lines[0].get_ydata(), [0.2, 0.4])
    original = FdmSd2020("Fe_sd0.txt")
    np.testing.assert_allclose(dos.lines[0].get_xdata(), original.get_eng()[:4] + 7112)
    np.testing.assert_allclose(dos.lines[1].get_ydata(), original.get_ldos("p")[:4])
    np.testing.assert_allclose(FdmTxt("Fe_0.txt").get_xas(), [0.5, 1])
    np.testing.assert_allclose(FdmConv("Fe_0_conv.txt").get_xas(), [2, 2.5, 3])
    np.testing.assert_allclose(FdmSd2020("Fe_0_sd0.txt").values, original.values[:4])
    assert Path("XAS.pdf").read_bytes().startswith(b"%PDF-")
    assert Path("XAS.eps").read_bytes().startswith(b"%!PS-Adobe")
    assert Path("XAS.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_ldos_projection_integral_and_raw_overlay(
    tmp_path, monkeypatch, capture_figures
):
    """Use a real 2020 SD file and compare the plot with its stored columns."""
    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    sample = load_script("FDplot_LDOS.py")
    output = sample.main(
        [
            "--broad",
            "--p",
            "--total",
            "--intdos",
            "--fermi",
            "--txtweight",
            "2",
            "--xasweight",
            "4",
            "--dosweight",
            "2",
            "--dmax_p",
            "5",
            "--nw",
        ]
    )
    assert output == Path("LDOS0_fermi.pdf")
    axes = capture_figures[output].axes
    assert len(axes) == 5
    xas, total, total_integral, orbital, orbital_integral = axes
    assert xas.get_position().y0 < total.get_position().y0 < orbital.get_position().y0
    assert xas.get_xlabel() == "Energy above Fermi [eV]"
    assert orbital.get_ylim()[1] == 5
    raw = FdmTxt("Fe.txt")
    convolved = FdmConv("Fe_conv.txt")
    reader = FdmSd2020("Fe_sd0.txt")
    np.testing.assert_allclose(xas.lines[0].get_xdata(), convolved.get_eng())
    np.testing.assert_allclose(xas.lines[0].get_ydata(), convolved.get_xas() / 4)
    np.testing.assert_allclose(xas.lines[1].get_ydata(), raw.get_xas() / 2)
    np.testing.assert_allclose(total.lines[0].get_ydata(), reader.get_tdos() / 2)
    np.testing.assert_allclose(
        total_integral.lines[0].get_ydata(), reader.get_inttdos() / 2
    )
    np.testing.assert_allclose(
        orbital_integral.lines[0].get_ydata(), reader.get_intldos("p") / 2
    )


def test_pdos_orbital_blocks(tmp_path, monkeypatch, capture_figures):
    """Check that plotted groups and projection magnitudes follow the SAE PDOS layout."""
    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    output = load_script("FDplot_PDOS.py").main(
        ["--xas", "--spd", "--label", "Fe", "--output", "projection", "--pdf", "--nw"]
    )
    assert output == Path("projection_0.pdf")
    xas, d_axis, p_axis, s_axis = capture_figures[output].axes
    assert [axis.get_position().y0 for axis in (xas, d_axis, p_axis, s_axis)] == sorted(
        axis.get_position().y0 for axis in (xas, d_axis, p_axis, s_axis)
    )
    reader = FdmSd2020("Fe_sd0.txt")
    line = d_axis.lines[2]
    assert line.get_label() == "Fe-d_3z2-r2"
    np.testing.assert_allclose(line.get_ydata(), reader.get_pdos(lm="dz2"))
    np.testing.assert_allclose(line.get_xdata(), reader.get_eng() + 7112)
    assert Path("projection_0.png").stat().st_size > 100


def test_magnetic_ldos_inverts_down_axis(tmp_path, monkeypatch, capture_figures):
    """Preserve positive spin-down densities while reversing its visual axis."""
    monkeypatch.chdir(tmp_path)
    Path("read_pdb.inp").write_text("Filout Fe\nMagnetism\nEnd\n")
    Path("Fe.txt").write_text("7112 26 -5 = E_edge Z E_Fermi\nEnergy XAS\n-4 1\n-2 2\n")
    Path("Fe_sd0.txt").write_text(
        "Energy Int_t(u) Int_t(d) n(0,0,u) Intn(0,0,u) n(0,0,d) "
        "Intn(0,0,d) n_l(0,u) Intn_l(0,u) n_l(0,d) Intn_l(0,d)\n"
        "-4 1 2 3 4 5 6 7 8 9 10\n-2 2 3 4 5 6 7 8 9 10 11\n"
    )
    path = load_script("FDplot_LDOS.py").main(["--year", "2016", "--intdos", "--nw"])
    assert path == Path("LDOS0_spin.pdf")
    down, down_integral, up, _ = capture_figures[path].axes
    assert down.yaxis_inverted() and down_integral.yaxis_inverted()
    assert not up.yaxis_inverted()
    np.testing.assert_allclose(down.lines[0].get_ydata(), [9, 10])


@pytest.mark.parametrize(
    "sample", ["FDplot_XAS.py", "FDplot_LDOS.py", "FDplot_PDOS.py"]
)
def test_display_policy(sample, tmp_path, monkeypatch):
    """Call show after saving by default, and omit it for --nw."""
    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    plt = pytest.importorskip("matplotlib.pyplot")

    saved_before_show = []

    def show():
        """Record whether the figure is already on disk."""
        saved_before_show.append(Path("display.pdf").is_file())

    monkeypatch.setattr(plt, "show", show)
    main = load_script(sample).main
    main(["--output", "display.pdf"])
    main(["--output", "batch.pdf", "--nw"])
    assert saved_before_show == [True]


def test_named_l23_columns_preserve_the_raw_grid(
    tmp_path, monkeypatch, capture_figures
):
    """Plot both explicitly labeled edge columns from the same raw file."""
    monkeypatch.chdir(tmp_path)
    Path("read_pdb.inp").write_text("Filout Fe\nEnd\n")
    Path("Fe.txt").write_text(
        "7112 26 = E_edge Z\nEnergy <xanes>_L2 <xanes>_L3\n-1 4 8\n0 5 9\n"
    )
    path = load_script("FDplot_XAS.py").main(["--xas", "--l23", "--nw"])
    lines = capture_figures[path].axes[0].lines
    assert [line.get_label() for line in lines[:2]] == ["XAS (L2)", "XAS (L3)"]
    np.testing.assert_allclose(lines[1].get_ydata(), [8, 9])


def test_photon_energy_input_shifts_dos_and_xas_to_fermi(
    tmp_path, monkeypatch, capture_figures
):
    """Correct the SAE photon-to-Fermi offset on each independent grid."""
    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    Path("read_pdb.inp").write_text("Filout Fe\nEnergpho\nEnd\n")
    Path("Fe.txt").write_text(
        "7112 26 -5 = E_edge Z E_Fermi\nEnergy XAS\n7107 1\n7109 2\n"
    )
    Path("Fe_conv.txt").write_text("Energy XAS\n7106 1\n7107 2\n7108 3\n")
    sd = FdmSd2020("Fe_sd0.txt")
    sd.values[:, 0] += 7112
    np.savetxt("Fe_sd0.txt", sd.values, header=" ".join(sd.columns), comments="")
    output = load_script("FDplot_LDOS.py").main(["--broad", "--fermi", "--p", "--nw"])
    xas, orbital = capture_figures[output].axes
    np.testing.assert_allclose(xas.lines[0].get_xdata(), [-1, 0, 1])
    np.testing.assert_allclose(xas.lines[1].get_xdata(), [0, 2])
    np.testing.assert_allclose(orbital.lines[0].get_xdata(), sd.values[:, 0] - 7107)
    np.testing.assert_allclose(orbital.lines[-1].get_xdata(), [0, 0])


def test_l_edge_spin_columns(tmp_path, monkeypatch, capture_figures):
    """Use both spin columns for the selected raw edge without mixing edges."""
    monkeypatch.chdir(tmp_path)
    Path("read_pdb.inp").write_text("Filout Fe\nEnd\n")
    Path("Fe.txt").write_text(
        "7112 26 = E_edge Z\n"
        "Energy <xanes>_L2_up <xanes>_L3_up <xanes>_L2_down <xanes>_L3_down\n"
        "-1 1 10 100 1000\n0 2 20 200 2000\n"
    )
    path = load_script("FDplot_XAS.py").main(["--xas", "--l3", "--spin", "--nw"])
    lines = capture_figures[path].axes[0].lines
    assert [line.get_label() for line in lines[:2]] == ["XAS (L3 up)", "XAS (L3 down)"]
    np.testing.assert_allclose(lines[0].get_ydata(), [10, 20])
    np.testing.assert_allclose(lines[1].get_ydata(), [1000, 2000])


def test_xas_site_grid_mismatch_does_not_write_averages(tmp_path, monkeypatch):
    """Reject incompatible grids within one spectrum family before saving outputs."""
    monkeypatch.chdir(tmp_path)
    Path("read_pdb.inp").write_text("Filout Fe\nEnd\n")
    for site in (1, 2):
        Path(f"Fe_{site}.txt").write_text(
            f"7112 26 = E_edge Z\nEnergy XAS\n{-site} 1\n0 2\n"
        )
        Path(f"Fe_{site}_conv.txt").write_text("Energy XAS\n-1 1\n0 2\n")
    main = load_script("FDplot_XAS.py").main
    with pytest.raises(ValueError, match="Energy grids differ"):
        main(["-a", "1", "2", "--nw"])
    assert not Path("Fe_0.txt").exists()
    assert not Path("XAS.pdf").exists()
