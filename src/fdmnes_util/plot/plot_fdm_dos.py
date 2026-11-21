#!/usr/bin/env python3
"""Plot FDMNES density-of-states data read by the SD file classes."""

from pathlib import Path


class PlotFdmDos:
    """Create density-of-states figures without parsing an SD file."""

    def plot_single_orbital(
        self,
        reader,
        output,
        *,
        orbital="p",
        emin=None,
        emax=None,
        dmax=None,
        edge_offset=0.0,
        fermi_position=0.0,
    ):
        """Draw a selected LDOS channel with optional axis limits.

        Args:
            reader: Year-specific FDMNES SD reader.
            output: Destination image path. Matplotlib infers its format.
            orbital: Orbital channel to plot, such as ``p``.
            emin: Optional minimum energy for the horizontal axis.
            emax: Optional maximum energy for the horizontal axis.
            dmax: Optional maximum density for the vertical axis.
            edge_offset: Offset added to the computed energy axis (eV).
            fermi_position: Position of the vertical Fermi marker (eV).

        Returns:
            pathlib.Path: The generated image file.
        """
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        energy = reader.get_eng() + edge_offset
        density = reader.get_ldos(orbital)

        figure, axis = plt.subplots(figsize=(7.0, 9.89))
        axis.plot(energy, density, linewidth=2, label=f"LDOS ({orbital})")
        axis.axvline(x=fermi_position, color="black", linewidth=1)
        axis.set_ylabel("LDOS [stat/eV]")
        axis.set_xlabel("Energy [eV]")
        axis.ticklabel_format(axis="x", useOffset=False)

        if emin is not None:
            axis.set_xlim(left=emin)
        if emax is not None:
            axis.set_xlim(right=emax)
        if dmax is not None:
            axis.set_ylim(top=dmax)

        axis.legend(loc="upper right")
        figure.tight_layout()
        figure.savefig(output)
        plt.close(figure)
        return Path(output)

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
