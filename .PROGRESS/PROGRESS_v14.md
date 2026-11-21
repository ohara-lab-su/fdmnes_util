# rebuild v14 — FDvasp2fdm input generation

- Added `WriteFdmInp` (`write_fdm_inp.py`) as a file-specific writer for the full calculation input `read_pdb.inp`.
- Reproduced the keyword sequence, defaults, and structural section of SAE `FDvasp2fdm.py` `write_fdmnes_inp()` using the original source in `sae.zip`.
- Updated editable `scripts/FDvasp2fdm.py` to write both `POSCAR.fdmnes` (or the requested output) and `read_pdb.inp`.
- POSCAR interpretation remains delegated to the external `vasp_util.vasp_poscar.VaspPoscar` module.
- Added two tests for complete input and molecule mode.
- Remaining: full equivalence of 28 original scripts, VASP output API, year-specific real-data coverage.
