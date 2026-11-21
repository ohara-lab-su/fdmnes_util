#!/usr/bin/env python3
#
# SAE原本: sae/fdmnes/inp.py
# 以下はSAE原本の冒頭コメントを原文のまま保存したものです。
# 原本に記された旧仕様・旧クラス名は現在のAPI仕様を意味しません。
# ---- SAE original header (verbatim) ----
# -*- coding: utf-8 -*-
###############################################################################
# K.NAKADA, kengo.nakada@gmail.com
#
#  Method --- ReadVaspPoscar
#  Method --- ReadFdmInp
#  Method --- ReaMxDatMethod -- ReadMxDat
#                            -- ReadMxDftscf
#                            -- ReadMxOut
#                            -- ReadMxPdos
#                            -- ReadMxTdos
#  Method --- ReadRmcpotCfg
#  Method --- ReadPwIn
#
###############################################################################
#
# FDMNES
# *.in ファイル
#
# 主に Crystal の部分の解析と読み込み
#
###############################################################################
#
# 2018.08.15
#  Python2/3 両対応
#
# 2015.11.20
#  convolution 用の結晶構造情報が無いファイルに対する対応
#
# 2015.08.25
#  統合化&Method でいろいろと分離
#
# 2015.08.20
#  Read.py との統合化のためのすりあわせ
#  position のソートルーチンの追加＆分離
#
# 2015.08.19
#  cellparam の基本並進ベクトル変換を ASE の coorsys を採用
#
# 2015.06.24
#  allsite 計算をしているか否かの判断を*.inp かおこなう
#
# 2015.06.19
#   読み込むタグをいくつか追加
#   コメントアウトの処理
#   タグ名とタグの内容が同一行でも対応可能に
#
# 2015.05.19 startup
#   cellpar(a,b,c,alpha,beta,gamma) --> cell(基本並進) への変換が意外に鬼門
#   ---> とりあえずこのルーチンの開発は一旦サスペンド
#
###############################################################################
# トップディレクトリ関係のエラーは ImportError ではキャッチ出来ない
###############################################################################
# import gzip
# import os
# import copy
# import SpaceGroupEnvironment as SGE
# for coorsys
# suing coorsys
###############################################################################
##########################################################################
#   name = 'POSCAR.inp'
##########################################################################
#   out = ReadFdmInp(name,sort=True)
#   cal = np.cos(alpha * np.pi / 180.0)
#   cbe = np.cos(beta * np.pi / 180.0)
#   cga = np.cos(gamma * np.pi /180.0)
#   sga = np.sin(gamma * np.pi /180.0)
#   t = np.array([
#                 [a, b * cga, c * cbe],\
#                 [0, b * sga, c * (cal - cbe * cga) / sga],\
#                 [0, 0, c * np.sqrt(1 - cal**2 -cbe**2 - cga**2 +\
#                                    2 * cal * cbe * cga) / sga],\
#                ]).transpose()
#   out.sort_atoms_index_j()
#   out.sort_atoms_number_j()
#   out.sort_fix()
#       print "NAME",name
# Copyright Kengo NAKADA; SAE class library.
# ---- End of SAE original header ----
# SAE source: sae/fdmnes/inp_writer.py
# ---- SAE original header ----
# -*- coding: utf-8 -*-
################################################################################
# VASP to FDMNES crystal 情報
#
# 構造ファイル & INPUT file
#
# (注意)
#  1) ASE のルーチン(cellconst) を使っている
#  2) ASE のmodule を呼び出している
#  3) atoms は ASE オブジェクトが前提
#
# FDvasp2fdm.py がベース --> class 化
#
################################################################################
################################################################################
#
################################################################################
## using cellconst
# from ase.io.xyz import *
################################################################################
# atoms.write('POSCAR.pdb',format='pdb')
# print atoms.positions
# print ""
# print atoms.cell
# print ""
# print atoms.get_scaled_positions()
# fdm.write_fdmnes(atoms=atoms, MOL=MOL)
# Copyright Kengo NAKADA; SAE class library.
# ---- End of SAE original header ----
"""Read and generate FDMNES calculation input files."""

