# Rebuild v22

- Added editable `scripts/fdExp_comp_XAS.py` from SAE `sae/commands/fdExp_comp_XAS.py`.
- Added `PlotFdmXas.plot_experiment_comparison()` to separate plotting from the sample script.
- Retained original FDMNES photon-energy transformation `conv.eng + txt.E_edge`.
- Made original hard-coded experimental filenames and axis limits configurable.
- Corrected four stale `COMMAND_AUDIT.md` entries against scripts actually present.
- Still incomplete: full 28-script coverage, exact plot appearance, source-header review, and Black formatting.
