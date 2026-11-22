#!/usr/bin/env python3
# SAE source: sae/commands/FDpbd2fdm.py.
# ---- Original SAE header (verbatim) ----
# PDB to FDMNES crystal 情報
#
#  using ASE version
#
# 2015.08.20
#  関数分離(ごく一部だけASE分離)
#
# 2015.05.18 startup
# ---- End of original SAE header ----
# Original author: Kengo NAKADA; Copyright 2015, MIT.
"""FDMNES の構造入力に使う ``*.pdb`` を ASE で読む。

Pdb は CRYST1 の有無から結晶と分子を区別し、FdmStructure に渡せる原子座標と格子を返す。
"""
from pathlib import Path


class Pdb:
    """構造入力の `*.pdb` から原子座標と単位胞情報を読む。

    SAE と同じく CRYST1 の有無で結晶と分子を判定し、ASE で原子座標を読む。

    Attributes:
        path: 対象ファイルのパス。
        molecule: PDB に CRYST1 がなく分子として扱うか。
    """

    def __init__(self, path: str | Path) -> None:
        """PDB を読み込み、結晶か分子かを判定する。

        Args:
            path: 対象ファイルのパス。

        Raises:
            FileNotFoundError: 入力ファイルが存在しない場合。
            ImportError: 任意依存の ASE がインストールされていない場合。
        """
        self.path = Path(path)
        if not self.path.is_file():
            raise FileNotFoundError(self.path)

        self.molecule = True
        with self.path.open(encoding="utf-8") as source:
            for line in source:
                if line.startswith("CRYST1"):
                    self.molecule = False
                    break

        # Import ASE only when a PDB file is actually opened.
        from ase.io import read

        self.atoms = read(str(self.path), format="proteindatabank")

    def get_symbols(self) -> list[str]:
        """入力の原子順で元素記号を返す。

        Returns:
            list[str]: 元素記号の並び。
        """
        return list(self.atoms.get_chemical_symbols())

    def get_cartesian_positions(self) -> list[tuple[float, float, float]]:
        """原子位置を Å 単位で返す。

        Returns:
            list[tuple[float, float, float]]: 直交座標。
        """
        positions = []
        for row in self.atoms.get_positions():
            positions.append((float(row[0]), float(row[1]), float(row[2])))
        return positions

    def get_lattice_vectors(self):
        """結晶構造に使う格子ベクトルを返す。

        Returns:
            numpy.ndarray: Å 単位の3本の格子ベクトル。
        """
        return self.atoms.cell.array

    def get_direct_positions(self):
        """結晶の原子位置を分率座標で返す。

        Returns:
            numpy.ndarray: 原子の分率座標。
        """
        return self.atoms.get_scaled_positions()
