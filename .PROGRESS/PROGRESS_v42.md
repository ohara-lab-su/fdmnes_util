# rebuild v42 — source-level repairs

- Inspected the actual v41 module tree: no Python module filename starts with `read_` or `write_`; no class or function definition begins with `Read` or `Write`. SAE's original historical comments still contain those names and must not be rewritten because they document the original API.
- Rewrote `fdm_xyz.py`: removed the stale `WriteFdmXyz` class description, added the confirmed original SAE authorship and dates, explicit XYZ serialization, Google-style documentation and input validation.
- Rewrote `structure_conversion.py`: removed machine-generated generic docstrings and compressed statements; documented the relationship to the SAE `FDvasp2fdm.py` source, retained the external `vasp_util` reader, and separated intermediate values for readability.
- Added three tests for XYZ output and malformed coordinate data.
- Test result: 86 passed, 4 skipped (`PYTHONPATH=src pytest -q`).

## Still outstanding

- Review remaining classes and scripts for misleading, machine-generated docstrings and condensed code.
- Compare all SAE original file headers with their actual descendants, not merely approximate source relationships.
- Reconstruct all remaining command options, numerical behavior and plot layouts. Presence of 28 scripts is not full reproduction.
- Black was not run; it is not installed in this environment.
