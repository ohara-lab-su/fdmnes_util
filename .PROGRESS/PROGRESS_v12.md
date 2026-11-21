# rebuild v12 — progress

- Added editable `scripts/fdXAS_specified.py` as the fifteenth installed example.
- Moved the original Fermi-relative energy subtraction into `AnalyzeFdmXas.fermi_relative_convolution()`.
- Kept reading in `ReadFdmTxt` / `ReadFdmConv` and drawing in `PlotFdmXas`.
- Added Google-style docstrings to the two XAS file readers and new example.
- `fdmnes_util install script` continues to install samples via `pyproject.toml` package data.
- Original example's font, axes layout, and interactive `plt.show()` are not yet reproduced; the CLI is partial.
- 2016 and 2020 readers remain separate; 2022 compatibility is not assumed.
