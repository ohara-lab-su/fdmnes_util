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

    def save_multiple_formats(
        self,
        readers,
        labels,
        output_prefix,
        *,
        formats=("eps", "pdf", "png"),
        edge_energy,
        fermi_energy,
        orbital="p",
        emin=None,
        emax=None,
    ):
        """Save the three-site LDOS figure in several image formats.

        The original SAE ``fdLDOSmulti.py`` exports EPS, PDF, and PNG.
        This method exposes that behavior without repeating the data
        preparation in an editable example script.

        Args:
            readers: Exactly three year-specific SD reader objects.
            labels: Three site labels in the same order as the readers.
            output_prefix: Output path without a filename extension.
            formats: Sequence of image extensions supported by Matplotlib.
            edge_energy: Absorption-edge energy in eV.
            fermi_energy: Fermi energy relative to the edge in eV.
            orbital: Orbital channel to plot.
            emin: Optional minimum photon energy in eV.
            emax: Optional maximum photon energy in eV.

        Returns:
            list[pathlib.Path]: Paths to the generated image files.

        Raises:
            ValueError: If formats is empty, contains duplicates, or
                includes an unsupported output format.
        """
        supported_formats = {"eps", "pdf", "png"}
        if not formats:
            raise ValueError("At least one output format is required")

        output_paths = []
        used_formats = set()
        for image_format in formats:
            normalized_format = image_format.lower().lstrip(".")
            if normalized_format not in supported_formats:
                raise ValueError(f"Unsupported format: {image_format}")
            if normalized_format in used_formats:
                raise ValueError(f"Duplicate format: {image_format}")
            used_formats.add(normalized_format)

            destination = Path(output_prefix).with_suffix(
                f".{normalized_format}"
            )
            self.plot_multiple_sites(
                readers,
                labels,
                destination,
                edge_energy=edge_energy,
                fermi_energy=fermi_energy,
                orbital=orbital,
                emin=emin,
                emax=emax,
            )
            output_paths.append(destination)

        return output_paths

    def plot_multiple_sites(
        self,
        readers,
        labels,
        output,
        *,
        edge_energy,
        fermi_energy,
        orbital="p",
        emin=None,
        emax=None,
    ):
        """Plot three site-resolved LDOS panels on a shared energy axis.

        The layout follows the three-panel arrangement in SAE's
        ``fdLDOSmulti.py``. Energy values are converted to photon energy
        using the absorption-edge energy from the corresponding XAS file.

        Args:
            readers: Three version-specific SD reader instances.
            labels: Three labels corresponding to the SD files.
            output: Path of the image to save.
            edge_energy: Absorption-edge energy in eV.
            fermi_energy: Fermi energy relative to the absorption edge in eV.
            orbital: Orbital channel to display, defaulting to p.
            emin: Optional lower photon-energy limit in eV.
            emax: Optional upper photon-energy limit in eV.

        Returns:
            pathlib.Path: Path of the saved figure.

        Raises:
            ValueError: If exactly three readers and labels are not supplied.
        """
        if len(readers) != 3:
            raise ValueError("Exactly three SD readers are required")
        if len(labels) != 3:
            raise ValueError("Exactly three labels are required")

        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        figure, axes = plt.subplots(
            3,
            1,
            figsize=(7.0, 9.89),
            sharex=True,
        )
        fermi_marker = edge_energy + fermi_energy

        for index, reader in enumerate(readers):
            axis = axes[index]
            photon_energy = reader.get_eng() + edge_energy
            density = reader.get_ldos(orbital)
            axis.plot(
                photon_energy,
                density,
                color="red",
                linewidth=1,
                label=labels[index],
            )
            axis.axvline(
                x=fermi_marker,
                color="black",
                linewidth=1,
            )
            axis.set_ylabel("LDOS [stat/eV]")
            axis.ticklabel_format(axis="x", useOffset=False)
            legend = axis.legend(loc="upper right")
            legend.get_frame().set_alpha(0.5)

        axes[-1].set_xlabel("Photon Energy [eV]")
        if emin is not None:
            axes[-1].set_xlim(left=emin)
        if emax is not None:
            axes[-1].set_xlim(right=emax)

        figure.tight_layout()
        figure.savefig(output)
        plt.close(figure)
        return Path(output)
