# rebuild v37

## Implemented

- Extended the editable `scripts/fdPDOS_XAS_av.py` example with `--raw-xas-files`.
- Used `FdmTxt` for non-convolved XAS and `FdmConv` for convolved XAS. Each family is averaged independently through `AnalyzeFdmAverage` and therefore retains its own energy grid.
- Extended `PlotFdmAverage.plot()` with `raw_xas_data` to overlay the unbroadened average on the broadened average, following the intent of the SAE `--broad` mode.
- Added checks for missing paired convolved files and mismatched raw-XAS file counts.
- Added two plot regression tests, including differing raw and convolved energy grids.

## Verification

`PYTHONPATH=src pytest -q`: **74 passed, 4 skipped**.

## Limitations

The original SAE `--broad` option used fixed project paths and handled energy offsets using input and XAS metadata. The new editable example accepts explicit file paths, but its energy-reference conversion is not yet equivalent to SAE. The original orbital grouping and all plotting layout details are also pending. This is not a claim of full reproduction.

The project-wide docstring, original-header, PEP 8 and Black audit is also incomplete. Black was not executed.
