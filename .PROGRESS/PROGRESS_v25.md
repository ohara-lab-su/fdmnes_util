# Rebuild v25 progress

- Added EPS/PDF/PNG batch export to `PlotFdmDos.save_multiple_formats()` for the SAE `fdLDOSmulti.py` example.
- Added `--all-formats` to the editable `scripts/fdLDOSmulti.py` while preserving the existing single-output behavior.
- Added regression tests for multi-format export and invalid formats.
- The original SAE source is available in `sae(1).zip`; the remaining 28-script reconstruction and full PEP 8/Black/docstring audit are not complete.
- `fdmnes_util install script` and `pyproject.toml` packaging remain unchanged.
