# Progress v36

## SAE historical bug-version scripts

The two original `FDvasp2fdm*BUG*.py` programs have their structure-conversion
calls commented out and print `gug version`. They are **not working converters**.
The editable historical examples preserve this distinction, original header
history, and original command-line arguments. They do not create FDMNES files.
For working conversion, use `FDvasp2fdm.py` and the external `vasp_util`.

All 28 named SAE scripts now have a corresponding sample file, but most remain
partial implementations. Presence does not mean functional equivalence.

The `fdmnes_util install script` command remains the distribution mechanism.
