#!/usr/bin/env python3
#
# SAE原本: sae/fdmnes/structure_writer.py
# 以下はSAE原本の冒頭コメントを原文のまま保存したものです。
# 原本に記された旧仕様・旧クラス名は現在のAPI仕様を意味しません。
# ---- SAE original header (verbatim) ----
# -*- coding: utf-8 -*-
################################################################################
# VASP to FDMNES crystal 情報のルーチン
# FDMNES の構造書き出しルーチン
#
# using ASE version
#
# (注意)
#  1) ASE のmodule を呼び出している
#
################################################################################
#
# 2018.08.21
#  Python2/3 両対応
#
# 2015.05.18 startup
#
################################################################################
################################################################################
#
# from ase.io.xyz import *
# using cellconst
# import os
# import optparse
# import numpy as np
################################################################################
## 独自実装版
##
################################################################################
## ASE 依存版 & atoms は ASEの構造
##
################################################################################
## ASE 依存版 & atoms(cell) は SAE の構造
##  ただし、conv_cellparam 内でまだASEを用いているので一部ASE依存
##
##  self.atoms_number_j
##  self.atoms_index_j
##  self.position
##
##  セルパラメータゲット: conv_cellparam*(cell)
##
#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
# VASP to FDMNES crystal 情報 関係の出力ルーチン
#
# using ASE version
#
# (注意)
#  1) ASE のmodule を呼び出している
#
################################################################################
#
# 2018.08.21
#  Python2/3 両対応
#
# 2015.05.18 startup
#
################################################################################
################################################################################
#
# from ase.io.xyz import *
# from ase.io.wien2k import *  ## using cellconst
# from ase import Atoms
# import os
# import optparse
################################################################################
## 独自実装版
##
################################################################################
## ASE 依存版 & atoms が ASE の構造を持つ
##
################################################################################
## ASE 依存版 & atoms が SAE の構造を持つ
##  ただし、conv_cellparam  内でまだASEを用いているので一部ASE依存版
##
##  self.atoms_number_j
##  self.atoms_index_j
##  self.position
##
##  セルパラメータゲット: conv_cellparam*(cell)
##
# Copyright Kengo NAKADA; SAE class library.
# ---- End of SAE original header ----
"""FDMNES の構造表現と元素表。"""

import math
from functools import cache
from importlib.resources import files
from pathlib import Path


class ElementTable:
    """SAE の sae/structure/elements.py に対応する元素番号と記号の対応表。"""

    @staticmethod
    @cache
    def _read():
        rows = files("fdmnes_util").joinpath("atomic_symbols.list")
        symbols = {}
        for row in rows.read_text(encoding="utf-8").splitlines():
            number, symbol = row.split()[:2]
            symbols[int(number)] = symbol
        numbers = {symbol: number for number, symbol in symbols.items()}
        return symbols, numbers

    @classmethod
    def get_atomic_symbol0(cls, num):
        """原子番号から元素記号を返す。"""
        symbols, _ = cls._read()
        return symbols[num]

    @classmethod
    def get_atomic_number1(cls, atom):
        """元素記号から原子番号を返す。"""
        _, numbers = cls._read()
        return numbers[atom]


