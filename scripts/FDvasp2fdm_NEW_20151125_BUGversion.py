#!/usr/bin/env python3
# Copyright Kengo NAKADA; SAE class library.
# SAE historical header (preserved from the original script):
################################################################################
# VASP to FDMNES crystal 情報
#
# using ASE version
#
# (注意)
#  1) ASE のルーチン(cellconst) を使っている
#  2) ASE のmodule を呼び出している
#
################################################################################
#
# 2018.08.17
#  Python2/3 両対応
#
# 2016.01.16
#  自分でASEのルーチンを置き換えた（完全分離させた)バージョンに致命的な
#  バグを発見。旧バージョンを復帰させる
#  --> 現在のバージョンを凍結
#
#   08.18 でバグが混入したと思われる。
#    このバージョンのブランチは 11.25 までつづく
#
# 2015.08.18
#  ASE で読み込む構造を止めて、拙作 SAEnvnv を用いる様にした
#    注意) scale ファクターは 1 を要求
#
# 2015.05.18 startup
#
################################################################################
################################################################################

"""POSCAR から FDMNES の ``*.inp`` への変換を停止した、SAE の旧スクリプトを保存する。

重大な不具合が判明した時点の SAE 原版を保存した例。原版では構造変換と FDMNES 入力の生成を呼び出す行がコメントアウトされている。

POSCAR の変換には、読み取りを vasp_util に委譲する FDvasp2fdm.py を使う。
"""

import argparse
from pathlib import Path


def main() -> int:
    """変換を停止したままの原版の動作を再現する。

    Returns:
        int: 旧版であることを報告して0を返す。
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--ipput", dest="input_file", default="POSCAR")
    parser.add_argument("-o", "--outname", default="read_pdb.inp")
    parser.add_argument("-m", "--mol", action="store_true")
    parser.add_argument("poscar", nargs="?")
    args = parser.parse_args()

    input_path = Path(args.input_file)
    if args.poscar is not None:
        input_path = Path(args.poscar)

    # The SAE original resolves the POSCAR path but never performs conversion.
    # Retain that distinction: do not silently generate an input file.
    if not input_path.exists():
        alternative = Path(str(input_path) + ".vasp")
        if alternative.exists():
            input_path = alternative
        else:
            contcar = Path("CONTCAR")
            if contcar.exists():
                input_path = contcar
            else:
                parser.error(f"POSCAR file not found: {input_path}")

    print("gug version")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
