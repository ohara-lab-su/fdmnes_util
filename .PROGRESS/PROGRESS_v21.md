# Rebuild v21

- Added `Cif` in `cif.py`, using ASE for CIF parsing, and editable `scripts/FDcif2fdm.py`.
- Preserved the available SAE command header comments and documented that the original script is explicitly marked `bug version` and **does not** implement the conversion.
- The new example provides an extension, not a claim of exact behavioral reproduction.
- `fdmnes_util install script` remains the sole example installation command, configured through `pyproject.toml`.
- Other outstanding issues (full 28-script parity, documentation quality, PEP 8/Black audit, source headers) remain open.
