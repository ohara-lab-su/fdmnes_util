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

The newly added `FDplot_XASs` plots convolved spectra for explicitly selected absorbing sites. The observed-spectrum overlay and Fermi-referenced axis have been added, but equivalence with every original command-line option is not yet established.

## References

- [SAE (Structural Analysis Environment)](https://github.com/ohara-lab-su/sae)
- [Ohara Lab public software](https://ohara-lab-su.github.io/)

## Coding conventions

Python modules include shebangs and docstrings. Class and public-method documentation follows Google style. Readability takes precedence over one-line expressions and compressed control flow.

## Plotting package

Plotting classes live in `fdmnes_util.plot`, separately from command-line entry points. `FDplot_XAS_LDOS` produces a stacked XAS and site-resolved LDOS figure. Select the verified SD layout explicitly with `--year 2016` or `--year 2020`.

## Rebuilding `fdLDOS0_specified`

The command retains the original `--emin`, `--emax`, and `--dmax` options and plots the p-orbital LDOS. It reads the calculation prefix from `Filout` in the input file rather than using the old hard-coded research directory. The 2016 and 2020 SD readers remain separate, and `PlotFdmDos` handles the figure.

```console
python fdLDOS0_specified.py -i read_pdb.inp --year 2020 --emin -10 --emax 20 --dmax 3
```

The command writes EPS, PDF, and PNG figures; unlike the old script, it does not open an interactive plot window. The 2022 layout is not treated as identical to the 2020 layout without supporting output files.

## Installing editable example scripts

The scripts in this project are editable examples of how to use the class library. Install the Python package, change to the directory where you want to work, and run:

```console
fdmnes_util install script
```

This copies the packaged Python scripts into your current directory. You can modify them for your own experiments. Existing files are left untouched; use `--force` only if you intentionally want to overwrite them. Use `--directory` to specify another destination.

```console
fdmnes_util install script --directory ./analysis
fdmnes_util install script --force
```

The single source of the example scripts is the repository's top-level `scripts/` directory. Scripts are bundled into the installed package at build time. The class library owns file-format parsing, numerical analysis, and plotting; the examples demonstrate those classes in readable Python code. Currently 14 of the 28 historical SAE script names have partial implementations.

The package build and editable sample installation are configured in `pyproject.toml`; no `setup.py` is used.


The editable `fdXAS_specified.py` example now uses a separate analysis method for Fermi-relative energy and a plotting class for rendering.

## VASP integration

POSCAR parsing is delegated to the separately installed `vasp_util` package. The editable `FDvasp2fdm.py` example uses `ReadVaspPoscar` and `WriteFdmStructure` to produce the FDMNES structure section. The original SAE calculation-input template is not yet reproduced. Writing POSCAR from FDMNES requires confirmation of the appropriate public `vasp_util` API.
