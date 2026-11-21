# Rebuild status

Clean tree. **No SAE classes copied wholesale**, no old compatibility package, `reference/`, duplicate reader generations, or historic intermediate progress files. Year-specific readers exist as distinct classes.

Implemented: input tags, fdmfile job list, 2016/2020 BAV dispatch, 2016/2020 SD readers, XAS/conv readers, derived photoenergy and XYZ writers, plot classes, result-file management; eleven *partial* thin CLI routes.

Unfinished: full behavior of 28 original commands (including combined XAS+LDOS/PDOS, old CLI options and average modes), POSCAR output API through vasp_util, verification for 2022 actual SD outputs, full cell-structure conversion, full BAV sections, 2016 real-world fixture. No assumption that the 2022 layout equals the 2020 layout.

Do not claim the named v3 modules implement every original SAE method. Do not delete user originals while replacing project tree.

Entrypoints exist for 11 partially ported names only. The other 17 are explicitly unimplemented.

## Checks performed on this snapshot

- `pytest -q tests`: 19 passed (real SAE Fe 2020 fixtures, synthetic 2016 SD layout, end-to-end thin commands).
- `python -m pip wheel --no-deps --no-build-isolation .`: wheel built successfully.
- Manual ZIP CRC check: passed.
- 2022 separate format remains unverified; the format dispatcher refuses it.

## Outstanding priority

1. Every original script option and analysis/plot branch must be mapped to a tested class method; 17 scripts are not implemented, and 11 are partial.
2. `ReadFdmInp` presently covers keyword/tag extraction but not all original Crystal/coordinate features.
3. Year-specific BAV readers cover key fields but not every section of SAE's original parsers.
4. 2016 tests use reconstructed header-layout fixtures; there is no original 2016 output sample in the supplied SAE archive.
5. VASP writing must use an actual confirmed `vasp_util` API; no writer is fabricated.

## v4 update

- Rewrote Japanese README against the style and explanatory structure of the Ohara Lab public website; English README follows the Japanese sections.
- Added `AnalyzeFdmXas.site_spectra` for selected absorbing-site outputs and `PlotFdmXas.plot_sites` for two-panel site visualization.
- Added the partial `FDplot_XASs` command. The command explicitly rejects unverified Fermi-axis behavior and does not claim the original experimental-overlay option.
- This is a partial implementation; it does not change the 2016/2020 format readers or claim support for 2022.
