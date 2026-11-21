# Rebuild v29

- Extended the editable `fdPDOS_XAS_av.py` example with `--xas-files` to average convolved XAS alongside orbital PDOS.
- Reused `FdmConv` and `AnalyzeFdmAverage`, including exact energy-grid validation, and `PlotFdmAverage`'s existing XAS panel.
- Require matching numbers of SD and convolved XAS files to prevent silent pairing errors.
- Corrected the contradictory audit entry for `fdPDOS_XAS_av.py`.
- Remaining: original script's Fermi/photon energy handling, broadening, spin/orbital group options, header/docstring review and other unfinished commands.
