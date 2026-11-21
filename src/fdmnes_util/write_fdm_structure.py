#!/usr/bin/env python3
"""Write the Crystal or Molecule section of a FDMNES input file."""

from pathlib import Path
from importlib.resources import files
import math

from fdmnes_util.read_vasp_poscar import ReadVaspPoscar


class WriteFdmStructure:
    """Convert structure information into a FDMNES structural section.

    The POSCAR file is interpreted exclusively by the external vasp_util
    package. This class implements only the FDMNES output representation.
    """

    def __init__(self, structure: ReadVaspPoscar) -> None:
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
