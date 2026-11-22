#!/usr/bin/env python3
"""Plot FDMNES density-of-states data read by the SD file classes."""

from pathlib import Path

from ..analyze_fdm_average import AnalyzeFdmAverage
from . import _PlotFigure


class PlotFdmDos(_PlotFigure):
    """Create density-of-states figures without parsing an SD file."""

    def plot_local(self, reader, output, *, orbit=1, integrated=False):
        """SAE の fdLDOS.py と同じ配置で一つの軌道を描く。

        Args:
            reader: SD ファイルのリーダー。
            output: 保存先のパス。
            orbit: 軌道角運動量の番号。
            integrated: True の場合は積分 LDOS を描く。

        Returns:
            保存した図のパス。
        """
        import matplotlib.pyplot as plt

        if integrated:
            dos = reader.get_intldos(l=orbit)
        else:
            dos = reader.get_ldos(l=orbit)
        eng = reader.get_eng()
        with plt.rc_context():
            plt.rcParams["font.family"] = "Times New Roman"
            # ラベル等のフォントサイズ
            plt.rcParams["font.size"] = 16
            # レジェンドのフォントサイズ
            plt.rcParams["legend.fontsize"] = 14
            # 軸の太さを設定。目盛りは変わらない
            plt.rcParams["axes.linewidth"] = 1.5
            # for portrait
            figure = plt.figure(figsize=(7.0, 9.89))
            orgx = 0.17
            orgy = 0.08
            xsize = 0.75
            ysize = 0.83 / 2.0
            plt.axes([orgx, orgy, xsize, ysize])
            plt.plot(eng, dos, linewidth=2, label="DOS")
            plt.axvline(x=0, color="black", linewidth=1)
            leg = plt.legend(loc="upper right")
            leg.get_frame().set_alpha(0.5)
            return self._save_figure(figure, output, show=True)

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
        divisor=None,
        extra_outputs=(),
    ):
        """Draw a selected LDOS channel with optional axis limits.

        Args:
            reader: SD reader or list of absorber-site SD readers.
            output: Destination image path. Matplotlib infers its format.
            orbital: Orbital channel to plot, such as ``p``.
            emin: Optional minimum energy for the horizontal axis.
            emax: Optional maximum energy for the horizontal axis.
            dmax: Optional maximum density for the vertical axis.
            edge_offset: Offset added to the computed energy axis (eV).
            fermi_position: Position of the vertical Fermi marker (eV).
            divisor: Optional normalization divisor for multiple sites.
            extra_outputs: Additional paths to save the same figure.

        Returns:
            pathlib.Path: The generated image file.
        """
        import matplotlib.pyplot as plt

        if isinstance(reader, (list, tuple)):
            eng, dos = AnalyzeFdmAverage().average(
                reader,
                "get_ldos",
                l=orbital,
                divisor=divisor,
            )
        else:
            eng = reader.get_eng()
            dos = reader.get_ldos(l=orbital)
        with plt.rc_context():
            plt.rcParams["font.family"] = "Times New Roman"
            # ラベル等のフォントサイズ
            plt.rcParams["font.size"] = 16
            # レジェンドのフォントサイズ
            plt.rcParams["legend.fontsize"] = 14
            # 軸の太さを設定。目盛りは変わらない
            plt.rcParams["axes.linewidth"] = 1.5
            # for portrait
            figure = plt.figure(figsize=(7.0, 9.89))
            orgx = 0.17
            orgy = 0.08
            xsize = 0.75
            ysize = 0.83 / 2.0
            plt.axes([orgx, orgy, xsize, ysize])
            plt.plot(eng + edge_offset, dos, linewidth=2, label=f"absorber LDOS ({orbital})")
            plt.ylabel("LDOS [stat/eV]")
            plt.axvline(x=fermi_position, color="black", linewidth=1)
            plt.ticklabel_format(axis="x", useOffset=False)
            leg = plt.legend(loc="upper right")
            leg.get_frame().set_alpha(0.5)
            plt.xlim(xmax=emax, xmin=emin)
            plt.ylim(ymax=dmax)
            return self._save_figure(figure, output, extra_outputs=extra_outputs, show=True)

    def plot_occupied_ldos(
        self,
        reader,
        output,
        *,
        orbital="p",
        edge_offset=0.0,
        fermi_position=0.0,
        emin=None,
        emax=None,
        dmax=None,
    ):
        """Plot LDOS with the occupied states shaded below the Fermi level.

        SAE's ``fdLDOS_color.py`` draws the LDOS in black and shades the
        occupied region in gray. The energy and Fermi reference must use
        the same coordinate system.

        Args:
            reader: FDMNES SD object for the selected format year.
            output: Destination figure path.
            orbital: Orbital channel whose LDOS is plotted.
            edge_offset: Energy offset added to SD energies, in eV.
            fermi_position: Fermi level in the shifted energy axis, in eV.
            emin: Optional lower energy limit, in eV.
            emax: Optional upper energy limit, in eV.
            dmax: Optional upper density limit.

        Returns:
            pathlib.Path: Destination of the saved figure.
        """
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        energy = reader.get_eng() + edge_offset
        density = reader.get_ldos(orbital)

        figure, axis = plt.subplots(figsize=(7.0, 9.89))
        axis.plot(energy, density, linewidth=1, color="black", label=orbital)

        # SAE marks occupied states by shading only below the Fermi energy.
        occupied = energy < fermi_position
        axis.fill_between(
            energy,
            density,
            where=occupied,
            color="#cccccc",
            linewidth=2,
        )
        axis.axvline(x=fermi_position, color="black", linewidth=1)
        axis.set_xlabel("Energy [eV]")
        axis.set_ylabel("LDOS [stat/eV]")
        axis.ticklabel_format(axis="x", useOffset=False)

        if emin is not None:
            axis.set_xlim(left=emin)
        if emax is not None:
            axis.set_xlim(right=emax)
        if dmax is not None:
            axis.set_ylim(top=dmax)

        axis.legend(loc="upper right")
        figure.tight_layout()
        return self._save_figure(figure, output)

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
        return self._save_figure(figure, output)

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
        output_paths = []
        used_formats = set()
        for image_format in formats:
            normalized_format = image_format.lower().lstrip(".")
            if normalized_format not in supported_formats:
                raise ValueError(f"Unsupported format: {image_format}")
            if normalized_format in used_formats:
                raise ValueError(f"Duplicate format: {image_format}")
            used_formats.add(normalized_format)
            destination = Path(output_prefix).with_suffix(f".{normalized_format}")
            output_paths.append(destination)

        if not output_paths:
            raise ValueError("At least one output format is required")

        # SAE の fdLDOSmulti.py と同様、同じ図を指定の各形式に保存する。
        figure = self._multiple_sites_figure(
            readers,
            labels,
            edge_energy=edge_energy,
            fermi_energy=fermi_energy,
            orbital=orbital,
            emin=emin,
            emax=emax,
        )
        self._save_figure(figure, output_paths[0], extra_outputs=output_paths[1:], show=True)
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
        figure = self._multiple_sites_figure(
            readers,
            labels,
            edge_energy=edge_energy,
            fermi_energy=fermi_energy,
            orbital=orbital,
            emin=emin,
            emax=emax,
        )
        return self._save_figure(figure, output, show=True)

    @staticmethod
    def _multiple_sites_figure(
        readers,
        labels,
        *,
        edge_energy,
        fermi_energy,
        orbital,
        emin,
        emax,
    ):
        if len(readers) != 3:
            raise ValueError("Exactly three SD readers are required")
        if len(labels) != 3:
            raise ValueError("Exactly three labels are required")

        import matplotlib.pyplot as plt

        with plt.rc_context():
            plt.rcParams["font.family"] = "Times New Roman"
            # ラベル等のフォントサイズ
            plt.rcParams["font.size"] = 16
            # レジェンドのフォントサイズ
            plt.rcParams["legend.fontsize"] = 14
            # 軸の太さを設定。目盛りは変わらない
            plt.rcParams["axes.linewidth"] = 1.5
            # for portrait
            fig = plt.figure(figsize=(7.0, 9.89))
            f0 = fig.add_subplot(311)
            f1 = fig.add_subplot(312, sharex=f0)
            f2 = fig.add_subplot(313, sharex=f0)
            ef = edge_energy + fermi_energy
            for axis, sd, label in zip((f0, f1, f2), readers, labels):
                dos = sd.get_ldos(orbital)
                axis.plot(
                    sd.get_eng() + edge_energy,
                    dos,
                    color="red",
                    linewidth=1,
                    label=label,
                )
                axis.axvline(x=ef, color="black", linewidth=1)
                axis.set_ylabel("LDOS [stat/eV]")
                legend = axis.legend(loc="upper right")
                legend.get_frame().set_alpha(0.5)
                axis.ticklabel_format(axis="x", useOffset=False)
            f2.set_xlim(left=emin, right=emax)
            return fig

    def plot_three_calculations(
        self,
        readers,
        fermi_energies,
        labels,
        output,
        *,
        orbital="p",
        emin=None,
        emax=None,
        density_max=5.0,
        extra_outputs=(),
    ):
        """Compare p-LDOS from three independent FDMNES calculations.

        This follows SAE ``fdMulti_3.py`` rather than ``fdLDOSmulti.py``.
        Each calculation has its own Fermi energy. Its energy axis is
        shifted independently so that the Fermi level is at zero.

        Args:
            readers: Three SD readers, one per calculation.
            fermi_energies: Three Fermi energies from the corresponding
                ``FdmTxt`` objects, expressed in the SD energy reference.
            labels: Labels for the three independent calculations.
            output: Destination image path.
            orbital: LDOS channel to plot.
            emin: Optional minimum Fermi-relative energy in eV.
            emax: Optional maximum Fermi-relative energy in eV.
            density_max: Upper bound of the LDOS axis.
            extra_outputs: Additional paths for saving the same figure.

        Returns:
            pathlib.Path: Path to the saved figure.

        Raises:
            ValueError: If input lengths are not three or limits are invalid.
        """
        if len(readers) != 3:
            raise ValueError("Three SD readers are required")
        if len(fermi_energies) != 3:
            raise ValueError("Three Fermi energies are required")
        if len(labels) != 3:
            raise ValueError("Three labels are required")
        if density_max <= 0:
            raise ValueError("density_max must be positive")

        import matplotlib.pyplot as plt

        with plt.rc_context():
            plt.rcParams["font.family"] = "Times New Roman"
            # ラベル等のフォントサイズ
            plt.rcParams["font.size"] = 16
            # レジェンドのフォントサイズ
            plt.rcParams["legend.fontsize"] = 14
            # 軸の太さを設定。目盛りは変わらない
            plt.rcParams["axes.linewidth"] = 1.5
            # for portrait
            figure = plt.figure(figsize=(7.0, 9.89))
            orgx = 0.17
            orgy = 0.08
            off = 0.015
            xsize = 0.72
            ysize0 = 0.75
            ysize = ysize0 / 3.0
            EF = 0.0
            colors = ("red", "blue", "green")
            for i, reader in enumerate(readers):
                # 各計算のフェルミ準位で、その計算の SD 軸をシフトする。
                Edge = -fermi_energies[i]
                ldos = reader.get_ldos(orbital)
                plt.axes([orgx, orgy, xsize, ysize])
                plt.plot(
                    reader.get_eng() + Edge,
                    ldos,
                    color=colors[i],
                    linewidth=1,
                    label=labels[i],
                )
                plt.axvline(x=EF, color="black", linewidth=1)
                if i > 0:
                    plt.xticks([])
                plt.ylim([0, density_max])
                plt.xlim(xmax=emax, xmin=emin)
                plt.legend(fontsize=12, loc="upper right")
                if i == 1:
                    plt.ylabel("Absorption [arb. unit]")
                orgy = orgy + ysize + off
            return self._save_figure(figure, output, extra_outputs=extra_outputs, show=True)

    def plot_composite(
        self,
        reader,
        output,
        *,
        groups,
        spins=(0,),
        spin_labels=("", ""),
        projected=False,
        integrated=False,
        xas=(),
        shift=0.0,
        fermi_position=0.0,
        xlabel="Photon Energy [eV]",
        limits=(None, None),
        density_max=None,
        orbital_max=None,
        xas_max=None,
        label="0",
        extra_formats=False,
        show=False,
        shade_occupied=False,
    ):
        """Draw the SAE portrait DOS stack, with optional XAS at the bottom.

        Args:
            reader: SD reader supplying densities on its own energy grid.
            output: Main figure filename.
            groups: Bottom-to-top groups of orbital names. Use ("total",)
                for a total DOS panel.
            spins: Spin channel order within each group, from bottom to top.
            spin_labels: Label suffixes indexed by spin channel.
            projected: Use individual orbital projections (PDOS).
            integrated: Add stored integral curves on right-hand axes.
            xas: Energy, intensity and label tuples for the absorption panel.
            shift: Reference-frame shift applied only to the SD grid, in eV.
            fermi_position: Position of the vertical energy marker, in eV.
            xlabel: Energy reference label shown on the bottom axis.
            limits: Lower and upper energy limits, with None for SD bounds.
            density_max: Default upper limit on DOS magnitudes.
            orbital_max: Optional mapping of group names to DOS limits.
            xas_max: Maximum intensity on the absorption panel.
            label: Site or material label used on the DOS curves.
            extra_formats: Also save PDF, EPS, and PNG.
            show: Display the figure after saving.
            shade_occupied: Shade LDOS below the displayed Fermi level.

        Returns:
            pathlib.Path: Main saved figure.

        Raises:
            ValueError: If there are no DOS panels or if integrals are
                requested for magnetic-sublevel projections.
        """
        import matplotlib.pyplot as plt

        if not groups or not spins:
            raise ValueError("At least one DOS group and spin are required")
        if projected and integrated:
            raise ValueError("Integrated DOS is available for LDOS groups only")

        energy = reader.get_eng() + shift
        left, right = limits
        if left is None:
            left = energy.min()
        if right is None:
            right = energy.max()
        orbital_max = orbital_max or {}
        gap, width, height = (0.015, 0.72, 0.75)
        if projected:
            gap, width, height = (0.016, 0.75, 0.81)

        spin_by_group = []
        for group in groups:
            if group == ("total",) and getattr(reader, "total_ispin", None) == 1:
                spin_by_group.append(spins[:1])
            else:
                spin_by_group.append(spins)
        panel_count = sum(map(len, spin_by_group)) + bool(xas)
        panel_height = height / panel_count
        first_orbital_group = int(groups[0] == ("total",))
        label_group = first_orbital_group
        if projected:
            label_group = max(first_orbital_group, len(groups) - 2)
        color_index = 0
        bottom = 0.08
        with plt.rc_context():
            plt.rcParams["font.family"] = "Times New Roman"
            # ラベル等のフォントサイズ
            plt.rcParams["font.size"] = 15
            # レジェンドのフォントサイズ
            plt.rcParams["legend.fontsize"] = 10
            # 軸の太さを設定。目盛りは変わらない
            plt.rcParams["axes.linewidth"] = 1.5
            # for portrait
            figure = plt.figure(figsize=(7.0, 9.89))
            axes = []
            if xas:
                axis = figure.add_axes([0.17, bottom, width, panel_height])
                for index, (grid, intensity, name) in enumerate(xas):
                    color = "black"
                    if index:
                        color_index += 1
                        color = plt.cm.prism(color_index * 10)
                    axis.plot(grid, intensity, color=color, label=name)
                    if index == 0 and xas_max is None:
                        xas_max = axis.get_ylim()[1]
                axis.set_ylim(bottom=0, top=xas_max)
                axis.set_ylabel("Absorption [arb. unit]")
                leg = axis.legend(loc="lower right")
                leg.get_frame().set_alpha(0.5)
                axes.append(axis)
                bottom += panel_height + gap

            for group_index, group in enumerate(groups):
                if not projected:
                    color_index += 1
                separate_spins = len(spin_by_group[group_index]) == 2
                for spin in spin_by_group[group_index]:
                    spin_label = spin_labels[spin]
                    if group == ("total",) and getattr(reader, "total_ispin", None) == 1:
                        spin_label = ""
                    axis = figure.add_axes([0.17, bottom, width, panel_height])
                    bottom += panel_height
                    axes.append(axis)
                    for orbital in group:
                        if orbital == "total":
                            values = reader.get_tdos(spin=spin)
                            name = orbital
                        elif projected:
                            values = reader.get_pdos(lm=orbital, spin=spin)
                            name = f"{label}-{orbital}"
                        else:
                            values = reader.get_ldos(l=orbital, spin=spin)
                            name = f"{label}-{orbital}"
                        if projected:
                            color_index += 1
                        color = plt.cm.prism((color_index + 1) * 10)
                        if shade_occupied and not projected and orbital != "total":
                            axis.plot(
                                energy,
                                values,
                                linewidth=1,
                                color="black",
                                label=name + spin_label,
                            )
                            axis.fill_between(
                                energy,
                                values,
                                color="#cccccc",
                                where=energy < fermi_position,
                                linewidth=2,
                            )
                        else:
                            axis.plot(
                                energy,
                                values,
                                linewidth=2,
                                color=color,
                                label=name + spin_label,
                            )

                    maximum = orbital_max.get(group[0], density_max)
                    if projected and maximum is None:
                        maximum = max(line.get_ydata().max() for line in axis.lines)
                        if maximum <= 0:
                            maximum = None
                    if projected or (spin == 1 and separate_spins):
                        axis.set_ylim(bottom=0, top=maximum)
                    elif maximum is not None:
                        axis.set_ylim(top=maximum)
                    if spin == 1 and separate_spins:
                        axis.invert_yaxis()
                    if group == ("total",):
                        axis.set_ylabel("TDOS")
                    elif group_index == label_group:
                        ylabel = "LDOS"
                        if projected:
                            ylabel = "DOS [state/eV]"
                        axis.set_ylabel(ylabel)
                    leg = axis.legend(loc="upper right")
                    leg.get_frame().set_alpha(0.5)

                    if integrated:
                        integral_axis = axis.twinx()
                        for orbital in group:
                            if orbital == "total":
                                integral = reader.get_inttdos(spin=spin)
                            else:
                                integral = reader.get_intldos(l=orbital, spin=spin)
                            integral_axis.plot(
                                energy,
                                integral,
                                color="black",
                                label="INT" + spin_label,
                            )
                        if spin == 1 and separate_spins:
                            integral_axis.invert_yaxis()
                        if group == ("total",):
                            integral_axis.set_ylabel("Integrated TDOS")
                        elif group_index == first_orbital_group:
                            integral_axis.set_ylabel("Integrated LDOS")
                bottom += gap

            for index, axis in enumerate(axes):
                axis.axvline(fermi_position, color="black", linewidth=1)
                if left != right:
                    axis.set_xlim(left, right)
                axis.ticklabel_format(axis="x", useOffset=False)
                axis.tick_params(axis="x", bottom=index == 0, labelbottom=index == 0)
            axes[0].set_xlabel(xlabel)
            return self._save_figure(figure, output, extra_formats=extra_formats, show=show)
