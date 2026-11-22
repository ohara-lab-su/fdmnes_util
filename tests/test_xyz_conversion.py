#!/usr/bin/env python3
"""編集可能な XYZ 変換サンプルを回帰検証する。"""

from fdmnes_util.fdm_structure import FdmStructure
from fdmnes_util.xyz import Xyz


def test_xyz_to_molecule(tmp_path):
    """直交座標と原子番号を保持することを検証する。"""
    source = tmp_path / "water.xyz"
    source.write_text("3\nwater\nO 0 0 0\nH 0 0 1\nH 0 1 0\n")
    xyz = Xyz(source)
    content = FdmStructure.render_xyz_molecule(xyz.symbols, xyz.positions)
    assert "molecule" in content
    assert "! O" in content
    assert "! H" in content
    assert "1.000000" in content


def test_xyz_rejects_short_file(tmp_path):
    """原子を省略せず、途中で切れた XYZ を拒否することを検証する。"""
    source = tmp_path / "bad.xyz"
    source.write_text("2\ncomment\nH 0 0 0\n")
    try:
        Xyz(source)
    except ValueError:
        return
    raise AssertionError("Truncated XYZ file must raise ValueError")
