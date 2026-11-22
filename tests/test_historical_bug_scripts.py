#!/usr/bin/env python3
"""変換を停止した SAE の旧スクリプトを回帰検証する。"""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "script_name",
    [
        "FDvasp2fdm_BUG.py",
        "FDvasp2fdm_NEW_20151125_BUGversion.py",
    ],
)
def test_historical_bug_scripts_do_not_convert(tmp_path, script_name):
    """バグのあった旧版が変換ファイルを出さないことを検証する。

    Args:
        tmp_path: pytest が用意する一時ディレクトリ。
        script_name: 変換を停止した SAE 旧版のスクリプト名。
    """
    script = Path(__file__).resolve().parents[1] / "scripts" / script_name
    (tmp_path / "POSCAR").write_text("placeholder\n")
    result = subprocess.run(
        [sys.executable, str(script), "-o", "read_pdb.inp"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "gug version"
    assert not (tmp_path / "read_pdb.inp").exists()
