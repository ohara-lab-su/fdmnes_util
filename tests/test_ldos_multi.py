#!/usr/bin/env python3
"""Test the three-site LDOS plotting example."""

from pathlib import Path

import numpy as np
import pytest

from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos


class ExampleSd:
    """Supply a minimal SD reader for the plotting contract."""

    def get_eng(self):
        """Return a short energy axis."""
        return np.array([-1.0, 0.0, 1.0])

    def get_ldos(self, orbital):
        """Return an orbital-resolved density array."""
        if orbital != "p":
            raise ValueError("This fixture only supplies p orbitals")
        return np.array([0.1, 0.5, 0.2])


def test_plot_three_sites(tmp_path):
    """Save a three-panel PDF with a shared photon-energy axis."""
    pytest.importorskip("matplotlib")
    readers = [ExampleSd(), ExampleSd(), ExampleSd()]
    labels = ["sd0", "sd1", "sd2"]
    destination = tmp_path / "LDOSmulti.pdf"

    result = PlotFdmDos().plot_multiple_sites(
        readers,
        labels,
        destination,
        edge_energy=7100.0,
        fermi_energy=2.0,
        emin=7098.0,
        emax=7102.0,
    )

    assert result == destination
    assert destination.stat().st_size > 100


def test_plot_requires_three_sites(tmp_path):
    """Reject missing SD sites rather than silently plotting fewer panels."""
    with pytest.raises(ValueError):
        PlotFdmDos().plot_multiple_sites(
            [ExampleSd()],
            ["sd0"],
            tmp_path / "bad.pdf",
            edge_energy=7100.0,
            fermi_energy=2.0,
        )


def test_plot_three_sites_all_formats(tmp_path):
    """Write all three image types used by the SAE plotting script."""
    pytest.importorskip("matplotlib")
    readers = [ExampleSd(), ExampleSd(), ExampleSd()]
    labels = ["sd0", "sd1", "sd2"]
    prefix = tmp_path / "LDOSmulti"

    paths = PlotFdmDos().save_multiple_formats(
        readers,
        labels,
        prefix,
        edge_energy=7100.0,
        fermi_energy=2.0,
    )

    assert [path.suffix for path in paths] == [".eps", ".pdf", ".png"]
    for path in paths:
        assert path.is_file()
        assert path.stat().st_size > 100


def test_plot_rejects_unsupported_format(tmp_path):
    """Reject invalid formats before generating any files."""
    with pytest.raises(ValueError, match="Unsupported format"):
        PlotFdmDos().save_multiple_formats(
            [ExampleSd(), ExampleSd(), ExampleSd()],
            ["sd0", "sd1", "sd2"],
            tmp_path / "LDOSmulti",
            formats=("svg",),
            edge_energy=7100.0,
            fermi_energy=2.0,
        )
