# Rebuild v6 progress

- Added `ReadAthenaNor` in `read_athena_nor.py`, independently reading Athena normalized XAFS data.
- Restored `FDplot_XASs` `-o/--obs` to its original meaning: observed-data overlay.
- Added a separate `--output` option for the output PDF.
- Added regression tests for Athena reading and observed-data plotting.
- Added shebang and module docstring to all distributed Python modules.
- Updated Japanese development history to explicitly distinguish the established research use of SAE from the interruption of its development.
- This release does not certify the full set of 28 commands.
- Rewrote `ReadFdmInp` with explicit branches, Google-style method docstrings and explanatory comments.
- Existing modules still require further method-level docstring and one-line-statement cleanup.
