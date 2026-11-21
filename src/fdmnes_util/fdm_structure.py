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
"""Write the Crystal or Molecule section of a FDMNES input file."""

from pathlib import Path
from importlib.resources import files
from pathlib import Path
import math

from fdmnes_util.vasp_poscar import VaspPoscarFile


class FdmStructure:
    """Convert structure information into a FDMNES structural section.

    The POSCAR file is interpreted exclusively by the external vasp_util
    package. This class implements only the FDMNES output representation.
    """

    def __init__(self, structure: VaspPoscarFile) -> None:
        """Initialize the FDMNES structure writer.

        Args:
            structure: Structure read using the external VASP module.
        """
        self.structure = structure

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
        """
        # Element numbers are FDMNES output data, not VASP parsing logic.
        atomic_numbers = {}
        symbols_path = files("fdmnes_util").joinpath("atomic_symbols.list")
        for line in symbols_path.read_text(encoding="utf-8").splitlines():
            columns = line.split()
            if len(columns) < 2:
                continue
            atomic_numbers[columns[1]] = int(columns[0])

        parameters = self._cell_parameters()
        lines = []
        if molecule:
            lines.append(" Molecule")
        else:
            lines.append(" Crystal")

        cell_line = "      " + " ".join(f"{value:8.4f}" for value in parameters)
        lines.append(cell_line)

        symbols = self.structure.get_symbols()
        positions = self.structure.get_direct_positions()
        if len(symbols) != len(positions):
            raise ValueError("Atom symbols and positions have different lengths")

        for symbol, position in zip(symbols, positions):
            atomic_number = atomic_numbers[symbol]
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

        atomic_numbers: dict[str, int] = {}
        symbols_path = files("fdmnes_util").joinpath("atomic_symbols.list")
        for line in symbols_path.read_text(encoding="utf-8").splitlines():
            columns = line.split()
            if len(columns) < 2:
                continue
            atomic_numbers[columns[1]] = int(columns[0])

        lines = [" molecule", "      1.0 1.0 1.0 90.0 90.0 90.0"]
        for symbol, position in zip(symbols, positions):
            if symbol not in atomic_numbers:
                raise ValueError(f"Unknown atomic symbol: {symbol}")
            number = atomic_numbers[symbol]
            x, y, z = position
            lines.append(
                f"   {number:2d} {x:12.6f} {y:12.6f} {z:12.6f}    ! {symbol}"
            )
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
