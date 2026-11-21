#!/usr/bin/env python3
"""Save figures and optionally display them using the active Matplotlib backend."""

from pathlib import Path


def save_figure(figure, output, *, extra_formats=False, show=False):
    """Save a figure, optionally display it, and release its resources.

    Args:
        figure: Matplotlib figure to save.
        output: Main output path, whose extension selects the format.
        extra_formats: Also save PDF, EPS, and PNG with the same basename.
        show: Open the figure with the currently selected interactive backend.

    Returns:
        Path: Main output path.
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
        if show:
            plt.show()
        return path
    finally:
        plt.close(figure)
