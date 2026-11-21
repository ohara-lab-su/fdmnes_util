#!/usr/bin/env python3
"""Read an Athena normalized XAFS spectrum from a ``*.nor`` file."""

from pathlib import Path
import re

import numpy as np


class AthenaNor:
    """Read the energy axis and normalized absorption from an Athena file.

    Attributes:
        path: Path to the source file.
        energy: Photon energies in eV.
        normalized: Normalized absorption values.
        e0: Optional absorption-edge energy from the header.
    """

    def __init__(self, filename):
        """Load an Athena normalized spectrum.

        Args:
            filename: Path to a ``*.nor`` text file.

        Raises:
            ValueError: If a data row has fewer than two numeric columns.
        """
        self.path = Path(filename)
        energies = []
        normalized = []
        self.e0 = None

        with self.path.open(encoding="utf-8", errors="replace") as stream:
            for line in stream:
                stripped = line.strip()
                if not stripped:
                    continue

                if stripped.startswith("#"):
                    self._read_e0_comment(stripped)
                    continue

                values = stripped.split()
                if len(values) < 2:
                    raise ValueError(
                        f"Invalid Athena data row in {self.path}: {stripped}"
                    )

                # Only the first two data columns are used by the original
                # SAE Athena reader. Remaining columns are not modified.
                energies.append(float(values[0]))
                normalized.append(float(values[1]))

        self.energy = np.asarray(energies, dtype=float)
        self.normalized = np.asarray(normalized, dtype=float)

    def _read_e0_comment(self, comment):
        """Extract the optional ``E0=`` field from an Athena comment.

        Args:
            comment: One comment line from the source file.
        """
        match = re.search(r"\bE0\s*=\s*([-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?)", comment)
        if match is not None:
            self.e0 = float(match.group(1))

    def get_eng(self):
        """Return the photon-energy axis.

        Returns:
            numpy.ndarray: Photon-energy values.
        """
        return self.energy

    def get_nor(self):
        """Return the normalized absorption spectrum.

        Returns:
            numpy.ndarray: Normalized absorption values.
        """
        return self.normalized
