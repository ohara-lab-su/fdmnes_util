#!/usr/bin/env python3
"""``*_sdN.txt`` と対応する XAS から平均済みの数値配列を受け取り、図を保存する。

PlotFdmAverage は軌道群と任意の生・畳み込み XAS を別のパネルに描く。同じ図を ``*.pdf``・``*.eps``・``*.png`` に保存できる。

SAE の `sae/commands/fdPDOS_XAS_av.py` と同じ縦長配置で軌道群を描き、必要に応じて XAS パネルを加える。
"""

from . import _PlotFigure


class PlotFdmAverage(_PlotFigure):
    """``*_sdN.txt`` と XAS 出力から平均済みの数値配列を受け取り、複合図を保存する。"""
    def plot(
        self,
        orbital_data,
        output,
        *,
        xas_data=None,
        raw_xas_data=None,
        emin=None,
        emax=None,
        dmax=None,
        ymax=None,
        energy_offset=0.0,
        orbital_groups=None,
        fermi_position=None,
        xlabel="Photon Energy [eV]",
        extra_formats=False,
        show=False,
    ):
        """軌道射影と任意の XAS を縦に並べた図を保存する。

        Args:
            orbital_data: 軌道ラベル、エネルギー、状態密度の組の並び。
            output: 保存先ファイルのパス。拡張子で出力形式を指定する。
            xas_data: 任意の畳み込み XAS のエネルギーと吸収強度。
            raw_xas_data: 任意の生 XAS のエネルギーと吸収強度。
            emin: 省略可能なエネルギー軸の下限。
            emax: 省略可能なエネルギー軸の上限。
            dmax: 省略可能な状態密度の上限。
            ymax: 省略可能な吸収強度の上限。
            energy_offset: 全曲線のエネルギー軸に加える値（eV）。
            orbital_groups: 軌道名のグループの並び。各グループを一段に描く。
            fermi_position: 表示に用いる基準でのフェルミ準位（eV）。縦線の位置に使う。
            xlabel: エネルギー軸のラベル。
            extra_formats: 同じ図を PDF・EPS・PNG でも保存する指定。
            show: 保存後に描画バックエンドで図を表示する指定。

        Returns:
            pathlib.Path: 保存したファイルのパス。

        Raises:
            ValueError: 軌道データが空の場合。
        """
        if raw_xas_data is not None and xas_data is None:
            raise ValueError("Raw XAS overlay requires convolved XAS")

        if not orbital_data:
            raise ValueError("At least one orbital is required")

        if dmax is not None:
            if dmax <= 0:
                raise ValueError("dmax must be positive")

        if ymax is not None:
            if ymax <= 0:
                raise ValueError("ymax must be positive")

        import numpy as np

        if not np.isfinite(energy_offset):
            raise ValueError("energy_offset must be finite")

        import matplotlib.pyplot as plt

        # The original SAE figure groups orbital curves into three panels.
        # Keep the ungrouped behavior for callers that do not select a mode.
        panels = []
        if orbital_groups is None:
            for curve in orbital_data:
                panels.append([curve])
        else:
            used_orbitals = set()
            for group in orbital_groups:
                panel_curves = []
                for orbital in group:
                    if orbital in used_orbitals:
                        raise ValueError("Orbital groups must not overlap")
                    used_orbitals.add(orbital)
                    for curve in orbital_data:
                        label = curve[0]
                        if label.endswith("-" + orbital):
                            panel_curves.append(curve)
                if panel_curves:
                    panels.append(panel_curves)
            if not panels:
                raise ValueError("No orbital data match the selected groups")

        panel_count = len(panels)
        if xas_data is not None:
            panel_count += 1

        with plt.rc_context():
            plt.rcParams["font.family"] = "Times New Roman"
            # ラベル等のフォントサイズ
            plt.rcParams["font.size"] = 15
            # レジェンドのフォントサイズ
            plt.rcParams["legend.fontsize"] = 10
            # 軸の太さを設定。目盛りは変わらない
            plt.rcParams["axes.linewidth"] = 1.4
            figure = plt.figure(figsize=(7.0, 9.89))
            orgx = 0.17
            orgy = 0.08
            off = 0.016
            xsize = 0.75
            ysize0 = 0.81
            ysize = ysize0 / panel_count
            num = 0
            if xas_data is not None:
                plt.axes([orgx, orgy, xsize, ysize])
                engx, xas = xas_data
                plt.plot(
                    np.asarray(engx) + energy_offset,
                    xas,
                    linewidth=2,
                    color="black",
                    label="XAS (with broadening)",
                )
                if raw_xas_data is not None:
                    eng_p, dos_p = raw_xas_data
                    color = plt.cm.prism((num + 1) * 10)
                    plt.plot(
                        np.asarray(eng_p) + energy_offset,
                        dos_p,
                        linewidth=1,
                        color=color,
                        label="XAS",
                    )
                plt.ticklabel_format(axis="x", useOffset=False)
                if fermi_position is not None:
                    plt.axvline(x=fermi_position, color="black", linewidth=1)
                plt.xlim(xmax=emax, xmin=emin)
                plt.ylim(ymin=0, ymax=ymax)
                leg = plt.legend(loc="lower right")
                leg.get_frame().set_alpha(0.5)
                plt.xlabel(xlabel)
                plt.ylabel("Absorption [arb. unit]")
                orgy = orgy + ysize + off
            for index, panel_curves in enumerate(reversed(panels)):
                plt.axes([orgx, orgy, xsize, ysize])
                for label, energy, density in panel_curves:
                    num += 1
                    color = plt.cm.prism((num + 1) * 10)
                    plt.plot(
                        np.asarray(energy) + energy_offset,
                        density,
                        linewidth=2,
                        color=color,
                        label=label,
                    )
                plt.ticklabel_format(axis="x", useOffset=False)
                if fermi_position is not None:
                    plt.axvline(x=fermi_position, color="black", linewidth=1)
                plt.xlim(xmax=emax, xmin=emin)
                plt.ylim(ymin=0, ymax=dmax)
                leg = plt.legend(loc="upper right")
                leg.get_frame().set_alpha(0.5)
                if index == min(1, len(panels) - 1):
                    plt.ylabel("DOS [state/eV]")
                if index == 0 and xas_data is None:
                    plt.xlabel(xlabel)
                else:
                    plt.xticks([])
                orgy = orgy + ysize + off
            return self._save_figure(figure, output, extra_formats=extra_formats, show=show)
