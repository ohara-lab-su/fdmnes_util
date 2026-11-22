#!/usr/bin/env python3
"""FDMNES の Crystal 節から POSCAR への変換例を検証する。"""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

from fdmnes_util.fdm_inp import FdmInp


def test_crystal_coordinates(tmp_path: Path) -> None:
    """格子と分率座標を順序を変えずに読み取ることを検証する。"""
    pytest.importorskip("ase")
    source = tmp_path / "sample.inp"
    source.write_text(
        "Crystal\n 3 4 5 90 90 90\n 26 0 0 0\n 8 0.5 0.5 0.5\nEnd\n",
        encoding="utf-8",
    )
    atoms = FdmInp(source).get_crystal_atoms()
    assert atoms.get_atomic_numbers().tolist() == [26, 8]
    assert atoms.get_scaled_positions().tolist() == [
        [0.0, 0.0, 0.0],
        [0.5, 0.5, 0.5],
    ]


def test_missing_crystal(tmp_path: Path) -> None:
    """結晶構造がない入力を拒否することを検証する。"""
    pytest.importorskip("ase")
    source = tmp_path / "sample.inp"
    source.write_text("Filout\n Fe\nEnd\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Crystal"):
        FdmInp(source).get_crystal_atoms()


def test_sample_writes_poscar(tmp_path: Path, monkeypatch) -> None:
    """編集用サンプルを実行して VASP の出力を検査する。"""
    ase = pytest.importorskip("ase")
    source = tmp_path / "sample.inp"
    source.write_text("Crystal\n 3 4 5 90 90 90\n 26 0 0 0\nEnd\n")
    output = tmp_path / "POSCAR"
    sample = Path(__file__).resolve().parents[1] / "scripts" / "FDfdm2vasp.py"
    spec = importlib.util.spec_from_file_location("fdm_to_vasp_sample", sample)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr("sys.argv", [str(sample), str(source), "-o", str(output)])
    module.main()
    atoms = ase.io.read(str(output), format="vasp")
    assert atoms.get_atomic_numbers().tolist() == [26]


@pytest.mark.parametrize(
    ("scale", "coordinates", "expected"),
    [
        ("1.9 1.9 1.9 90 90 90", "0 1 0", [0.0, 1.9, 0.0]),
        ("1.9 2.5", "1 90 0.4", [0.0, 1.9, 1.0]),
        ("1.9", "1 90 90", [0.0, 1.9, 0.0]),
    ],
)
def test_molecule_coordinates(tmp_path, scale, coordinates, expected):
    """FDMNES マニュアルにある3通りの Molecule 座標指定を変換する。"""
    pytest.importorskip("ase")
    source = tmp_path / "sample.inp"
    source.write_text(
        f"Molecule\n {scale} = scale\n 26 0 0 0\n 8 {coordinates} = Z, x, y, z\nEnd\n",
        encoding="utf-8",
    )
    atoms = FdmInp(source).get_molecule_atoms()
    assert atoms.numbers.tolist() == [26, 8]
    assert atoms.positions[1] == pytest.approx(expected, abs=1e-12)
    assert not atoms.pbc.any()


def test_sample_writes_molecule_poscar(tmp_path, monkeypatch):
    """SAE の入力オプションで指定し、POSCAR の原子間距離と真空層を検証する。"""
    ase_io = pytest.importorskip("ase.io")
    source = tmp_path / "molecule.inp"
    source.write_text("Molecule\n 1.9\n 26 0 0 0\n 8 1 90 0\nEnd\n")
    sample = Path(__file__).resolve().parents[1] / "scripts" / "FDfdm2vasp.py"
    spec = importlib.util.spec_from_file_location("fdm_to_vasp_molecule", sample)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(
        "sys.argv", [str(sample), "--input", str(source), "--vacuum", "5"]
    )
    module.main()
    atoms = ase_io.read(str(source) + ".vasp", format="vasp")
    assert np.linalg.norm(atoms.positions[0] - atoms.positions[1]) == pytest.approx(1.9)
    assert atoms.cell.lengths() == pytest.approx([11.9, 10.0, 10.0])
