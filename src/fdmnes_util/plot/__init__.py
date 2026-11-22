#!/usr/bin/env python3
"""FDMNES データの描画と、``*.pdf``・``*.eps``・``*.png`` などへの図の保存を扱う。

各描画クラスは上位処理から数値配列やリーダーを受け取る。ここにある共通処理は Matplotlib の図を保存・表示し、終了時に閉じる。
"""
from pathlib import Path


class _PlotFigure:
    """Matplotlib の図を ``*.pdf``・``*.eps``・``*.png`` などに保存し、表示と終了を管理する。"""
    @staticmethod
    def _save_figure(
        figure,
        output,
        *,
        extra_formats=False,
        extra_outputs=(),
        show=False,
    ):
        """図を保存し、必要に応じて表示して描画リソースを解放する。

        Args:
            figure: 保存する Matplotlib の図。
            output: 保存先ファイルのパス。拡張子で出力形式を指定する。
            extra_formats: 同じ図を PDF・EPS・PNG でも保存する指定。
            extra_outputs: 同じ図を追加保存するパスの並び。
            show: 保存後に描画バックエンドで図を表示する指定。

        Returns:
            Path: 保存したファイルのパス。
        """
        import matplotlib.pyplot as plt

        path = Path(output)
        try:
            figure.savefig(path)
            if extra_formats:
                for suffix in (".pdf", ".eps", ".png"):
                    extra = path.with_suffix(suffix)
                    if extra != path:
                        figure.savefig(extra)
            for extra in extra_outputs:
                figure.savefig(extra)
            if show:
                plt.show()
            return path
        finally:
            plt.close(figure)
