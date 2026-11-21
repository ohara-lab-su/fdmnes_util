#!/usr/bin/env python3
# Original SAE source: fdmfile.py
# SAE: K.NAKADA, kengo.nakada@gmail.com
# SAE: 2018.08.15
# SAE: 2015.11.12 startup
# SAE: Copyright Kengo NAKADA; SAE class library.
"""Read the FDMNES ``fdmfile.txt`` list of calculation inputs."""

from pathlib import Path


class ReadFdmfile:
    """Read the filenames contained in an FDMNES batch list."""

    def __init__(self, filename="fdmfile.txt"):
        """Load the batch list.

        Args:
            filename: Path to ``fdmfile.txt``.

        Raises:
            ValueError: If the list is empty or incomplete.
        """
        self.path = Path(filename)
        lines = []
        for line in self.path.read_text().splitlines():
            stripped = line.strip()
            if stripped:
                lines.append(stripped)
        if not lines:
            raise ValueError("Empty fdmfile.txt")
        count = int(lines[0])
        self.filenames = lines[1 : 1 + count]
        if len(self.filenames) != count:
            raise ValueError("Incomplete fdmfile.txt")

    def get_filout(self):
        """Return the first calculation filename, or an empty string."""
        if self.filenames:
            return self.filenames[0]
        return ""
