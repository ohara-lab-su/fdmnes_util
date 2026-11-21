# Progress v28

- Added editable `scripts/fdPDOS_XAS_av.py` based on the SAE source.
- Added `AnalyzeFdmAverage` for pointwise averaging with explicit energy-grid checks.
- Added `PlotFdmAverage` for a stacked orbital plot.
- Added two regression tests for averaging and mismatched energy grids.
- **Partial reconstruction only:** SAE's original optional XAS averaging, Fermi/photoenergy shifts, orbital grouping, and output-format options are not yet exposed by the sample. The plotting class already accepts an XAS panel.
- The new sample retains the original source history but does not claim full fidelity.
