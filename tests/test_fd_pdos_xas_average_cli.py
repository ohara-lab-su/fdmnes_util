#!/usr/bin/env python3
"""編集用の平均 PDOS・XAS サンプルの結合テストを行う。"""

import importlib.util
from pathlib import Path

import numpy as np
import pytest


class FakeSdReader:
    """SD リーダーと同じ I/F で軌道データを提供する。"""

    def get_eng(self):
        """テスト用の SD エネルギー格子を返す。"""
        return np.array([0.0, 1.0, 2.0])

    def get_pdos(self, lm=None, spin=0):
        """テスト用の軌道射影状態密度を返す。"""
        return np.array([1.0, 2.0, 3.0])


class FakeSd:
    """CLI の結合テスト用に SD の形式選択を差し替える。"""

    def __init__(self, filename, format_year):
        """実際の SD 形式選択クラスと同じ引数を受け取る。

        Args:
            filename: 対象ファイルのパス。
            format_year: 対応する形式年。None なら列名で判定する。
        """
        self.filename = filename
        self.format_year = format_year

    def select_reader(self):
        """テスト用の SD リーダーを返す。"""
        return FakeSdReader()


def load_example():
    """リポジトリの scripts フォルダから配布用サンプルを取り込む。"""
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "fdPDOS_XAS_av.py"
    spec = importlib.util.spec_from_file_location("fd_pdos_xas_example", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_conv(path, absorption):
    """リーダーのテスト用に最小限の FDMNES 畳み込みファイルを作る。

    Args:
        path: 対象ファイルのパス。
        absorption: 対応するエネルギー点の吸収強度。
    """
    lines = ["Energy XAS"]
    energies = [0.0, 1.0, 2.0]
    for index in range(len(energies)):
        energy = energies[index]
        value = absorption[index]
        lines.append(f"{energy:.1f} {value:.1f}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_example_generates_average_xas_figure(tmp_path, monkeypatch):
    """CLI、畳み込みの読み取り、平均化、描画をまとめて検証する。"""
    module = load_example()
    monkeypatch.setattr(module, "FdmSd", FakeSd)

    first = tmp_path / "first_conv.txt"
    second = tmp_path / "second_conv.txt"
    write_conv(first, [2.0, 4.0, 6.0])
    write_conv(second, [4.0, 8.0, 12.0])
    output = tmp_path / "average.pdf"

    module.main(
        [
            "--year",
            "2020",
            "--orbitals",
            "s",
            "--xas-files",
            str(first),
            str(second),
            "--output",
            str(output),
            "first_sd.txt",
            "second_sd.txt",
        ]
    )

    assert output.is_file()
    assert output.stat().st_size > 0


def test_example_rejects_unpaired_xas_files(tmp_path, monkeypatch):
    """XAS を読む前に SD と XAS のファイル数の不一致を検出することを検証する。"""
    module = load_example()
    monkeypatch.setattr(module, "FdmSd", FakeSd)
    with pytest.raises(SystemExit) as error:
        module.main(
            [
                "--year",
                "2020",
                "--xas-files",
                "only_one_conv.txt",
                "--output",
                str(tmp_path / "unused.pdf"),
                "first_sd.txt",
                "second_sd.txt",
            ]
        )
    assert error.value.code == 2


@pytest.mark.parametrize("fermi, expected", [(False, 107.0), (True, 2.0)])
def test_example_draws_fermi_marker_on_displayed_axis(
    tmp_path, monkeypatch, fermi, expected,
):
    """選択したエネルギー基準でフェルミ準位を描画に渡すことを検証する。"""
    from matplotlib.figure import Figure

    module = load_example()
    monkeypatch.setattr(module, "FdmSd", FakeSd)
    markers = []

    def record_figure(figure, *args, **kwargs):
        for axis in figure.axes:
            positions = []
            for line in axis.lines:
                x = line.get_xdata()
                if len(x) == 2 and x[0] == x[1]:
                    positions.append(x[0])
            markers.append(positions)

    monkeypatch.setattr(Figure, "savefig", record_figure)
    inp = tmp_path / "read_pdb.inp"
    inp.write_text("Filout Fe\nEnd\n")
    raw = tmp_path / "Fe.txt"
    raw.write_text(
        "100.0 26 5.0 = E_edge Z E_Fermi\n"
        "Energy XAS\n0.0 1.0\n1.0 2.0\n2.0 3.0\n"
    )
    conv = tmp_path / "Fe_conv.txt"
    write_conv(conv, [1.0, 2.0, 3.0])
    args = [
        "Fe_sd0.txt",
        "--orbitals",
        "s",
        "--input",
        str(inp),
        "--energy-offset",
        "2.0",
        "--xas-files",
        str(conv),
        "--raw-xas-files",
        str(raw),
        "--output",
        str(tmp_path / "out.pdf"),
    ]
    if fermi:
        args.append("--fermi")
    module.main(args)
    assert markers == [[expected], [expected]]


def test_example_preserves_sae_orbital_label_rules(monkeypatch, tmp_path):
    """--label がない場合は SAE の原子接頭辞が使われることを検証する。"""
    module = load_example()
    monkeypatch.setattr(module, "FdmSd", FakeSd)
    recorded_labels = []

    class RecordingPlotter:
        """編集用サンプルから渡される曲線を記録する。"""

        def plot(self, orbital_data, output, **kwargs):
            """描画せずにラベルを保持する。

            Args:
                orbital_data: 軌道ラベル、エネルギー、状態密度の組の並び。
                output: 保存先ファイルのパス。拡張子で出力形式を指定する。
                **kwargs: 対象のメソッドに渡す追加のキーワード引数。
            """
            for label, energy, density in orbital_data:
                recorded_labels.append(label)

    monkeypatch.setattr(module, "PlotFdmAverage", RecordingPlotter)

    module.main(["--year", "2020", "--atom", "3", "sample_sd.txt"])
    assert recorded_labels == ["3-s", "3-p_z"]

    recorded_labels.clear()
    module.main(["--year", "2020", "--label", "Pd", "sample_sd.txt"])
    assert recorded_labels == ["Pd-s", "Pd-p_z"]
