# Progress v8

- Added `commands/fd_ldos0_specified.py`, targeting original `fdLDOS0_specified.py`.
- Preserved the original `--emin`, `--emax`, `--dmax` flags and p-orbital `*_sd0.txt` density selection. Default output formats are EPS, PDF, PNG.
- Removed the source script's hard-coded Pd6 input/output path; resolve the calculation prefix from the FDMNES input `Filout`. A year must be explicit (2016 or 2020); 2022 remains unverified.
- Added `PlotFdmDos.plot_single_orbital()`; no plotting or numerical SD parsing is performed in the CLI.
- Expanded `ReadFdmSd2020` into readable statements, full Google-style method documentation, and explicit column handling; retained its behavior, including existing API methods.
- The original script showed an interactive figure; the new CLI writes files but does not open a GUI figure. Other original script options remain subject to full coverage review.
- Do not count partial scripts as fully equivalent to SAE.
