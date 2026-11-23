# fdmnes_util

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/ohara-lab-su/fdmnes_util/blob/main/README.md)
[![ja](https://img.shields.io/badge/lang-ja-yellow.svg)](https://github.com/ohara-lab-su/fdmnes_util/blob/main/README.ja.md)

[![GitHub](https://img.shields.io/badge/GitHub-ohara--lab--su%2Ffdmnes_util-181717?logo=github)](https://github.com/ohara-lab-su/fdmnes_util/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Documentation-222222?logo=githubpages&logoColor=white)](https://ohara-lab-su.github.io/fdmnes_util/)
[![Ohara Lab](https://img.shields.io/badge/Ohara%20Lab-Home-4B5563?logo=homeassistant&logoColor=white)](https://ohara-lab-su.github.io/)

A Python class library for reading and analyzing FDMNES input and output files.

FDMNES produces different types of files for calculation settings, calculation logs, XANES spectra, site- and orbital-resolved density of states (SD), and convolved spectra. This package groups file operations by format, including reading and writing where supported. Numerical analysis and plotting belong to separate classes.

## Development history

`fdmnes_util` is based on the FDMNES-related programs I developed around 2014 for [Structural Analysis Environment (SAE)](https://github.com/ohara-lab-su/sae). At the time, I added functions to SAE whenever I needed them for XANES calculations and analysis. The work on SAE was also described in SPring-8 publications, while the programs themselves were shared directly with colleagues and other interested users. This was before I started using Git.

At SPring-8 BL14B2, I was also involved in introducing FDMNES to XAFS users through training workshops and related activities. I later transferred from BL14B2 to JASRI's Controls and Computing Division, and development of the FDMNES tools in SAE stopped. I continued to take part in FDMNES workshops, however. Some materials are still available: the [2016 FDMNES hands-on session (PDF, Japanese)](https://support.spring8.or.jp/new/assets/materials/190228_4.nakada_160128.pdf), the [2019 workshop materials](https://support.spring8.or.jp/new/event-materials.html), and the [2019 FDMNES hands-on session (PDF, Japanese)](https://support.spring8.or.jp/assets/materials/190228_5.nakada.pdf).

Recently, I needed to use FDMNES again and dug out these programs from more than ten years ago. I thought it would be worth trying them again, so I have been getting them to work with a current Python environment. Along the way, I am reorganizing the input/output classes and moving the analysis and plotting functions from SAE's `FD*` / `fd*` scripts into the library.

There are now other libraries, including [pyFDMNES](https://github.com/tinaw/pyFDMNES). For now, though, I am not particularly interested in building a wrapper to manage the entire FDMNES calculation workflow. My priority is to restore the analysis functions I used before, then revisit the current FDMNES manual and add functions as they become useful for my research.
## Classes

Classes are organized by file format, with reading and writing operations for a given format handled by the same class where needed. Separate classes are used when the format differs between FDMNES versions.

| File | Class | Main contents |
| --- | --- | --- |
| `*.inp` | `FdmInp` | Calculation parameters, `Filout`, and crystal information |
| `fdmfile.txt` | `Fdmfile` | List of multiple calculation input files |
| `*_bav.txt` | `FdmBav2016` / `FdmBav2020` | Calculation logs, atomic information, and energies |
| `*_sd*.txt` | `FdmSd2016` / `FdmSd2020` | LDOS, PDOS, TDOS, etc. |
| `*.txt` | `FdmTxt` | XANES spectra |
| `*_conv.txt` | `FdmConv` | Convolved spectra |

Class and module names follow Python naming conventions: for example, `FdmSd2016` is defined in `fdm_sd_2016.py`. The 2016 and 2020 formats have separate classes. The 2022 format will not be assumed to be identical to the 2020 format until actual output files have been compared.

The version-specific BAV readers expose the calculation cluster. Classes such as `AnalyzeFdmXas` and `AnalyzeFdmAverage` handle numerical analysis. Plotting is handled by `PlotFdmXas` and `PlotFdmDos`. **Scripts call these classes rather than duplicating analysis formulas or plotting logic.**
## Class library API

Use these references to call the public classes in `src/fdmnes_util` directly from Python.

- [Handwritten API reference](docs/en/manual_reference.md) for imports, method inputs and return values, and Python examples.
- [Sphinx-generated API](https://ohara-lab-su.github.io/fdmnes_util/en/api/) for source signatures and docstrings.
## Example

This example retrieves the energy axis and d-orbital density of states from an SD file in the 2020 format.

```python
from fdmnes_util.fdm_sd_2020 import FdmSd2020

sd = FdmSd2020("Fe_sd0.txt")
energy = sd.get_eng()
d_dos = sd.get_ldos("d")
```

VASP POSCAR files are handled by importing the separate `vasp_util` package as a Python module. VASP file I/O is not duplicated in this package.
## Installing editable example scripts

The scripts in this library are editable examples intended for users to adapt locally. After installing the Python package, run the following command in the directory where you want to perform your analysis.

```console
fdmnes_util install
fdmnes_util install script
fdmnes_util install FDplot_XAS
fdmnes_util install list
```

`install` and `install script` both copy all scripts to the current directory. `install FDplot_XAS` copies only `FDplot_XAS.py`. `install list` displays one script name and description per line. Use these names without the `.py` extension.

Open `FDplot_XAS.py` for an example of reading XAS files and generating plots with the class library. You can modify the copied scripts to suit your calculation conditions and plotting needs.

Existing scripts with the same names are not overwritten. Specify `--force` only when overwriting them, or `--directory` to change the destination.

```console
fdmnes_util install script --directory ./analysis
fdmnes_util install script --force
```

The editable source scripts are kept in the repository's top-level `scripts/` directory. The `pyproject.toml` configuration includes them in the wheel for installation; `setup.py` is not used. Analysis and plotting algorithms belong in the library itself, while each script provides a concrete usage example.

Editable examples corresponding to all 28 SAE scripts are included. See the command audit for the status of option and output reproduction.

## Running FDMNES calculations

Prepare the FDMNES calculation input by hand first. This example assumes that `Cu_inp.txt` is in the current directory and that the FDMNES executable is available as `fdmnes` on PATH. Copy [FDrun.py](scripts/FDrun.py) into the same directory and pass it the input filename.

```console
fdmnes_util install FDrun
python FDrun.py Cu_inp.txt
```

`FDrun.py` prepares the `fdmfile.txt` that FDMNES needs for a single input. It replaces any existing file with that name. The calculation runs in the current directory, and the input's `Filout` sets the output location and prefix. FDMNES standard output appears on screen and is also saved to `fdmnes-*.log`.

## Generate and run a calculation input from Python

This example uses `FdmInp` to build the structure and calculation settings for face-centered cubic copper and saves them as `Cu_generated.inp`. Pass the saved file to `FdmRun` to launch FDMNES in the same way as for a manually prepared input.

```python
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_run import FdmRun

model = FdmInp.from_text("End\n")
model.set_filout("Cu_generated")
model.set_absorber(1)
model.set_edge("K")
model.set_range(-1.0, 0.2, 2.0)
model.set_radius(3.0)
model.set_structure(
    (3.61, 3.61, 3.61, 90, 90, 90),
    (29, 0.0, 0.0, 0.0),
    (29, 0.5, 0.5, 0.0),
    (29, 0.5, 0.0, 0.5),
    (29, 0.0, 0.5, 0.5),
)
input_file = model.save("Cu_generated.inp")
FdmRun().run(input_file)
```

| Method | Purpose |
| --- | --- |
| `FdmInp.from_text(text)` | Start from input text supplied in Python. The example starts with just the `End` keyword. |
| `FdmInp.from_poscar("POSCAR")` | Read a POSCAR with `vasp_util` and build an FDMNES structure section. |
| `FdmInp(filename, format_year=2026)` | Open a saved input for editing. |
| `set_structure(cell, *atoms)` | Set the crystal cell parameters and the rows of atomic numbers and fractional coordinates. Use `molecule=True` for a molecular structure section. |
| `set_filout(prefix)` / `get_filout()` | Set or read the prefix used for calculation output files. |
| `set_absorber(index)` / `get_absorber()` | Select an absorbing site by its one-based atom row in the structure. Use `get_absorbers()` to read multiple sites. |
| `set_edge(edge)` / `get_edge()` | Set or read the absorption edge, such as K, L₃, or L₂ and L₃ together. |
| `set_range(emin, step, emax)` / `get_range()` | Set or read the photoelectron energy limits and step in eV relative to the Fermi level. |
| `set_radius(radius)` | Set the cluster radius in ångströms. |
| `render_input()` / `save(filename)` | Inspect the current input text or save it to a file. `save()` returns the saved path. |
| `FdmRun.run(input_file)` | Launch FDMNES with the saved input file. |

Use `set_structure()` to build a `Crystal` or `Molecule` section. Set the calculation range and absorption edge with `set_range()` and `set_edge()`. For options without a dedicated method, pass the keyword and its data rows to `set_keyword()` in the format described in the FDMNES manual.

### Run multiple inputs in order

Use Python to choose which inputs to run and in what order. Prepare separate inputs for different materials, crystal structures, or stoichiometries. For example, run Cu, Cu₂O, and CuO in sequence, with a distinct `Filout` in each input.

```python
from fdmnes_util.fdm_run import FdmRun

runner = FdmRun()
for input_file in ("Cu_inp.txt", "Cu2O_inp.txt", "CuO_inp.txt"):
    runner.run(input_file)
```

Python can also generate inputs with different settings for the same material. This example starts from `Cu_inp.txt`, varies the cluster radius, and gives each calculation its own input file and output prefix.

```python
from fdmnes_util.fdm_inp import FdmInp
from fdmnes_util.fdm_run import FdmRun

runner = FdmRun()
for radius in (3.0, 4.0, 5.0):
    model = FdmInp("Cu_inp.txt", format_year=2026)
    prefix = f"Cu_R{radius:g}"
    model.set_filout(prefix)
    model.set_radius(radius)
    input_file = model.save(f"{prefix}.inp")
    runner.run(input_file)
```

For argument details, units, return values, and rules for editing existing inputs, see the API documentation generated from the method docstrings. [Sphinx-generated API](docs/en/api/index.md) · [API reference](docs/en/manual_reference.md)

## Bundled scripts

The bundled scripts show how to use the library for structure conversion, running calculations, analysis, and plotting. They include examples that reproduce operations from SAE's FDMNES scripts.

SAE named its tools by combining a calculation-code prefix with the operation name. The convention was inspired by utilities such as `LAcopy`, distributed with Professor Oguchi's HiLAPW. Similar names across codes made it possible to apply the same habits to different programs, for example when moving from `LAcopy` to `FDcopy`. [SAE naming conventions](https://github.com/ohara-lab-su/sae/blob/main/README.md#basic-conventions)

- **`FD*.py`** are general-purpose commands that can be run as supplied by passing arguments. Examples include `FDrun.py` and `FDplot_XAS.py`.
- **`fd*.py`** are scripts that you can edit to suit your samples, input filenames, or plotting settings. One example is `fdLDOS0_specified.py`.

The earlier utilities were written as shell scripts and similar tools. I moved them to Python and organized input and output, analysis, and plotting as class methods that other programs can reuse. AI can now build this kind of framework quickly. I am maintaining these tools because they are part of the day-to-day calculations and analyses I want to keep using.

You can reuse the underlying methods in your own Python programs. For example, `AnalyzeFdmAverage.average()` averages site-resolved XAS and `PlotFdmXas.plot_composite()` can draw a combined XAS and LDOS figure. Some SAE operations and usage examples are still being refined, and I plan to improve them as I use the library in calculations and analysis.

Run `fdmnes_util install script` to copy all 33 scripts. To copy one script, use its name from the table without the extension, for example `fdmnes_util install FDrun`. Run `fdmnes_util install script list` for a terminal listing of names and descriptions. [Script guide](docs/en/scripts.md)

| Script name | Purpose | Main classes |
| --- | --- | --- |
| [`FDbav2xyz`](scripts/FDbav2xyz.py) | Convert BAV cluster coordinates to XYZ | `FdmBav`, `Xyz` |
| [`FDcif2fdm`](scripts/FDcif2fdm.py) | Convert CIF to an FDMNES structure section | `Cif`, `FdmStructure` |
| [`FDclean`](scripts/FDclean.py) | Delete the outputs of a selected calculation | `FdmInp`, `ResultFileOperations` |
| [`FDconv_e2photoe`](scripts/FDconv_e2photoe.py) | Convert convolved XAS to a photon-energy axis | `AnalyzeFdmXas`, `FdmConv`, `FdmPhotoenergy` |
| [`FDconv_sites`](scripts/FDconv_sites.py) | Prepare a multi-site convolution input with weights and shifts | `FdmInp` |
| [`FDfdm2vasp`](scripts/FDfdm2vasp.py) | Convert the structure in an FDMNES input to POSCAR | `FdmStructure` |
| [`FDgetfermi`](scripts/FDgetfermi.py) | Show the Fermi level and absorption edge | `FdmTxt`, `FdmBav` |
| [`FDmakeCconvAllsite`](scripts/FDmakeCconvAllsite.py) | Prepare per-site convolution jobs and their job list | `FdmInp`, `SiteConvolutionJobPreparer` |
| [`FDmanual_examples`](scripts/FDmanual_examples.py) | Build and run inputs from manual examples or POSCAR | `FdmInp`, `FdmRun` |
| [`FDmove`](scripts/FDmove.py) | Move or rename the outputs of a selected calculation | `FdmInp`, `ResultFileOperations` |
| [`FDpbd2fdm`](scripts/FDpbd2fdm.py) | Convert PDB to an FDMNES structure section | `Pdb`, `FdmStructure` |
| [`FDplot_LDOS`](scripts/FDplot_LDOS.py) | Plot LDOS with optional XAS | `DosPlotWorkflow`, `PlotFdmDos` |
| [`FDplot_PDOS`](scripts/FDplot_PDOS.py) | Plot orbital-resolved PDOS with optional XAS | `DosPlotWorkflow`, `PlotFdmDos` |
| [`FDplot_SCF`](scripts/FDplot_SCF.py) | Plot total energy over SCF cycles | `FdmBav` |
| [`FDplot_SD`](scripts/FDplot_SD.py) | Plot an orbital group or projection from SD output | `FdmSd`, `PlotFdmDos` |
| [`FDplot_XAS`](scripts/FDplot_XAS.py) | Plot raw and convolved XAS with optional measured XAS or LDOS | `FdmTxt`, `FdmConv`, `AnalyzeFdmAverage`, `PlotFdmXas` |
| [`FDplot_XAS_LDOS`](scripts/FDplot_XAS_LDOS.py) | Plot XAS and LDOS in one figure | `FdmTxt`, `FdmConv`, `FdmSd`, `PlotFdmXasLdos` |
| [`FDplot_XASs`](scripts/FDplot_XASs.py) | Compare XAS spectra across sites | `FdmTxt`, `AnalyzeFdmXas`, `PlotFdmXas` |
| [`FDrun`](scripts/FDrun.py) | Run FDMNES with one input or an existing job list | `FdmRun` |
| [`FDvasp2fdm`](scripts/FDvasp2fdm.py) | Create an FDMNES structure section and input from POSCAR | `VaspPoscar`, `FdmStructure`, `FdmInp` |
| [`FDvasp2fdm_BUG`](scripts/FDvasp2fdm_BUG.py) | Historical SAE script with conversion disabled | — |
| [`FDvasp2fdm_NEW_20151125_BUGversion`](scripts/FDvasp2fdm_NEW_20151125_BUGversion.py) | Historical SAE script with conversion disabled | — |
| [`FDxyz2fdm`](scripts/FDxyz2fdm.py) | Convert XYZ to an FDMNES molecular structure section | `Xyz`, `FdmStructure` |
| [`fdExp_comp_XAS`](scripts/fdExp_comp_XAS.py) | Compare calculated XAS with measured XAS from Athena | `FdmTxt`, `FdmConv`, `AthenaNor`, `PlotFdmXas` |
| [`fdLDOS`](scripts/fdLDOS.py) | Plot LDOS for a selected site and orbital | `FdmSd`, `PlotFdmDos` |
| [`fdLDOS0_specified`](scripts/fdLDOS0_specified.py) | Plot p-LDOS using dataset-specific settings | `FdmSd`, `PlotFdmDos` |
| [`fdLDOS_color`](scripts/fdLDOS_color.py) | Plot LDOS with occupied states shaded | `DosPlotWorkflow`, `FdmSd`, `PlotFdmDos` |
| [`fdLDOSmulti`](scripts/fdLDOSmulti.py) | Plot LDOS for three sites in one figure | `FdmTxt`, `FdmSd`, `PlotFdmDos` |
| [`fdMulti_2_XAS+LDOS+EXP`](scripts/fdMulti_2_XAS+LDOS+EXP.py) | Plot calculated and measured XAS alongside p-LDOS | `FdmTxt`, `FdmConv`, `FdmSd`, `AthenaNor`, `PlotFdmXasLdos` |
| [`fdMulti_3`](scripts/fdMulti_3.py) | Compare three calculations aligned at the Fermi level | `FdmTxt`, `FdmSd`, `PlotFdmDos` |
| [`fdPDOS_XAS_av`](scripts/fdPDOS_XAS_av.py) | Plot site-averaged PDOS and XAS | `AnalyzeFdmAverage`, `FdmSd`, `PlotFdmAverage` |
| [`fdXAS`](scripts/fdXAS.py) | Plot convolved XAS | `FdmConv`, `PlotFdmXas` |
| [`fdXAS_specified`](scripts/fdXAS_specified.py) | Plot XAS relative to the Fermi level | `FdmTxt`, `FdmConv`, `AnalyzeFdmXas`, `PlotFdmXas` |

## Rebuilding the original scripts

The target is all 28 `FD*` / `fd*` scripts from SAE. Rather than preserving only their command names, the goal is to reorganize their functionality into file-reading, analysis, and plotting classes and reproduce the same operations.

Not all functions of the 28 scripts have been reproduced yet. Progress and command options that remain unverified are documented in [`COMMAND_AUDIT.md`](.PROGRESS/COMMAND_AUDIT.md).

`FDplot_XASs` reads and plots convolved spectra for multiple absorbing sites. The original `-o` option specifies display of experimental data. Athena `*_obs.txt.nor` files are read using `AthenaNor`. Conversion to a Fermi-level-referenced energy axis is also separated into an analysis class. Compatibility with all options of the original script still needs to be checked; full equivalence has not yet been established.
## References

- [SAE (Structural Analysis Environment)](https://github.com/ohara-lab-su/sae)

## Coding conventions

Python modules include shebangs and docstrings. Class and public-method documentation follows Google style. Readability takes precedence over one-line expressions and compressed control flow.
## Plotting package

Plotting classes live in `fdmnes_util.plot`, separately from command-line entry points. `FDplot_XAS_LDOS` produces a stacked XAS and site-resolved LDOS figure. Select the verified SD layout explicitly with `--year 2016` or `--year 2020`.
## Rebuilding `fdLDOS0_specified`

The command retains the original `--emin`, `--emax`, and `--dmax` options and plots p-orbital LDOS. Rather than fixing the results directory, it uses `Filout` from the input file. Reading is handled by the version-specific `FdmSd2016` or `FdmSd2020` class, and plotting by `PlotFdmDos`.

```console
python fdLDOS0_specified.py -i read_pdb.inp --year 2020 --emin -10 --emax 20 --dmax 3
```

The command outputs EPS, PDF, and PNG files. Unlike the original script, it does not display an interactive plot window. The 2022 format is not processed as the 2020 format because actual output data has not yet been checked.

The `fdXAS_specified.py` example has also been added. Fermi-level-referenced energy conversion from the original SAE script is handled by an analysis class, and plotting uses a class in `plot/`.
## VASP integration

`FDvasp2fdm.py` reads POSCAR with `vasp_util.vasp_poscar.VaspPoscar` and writes the FDMNES structure section with `FdmStructure`. In the reverse direction, `FdmStructure` assembles the crystal or molecular structure for POSCAR output.

```console
fdmnes_util install script
python FDvasp2fdm.py -i POSCAR
```

`FDfdm2vasp.py` uses ASE to write POSCAR from an FDMNES `Crystal` or `Molecule` section. For molecules, `--vacuum` specifies the vacuum padding (10 Å on each side by default).

`FDvasp2fdm.py` creates a structure file and `read_pdb.inp` with calculation parameters from POSCAR. `FdmInp` generates the input file, while `FdmStructure` writes the crystal structure.
## File-based classes

Modules and classes are organized by FDMNES file format, rather than by read/write operations. For example, `FdmInp` in `fdm_inp.py` and `Fdmfile` in `fdmfile.py` handle operations for their respective formats. BAV and SD retain separate 2016 and 2020 classes for their differing formats.
## CIF conversion example

Added `FDcif2fdm.py`. The original SAE script reads CIF but only prints `bug version`; the conversion here is a new extension, not a faithful reconstruction of a working original. It uses ASE through `Cif` and `FdmStructure`.

### Selecting an SD format

Select the verified SD layout explicitly with `FdmSd(..., format_year=2016).select_reader()` or `format_year=2020`. Unverified years are not automatically treated as the 2020 layout.

### Averaging PDOS across calculations (v28)

The editable `fdPDOS_XAS_av.py` example averages orbital PDOS across SD files after validating matching energy grids. The original SAE options for XAS overlay and energy-reference switching remain to be ported.

Added the editable `fdMulti_3.py` example for comparing LDOS from three independent calculations aligned to their respective Fermi levels.

### v37: Averaged XAS overlay

In `fdPDOS_XAS_av.py`, use `--xas-files` for convolved XAS and `--raw-xas-files` for unbroadened XAS to overlay both averaged spectra. Each family is averaged on its own energy grid. SAE energy-reference conversion is not yet reproduced.

### v40: averaged PDOS/XAS energy reference

The editable `fdPDOS_XAS_av.py` example accepts `--input` and `--raw-xas-files` to determine the energy reference from the FDMNES input mode and the raw XAS edge/Fermi metadata. Use `--fermi` for a Fermi-relative axis. `--energy-offset` remains an additional correction.
