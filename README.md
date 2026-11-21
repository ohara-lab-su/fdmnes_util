# fdmnes_util

A Python class library for reading and analyzing FDMNES input and output files.

FDMNES produces different types of files for calculation settings, calculation logs, XANES spectra, site- and orbital-resolved density of states (SD), and convolved spectra. This package assigns each file format its own reader. Numerical analysis and plotting belong to separate classes.

## Development history

The project originated in the FDMNES tools of [Structural Analysis Environment (SAE)](https://github.com/ohara-lab-su/sae). Development began around the same period as the early pyFDMNES project, initially as scripts written to support XANES calculations and data analysis. The scripts gradually became part of SAE, which grew into a broader structural-analysis environment. Development of the FDMNES tools was later interrupted.

Rather than copying SAE into another package, this project reorganizes its FDMNES input/output functionality around individual file formats. Analysis and plotting logic originally embedded in `FD*` / `fd*` scripts is moved into reusable classes. Historical references to SAE in SPring-8 BL14B2 user reports will be cited after their exact bibliographic details have been verified. A research paper using FDMNES does not necessarily mention this auxiliary software.

## Classes

| File format | Class | Purpose |
| --- | --- | --- |
| `*.inp` | `ReadFdmInp` | Calculation parameters and structural information |
| `fdmfile.txt` | `ReadFdmfile` / `WriteFdmfile` | Lists of calculation input files |
| `*_bav.txt` | `ReadFdmBav2016` / `ReadFdmBav2020` | Calculation logs |
| `*_sd*.txt` | `ReadFdmSd2016` / `ReadFdmSd2020` | Orbital- and site-resolved DOS |
| `*.txt` | `ReadFdmTxt` | XANES |
| `*_conv.txt` | `ReadFdmConv` | Convolved XANES |

Python module names follow snake_case, so `ReadFdmSd2016` is defined in `read_fdm_sd_2016.py`. The 2016 and 2020 file layouts have separate readers. The 2022 file layout has not yet been verified, and is not automatically treated as the 2020 format.

`AnalyzeFdmXas` and `AnalyzeFdmLog` implement numerical processing. `PlotFdmXas` and `PlotFdmDos` handle visualization. The command scripts call these classes rather than duplicating their algorithms. VASP POSCAR handling is delegated to the separately installed `vasp_util` module rather than copied into this package.

## Example

```python
from fdmnes_util.read_fdm_sd_2020 import ReadFdmSd2020

sd = ReadFdmSd2020("Fe_sd0.txt")
energy = sd.get_eng()
d_dos = sd.get_ldos("d")
```

## Rebuilding the original scripts

The full scope consists of all 28 `FD*` / `fd*` commands from SAE. The goal is to reproduce their functionality using the file readers, analysis classes, and plotting classes, not merely to preserve command names. Current coverage and unverified command options are recorded in [COMMAND_AUDIT.md](COMMAND_AUDIT.md). Full equivalence has not yet been achieved.

The newly added `FDplot_XASs` plots convolved spectra for explicitly selected absorbing sites. Overlaying observed spectra and converting to a Fermi-referenced axis are not yet supported.

## References

- [SAE (Structural Analysis Environment)](https://github.com/ohara-lab-su/sae)
- [Ohara Lab public software](https://ohara-lab-su.github.io/)

## Coding conventions

Python modules include shebangs and docstrings. Class and public-method documentation follows Google style. Readability takes precedence over one-line expressions and compressed control flow.

## Plotting package

Plotting classes live in `fdmnes_util.plot`, separately from command-line entry points. `FDplot_XAS_LDOS` produces a stacked XAS and site-resolved LDOS figure. Select the verified SD layout explicitly with `--year 2016` or `--year 2020`.
