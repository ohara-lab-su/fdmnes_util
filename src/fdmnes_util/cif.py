#!/usr/bin/env python3
# SAE source: sae/commands/FDcif2fdm.py.
# ---- Original SAE header (verbatim, comment text) ----
# VASP to FDMNES crystal 情報
#
# using ASE version
#
# (注意)
#  1) ASE のルーチン(cellconst) を使っている
#  2) ASE のmodule を呼び出している
#
# 2018.08.17
#  Python2/3 両対応
#
# 2015.05.18 startup
# ---- End of original SAE header ----
# Original author: Kengo NAKADA; Copyright 2015, MIT.
"""FDMNES の構造入力に使う ``*.cif`` を ASE で読む。

Cif は元素記号、格子、原子座標を返す。FDMNES の Crystal 節の生成には FdmStructure を使う。

SAE の FDcif2fdm.py は ASE で CIF を読み込んだ後に bug version と表示して終了する。このクラスは ASE が読んだ構造を提供する。
"""

from pathlib import Path


class Cif:
    """構造入力の `*.cif` を読み、FDMNES 用の構造変換に渡す。

    Attributes:
        path: 対象ファイルのパス。
        atoms: ASE が返した原子構造。
    """

    def __init__(self, path: str | Path) -> None:
        """CIF ファイルを読み込む。

        Args:
            path: 対象ファイルのパス。

        Raises:
            FileNotFoundError: 入力ファイルが存在しない場合。
            ImportError: ASE がインストールされていない場合。
        """
        self.path = Path(path)
        if not self.path.is_file():
            raise FileNotFoundError(self.path)

        # CIF interpretation belongs to ASE, not to fdmnes_util.
        from ase.io import read

        self.atoms = read(str(self.path), format="cif")

    def get_symbols(self) -> list[str]:
        """ASE が返した順に元素記号を返す。

        Returns:
            list[str]: 原子の元素記号。
        """
        return list(self.atoms.get_chemical_symbols())

    def get_lattice_vectors(self):
        """3本の格子ベクトルを Å 単位で返す。

        Returns:
            numpy.ndarray: 3×3 の格子ベクトル配列。
        """
        return self.atoms.cell.array

    def get_direct_positions(self):
        """CIF 単位胞内の分率座標を返す。

        Returns:
            numpy.ndarray: 分率座標での原子位置。
        """
        return self.atoms.get_scaled_positions()

    def get_cartesian_positions(self):
        """直交座標を Å 単位で返す。

        Returns:
            numpy.ndarray: 直交座標での原子位置。
        """
        return self.atoms.get_positions()
