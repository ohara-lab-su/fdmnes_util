#!/usr/bin/env python3
"""``cu.inp``・``magnetite.inp``・``feo6.inp`` を作成する。POSCAR から ``poscar.inp`` を作ることもできる。

実行時は入力を指定順で FDMNES に渡し、``fdmnes-*.log`` にログを残す。スペクトルなどの計算出力は FDMNES 本体が書く。
"""

# 実行例（このスクリプトがあるディレクトリで実行）
# --executable を省略する場合は PATH に fdmnes が必要。
#
# FCC 銅の入力を作って実行する。作業先は既定の manual_calculations。
# python FDmanual_examples.py cu
#
# FCC 銅の入力を cu_run/cu.inp に保存する。ここでは FDMNES を起動しない。
# python FDmanual_examples.py cu --directory cu_run --write-only
# 保存内容を確認してから、スクリプトのあるディレクトリで次を実行する。
# python FDrun.py cu.inp --directory cu_run
#
# FCC 銅・磁鉄鉱・FeO₆ を1件ずつ順に実行する。900秒は3件全体の制限時間。
# python FDmanual_examples.py all --directory manual_run --timeout 900
#
# 手元の POSCAR から poscar_run/poscar.inp を作り、半径を4 Åにして実行する。
# POSCAR の読み込みには vasp_util が必要。/path/to/fdmnes は実際のパスに置き換える。
# python FDmanual_examples.py poscar --poscar POSCAR --directory poscar_run --radius 4 --executable /path/to/fdmnes

import argparse
from pathlib import Path

from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_run import FdmRun


def copper():
    """基本キーワードの例である面心立方の銅を組み立てる。"""
    document = FdmInp(None, format_year=2026)
    document.set_keyword("Filout", "Cu")
    document.set_keyword("Range", (-2, 0.2, 5, 0.5, 10, 1, 40))
    document.set_radius(3.0)
    document.set_structure(
        (3.610, 3.610, 3.610, 90, 90, 90),
        (29, 0, 0, 0),
        (29, 0.5, 0.5, 0),
        (29, 0.5, 0, 0.5),
        (29, 0, 0.5, 0.5),
    )
    return document.set_keyword("Convolution")


def magnetite():
    """初回計算の例である磁鉄鉱を空間群指定で組み立てる。"""
    document = FdmInp(None, format_year=2026)
    document.set_keyword("Filout", "Fe3O4")
    document.set_keyword("Range", (-5, 0.1, 5, 0.2, 10, 0.5, 20, 1, 30, 2, 60, 4, 100))
    document.set_radius(3.0)
    document.set_keyword("Green")
    document.set_keyword("Spgroup", "Fd-3m:1")
    document.set_structure(
        (8.394, 8.394, 8.394, 90, 90, 90),
        (26, 0.625, 0.625, 0.625),
        (26, 0, 0, 0),
        (8, 0.38, 0.38, 0.38),
    )
    return document.set_keyword("Convolution")


def iron_octahedron():
    """マニュアルの FeO₆ 八面体構造で短い Fe K 吸収端計算を組み立てる。"""
    document = FdmInp(None, format_year=2026)
    document.set_keyword("Filout", "FeO6")
    document.set_keyword("Range", (-3, 1, 10))
    document.set_radius(3.0)
    document.set_keyword("Edge", "K")
    document.set_keyword("Green")
    document.set_structure(
        (1.9, 1.9, 1.9, 90, 90, 90),
        (26, 0, 0, 0),
        (8, 1, 0, 0),
        (8, -1, 0, 0),
        (8, 0, 1, 0),
        (8, 0, -1, 0),
        (8, 0, 0, 1),
        (8, 0, 0, -1),
        molecule=True,
    )
    return document.set_keyword("Convolution")


def main(argv=None):
    """選んだ入力を保存し、指定順に実行する。"""
    examples = {"cu": copper, "magnetite": magnetite, "feo6": iron_octahedron}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("example", choices=(*examples, "all", "poscar"))
    parser.add_argument("--poscar", type=Path)
    parser.add_argument("--executable", default="fdmnes")
    parser.add_argument("--directory", type=Path, default=Path("manual_calculations"))
    parser.add_argument("--radius", type=float, help="Override the cluster radius in Å")
    parser.add_argument("--timeout", type=float, help="Timeout for the entire batch")
    parser.add_argument("--write-only", action="store_true")
    options = parser.parse_args(argv)

    if options.example == "poscar":
        if options.poscar is None:
            parser.error("The poscar example requires --poscar FILE")
        model = FdmInp.from_poscar(options.poscar)
        model.set_keyword("Filout", "POSCAR_xanes")
        model.set_keyword("Range", (-3, 1, 10))
        model.set_radius(3.0)
        model.set_keyword("Green")
        model.set_keyword("Convolution")
        models = [("poscar", model)]
    elif options.example == "all":
        models = [(name, build()) for name, build in examples.items()]
    else:
        models = [(options.example, examples[options.example]())]

    options.directory.mkdir(parents=True, exist_ok=True)
    inputs = []
    for name, model in models:
        if options.radius is not None:
            model.set_radius(options.radius)
        inputs.append(model.save(options.directory / f"{name}.inp").resolve())
        print(inputs[-1])
    if not options.write_only:
        logs = FdmRun(options.executable).run_inputs(
            inputs,
            directory=options.directory,
            timeout=options.timeout,
        )
        for log in logs:
            print(log)


if __name__ == "__main__":
    main()