from math import cos, isfinite, radians, sin
from pathlib import Path


class FdmInp:
    """Read, inspect, and generate FDMNES calculation inputs.

    An input file without a ``Crystal`` section is valid. The reader retains
    the original text as well as the values associated with each keyword.

    Attributes:
        path: Path to the input file.
        lines: Original input lines without trailing newline characters.
        tags: Mapping of recognized keywords to their associated values.
    """

    KEYWORDS = {
        "filout",
        "spin",
        "magnetism",
        "allsite",
        "energpho",
        "energygpho",
        "convolution",
        "conv_out",
        "calculation",
        "nonexc",
        "crystal",
        "molecule",
        "absorber",
    }

    def __init__(self, filename="read_pdb.inp"):
        """Read an input file and extract the supported keywords.

        Args:
            filename: Path to the FDMNES input file.
        """
        self.path = Path(filename)
        self.lines = self.path.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines()

        self.tags = {}
        current_keyword = None

        for line in self.lines:
            # FDMNES input files may contain inline explanations.
            content = line.split("!", 1)[0]
            content = content.split("#", 1)[0]
            content = content.strip()

            if not content:
                continue

            words = content.split()
            keyword = words[0].lower()

            if keyword == "end":
                break

            if keyword in self.KEYWORDS:
                current_keyword = keyword
                if keyword not in self.tags:
                    self.tags[keyword] = []

                if len(words) > 1:
                    value = " ".join(words[1:])
                    self.tags[keyword].append(value)
                continue

            # Values on subsequent lines belong to the preceding keyword.
            if current_keyword is not None:
                self.tags[current_keyword].append(content)

    def get_filout(self):
        """Return the output-file prefix specified by ``Filout``.

        Returns:
            str: Output prefix, or an empty string when absent.
        """
        values = self.tags.get("filout", [])
        if values:
            return values[0]
        return ""

    def get_absorber(self) -> int:
        """Return the one-based absorber index, defaulting to the first atom.

        Returns:
            The atom index specified by the Absorber keyword, or one.

        Raises:
            ValueError: If the Absorber record is missing a positive integer.
        """
        if "absorber" not in self.tags:
            return 1
        values = self.tags["absorber"]
        if not values:
            raise ValueError("Absorber requires a positive atom index")
        try:
            index = int(values[0])
        except ValueError as error:
            raise ValueError("Absorber requires a positive atom index") from error
        if index < 1:
            raise ValueError("Absorber requires a positive atom index")
        return index

    def get_ispin(self):
        """Return the number of spin channels indicated by the input.

        Returns:
            int: Two when ``Spin`` or ``Magnetism`` is specified, otherwise one.
        """
        if "spin" in self.tags or "magnetism" in self.tags:
            return 2
        return 1

    def get_allsite(self):
        """Determine whether all-site calculations were requested.

        Returns:
            bool: True when ``Allsite`` is present.
        """
        return "allsite" in self.tags

    def get_energygpho(self):
        """Determine whether photon-energy input was requested.

        Returns:
            bool: True when ``Energpho`` or ``Energygpho`` is present.
        """
        return "energpho" in self.tags or "energygpho" in self.tags

    def get_nonexc(self):
        """Determine whether ``Nonexc`` is specified.

        Returns:
            bool: True when the keyword is present.
        """
        return "nonexc" in self.tags

    def get_convolution(self):
        """Determine whether convolution was requested.

        Returns:
            bool: True when ``Convolution`` is present.
        """
        return "convolution" in self.tags

    def get_conv_out(self):
        """Return the value associated with ``Conv_out``.

        Returns:
            str: Convolution-output value, or an empty string.
        """
        values = self.tags.get("conv_out", [])
        if values:
            return values[0]
        return ""

    def get_calculation(self):
        """Return the value associated with ``Calculation``.

        Returns:
            str: Calculation value, or an empty string.
        """
        values = self.tags.get("calculation", [])
        if values:
            return values[0]
        return ""

    def get_cellparam(self):
        """Return the first six numeric crystal-cell parameters, if present.

        Returns:
            list[float] | None: The six cell parameters, or None when absent.
        """
        entries = self.tags.get("crystal", [])
        for row in entries:
            tokens = row.split()[:6]
            try:
                numbers = []
                for token in tokens:
                    numbers.append(float(token))
            except ValueError:
                continue

            if len(numbers) == 6:
                return numbers

        return None

    def get_crystal_atoms(self):
        """Build an ASE atomic structure from a FDMNES Crystal section.

        The first six values after ``Crystal`` define the cell lengths and
        angles. Subsequent rows contain an atomic number and three fractional
        coordinates. A new FDMNES keyword ends the structure section.

        Returns:
            ase.Atoms: Periodic atomic structure with fractional positions.

        Raises:
            ValueError: If the Crystal section is absent or malformed.
            ImportError: If ASE is not installed.
        """
        from ase import Atoms
        from ase.cell import Cell

        crystal_lines = self._get_structure_lines("crystal")
        if not crystal_lines:
            raise ValueError("No Crystal section was found")

        cell_values = self.get_cellparam()
        if cell_values is None:
            raise ValueError("Crystal cell parameters are missing")

        atomic_numbers = []
        scaled_positions = []
        for line in crystal_lines[1:]:
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

    def get_molecule_atoms(self):
        """Build an isolated ASE structure from an FDMNES Molecule block.

        The scale record selects spherical (one value), cylindrical (two),
        or fractional (six) coordinates as in the FDMNES manual.

        Returns:
            ase.Atoms: Atom positions in angstroms, with periodicity disabled.

        Raises:
            ValueError: If the scale or atomic-coordinate records are invalid.
            ImportError: If ASE is not installed.
        """
        from ase import Atoms
        from ase.cell import Cell

        lines = self._get_structure_lines("molecule")
        if len(lines) < 2:
            raise ValueError("Molecule requires scale parameters and atom rows")
        scale = [float(value.replace("D", "E")) for value in lines[0].split()]
        if len(scale) not in (1, 2, 6) or any(
            not isfinite(value) or value <= 0 for value in scale
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
            if not all(isfinite(value) for value in coordinates):
                raise ValueError("Molecule coordinates must be finite")
            positions.append(coordinates)

        if len(scale) == 6:
            # The three angles define the basis for the fractional positions.
            cell = Cell.fromcellpar(scale)
            positions = cell.cartesian_positions(positions)
        else:
            for index, (radius, second, third) in enumerate(positions):
                radius *= scale[0]
                angle = radians(second)
                if len(scale) == 2:
                    positions[index] = [
                        radius * cos(angle),
                        radius * sin(angle),
                        third * scale[1],
                    ]
                else:
                    azimuth = radians(third)
                    planar_radius = radius * sin(angle)
                    positions[index] = [
                        planar_radius * cos(azimuth),
                        planar_radius * sin(azimuth),
                        radius * cos(angle),
                    ]
        return Atoms(numbers=numbers, positions=positions)

    def _get_structure_lines(self, section: str) -> list[str]:
        """Collect the scale and atom rows following a structure keyword.

        Args:
            section: Lowercase FDMNES structure keyword.

        Returns:
            list[str]: Cell and atomic-coordinate records.
        """
        lines = []
        in_section = False
        for original_line in self.lines:
            line = original_line.split("!", 1)[0]
            line = line.split("#", 1)[0]
            # The FDMNES examples annotate structure rows with "= a, b, c…".
            line = line.partition("=")[0]
            line = line.strip()
            if not line:
                continue

            fields = line.split()
            keyword = fields[0].lower()
            if not in_section:
                if keyword == "end":
                    break
                if keyword == section:
                    in_section = True
                    if len(fields) > 1:
                        lines.append(" ".join(fields[1:]))
                continue

            if keyword in self.KEYWORDS or keyword == "end":
                break

            # Stop when an unrelated alphabetic keyword starts a new block.
            if fields[0][0].isalpha():
                break

            lines.append(line)
        return lines

    @staticmethod
    def render(
        absorber: int = 1,
        fileout: str = "Cu",
        energy_range: str = "-15. 0.2  0. 0.5 10. 1. 45.",
        edge: str = "K",
        radius: float = 5,
        molecule: bool = False,
        structure_writer=None,
    ) -> str:
        """Construct a complete FDMNES input file.

        Args:
            absorber: Absorber number in the FDMNES input.
            fileout: Prefix for calculated output files.
            energy_range: Energy mesh definition in electronvolts.
            edge: Absorption edge, for example K or L3.
            radius: Cluster radius in angstroms.
            molecule: Select the Molecule keyword instead of Crystal.
            structure_writer: Object providing the FDMNES structure section.

        Returns:
            str: FDMNES input content including the structural section.

        Raises:
            ValueError: If no structure writer is provided.
        """
        if structure_writer is None:
            raise ValueError("A structure writer is required")

        # Keep the keyword sequence and defaults of SAE's FDvasp2fdm.py.
        lines = [
            "! FDMNES indata file",
            "",
            "!Nonexc",
            "",
            " Absorber",
            f"  {absorber}",
            "! allsite",
            "",
            " Filout",
            f"  {fileout}",
            "",
            " Range                        ! Energy range of calculation (eV)",
            (
                f"  {energy_range}  ! first energy, step, intermediary "
                "energy, step ..., last energy "
            ),
            "! -15. 0.1 50. 1. 200.        !",
            "",
            "!Energpho",
            "",
            " Edge",
            f"  {edge}",
            "! L23",
            "",
            "!Quadrupole",
            "",
            " Relativism",
            "",
            " Convolution",
            "",
            "!No_Fermi",
            "!Efermi",
            "!  -6.0",
            "!Estart",
            "! -10.0",
            "",
            "!SCF",
            "!R_self",
            "! 5.0",
            "!N_self",
            "! 100",
            "!P_self",
            "! 0.05",
            "!Delta_E_conv",
            "! 0.01",
            "",
            "!Magnetism",
            "!SCF_mag_free",
            "",
            "!Hubbard",
            "! 0.0 6.3 0.0",
            "",
            "!TDDFT",
            "",
            "!Green",
            "",
            (
                " Radius                       ! Radius of the cluster "
                "where final state calculation is performed"
            ),
            (
                f"   {radius}  ! For a good calculation, this radius "
                "must be increased up to 6 or 7 Angstroems"
            ),
            "",
            " Memory_save",
            "",
        ]
        # The structure section is produced by its own file-format writer.
        structure_content = structure_writer.render(molecule=molecule)
        lines.extend(structure_content.rstrip("\n").splitlines())
        lines.extend(
            [
                "",
                "!Cif_file",
                "!  POSCAR.cif",
                "",
                " Density",
                "  state_all",
                "",
                "!Adimp",
                "! 0.20",
                "",
                " End",
                "",
            ]
        )
        return "\n".join(lines) + "\n"

    @staticmethod
    def write(filename: str | Path = "read_pdb.inp", **kwargs) -> Path:
        """Write a complete FDMNES calculation input.

        Args:
            filename: Destination filename.
            **kwargs: Calculation settings accepted by :meth:`render`.

        Returns:
            Path: Destination of the written input file.
        """
        destination = Path(filename)
        content = FdmInp.render(**kwargs)
        destination.write_text(content, encoding="utf-8")
        return destination
