# Rebuild v40

- Reconstructed the SAE `fdPDOS_XAS_av.py` energy-reference branches in `AnalyzeFdmAverage.energy_reference()`.
- Added `--input` and `--fermi` to the editable sample. The input file and raw XAS metadata are required to infer the reference. `--energy-offset` remains an additional user-defined correction.
- Fixed the source script defect `eng_off - txt.E_Fermi - txt.E_edge` (no assignment), interpreting photon-to-Fermi conversion as subtracting both terms.
- Added four mode-combination regression tests.
- Remaining: complete original orbital-group layout, source header and docstring audit, Black formatting and complete feature parity for 28 scripts.
