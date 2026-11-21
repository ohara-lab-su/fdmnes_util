# rebuild v27 — SD format selector refactoring

## Changes

- Replaced the lowercase `fdm_sd()` selector function with the `FdmSd` class in `fdm_sd.py`.
- The selector explicitly accepts only the 2016 and 2020 SD layouts. It delegates parsing to `FdmSd2016` and `FdmSd2020` using `select_reader()`.
- Updated all editable scripts and tests that used the old function. No compatibility alias remains.
- Added three tests covering the year-specific dispatch, spin/weight argument handling, and rejection of unverified layouts.
- Preserved the original SAE header comments in the SD selector module.

## Verification

- `PYTHONPATH=src pytest -q --disable-warnings`: 54 passed, 1 skipped.
- Black is not installed in the execution environment; Black compliance is not claimed.

## Outstanding

- Six original SAE script names are not yet included in the editable examples.
- Full option/behavior parity of existing examples, provenance audit, detailed Google-style docstrings, and complete formatting review remain incomplete.