class FdmStructure:
    """FDMNES の Crystal・Molecule と原子構造を相互に変換する。"""

    def __init__(self, structure) -> None:
        """構造リーダーを受け取る。

        Args:
            structure: vasp_util の VaspPoscar、または格子・元素記号・
                分率座標を取得できる CIF・PDB などのリーダー。
        """
        self.structure = structure

    @staticmethod
    def fdm_to_atoms(filename, *, vacuum=10.0):
        """FDMNES の結晶または分子を POSCAR 用の構造に変換する。

        Args:
            filename: FDMNES 入力ファイル。
            vacuum: 分子を囲む各側の真空層の厚さ（Å）。

        Returns:
            ase.Atoms: 元の結晶格子、または真空層を付けた分子構造。

        Raises:
            ValueError: 構造データまたは分子の真空層の厚さが不正な場合。
        """
        from .fdm_inp import FdmInp

        input_file = FdmInp(filename)
        if "molecule" not in input_file.tags:
            return input_file.get_crystal_atoms()

        if not math.isfinite(vacuum) or vacuum <= 0:
            raise ValueError("--vacuum must be a positive finite distance")
        atoms = input_file.get_molecule_atoms()
        # POSCAR needs a periodic cell even though Molecule has no translation.
        atoms.center(vacuum=vacuum)
        return atoms

    @staticmethod
    def poscar_to_atoms(filename):
        """vasp_util で POSCAR を読み、ASE の周期構造を組み立てる。

        Args:
            filename: POSCAR のパス。

        Returns:
            ase.Atoms: POSCAR と同じ格子と原子順を持つ周期構造。
        """
        from ase import Atoms
        from vasp_util.vasp_poscar import VaspPoscar

        poscar = VaspPoscar(str(filename))
        return Atoms(
            symbols=poscar.get_atom_indices(),
            scaled_positions=poscar.get_coords_direct(),
            cell=poscar.get_lattice_vectors(),
            pbc=True,
        )

    @staticmethod
    def crystal_atoms(cell_values, atom_lines):
        """結晶の格子定数と分率座標の各行から ASE 構造を組み立てる。

        Args:
            cell_values: 格子の長さと角度を並べた6要素。
            atom_lines: 原子番号と分率座標を記した行。

        Returns:
            ase.Atoms: 周期境界を持つ結晶構造。
        """
        from ase import Atoms
        from ase.cell import Cell

        atomic_numbers = []
        scaled_positions = []
        for line in atom_lines:
            fields = line.split()
            if len(fields) < 4:
                continue

            try:
                atomic_number = int(fields[0])
                coordinates = [float(value) for value in fields[1:4]]
            except ValueError:
                continue

            if atomic_number < 1 or atomic_number > 118:
                raise ValueError("Invalid atomic number in Crystal section")

            atomic_numbers.append(atomic_number)
            scaled_positions.append(coordinates)

        if not atomic_numbers:
            raise ValueError("No atoms were found in the Crystal section")

        cell = Cell.fromcellpar(cell_values)
        return Atoms(
            numbers=atomic_numbers,
            scaled_positions=scaled_positions,
            cell=cell,
            pbc=True,
        )

    @staticmethod
    def molecule_atoms(lines):
        """分子のスケールと原子座標の各行から ASE 構造を組み立てる。

        Args:
            lines: スケール行に続く原子番号と座標の行。

        Returns:
            ase.Atoms: Å 単位の直交座標を持つ孤立分子。
        """
        from ase import Atoms
        from ase.cell import Cell

        if len(lines) < 2:
            raise ValueError("Molecule requires scale parameters and atom rows")
        scale = [float(value.replace("D", "E")) for value in lines[0].split()]
        if len(scale) not in (1, 2, 6) or any(
            not math.isfinite(value) or value <= 0 for value in scale
        ):
            raise ValueError("Molecule requires one, two, or six positive parameters")

        numbers = []
        positions = []
        for line in lines[1:]:
            fields = line.split()
            if len(fields) < 4:
                raise ValueError(
                    "Molecule atom rows require a number and three coordinates"
                )
            number = int(fields[0])
            if not 1 <= number <= 118:
                raise ValueError("Invalid atomic number in Molecule section")
            numbers.append(number)
            coordinates = [float(value.replace("D", "E")) for value in fields[1:4]]
            if not all(math.isfinite(value) for value in coordinates):
                raise ValueError("Molecule coordinates must be finite")
            positions.append(coordinates)

        if len(scale) == 6:
            # The three angles define the basis for the fractional positions.
            cell = Cell.fromcellpar(scale)
            positions = cell.cartesian_positions(positions)
        else:
            for index, (radius, second, third) in enumerate(positions):
                radius *= scale[0]
                angle = math.radians(second)
                if len(scale) == 2:
                    positions[index] = [
                        radius * math.cos(angle),
                        radius * math.sin(angle),
                        third * scale[1],
                    ]
                else:
                    azimuth = math.radians(third)
                    planar_radius = radius * math.sin(angle)
                    positions[index] = [
                        planar_radius * math.cos(azimuth),
                        planar_radius * math.sin(azimuth),
                        radius * math.cos(angle),
                    ]
        return Atoms(numbers=numbers, positions=positions)

    def _cell_parameters(self) -> list[float]:
        """Calculate cell lengths and angles from the lattice matrix.

        Returns:
            list[float]: a, b, c, alpha, beta and gamma in degrees.

        Raises:
            ValueError: If a lattice vector has zero length.
        """
        import numpy as np

        lattice = self.structure.get_lattice_vectors()
        lengths = []
        for vector in lattice:
            length = float(np.linalg.norm(vector))
            if length == 0.0:
                raise ValueError("Lattice vectors must have nonzero length")
            lengths.append(length)

        angles = []
        pairs = [(1, 2), (0, 2), (0, 1)]
        for first, second in pairs:
            numerator = float(np.dot(lattice[first], lattice[second]))
            denominator = lengths[first] * lengths[second]
            cosine = numerator / denominator
            cosine = max(-1.0, min(1.0, cosine))
            angle = math.degrees(math.acos(cosine))
            angles.append(angle)

        return lengths + angles

    def render(self, molecule: bool = False) -> str:
        """Create a FDMNES structure section.

        Args:
            molecule: Write the ``Molecule`` keyword instead of ``Crystal``.

        Returns:
            str: Formatted FDMNES structure section.

        Raises:
            ValueError: If the structure has inconsistent symbol and position counts.
            KeyError: If an element symbol cannot be converted to an atomic number.
        """
        parameters = self._cell_parameters()
        lines = []
        if molecule:
            lines.append(" Molecule")
        else:
            lines.append(" Crystal")

        cell_line = "      " + " ".join(f"{value:8.4f}" for value in parameters)
        lines.append(cell_line)

        if hasattr(self.structure, "get_coords_direct"):
            symbols = self.structure.get_atom_indices()
            positions = self.structure.get_coords_direct()
        else:
            symbols = self.structure.get_symbols()
            positions = self.structure.get_direct_positions()
        if len(symbols) != len(positions):
            raise ValueError("Atom symbols and positions have different lengths")

        for symbol, position in zip(symbols, positions):
            atomic_number = ElementTable.get_atomic_number1(symbol)
            atom_line = (
                f"   {atomic_number:2d} "
                f"{position[0]:8.4f} {position[1]:8.4f} {position[2]:8.4f}"
                f"    ! {symbol}"
            )
            lines.append(atom_line)

        return "\n".join(lines) + "\n"

    @staticmethod
    def render_xyz_molecule(
        symbols: list[str],
        positions: list[tuple[float, float, float]],
    ) -> str:
        """Render SAE-compatible molecular coordinates from an XYZ file.

        The SAE ``FDxyz2fdm.py`` script used a unit cubic cell and Cartesian
        coordinates in a ``molecule`` section, rather than fractional crystal
        coordinates.

        Args:
            symbols: Chemical symbols in atom order.
            positions: Cartesian positions in angstroms.

        Returns:
            FDMNES molecule section with the original SAE coordinate format.

        Raises:
            ValueError: If atom counts differ or a symbol is unknown.
        """
        if len(symbols) != len(positions):
            raise ValueError("Atom/coordinate count mismatch")

        lines = [" molecule", "      1.0 1.0 1.0 90.0 90.0 90.0"]
        for symbol, position in zip(symbols, positions):
            try:
                number = ElementTable.get_atomic_number1(symbol)
            except KeyError as error:
                raise ValueError(f"Unknown atomic symbol: {symbol}") from error
            x, y, z = position
            lines.append(f"   {number:2d} {x:12.6f} {y:12.6f} {z:12.6f}    ! {symbol}")
        return "\n".join(lines) + "\n"

    def write(self, filename: str | Path, molecule: bool = False) -> Path:
        """Write the FDMNES structural section to a file.

        Args:
            filename: Destination filename.
            molecule: Whether to use the Molecule keyword.

        Returns:
            Path: Written file path.
        """
        destination = Path(filename)
        content = self.render(molecule=molecule)
        destination.write_text(content, encoding="utf-8")
        return destination
