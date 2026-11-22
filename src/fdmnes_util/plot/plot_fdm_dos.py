#!/usr/bin/env python3
"""``*_sdN.txt`` を読んだリーダーから状態密度を取得し、図として保存する。

PlotFdmDos は LDOS・PDOS・積分値の配置や、占有領域の塗り分けを担当する。SD の形式判定は FdmSd が行う。
"""
from pathlib import Path

from ..analyze_fdm_average import AnalyzeFdmAverage
from . import _PlotFigure


class PlotFdmDos(_PlotFigure):
    """``*_sdN.txt`` を読んだリーダーや数値配列から状態密度を描き、図として保存する。"""
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
        """指定した LDOS を任意の軸範囲で描く。

        Args:
            reader: SD リーダー、または複数の吸収サイトの SD リーダーのリスト。
            output: 保存先ファイルのパス。拡張子で出力形式を指定する。
            orbital: 対象の軌道名。
            emin: 省略可能なエネルギー軸の下限。
            emax: 省略可能なエネルギー軸の上限。
            dmax: 省略可能な状態密度の上限。
            edge_offset: 計算のエネルギー軸に加える量（eV）。
            fermi_position: 表示に用いる基準でのフェルミ準位（eV）。縦線の位置に使う。
            divisor: 合計を割る正の値。必要に応じて原子あたりの値に換算する。
            extra_outputs: 同じ図を追加保存するパスの並び。

        Returns:
            pathlib.Path: 保存した画像ファイルのパス。
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
        """フェルミ準位より下の占有領域を塗り分けて LDOS を描く。

        SAE の fdLDOS_color.py と同じく LDOS を黒線で、占有領域を灰色で描く。エネルギー軸とフェルミ準位の基準は揃えて渡す。

        Args:
            reader: 状態密度データを取得する SD リーダー。
            output: 保存先ファイルのパス。拡張子で出力形式を指定する。
            orbital: 対象の軌道名。
            edge_offset: 計算のエネルギー軸に加える量（eV）。
            fermi_position: 表示に用いる基準でのフェルミ準位（eV）。縦線の位置に使う。
            emin: 省略可能なエネルギー軸の下限。
            emax: 省略可能なエネルギー軸の上限。
            dmax: 省略可能な状態密度の上限。

        Returns:
            pathlib.Path: 図の保存先。
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
        """軌道群別の状態密度曲線を描く。

        Args:
            reader: get_*dos メソッドを持つ年別 SD リーダー。
            output: 保存先ファイルのパス。拡張子で出力形式を指定する。
            orbitals: 描画する軌道の順序付きの並び。
            integrated: 積分値を描く指定。

        Returns:
            pathlib.Path: 保存したファイルのパス。
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
        """3サイトの LDOS 図を複数の画像形式で保存する。

        SAE の fdLDOSmulti.py と同様に、同じデータから EPS・PDF・PNG に保存する。

        Args:
            readers: 三つのサイトに対応する年別 SD リーダー。
            labels: 各リーダーに対応するラベルの並び。
            output_prefix: 保存先の拡張子なしのパス。
            formats: Matplotlib が対応する保存形式の並び。
            edge_energy: 吸収端エネルギー（eV）。
            fermi_energy: エネルギー軸の基準に対応するフェルミエネルギー（eV）。
            orbital: 対象の軌道名。
            emin: 省略可能なエネルギー軸の下限。
            emax: 省略可能なエネルギー軸の上限。

        Returns:
            list[pathlib.Path]: 生成した画像ファイルのパスの並び。

        Raises:
            ValueError: 保存形式が空、重複あり、または非対応形式を含む場合。
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
        """共通のエネルギー軸で3サイトの LDOS を別々のパネルに描く。

        SAE の fdLDOSmulti.py と同じ三段構成。該当する XAS の吸収端エネルギーを使い、エネルギー軸を光子エネルギーに変換する。

        Args:
            readers: 三つのサイトに対応する年別 SD リーダー。
            labels: 各リーダーに対応するラベルの並び。
            output: 保存先ファイルのパス。拡張子で出力形式を指定する。
            edge_energy: 吸収端エネルギー（eV）。
            fermi_energy: エネルギー軸の基準に対応するフェルミエネルギー（eV）。
            orbital: 対象の軌道名。
            emin: 省略可能なエネルギー軸の下限。
            emax: 省略可能なエネルギー軸の上限。

        Returns:
            pathlib.Path: 保存したファイルのパス。

        Raises:
            ValueError: リーダーまたはラベルが3件でない場合。
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
        """三つのサイトの LDOS を光子エネルギー軸上に並べた図を組み立てる。"""
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
        """独立した三つの FDMNES 計算の p-LDOS を比較する。

        SAE の fdMulti_3.py に従い、各計算の軸を独立に移動してその計算のフェルミ準位をゼロに揃える。

        Args:
            readers: 各計算に対応する三つの SD リーダー。
            fermi_energies: 対応する三つの FdmTxt から取得した、SD 軸と同じ基準のフェルミエネルギー。
            labels: 各リーダーに対応するラベルの並び。
            output: 保存先ファイルのパス。拡張子で出力形式を指定する。
            orbital: 対象の軌道名。
            emin: 省略可能なエネルギー軸の下限。
            emax: 省略可能なエネルギー軸の上限。
            density_max: 状態密度軸の上限。
            extra_outputs: 同じ図を追加保存するパスの並び。

        Returns:
            pathlib.Path: 保存したファイルのパス。

        Raises:
            ValueError: 入力が3件でないか、軸範囲が不正な場合。
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
        """SAE の縦長 DOS 図を描き、指定があれば最下段に XAS を配置する。

        Args:
            reader: 状態密度データを取得する SD リーダー。
            output: 保存先ファイルのパス。拡張子で出力形式を指定する。
            groups: 下から上へ並べる軌道名のグループ。全状態密度の段は ("total",)。
            spins: 各グループ内で下から上へ並べるスピンの順序。
            spin_labels: スピン番号に対応するラベルの接尾辞。
            projected: True の場合は個々の軌道射影を描く。
            integrated: 積分値を描く指定。
            xas: 吸収パネルに渡すエネルギー、強度、ラベルの組の並び。
            shift: SD にのみ加えるエネルギー移動量（eV）。
            fermi_position: 表示に用いる基準でのフェルミ準位（eV）。縦線の位置に使う。
            xlabel: エネルギー軸のラベル。
            limits: エネルギー軸の下限と上限。None の箇所は SD の範囲を使う。
            density_max: 状態密度軸の上限。
            orbital_max: 軌道群名ごとの状態密度の上限。省略可能。
            xas_max: XAS パネルの吸収強度の上限。
            label: 状態密度曲線に付けるサイト名または試料名。
            extra_formats: 同じ図を PDF・EPS・PNG でも保存する指定。
            show: 保存後に描画バックエンドで図を表示する指定。
            shade_occupied: 表示するフェルミ準位より下の LDOS を塗る指定。

        Returns:
            pathlib.Path: 主図の保存先。

        Raises:
            ValueError: DOS パネルが空、または磁気副準位ごとの射影に積分が指定された場合。
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
