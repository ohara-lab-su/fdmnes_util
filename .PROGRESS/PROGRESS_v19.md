# v19 changes

- Added `Xyz` class for standard XYZ input, separate from FDMNES file formats.
- Added `FdmStructure.render_xyz_molecule()` to reproduce SAE molecular coordinate formatting.
- Added editable `scripts/FDxyz2fdm.py`, included automatically by the existing `pyproject.toml` wildcard and `fdmnes_util install script`.
- Added two XYZ conversion regression tests.
- **Not complete:** Original SAE `FDxyz2fdm.py` also supports OpenMX MD input and writes a full `read_pdb.inp` through `AseInputOperations`. Those features are not reproduced here.
- **Not complete:** Full project-wide docstring/comment/style review and 28-script parity.
