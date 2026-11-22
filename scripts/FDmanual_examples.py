#!/usr/bin/env python3
"""``cu.inp``・``magnetite.inp``・``feo6.inp`` を作成する。POSCAR から ``poscar.inp`` を作ることもできる。

実行時は入力を指定順で FDMNES に渡し、``fdmnes-*.log`` にログを残す。スペクトルなどの計算出力は FDMNES 本体が書く。
"""
import argparse
from pathlib import Path

from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_run import FdmRun


def copper():
    """基本キーワードの例である面心立方の銅を組み立てる。"""
    document = FdmInp(None, format_year=2026)
    document.set_block("Filout", "Cu")
    document.set_block("Range", (-2, 0.2, 5, 0.5, 10, 1, 40))
    document.set_radius(3.0)
    document.set_block(
        "Crystal",
        (3.610, 3.610, 3.610, 90, 90, 90),
        (29, 0, 0, 0),
        (29, 0.5, 0.5, 0),
        (29, 0.5, 0, 0.5),
        (29, 0, 0.5, 0.5),
    )
    return document.set_block("Convolution")


def magnetite():
    """初回計算の例である磁鉄鉱を空間群指定で組み立てる。"""
    document = FdmInp(None, format_year=2026)
    document.set_block("Filout", "Fe3O4")
    document.set_block("Range", (-5, 0.1, 5, 0.2, 10, 0.5, 20, 1, 30, 2, 60, 4, 100))
    document.set_radius(3.0)
    document.set_block("Green")
    document.set_block("Spgroup", "Fd-3m:1")
    document.set_block(
        "Crystal",
        (8.394, 8.394, 8.394, 90, 90, 90),
        (26, 0.625, 0.625, 0.625),
        (26, 0, 0, 0),
        (8, 0.38, 0.38, 0.38),
    )
    return document.set_block("Convolution")


def iron_octahedron():
    """マニュアルの FeO₆ 八面体構造で短い Fe K 吸収端計算を組み立てる。"""
    document = FdmInp(None, format_year=2026)
    document.set_block("Filout", "FeO6")
    document.set_block("Range", (-3, 1, 10))
    document.set_radius(3.0)
    document.set_block("Edge", "K")
    document.set_block("Green")
    document.set_block(
        "Molecule",
        (1.9, 1.9, 1.9, 90, 90, 90),
        (26, 0, 0, 0),
        (8, 1, 0, 0),
        (8, -1, 0, 0),
        (8, 0, 1, 0),
        (8, 0, -1, 0),
        (8, 0, 0, 1),
        (8, 0, 0, -1),
    )
    return document.set_block("Convolution")


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
        model.set_block("Filout", "POSCAR_xanes")
        model.set_block("Range", (-3, 1, 10))
        model.set_radius(3.0)
        model.set_block("Green")
        model.set_block("Convolution")
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
        log = FdmRun(options.executable).run_inputs(
            inputs,
            directory=options.directory,
            timeout=options.timeout,
        )
        print(log)


if __name__ == "__main__":
    main()
