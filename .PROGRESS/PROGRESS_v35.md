# Rebuild v35

- Added editable `scripts/FDfdm2vasp.py`, based on the SAE command.
- Added `FdmInp.get_crystal_atoms()` and `_get_crystal_lines()` to keep FDMNES input parsing inside its file class.
- Crystal parameters and fractional coordinates are converted to an ASE Atoms structure; ASE writes POSCAR. The external `vasp_util` remains the POSCAR reader for the reverse conversion.
- Molecular input is not supported; SAE explicitly documented a molecular unit-cell scaling issue.
- Added three tests for parsing, absent structure, and POSCAR output (ASE-dependent).
- All 28 original command names are not yet represented; original options and numerical behavior remain incomplete.
