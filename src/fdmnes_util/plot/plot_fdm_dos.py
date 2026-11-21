#!/usr/bin/env python3
"""Plot FDMNES density-of-states data read by the SD file classes."""

from pathlib import Path


class PlotFdmDos:
    """Create density-of-states figures without parsing an SD file."""

    def plot(self, reader, output, orbitals=("s", "p", "d"), *, integrated=False):
        """Plot orbital-resolved density-of-states curves.

        Args:
            reader: A version-specific SD reader exposing the ``get_*dos`` API.
            output: Path of the output image or PDF.
            orbitals: Orbital channels to draw in the requested order.
            integrated: Plot integrated LDOS instead of LDOS when True.

        Returns:
            pathlib.Path: Path to the figure written to disk.
        """
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        figure, axis = plt.subplots()
        lmax = reader.get_lmax()
        available_orbitals = ("s", "p", "d")

        for orbital in orbitals:
            # The numerical orbital indices follow the FDMNES s/p/d convention.
            orbital_index = available_orbitals.index(orbital)
            if orbital_index > lmax:
                continue

            if integrated:
                intensity = reader.get_intldos(orbital)
            else:
                intensity = reader.get_ldos(orbital)

            axis.plot(reader.get_eng(), intensity, label=orbital)

        axis.set_xlabel("Energy (eV)")
        axis.set_ylabel("DOS")
        axis.legend()
        figure.tight_layout()
        figure.savefig(output)
        plt.close(figure)
        return Path(output)
