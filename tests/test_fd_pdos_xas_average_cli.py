#!/usr/bin/env python3
"""Integration tests for the editable averaged PDOS/XAS example."""

import importlib.util
from pathlib import Path

import numpy as np
import pytest


class FakeSdReader:
    """Provide orbital data with the same interface as an SD reader."""

    def get_eng(self):
        """Return the synthetic SD energy grid."""
        return np.array([0.0, 1.0, 2.0])

    def get_pdos(self, lm=None, spin=0):
        """Return a synthetic orbital-projected density."""
        return np.array([1.0, 2.0, 3.0])


class FakeSd:
    """Replace the SD file dispatcher in an isolated CLI integration test."""

    def __init__(self, filename, format_year):
        """Accept the same arguments as the real SD dispatcher.

        Args:
            filename: Name of a synthetic SD file.
            format_year: Requested FDMNES output format year.
        """
        self.filename = filename
        self.format_year = format_year

    def select_reader(self):
        """Return a synthetic SD reader."""
        return FakeSdReader()


def load_example():
    """Import the distributed script from the repository's scripts folder."""
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "fdPDOS_XAS_av.py"
    spec = importlib.util.spec_from_file_location("fd_pdos_xas_example", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_conv(path, absorption):
    """Create a minimal real FDMNES convolution file for the reader.

    Args:
        path: Output file path.
        absorption: Absorption values at three energy points.
    """
    lines = ["Energy XAS"]
    energies = [0.0, 1.0, 2.0]
    for index in range(len(energies)):
        energy = energies[index]
        value = absorption[index]
        lines.append(f"{energy:.1f} {value:.1f}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_example_generates_average_xas_figure(tmp_path, monkeypatch):
    """Exercise the CLI, real convolution reader, averaging, and plotting."""
    module = load_example()
    monkeypatch.setattr(module, "FdmSd", FakeSd)

    first = tmp_path / "first_conv.txt"
    second = tmp_path / "second_conv.txt"
    write_conv(first, [2.0, 4.0, 6.0])
    write_conv(second, [4.0, 8.0, 12.0])
    output = tmp_path / "average.pdf"

    module.main(
        [
            "--year", "2020",
            "--orbitals", "s",
            "--xas-files", str(first), str(second),
            "--output", str(output),
            "first_sd.txt", "second_sd.txt",
        ]
    )

    assert output.is_file()
    assert output.stat().st_size > 0


def test_example_rejects_unpaired_xas_files(tmp_path, monkeypatch):
    """Reject mismatched SD/XAS file counts before reading XAS files."""
    module = load_example()
    monkeypatch.setattr(module, "FdmSd", FakeSd)
    with pytest.raises(SystemExit) as error:
        module.main(
            [
                "--year", "2020",
                "--xas-files", "only_one_conv.txt",
                "--output", str(tmp_path / "unused.pdf"),
                "first_sd.txt", "second_sd.txt",
            ]
        )
    assert error.value.code == 2
