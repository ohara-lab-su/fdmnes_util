#!/usr/bin/env python3
"""VASP の読み取りをインストール済みの vasp_util に委譲することを検証する。"""

import sys
import types

import numpy as np
import pytest

from fdmnes_util.fdm_structure import FdmStructure
from test_commands import load_script


@pytest.mark.parametrize("option", ["-i", "--ipput", None])
def test_vasp_sample_calls_external_reader_directly(monkeypatch, tmp_path, option):
    """POSCAR 変換コマンドが vasp_util の公開 API を直接使う。"""
    filenames = []

    class FakeVaspPoscar:
        """テストに必要な vasp_util の公開 I/F を模擬する。"""

        def __init__(self, filename):
            filenames.append(filename)

        def get_lattice_vectors(self):
            """テスト用の直方格子を返す。"""
            return np.diag([3.0, 4.0, 5.0])

        def get_coords_direct(self):
            """分率座標を返す。"""
            return np.array([[0.0, 0.0, 0.0]])

        def get_atom_indices(self):
            """元素記号を返す。"""
            return ["Fe"]

    package = types.ModuleType("vasp_util")
    module = types.ModuleType("vasp_util.vasp_poscar")
    module.VaspPoscar = FakeVaspPoscar
    monkeypatch.setitem(sys.modules, "vasp_util", package)
    monkeypatch.setitem(sys.modules, "vasp_util.vasp_poscar", module)

    monkeypatch.chdir(tmp_path)
    poscar = tmp_path / "POSCAR"
    poscar.touch()
    argv = ["FDvasp2fdm.py"]
    if option is not None:
        argv.append(option)
    argv.append(str(poscar))
    monkeypatch.setattr(sys, "argv", argv)
    assert load_script("FDvasp2fdm.py").main() == 0
    assert filenames == [str(poscar)]
    assert "   26" in (tmp_path / "POSCAR.fdmnes").read_text()
    assert "Crystal" in (tmp_path / "read_pdb.inp").read_text()


def test_fdmnes_writer_accepts_vasp_util_poscar(tmp_path):
    """vasp_util が変換した Cartesian 座標をそのまま構造出力へ渡す。"""
    vasp_poscar = pytest.importorskip("vasp_util.vasp_poscar")
    pytest.importorskip("ase")
    poscar = tmp_path / "POSCAR"
    poscar.write_text(
        "FeO\n2.0\n3 0 0\n0 4 0\n0 0 5\nFe O\n1 1\n"
        "Cartesian\n0 0 0\n0.75 2.0 3.75\n",
        encoding="utf-8",
    )

    writer = FdmStructure(vasp_poscar.VaspPoscar(str(poscar)))
    output = writer.write(tmp_path / "POSCAR.fdmnes")
    content = output.read_text(encoding="utf-8")
    assert "Crystal" in content
    assert "6.0000   8.0000  10.0000" in content
    assert "    8   0.2500   0.5000   0.7500" in content
    atoms = FdmStructure.poscar_to_atoms(poscar)
    assert atoms.get_chemical_symbols() == ["Fe", "O"]
    np.testing.assert_allclose(atoms.cell.lengths(), [6, 8, 10])
    np.testing.assert_allclose(atoms.get_scaled_positions()[1], [0.25, 0.5, 0.75])
