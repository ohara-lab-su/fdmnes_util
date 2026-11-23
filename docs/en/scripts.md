# Script guide

Run `python <filename> --help` for each example's arguments. Filenames are case-sensitive.

## How SAE used these scripts

SAE used uppercase `FD*.py` names for general-purpose commands that can be run as supplied by passing arguments. Lowercase `fd*.py` scripts can be edited to suit individual samples or analysis settings. Both are available through `fdmnes_util install script`. SAE itself is unnecessary at runtime. [SAE naming conventions](https://github.com/ohara-lab-su/sae/blob/main/README.md#basic-conventions)

For scripts derived from SAE, the supplied `sae_original.zip` contains the original at `sae/commands/<filename>`. See the [command audit](https://github.com/ohara-lab-su/fdmnes_util/blob/main/.PROGRESS/COMMAND_AUDIT.md) for option differences and the scope of behavioral verification.

## 2026 output and calculation runner

| Script | Purpose | Main classes |
| --- | --- | --- |
| `FDrun.py` | Run FDMNES with one manually prepared input or an existing job list | `FdmRun` |
| `FDmanual_examples.py` | Build and run inputs from manual examples or POSCAR | `FdmInp`, `FdmRun` |
| `FDplot_SD.py` | Plot an orbital group or projection from SD output | `FdmSd`, `PlotFdmDos` |
| `FDplot_SCF.py` | Plot total energy over SCF cycles from BAV output | `FdmBav` |
| `FDconv_sites.py` | Prepare a multi-site convolution input with weights and shifts | `FdmInp` |

```console
python FDrun.py Cu_inp.txt
python FDmanual_examples.py cu --write-only
python FDplot_SD.py Au_sd0.txt --orbital '(3,0)' --nw -o Au_f.pdf
python FDplot_SCF.py Fe_bav.txt --nw -o Fe_scf.pdf
python FDconv_sites.py --site Fe_1.txt 1 0.2 --site Fe_2.txt 1 -0.2 --header --energy-step 0.25 --per-atom
python FDrun.py conv.inp
```

## POSCAR reading and the vasp_util source

The SAE `FDvasp2fdm.py` read POSCAR through ASE and used `AseInputOperations` for FDMNES structure conversion. The script uses the separately installed `vasp_util.vasp_poscar.VaspPoscar` class directly. Its `get_lattice_vectors()`, `get_coords_direct()`, and `get_atom_indices()` methods supply the lattice, fractional positions, and symbols in atom order. These methods are defined in `vasp_util/vasp_poscar.py` in `vasp_util_original.zip`. `FdmStructure` and `FdmInp` produce the FDMNES files. In the reverse direction, `FDfdm2vasp.py` reads the structure from FDMNES input and uses ASE to write POSCAR.

## Choose a composite plot

- `FDplot_XAS.py` focuses on XAS and can add experiment above and LDOS below. `--xas` selects raw XAS only. `--broad` selects convolved XAS only.
- `FDplot_LDOS.py` and `FDplot_PDOS.py` focus on DOS. `--xas` adds convolved XAS at the bottom. `--broad` also overlays raw XAS.
- These three scripts save PDF by default. Use `--pdf` to add EPS and PNG, and `--nw` to suppress GUI display. Check the input and SD layout before running them.
- `FDplot_XAS.py -a 1 2 -w 4` divides the sum for sites 1 and 2 by four. The default divisor is the site count. The selected data determine which averages are written to `*_0.txt`, `*_0_conv.txt`, and `*_0_sd0.txt`.

## Script reference

Run these examples in a working directory containing the scripts from `fdmnes_util install script` and your input data. In the examples, `Fe` is the calculation prefix and `--year 2020` selects the SD layout. The SAE originals in this section are in `sae/commands/` in `sae_original.zip` under the same names. Plotting requires Matplotlib. Reading CIF or PDB and writing POSCAR require ASE. Reading POSCAR requires `vasp_util`. [Installation](usage.md)

### `FDbav2xyz.py`

**Original purpose**
The SAE tool extracts the cluster selected by the calculation radius so it can be inspected in viewers such as VESTA.

**Current inputs and outputs**
Pass the prefix `Fe` or `Fe_bav.txt` to write `Fe.xyz`. With `--std`, the same XYZ data go to stdout.

**Example**

```bash
python FDbav2xyz.py -i Fe
```

**Changes from SAE**
The current version keeps the original ten decimal places for coordinates. With no argument, it looks for `Cu_bav.txt` and then a unique BAV file. Specify the file explicitly when several candidates exist.

### `FDcif2fdm.py`

**Original purpose**
SAE's README describes preparing XANES inputs from CIF. The archived script reads CIF with ASE and ends after printing `bug version`.

**Current inputs and outputs**
The script reads CIF and writes a `Crystal` section to `Fe.fdmnes`. Use `--mol` to write a `Molecule` section.

**Example**

```bash
python FDcif2fdm.py Fe.cif --output Fe.fdmnes
```

**Changes from SAE**
The current version implements structure output. Insert the resulting section into an input containing the calculation settings.

### `FDclean.py`

**Original purpose**
SAE used this to remove generated files for a `Filout` prefix before rerunning a calculation.

**Current inputs and outputs**
The script reads `Filout` from the calculation input, deletes the associated raw and convolved XAS, BAV, SD, and auxiliary logs, and prints their paths. Try the example in a directory containing copies of the outputs.

**Example**

```bash
python FDclean.py -i read_pdb.inp
```

**Changes from SAE**
Cleanup is scoped to the `Filout` directory. With no argument, the script uses the first job in `fdmfile.txt`, or `read_pdb.inp` if the job list is absent.

### `FDconv_e2photoe.py`

**Original purpose**
SAE used this to move convolved spectra from calculations without `Energpho` onto a photon-energy axis for comparison with experiment.

**Current inputs and outputs**
The calculation input, raw XAS header, and convolved result produce a two-column `Fe_conv_photoe.txt`. Inputs already using photon energies raise an error. `--fermi` subtracts the Fermi energy after adding the edge energy.

**Example**

```bash
python FDconv_e2photoe.py -i read_pdb.inp -t Fe.txt -c Fe_conv.txt
```

**Changes from SAE**
The current version pairs the convolution file's own energy grid with its intensities, so the raw and convolved grids can have different lengths.

### `FDfdm2vasp.py`

**Original purpose**
SAE converts the structure embedded in FDMNES input to VASP POSCAR, for example to reuse a hand-edited FDMNES structure.

**Current inputs and outputs**
The script writes a POSCAR from an input containing a `Crystal` or `Molecule` section. The example's `--vacuum 12` adds 12 Å on each side of a molecule. Without `-o`, the output name appends `.vasp` to the input name.

**Example**

```bash
python FDfdm2vasp.py -i read_pdb.inp -o POSCAR --vacuum 12
```

**Changes from SAE**
`FdmInp` interprets the structure and ASE writes the POSCAR. Molecular padding is configurable.

### `FDgetfermi.py`

**Original purpose**
SAE used this to inspect the Fermi and absorption-edge energies when checking or aligning spectra.

**Current inputs and outputs**
The script reads `Fe.txt` and `Fe_bav.txt` and prints the Fermi energy, edge label, and edge energy. Use `-i read_pdb.inp` to take the prefix from the input's `Filout`.

**Example**

```bash
python FDgetfermi.py --name Fe
```

**Changes from SAE**
The edge label comes from a revision-specific BAV reader. `--name` selects result files directly without needing the original calculation input.

### `FDmakeCconvAllsite.py`

**Original purpose**
SAE prepared an FDMNES batch to convolve each absorbing site's spectrum after a multisite run.

**Current inputs and outputs**
The script looks for numbered raw XAS files such as `Fe_1.txt`, then writes `conv_1.inp` and subsequent jobs plus `fdmfile.txt` in the working directory. It replaces any existing job list.

**Example**

```bash
python FDmakeCconvAllsite.py -i read_pdb.inp
```

**Changes from SAE**
The current version retains the original filename ordering and writes paths relative to the jobs' working directory. Run FDMNES to execute the generated jobs.

### `FDmove.py`

**Original purpose**
SAE used this to rename a group of calculation outputs so they could be kept before a rerun.

**Current inputs and outputs**
The example changes the prefix on `Fe.txt`, `Fe_bav.txt`, `Fe_conv.txt`, and `Fe_sd*.txt` to `Fe_saved` and prints the destination paths. With one argument, the source prefix comes from the input's `Filout`.

**Example**

```bash
python FDmove.py Fe Fe_saved
```

**Changes from SAE**
Rename destinations are checked for collisions first. `python FDmove.py -i read_pdb.inp -d archive` moves the results to another directory under their original names.

### `FDpbd2fdm.py`

**Original purpose**
The SAE tool makes the PDB coordinates and lattice explicit in a FDMNES structure section so they can be inspected in the input.

**Current inputs and outputs**
The script reads the PDB atom records and `CRYST1`, writing a `Crystal` or `Molecule` section to `Fe.fdmnes`.

**Example**

```bash
python FDpbd2fdm.py Fe.pdb --output Fe.fdmnes
```

**Changes from SAE**
The filename retains the original spelling `pbd`. The current version uses the package's `Pdb` and `FdmStructure` classes.

### `FDplot_LDOS.py`

**Original purpose**
SAE uses stacked orbital-group LDOS panels to examine a site's DOS, integrals, and XANES together.

**Current inputs and outputs**
With `Filout=Fe`, the example uses `Fe.txt`, `Fe_sd0.txt`, and `Fe_conv.txt` for `--xas`, and writes `LDOS0.pdf`. `--intdos` plots the stored integrals.

**Example**

```bash
python FDplot_LDOS.py -i read_pdb.inp -a 0 --year 2020 --sp --total --intdos --xas --nw
```

**Changes from SAE**
The current script selects the SD layout from its column names. Use `--year` to select it explicitly. Conversion from photon energy to the Fermi-relative axis subtracts both the edge and Fermi energies.

### `FDplot_PDOS.py`

**Original purpose**
SAE resolved orbital groups into individual components, for example to compare `p_z` against the in-plane `p_x` and `p_y`.

**Current inputs and outputs**
With `Filout=Fe`, the calculation input, `Fe.txt`, `Fe_sd0.txt`, and `Fe_conv.txt` produce `PDOS0.pdf`. `--sp` selects s and p and `--spd` adds d.

**Example**

```bash
python FDplot_PDOS.py -i read_pdb.inp -a 0 --year 2020 --sp --xas --nw
```

**Changes from SAE**
The current version supports explicit SD layout selection and `--total` for a total-DOS panel. As in the original, `--intdos` leaves component integrals off the plot.

### `FDplot_XAS.py`

**Original purpose**
SAE used this general-purpose plotter to compare raw and convolved XANES with experiment and LDOS, including averages across absorbing sites.

**Current inputs and outputs**
With `Filout=Fe`, the example reads the calculation input, `Fe.txt`, `Fe_conv.txt`, `Fe_obs.txt.nor`, and `Fe_sd0.txt`, and saves `Fe_XAS.pdf`. `--nw` skips display.

**Example**

```bash
python FDplot_XAS.py -i read_pdb.inp --obs Fe_obs.txt.nor --dos --year 2020 --nw --output Fe_XAS.pdf
```

**Changes from SAE**
Site averaging checks the energy grid within each series. `-a 1 2 -w 4` divides the sum for sites 1 and 2 by four. It writes `Fe_0.txt` and `Fe_0_conv.txt`, and with `--dos`, `Fe_0_sd0.txt`. As in the archived code, `--pdf` adds EPS and PNG.

### `FDplot_XAS_LDOS.py`

**Original purpose**
SAE produced a stacked plot of convolved XAS and one site's orbital-group LDOS for orbital analysis.

**Current inputs and outputs**
With `Filout=Fe`, the calculation input, `Fe.txt`, `Fe_conv.txt`, and `Fe_sd0.txt` produce `XAS_LDOS0.pdf`. Use `--fermi` for a Fermi-relative axis.

**Example**

```bash
python FDplot_XAS_LDOS.py -i read_pdb.inp -a 0
```

**Changes from SAE**
The current version detects the SD format from the column names and draws the available s, p, and d groups. Use `--year` to select a layout explicitly. Orbital-selection aliases `--orbit` and `-l` belong to the original.

### `FDplot_XASs.py`

**Original purpose**
The archived SAE code compares convolved XAS from several absorbing sites and can include experimental curves.

**Current inputs and outputs**
With `Filout=Fe`, the script reads `Fe_N.txt` and `Fe_N_conv.txt` for sites 1 and 2. The example's `--obs` also reads `Fe_N_obs.txt.nor` and saves `Fe_sites.pdf`.

**Example**

```bash
python FDplot_XASs.py -i read_pdb.inp -a 1 2 --obs --output Fe_sites.pdf
```

**Changes from SAE**
As in SAE, `-a` selects the curves, which remain separate and appear in the requested order. The current `--output` option sets the destination.

### `FDvasp2fdm.py`

**Original purpose**
SAE reused a VASP structure to prepare a starting FDMNES input for XANES calculations.

**Current inputs and outputs**
POSCAR provides the structure for `Fe.fdmnes` and the complete sample input `read_pdb.inp` in the working directory. `--mol` selects a molecular section.

**Example**

```bash
python FDvasp2fdm.py -i POSCAR -o Fe.fdmnes
```

**Changes from SAE**
The original reads POSCAR through ASE. The current script gets lattice, positions, and symbols through external `vasp_util` and uses `-o` for the structure-section path.

### `FDvasp2fdm_BUG.py`

**Original purpose**
This earlier attempt replaced ASE with SAE's own POSCAR handling. The archived script disables conversion after a serious defect was found.

**Current inputs and outputs**
The script checks for a candidate POSCAR path, prints `gug version`, and exits. It creates no files.

**Example**

```bash
python FDvasp2fdm_BUG.py -i POSCAR
```

**Changes from SAE**
The current version preserves path checking and the message. Use `FDvasp2fdm.py` for structure conversion.

### `FDvasp2fdm_NEW_20151125_BUGversion.py`

**Original purpose**
This is the separate November 25, 2015 attempt. The archived code retains the conversion work but disables the calls that would run it.

**Current inputs and outputs**
The script checks for a candidate POSCAR path, prints `gug version`, and exits. It creates no files.

**Example**

```bash
python FDvasp2fdm_NEW_20151125_BUGversion.py -i POSCAR
```

**Changes from SAE**
The current package keeps it under its historical filename with conversion disabled.

### `FDxyz2fdm.py`

**Original purpose**
The original uses SAE's OpenMX `ReadMd` to read XYZ-style MD data and generate a FDMNES molecular input.

**Current inputs and outputs**
The current script reads standard XYZ with an atom count, comment, symbols, and Cartesian coordinates, and writes a `Molecule` section to `cluster.fdmnes`.

**Example**

```bash
python FDxyz2fdm.py cluster.xyz --output cluster.fdmnes
```

**Changes from SAE**
The current output is the structure section. To run a calculation, insert it into an input with the desired settings.

### `fdExp_comp_XAS.py`

**Original purpose**
SAE provided this small, editable example to overlay normalized Athena data and calculated XAS.

**Current inputs and outputs**
The convolved result, raw XAS, and Athena `.nor` file produce `Fe_compare.pdf` on a photon-energy axis.

**Example**

```bash
python fdExp_comp_XAS.py -i Fe_conv.txt --txt Fe.txt --experiment Fe_obs.txt.nor --xmin 7100 --xmax 7200 --output Fe_compare.pdf
```

**Changes from SAE**
The current script retains the edge-energy shift and accepts file paths, axis bounds, and an output name. Its default bounds are for Au.

### `fdLDOS.py`

**Original purpose**
SAE provided a minimal example for extracting and plotting LDOS for a site.

**Current inputs and outputs**
The script reads `Filout` from `read_pdb.inp` and plots p-LDOS for site 1 by default. Use `-i` for the calculation input, `-a` for the site index, and `-l` for the orbital angular momentum index. Add `--intdos` to plot the stored integrals.

**Example**

```bash
python fdLDOS.py -i read_pdb.inp -a 0 -l 1 --year 2020 -o Fe_LDOS.pdf
```

**Changes from SAE**
You can also supply an SD file directly. Use `--year` to select the SD layout explicitly and `-o` to set the output path.

### `fdLDOS0_specified.py`

**Original purpose**
The original used Pd6 results to plot p-LDOS with adjustable bounds.

**Current inputs and outputs**
If the calculation input has `Filout=Fe`, the script reads `Fe_sd0.txt` and writes `LDOS.pdf` with the selected bounds. Omitting `--formats` saves EPS, PDF, and PNG.

**Example**

```bash
python fdLDOS0_specified.py -i read_pdb.inp --year 2020 --emin -10 --emax 10 --dmax 5 --formats pdf
```

**Changes from SAE**
With no input argument, the script sums the five Pd6 site spectra and divides by six, as in SAE. With an explicit calculation input, it plots that calculation's `_sd0.txt`.

### `fdLDOS_color.py`

**Original purpose**
This SAE example shades occupied DOS to make states below the Fermi level easier to see.

**Current inputs and outputs**
The script reads SD directly and writes `Fe_occupied.pdf` with the selected orbital group shaded below `--fermi`. The example uses 0 eV on the plotted axis. `--edge-offset` adds a shift to that axis.

**Example**

```bash
python fdLDOS_color.py Fe_sd0.txt --year 2020 --orbital p --fermi 0 --output Fe_occupied.pdf
```

**Changes from SAE**
The calculation-input workflow retains SAE's stacked LDOS, TDOS, and XAS options. For example, `-i read_pdb.inp --p --total --xas --nw` plots p-LDOS, TDOS, and XAS.

### `fdLDOSmulti.py`

**Original purpose**
The original compares Ba and Ti p-LDOS across three sites in `BaTiO3_R3m`.

**Current inputs and outputs**
The script uses `Fe.txt` and `Fe_sd0.txt` through `Fe_sd2.txt` to make a three-site figure. With no output path it saves EPS, PDF, and PNG using the original `LDOSmulti` basename.

**Example**

```bash
python fdLDOSmulti.py --input Fe --year 2020 --orbital p --all-formats
```

**Changes from SAE**
The calculation prefix, orbital, and axis bounds are configurable. The default `BaTiO3_R3m` example uses the original Ba, Ba, and Ti site labels.

### `fdMulti_2_XAS+LDOS+EXP.py`

**Original purpose**
The original compares calculated and measured Cu XAS above a p-LDOS panel to relate spectral features to orbitals.

**Current inputs and outputs**
The convolved spectrum, raw XAS header, SD, and Athena measurement produce the two-panel `Cu_compare.pdf`.

**Example**

```bash
python fdMulti_2_XAS+LDOS+EXP.py --conv Cu_conv.txt --txt Cu.txt --sd Cu_sd0.txt --experiment Cu_obs.txt.nor --year 2020 --output Cu_compare.pdf
```

**Changes from SAE**
The original Cu corrections remain the defaults. `--energy-offset`, `--experiment-scale`, `--experiment-offset`, and the axis bounds can be set explicitly.

### `fdMulti_3.py`

**Original purpose**
The original compares two Pd55 calculations and `FCC/Pd`, aligning each p-LDOS curve to its own Fermi energy.

**Current inputs and outputs**
The script loads the `.txt` and `_sd0.txt` pair for each prefix and saves `Fe_three.eps`, `Fe_three.pdf`, and `Fe_three.png`. `--site` selects another SD index.

**Example**

```bash
python fdMulti_3.py run1/Fe run2/Fe run3/Fe --year 2020 --site 0 --output Fe_three
```

**Changes from SAE**
With no prefixes, the script uses the original Pd calculation paths. The calculation prefixes, orbital, site, and plot bounds are configurable.

### `fdPDOS_XAS_av.py`

**Original purpose**
The original averaged PDOS and XAS from three `R5_fdm_ad_on_*` calculations to compare common features.

**Current inputs and outputs**
The script reads multiple SD files and, optionally, the same number of convolved XAS files. It saves `Fe_average.pdf`. Energy grids must match within each series.

**Example**

```bash
python fdPDOS_XAS_av.py Fe_1_sd0.txt Fe_2_sd0.txt --year 2020 --sp --xas-files Fe_1_conv.txt Fe_2_conv.txt -o Fe_average.pdf
```

**Changes from SAE**
With no SD paths, the script uses the original three calculations. Add `--xas` for convolved XAS and `--broad` to overlay raw XAS. For explicit SD paths, supply the matching `--xas-files` and `--raw-xas-files`. Use `--fermi` for Fermi-relative plots and, when providing explicit paths, supply `--input` to determine the energy reference.

### `fdXAS.py`

**Original purpose**
This is SAE's small standalone convolved XAS example, suitable as a starting point for adapting styles or curves.

**Current inputs and outputs**
The script plots the energy and first absorption column of `Fe_conv.txt` using SAE's layout and marks the Fermi level at 0 eV. Supply the input as a positional argument or with `-i`. If omitted, the script reads `POSCAR_conv.txt` or the only `*_conv.txt` file in the working directory. Without `-o`, it writes `XAS.pdf`.

**Example**

```bash
python fdXAS.py -i Fe_conv.txt -o Fe_XAS.pdf
```

**Changes from SAE**
The current script retains `-i` from SAE and adds `-o` for the output name. `FdmConv` and `PlotFdmXas` handle reading and plotting.

### `fdXAS_specified.py`

**Original purpose**
The original used an Au spectrum and set the axis origin using the Fermi energy from the raw XAS header.

**Current inputs and outputs**
With prefix `Fe`, the script reads `Fe.txt` and `Fe_conv.txt`, subtracts `E_Fermi` from the convolution axis, and writes `Fe_fermi.pdf`.

**Example**

```bash
python fdXAS_specified.py -i Fe -o Fe_fermi.pdf
```

**Changes from SAE**
The current version retains the original Fermi subtraction and accepts a calculation prefix and figure destination.
