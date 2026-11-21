#!/usr/bin/env python3
"""Read keywords and crystal parameters from a FDMNES input file."""

from pathlib import Path


class ReadFdmInp:
    """Read the input keywords used by FDMNES command-line utilities.

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
        "allsite",
        "energpho",
        "energygpho",
        "convolution",
        "conv_out",
        "calculation",
        "nonexc",
        "crystal",
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

    def get_ispin(self):
        """Return the number of spin channels indicated by the input.

        Returns:
            int: Two when ``Spin`` is specified, otherwise one.
        """
        if "spin" in self.tags:
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
