#!/usr/bin/env python3
"""``*_bav.txt`` にある SCF の全エネルギーを描き、既定で ``SCF.pdf`` に保存する。"""
import argparse

from fdmnes_util.fdm_bav import FdmBav


def main(argv=None):
    """BAV の SCF 全エネルギーをサイクル番号に対して描く。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("-o", "--output", default="SCF.pdf")
    parser.add_argument("--nw", action="store_true")
    options = parser.parse_args(argv)
    reader = FdmBav(options.input)
    recorded = [
        (cycle, energy)
        for cycle, energy in reader.get_scf_history()
        if energy is not None
    ]
    if not recorded:
        parser.error("No cycle-resolved SCF total energies found")

    import matplotlib.pyplot as plt

    cycles, energies = zip(*recorded)
    figure, axis = plt.subplots()
    axis.plot(cycles, energies, marker="o")
    axis.set(xlabel="SCF cycle", ylabel="Total energy (eV)")
    try:
        figure.savefig(options.output)
        if not options.nw:
            plt.show()
    finally:
        plt.close(figure)


if __name__ == "__main__":
    main()
