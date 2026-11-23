# Handwritten API reference

This handwritten reference covers the classes in `src/fdmnes_util` for direct use from Python. Each class lists its import, every public method’s parameters, defaults and return value, and a short example for each class. See the [Sphinx-generated API](api/index.md) for full signatures and docstrings and the [script guide](scripts.md) for command-line examples.

Parameters with `=` have defaults. Parameters after `*` are keyword-only. `__init__` initializes the object. Calling the class returns an instance. `ndarray` is a NumPy array and `Path` is `pathlib.Path`. Replace example filenames with your calculation or measurement files.

## Calculation inputs and batch jobs

### `FdmInp`

`from fdmnes_util.fdm_inp import FdmInp`

Read, inspect, and generate FDMNES calculation inputs.

Input files have no revision line. Use `FdmInp(filename, format_year=2026)` for extended input. The default is 2016. `get_absorbers()` returns site indices, and `get_calculations()` returns (filename, weight, shift, cutoff) records. `FdmInp.write(..., format_year=2026)` accepts `absorber=[1, 2]`, `density_complex=True`, and `lmax_dosout=3`. `FdmInp.write_convolution(filename, calculations, *, output, format_year=2026, header=False, energy_step=None, per_atom=False)` writes a combined convolution input. Each calculation is a (raw XAS path, weight, shift in eV) tuple.

Use `format_year=2026` for the setters and for `get_range()`, `get_edge()`, `get_radius()`, `get_green()`, and `get_spgroup()`.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(filename='read_pdb.inp', *, format_year=2016)` | `filename` Path to the FDMNES input file. | None. |
| `from_text(text)` | Input text assembled in Python. | Editable `FdmInp`. |
| `from_poscar(filename, *, molecule=False)` | POSCAR path. Use `molecule=True` to create a molecular structure section. Reading POSCAR requires `vasp_util`. | Editable `FdmInp`. |
| `set_keyword(keyword, *rows, old_rows=None)` | Keyword and data rows. When replacing a variable-length block, provide the previous row count in `old_rows`. | Updated `FdmInp`. |
| `set_structure(cell, *atoms, molecule=False, old_rows=None)` | Cell row and atom rows. The default is `Crystal`; set `molecule=True` for `Molecule`. When replacing the same section, pass the previous row count including the cell row. | Updated `FdmInp`. |
| `set_range(*grid)` / `get_range()` | Photoelectron energy minimum, step, and maximum in eV relative to the Fermi level. Insert transition energies and new steps before the maximum for variable spacing. | Setter returns the updated input. Getter returns the values in order, or None when absent. |
| `set_edge(edge)` / `get_edge()` | Absorption-edge label, such as `K`, `L3`, or `L23`. | Setter returns the updated input. Getter returns the label, or `K` when absent. |
| `set_absorber(absorber)` / `get_absorber()` / `get_absorbers()` | One-based atom row from the structure, or a sequence of row numbers. | Setter returns the updated input. Getters return the first index or the list of indices. |
| `set_filout(prefix)` / `get_filout()` | Output filename prefix. Relative paths are resolved from the working directory. | Setter returns the updated input. Getter returns the specified prefix or an empty string. |
| `set_green(enabled=True)` / `get_green()` | Multiple-scattering calculation with a muffin-tin potential. | Setter returns the updated input. Getter reports whether the keyword is present. |
| `set_convolution(enabled=True)` / `get_convolution()` | Broadening with the arctangent model. | Setter returns the updated input. Getter reports whether the keyword is present. |
| `set_spgroup(space_group)` / `get_spgroup()` | Full space-group symbol or number used to expand inequivalent atom rows. | Setter returns the updated input. Getter returns the input notation or an empty string. |
| `set_block(keyword, *rows, old_rows=None)` | Compatible entry point for existing callers. Takes the same arguments as `set_keyword()`. | Updated `FdmInp`. |
| `remove_block(keyword, *, old_rows=None)` | Keyword to remove. For a variable-length block, provide the previous row count. | Updated `FdmInp`. |
| `set_radius(radius, *changes)` / `get_radius()` | Radius in Å. Additional pairs give the transition energy in eV and the new radius in Å. | Setter returns the updated input. Getter returns the values in order, or None when absent. |
| `render_input()` | — | str. The current input text. |
| `save(filename, *, overwrite=False)` | Destination path. Set `overwrite=True` to replace an existing file. | Path. Pass it directly to `FdmRun.run()`. |
| `get_ispin()` | — | int: Two when `Spin` or `Magnetism` is specified, otherwise one. |
| `get_allsite()` | — | bool: True when `Allsite` is present. |
| `get_energygpho()` | — | bool: True when `Energpho` or `Energygpho` is present. |
| `get_nonexc()` | — | bool: True when the keyword is present. |
| `get_conv_out()` | — | str: Convolution-output value, or an empty string. |
| `get_calculation()` | — | str: First filename in the last `Calculation` block, or an empty string. |
| `get_cellparam()` | — | list[float] \| None: The six cell parameters, or None when absent. |
| `get_crystal_atoms()` | — | ase.Atoms: Periodic atomic structure with fractional positions. |
| `get_molecule_atoms()` | — | ase.Atoms: Atom positions in angstroms, with periodicity disabled. |
| `render(absorber: int=1, fileout: str='Cu', energy_range: str='-15. 0.2  0. 0.5 10. 1. 45.', edge: str='K', radius: float=5, molecule: bool=False, structure_writer=None)` (static) | `absorber` Absorber number in the FDMNES input. `fileout` Prefix for calculated output files. `energy_range` Energy mesh definition in electronvolts. `edge` Absorption edge, for example K or L3. `radius` Cluster radius in angstroms. `molecule` Select the Molecule keyword instead of Crystal. `structure_writer` Object providing the FDMNES structure section. | str: FDMNES input content including the structural section. |
| `write(filename: str \| Path='read_pdb.inp', **kwargs)` (static) | `filename` Destination filename. `**kwargs` Settings passed to `render()`, with the same defaults. | Path: Destination of the written input file. |

**Example**

```python
from fdmnes_util.fdm_inp import FdmInp
inp = FdmInp("read_pdb.inp")
prefix = inp.get_filout()
absorber = inp.get_absorber()
```

### `Fdmfile`

`from fdmnes_util.fdmfile import Fdmfile`

Represent the ordered input filenames in an FDMNES batch list.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(filename='fdmfile.txt')` | `filename` Path to `fdmfile.txt`. | None. |
| `get_filout()` | — | str. First job’s input filename, or an empty string. |
| `select_input(filename: str \| Path \| None=None)` (class method) | `filename` Explicit calculation input. If omitted, use the first job in `fdmfile.txt` or default to `read_pdb.inp`. | Path. Selected calculation input path. |
| `write(filenames, filename='fdmfile.txt')` (static) | `filenames` Iterable of FDMNES input filenames. `filename` Destination path for the job-list file. | Path: Path of the generated job-list file. |

**Example**

```python
from fdmnes_util.fdmfile import Fdmfile
jobs = Fdmfile("fdmfile.txt")
first_input = jobs.get_filout()
```

### `FdmRun`

`from fdmnes_util.fdm_run import FdmRun`

Launch FDMNES using `fdmfile.txt` in the working directory. Standard output goes to the screen and to `fdmnes-*.log`. FDMNES writes calculation results according to `Filout`.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(executable='fdmnes', *, echo=True)` | Executable path or command name. `echo` is accepted for compatibility with existing callers. | None. |
| `run(input_file=None, *, directory=None, timeout=None)` | When an input is specified, register and run that single input. Otherwise use the existing job list. The working directory defaults to the current directory. The timeout is in seconds. | subprocess.CompletedProcess. |
| `run_fdmfile(*, directory=None, timeout=None)` | Use the existing `fdmfile.txt` in the specified or current directory. The timeout is in seconds. | subprocess.CompletedProcess. |
| `run_inputs(input_files, *, directory, timeout=None)` | Run the inputs one at a time in the supplied order. The timeout applies to the entire sequence. | list[subprocess.CompletedProcess]. One result per input, in order. |

See the [usage guide](usage.md) for examples of preparing and running inputs.

## XAS and experimental spectra

### `FdmTxt`

`from fdmnes_util.fdm_txt import FdmTxt`

Read one XAS output, including edge and Fermi-energy metadata.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(filename)` | `filename` Path to the FDMNES output file. | None. |
| `get_eng()` | — | ndarray. Energy axis in the reference frame stored in the file. |
| `get_xas(spin=0)` | `spin` Zero-based index of the absorption column. | numpy.ndarray: Absorption intensity values. |
| `get_xas_all()` | — | ndarray. Absorption matrix with one row per energy point. |
| `get_edge_xas(edge, spin=0)` | `edge` Edge label as used in the output header, such as L2 or L3. `spin` Zero-based index among columns for the selected edge. | numpy.ndarray: The matching absorption intensities. |
| `get_eedge()` | — | float or None. Edge energy in eV, if present. |
| `get_efermi()` | — | float. Fermi energy in eV, defaulting to 0.0. |
| `write_spectrum(filename, metadata, spectrum)` (static) | `filename` Destination raw XAS filename. `metadata` First-line parameters from the corresponding raw file. `spectrum` Energy and intensity arrays in the original reference. | None. Writes the two-column spectrum with its raw header. |

**Example**

```python
from fdmnes_util.fdm_txt import FdmTxt
raw = FdmTxt("Fe.txt")
energy, intensity = raw.get_eng(), raw.get_xas()
edge = raw.get_eedge()
```

### `FdmConv`

`from fdmnes_util.fdm_conv import FdmConv`

Retain the energy axis and all absorption columns of one output file.

Use `FdmConv(filename, format_year=None)` to detect the November 5, 2026 revision line output by `Header`. Ordinary output uses the 2016 layout. Set `format_year=2016` or `2026` to choose explicitly. With the 2026 layout, `preamble`, `parameters`, and `shifts` expose the extra header data.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(filename, *, format_year=None)` | `filename` Path to the FDMNES output file. | None. |
| `get_eng()` | — | ndarray. Energy axis in the reference frame stored in the file. |
| `get_xas(spin=0)` | `spin` Zero-based index of the absorption column. | numpy.ndarray: Absorption intensity values. |
| `write_spectrum(filename, spectrum)` (static) | `filename` Destination convolution filename. `spectrum` Energy and intensity arrays in the original reference. | None. Writes the two-column spectrum. |

**Example**

```python
from fdmnes_util.fdm_conv import FdmConv
conv = FdmConv("Fe_conv.txt")
energy, intensity = conv.get_eng(), conv.get_xas()
```

### `AthenaNor`

`from fdmnes_util.athena_nor import AthenaNor`

Read the energy axis and normalized absorption from an Athena file.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(filename)` | `filename` Path to a `*.nor` text file. | None. |
| `get_eng()` | — | numpy.ndarray: Photon-energy values. |
| `get_nor()` | — | numpy.ndarray: Normalized absorption values. |

**Example**

```python
from fdmnes_util.athena_nor import AthenaNor
measured = AthenaNor("Fe_obs.txt.nor")
photon_energy, normalized = measured.get_eng(), measured.get_nor()
```

### `FdmPhotoenergy`

`from fdmnes_util.fdm_photoenergy import FdmPhotoenergy`

Represent the `*_conv_photoe.txt` output file format.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `write(energy, intensity, filename)` | `energy` One-dimensional photon-energy values in eV. `intensity` One-dimensional absorption values at those energies. `filename` Destination path for the converted spectrum. | pathlib.Path: Path to the generated text file. |

**Example**

```python
from fdmnes_util.fdm_photoenergy import FdmPhotoenergy
output = FdmPhotoenergy().write([7112.0, 7113.0], [0.2, 0.5], "Fe_conv_photoe.txt")
```

## SD and BAV readers

### `FdmSd`

`from fdmnes_util.fdm_sd import FdmSd`

Select the format-specific parser for a site-resolved DOS file. For files such as the 2019 Cu output, the BAV revision does not identify the SD layout. Pass `format_year=None` to inspect the SD column names.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(filename, *, format_year, ispin=1, weight=None)` | `filename` Path to the FDMNES site-resolved DOS file. `format_year` Supported SD layout year (2016, 2020 or 2026), or None to inspect the SD column names. `ispin` Number of spin channels for the 2016 layout. `weight` Optional divisor for density and integral columns. | None. |
| `select_reader()` | — | FdmSd2016, FdmSd2020, or FdmSd2026. |
| `format_from_bav(filename)` (static) | `filename` Path to the companion BAV file. This legacy method estimates the layout from the revision. | int: Supported SD layout year. |
| `write_table(filename, columns, grid, densities)` (static) | `filename` Destination SD filename. `columns` Column names, beginning with the energy label. `grid` Original energy grid in eV. `densities` Averaged density and integral columns, without energy. | None. Writes the SD table. |

**Example**

```python
from fdmnes_util.fdm_sd import FdmSd
sd = FdmSd("Fe_sd0.txt", format_year=None).select_reader()
energy, p_ldos = sd.get_eng(), sd.get_ldos("p")
```

### `FdmSd2016`

`from fdmnes_util.fdm_sd_2016 import FdmSd2016`

Read DOS projections and spin channels from a 2016 SD file.

`spin` accepts 0 or, for two spins, 1. Aliases for 0 are `up`, `non`, and `nonmag`. Aliases for 1 are `dn` and `down`. Group names are s, p, d, and f.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(filename, *, ispin=1, weight=None)` | `filename` Path to an SD output file. `ispin` Number of spin channels (one or two). `weight` Optional normalization divisor. | None. |
| `get_densities()` | — | ndarray. Density and integral columns in file order, excluding energy. |
| `get_eng()` | — | ndarray. Energy axis in eV. |
| `get_lmax()` | — | int. Maximum orbital angular momentum index. |
| `get_ispin()` | — | int. Number of spin channels. |
| `get_ldos(l=0, spin=0)` | `l` Angular momentum index or the orbital group name s, p, d, or f. `spin` Zero-based spin index or an SAE spin name, such as up or down. | numpy.ndarray: One value per energy point. |
| `get_intldos(l=0, spin=0)` | `l` Angular momentum index or the orbital group name s, p, d, or f. `spin` Zero-based spin index or an SAE spin name, such as up or down. | numpy.ndarray: One value per energy point. |
| `get_pdos(l=0, m=0, lm=None, spin=0)` | `l` Angular momentum index. `m` Magnetic quantum number. `lm` Optional orbital name overriding l and m. `spin` Zero-based spin index or an SAE spin name. | numpy.ndarray: Orbital densities on the file's energy grid. |
| `get_tdos(spin=0)` | `spin` Zero-based spin index or an SAE spin name. | ndarray. Sum of the orbital-group DOS for the selected spin. |
| `get_inttdos(spin=0)` | `spin` Zero-based spin index or an SAE spin name. | ndarray. Sum of the leading integral column and orbital-group integrals for the selected spin. |

**Example**

```python
from fdmnes_util.fdm_sd_2016 import FdmSd2016
sd = FdmSd2016("Fe_2016_sd0.txt", ispin=1)
energy, s_ldos = sd.get_eng(), sd.get_ldos("s")
```

### `FdmSd2020`

`from fdmnes_util.fdm_sd_2020 import FdmSd2020`

Read orbital-resolved density of states from a 2020-format SD file.

This reader supports nonmagnetic columns and the 31-column magnetic layout verified on 2021 and 2026 Ni output. Pass 0 (`up`, `non`, or `nonmag`) or, for magnetic output, 1 (`dn` or `down`). The `total` and `Int(total)` columns describe both spins together.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(filename, *, weight=None)` | `filename` Path to the SD file, including its suffix. `weight` Optional divisor for all density and integrated columns. | None. |
| `get_densities()` | — | ndarray. Density and integral columns in file order, excluding energy. |
| `get_eng()` | — | ndarray. Energy axis in eV. |
| `get_lmax()` | — | int. Maximum orbital angular momentum index. |
| `get_ispin()` | — | int. Number of spin channels. |
| `get_ldos(l=0, spin=0)` | `l` Orbital angular momentum index or the name s, p, or d. `spin` Spin channel number or name. | numpy.ndarray: Density values for the requested orbital. |
| `get_intldos(l=0, spin=0)` | `l` Angular momentum index or group name s, p, or d. `spin` Spin channel number or name. | numpy.ndarray: Integrated densities on the file's energy grid. |
| `get_pdos(l=0, m=0, lm=None, spin=0)` | `l` Orbital angular momentum index. `m` Magnetic quantum number. `lm` Optional orbital name, such as `dxy` or `p_x`. `spin` Spin channel number or name. | numpy.ndarray: Partial density values. |
| `get_tdos(spin=0)` | `spin` Spin channel number or name. | ndarray. Stored total DOS across all spins. |
| `get_inttdos(spin=0)` | `spin` Spin channel number or name. | ndarray. Stored integrated total DOS across all spins. |

**Example**

```python
from fdmnes_util.fdm_sd_2020 import FdmSd2020
sd = FdmSd2020("Fe_sd0.txt")
energy, pz_pdos = sd.get_eng(), sd.get_pdos(lm="p_z")
```

### `FdmSd2026`

This reader supports complex and f-orbital projections. Use `FdmSd(filename, format_year=None)` to detect the layout from the columns, or choose `format_year=2026`. For example, `get_pdos(l=3, m=0)` reads a complex projection, `get_pdos(lm="fxyz")` reads a real f projection, and `get_ldos(l=3)` reads the f group. Ordinary s, p, and d columns from the 2026 binary use the existing reader.

### `FdmBav`

`from fdmnes_util.fdm_bav import FdmBav`

Inspect a `_bav.txt` header and select its version-specific parser.

Each version reader parses its own BAV records. `FdmBav` selects the reader from the revision line and forwards the 13 common methods, such as `get_edge()`, to their counterparts. Direct calls reuse the reader selected on the first call.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(filename)` | `filename` Calculation-log filename. | None. |
| `select_reader()` | — | FdmBav2016 through 2016, FdmBav2020 for 2017–2021, and FdmBav2026 for November 5, 2026. Other revisions from 2022 onward raise ValueError. |
| `get_scf_history()` | — | list[tuple[int, float \| None]]. Cycle numbers and total energies (eV) for the 2026 release. A missing energy is None. An unavailable history is an empty list. |

**Example**

```python
from fdmnes_util.fdm_bav import FdmBav
bav = FdmBav("Fe_bav.txt")
print(bav.year, bav.get_edge())
```

### `FdmBav2016`

`from fdmnes_util.fdm_bav_2016 import FdmBav2016`

Extract calculation information from a 2016-format `_bav.txt` file.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(filename)` | `filename` Path to the FDMNES calculation log. | None. |
| `get_edge()` | — | str. Absorption-edge label, or an empty string. |
| `get_nspin()` | — | int. One or two spin channels. |
| `is_self_consistent()` | — | bool. Whether the log reports a self-consistent calculation. |
| `get_max_scf_iterations()` | — | int or None. Reported SCF iteration limit. |
| `get_n_scf_loop()` | — | int. Last reported SCF cycle number, or zero. |
| `get_scf_toten()` | — | list[float]. Unit-cell energy for each SCF record. |
| `get_position()` | — | ndarray. Cartesian cluster coordinates. |
| `get_atoms_index_j()` | — | list[str]. Chemical symbols in cluster order. |
| `get_natom()` | — | int. Number of atoms in the cluster. |
| `get_e_edge()` | — | float or None. Recorded absorption-edge energy. |
| `get_ngroup()` | — | int or None. Number of atom groups, if available. |
| `get_t()` | — | ndarray or None. 3×3 crystal-basis transformation matrix. |
| `get_lmax()` | — | int or None. Highest angular momentum index in the atom listing. |

**Example**

```python
from fdmnes_util.fdm_bav_2016 import FdmBav2016
log = FdmBav2016("Fe_2016_bav.txt")
edge, last_cycle = log.get_edge(), log.get_n_scf_loop()
```

### `FdmBav2020`

`from fdmnes_util.fdm_bav_2020 import FdmBav2020`

Extract calculation information from a 2020-format `_bav.txt` file.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(filename)` | `filename` Path to the FDMNES calculation log. | None. |
| `get_edge()` | — | str. Absorption-edge label, or an empty string. |
| `get_nspin()` | — | int. One or two spin channels. |
| `is_self_consistent()` | — | bool. Whether the log reports a self-consistent calculation. |
| `get_max_scf_iterations()` | — | int or None. Reported SCF iteration limit. |
| `get_n_scf_loop()` | — | int. Last reported SCF cycle number, or zero. |
| `get_scf_toten()` | — | list[float]. Unit-cell energy for each SCF record. |
| `get_position()` | — | ndarray. Cartesian cluster coordinates. |
| `get_atoms_index_j()` | — | list[str]. Chemical symbols in cluster order. |
| `get_natom()` | — | int. Number of atoms in the cluster. |
| `get_e_edge()` | — | float or None. Recorded absorption-edge energy. |
| `get_ngroup()` | — | int or None. Number of atom groups, if available. |
| `get_t()` | — | ndarray or None. 3×3 crystal-basis transformation matrix. |
| `get_lmax()` | — | int or None. Highest angular momentum index in the atom listing. |

**Example**

```python
from fdmnes_util.fdm_bav_2020 import FdmBav2020
log = FdmBav2020("Fe_bav.txt")
symbols, positions = log.get_atoms_index_j(), log.get_position()
```

### `FdmBav2026`

`from fdmnes_util.fdm_bav_2026 import FdmBav2026`

Read BAV reports from the November 5, 2026 release. The public reader methods match `FdmBav2016` and `FdmBav2020`. Use the common `FdmBav` entry point to read total energies by cycle.

```python
from fdmnes_util.fdm_bav import FdmBav
log = FdmBav("Fe_SCF_bav.txt")
history = log.get_scf_history()
```

## Structure I/O

### `Cif`

`from fdmnes_util.cif import Cif`

Provide FDMNES structure conversion with CIF-backed atomic data.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(path: str \| Path)` | `path` Input CIF file path. | None. |
| `get_symbols()` | — | list[str]: Atomic symbols. |
| `get_lattice_vectors()` | — | numpy.ndarray: A 3-by-3 array of lattice vectors. |
| `get_direct_positions()` | — | numpy.ndarray: Atomic positions in fractional coordinates. |
| `get_cartesian_positions()` | — | numpy.ndarray: Cartesian atomic positions. |

**Example**

```python
from fdmnes_util.cif import Cif
cell = Cif("Fe.cif")
symbols, lattice = cell.get_symbols(), cell.get_lattice_vectors()
```

### `Pdb`

`from fdmnes_util.pdb import Pdb`

Represent the atomic structure and cell information in a PDB file.

Without a `CRYST1` record, `molecule` is true. Lattice vectors and fractional coordinates are for periodic structures.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(path: str \| Path)` | `path` Input PDB filename. | None. |
| `get_symbols()` | — | list[str]: Chemical symbols. |
| `get_cartesian_positions()` | — | list[tuple[float, float, float]]: Cartesian coordinates. |
| `get_lattice_vectors()` | — | numpy.ndarray: Three lattice vectors in angstroms. |
| `get_direct_positions()` | — | numpy.ndarray: Fractional atomic coordinates. |

**Example**

```python
from fdmnes_util.pdb import Pdb
pdb = Pdb("Fe.pdb")
symbols, coordinates = pdb.get_symbols(), pdb.get_cartesian_positions()
```

### `Xyz`

`from fdmnes_util.xyz import Xyz`

Read and write atomic symbols and Cartesian coordinates in standard XYZ format.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(filename: str \| Path)` | `filename` Path to a standard XYZ coordinate file. | None. |
| `read()` | — | None. Refreshes symbols and positions in place. |
| `render(symbols, positions)` (static) | `symbols` Chemical symbols in the desired output order. `positions` Cartesian positions in angstroms, each with three values. | str. Complete XYZ text, including a trailing newline. |
| `write(symbols, positions, filename)` (class method) | `symbols` Chemical symbols in the desired output order. `positions` Cartesian positions in angstroms, each with three values. `filename` Destination filename or path. | Path. Saved XYZ path. |

**Example**

```python
from fdmnes_util.xyz import Xyz
cluster = Xyz("cluster.xyz")
symbols, positions = cluster.symbols, cluster.positions
```

### `ElementTable`

`from fdmnes_util.fdm_structure import ElementTable`

Look up atomic numbers and element symbols used in structure records.

| Method | Argument | Return value |
| --- | --- | --- |
| `get_atomic_symbol0(num)` | Atomic number. | Element symbol as str. |
| `get_atomic_number1(atom)` | Element symbol. | Atomic number as int. |

### `FdmStructure`

`from fdmnes_util.fdm_structure import FdmStructure`

Convert structure information into a FDMNES structural section.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(structure)` | `structure` A `vasp_util.vasp_poscar.VaspPoscar` instance or a reader such as `Cif` or `Pdb` exposing element symbols, lattice vectors, and fractional coordinates. | None. |
| `fdm_to_atoms(filename, *, vacuum=10.0)` (static) | FDMNES input path. `vacuum` is the padding in Å on each side of the molecule. | ase.Atoms for POSCAR writing. |
| `poscar_to_atoms(filename)` (static) | POSCAR path passed to vasp_util. | Periodic ase.Atoms with the original lattice and atom order. |
| `crystal_atoms(cell_values, atom_lines)` (static) | Six cell lengths and angles, followed by atom records containing atomic numbers and fractional coordinates. | ase.Atoms with periodic boundaries. |
| `molecule_atoms(lines)` (static) | Molecular scale and atomic-coordinate records. | ase.Atoms for an isolated molecule with Cartesian coordinates in Å. |
| `render(molecule: bool=False)` | `molecule` Write the `Molecule` keyword instead of `Crystal`. | str: Formatted FDMNES structure section. |
| `render_xyz_molecule(symbols: list[str], positions: list[tuple[float, float, float]])` (static) | `symbols` Chemical symbols in atom order. `positions` Cartesian positions in angstroms. | str. FDMNES Molecule section from XYZ coordinates. |
| `write(filename: str \| Path, molecule: bool=False)` | `filename` Destination filename. `molecule` Whether to use the Molecule keyword. | Path: Written file path. |

**Example**

```python
from fdmnes_util.fdm_structure import FdmStructure
from vasp_util.vasp_poscar import VaspPoscar

structure = FdmStructure(VaspPoscar("POSCAR"))
output = structure.write("Fe.fdmnes")
```

## Analysis

### `AnalyzeFdmAverage`

`from fdmnes_util.analyze_fdm_average import AnalyzeFdmAverage`

Average data from independent calculations on a shared energy grid.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `energy_reference(input_file, spectrum, fermi=False)` | `input_file` FdmInp instance describing the calculation mode. `spectrum` FdmTxt instance containing edge and Fermi energies. `fermi` If True, use the Fermi-relative energy reference. Otherwise, use photon energy. | tuple[float, float]: Energy-axis shift and absolute Fermi position in the photon-energy reference, both in eV. |
| `average(readers, value_method, *, divisor=None, **kwargs)` | `readers` Nonempty sequence of FDMNES output objects. `value_method` Name of the data access method on each object. `divisor` Optional positive divisor for the sum, used for SAE's per-atom normalization. Defaults to the number of readers. `**kwargs` Arguments passed to the selected data access method. | tuple[numpy.ndarray, numpy.ndarray]: Energy and mean values. |

**Example**

```python
from fdmnes_util.analyze_fdm_average import AnalyzeFdmAverage
from fdmnes_util.fdm_conv import FdmConv

readers = [FdmConv("Fe_1_conv.txt"), FdmConv("Fe_2_conv.txt")]
energy, mean_xas = AnalyzeFdmAverage().average(readers, "get_xas")
```

### `AnalyzeFdmXas`

`from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas`

Numerical analysis of FDMNES absorption spectra.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `average(spectra, weights=None)` (static) | `spectra` Iterable of spectra sampled at exactly the same energies. `weights` One relative weight per spectrum. The default is uniform. | tuple[numpy.ndarray, numpy.ndarray]: Common energy grid and mean XAS. |
| `photon_energy(convolution, raw_xas, *, subtract_fermi=False, fermi_energy=None)` (static) | `convolution` `FdmConv` containing the convolved energy grid. `raw_xas` `FdmTxt` supplying the absorption-edge energy. `subtract_fermi` Subtract the Fermi-energy offset when True. `fermi_energy` Fermi-energy offset in eV, when subtraction is used. | tuple[numpy.ndarray, numpy.ndarray]: Converted energy and XAS. |
| `fermi_relative_convolution(convolution, raw_xas)` (static) | `convolution` Reader for the convolved FDMNES spectrum. `raw_xas` Reader for the corresponding non-convolved spectrum. | tuple[numpy.ndarray, numpy.ndarray]: Fermi-relative energy and absorption intensity, in the original row order. |
| `energy_reference(energy, raw_xas, *, input_is_photon, fermi)` (static) | `energy` Energy values in the file's original reference frame. `raw_xas` Raw spectrum providing edge and Fermi energies. `input_is_photon` Whether the input uses the Energpho keyword. `fermi` Whether to return a Fermi-relative energy grid. | numpy.ndarray: Energy grid in the requested reference frame, in eV. |
| `site_spectra(base_name, site_indices, *, convolved=True, input_is_photon=None, fermi=None)` (class method) | `base_name` Filout prefix, optionally with a directory. `site_indices` One-based absorbing-site indices in plot order. `convolved` Select convolved instead of raw site spectra. `input_is_photon` Whether the original calculation used Energpho. `fermi` Whether to return Fermi-relative energy values. | list[tuple]: Tuples of energy, intensity, and site label. |

**Example**

```python
from fdmnes_util.analyze_fdm_xas import AnalyzeFdmXas
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.fdm_txt import FdmTxt

conv, raw = FdmConv("Fe_conv.txt"), FdmTxt("Fe.txt")
energy, intensity = AnalyzeFdmXas.photon_energy(conv, raw)
```

## Plotting

Plotting requires Matplotlib. Match the number of energies to the number of values in each curve and convert compared curves to the same energy reference. Plotting methods return the saved `Path`. `save_multiple_formats()` returns a list of paths.

### `PlotFdmXas`

`from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas`

Matplotlib visualizations for FDMNES XAS.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `plot_convolved(eng, xas, output, *, specified=False)` | `eng` Fermi-relative energies. `xas` Convolved absorption. `output` Figure path. `specified` Use the original `fdXAS_specified.py` ticks and legend. | Path to the saved figure. |
| `plot(spectra, output, *, title=None, xlabel='Energy (eV)', ylabel='XAS', xmin=None, xmax=None, ymax=None, fermi_position=None)` | `spectra` Sequence of energy, intensity, and curve-label tuples. `output` Destination path. The extension determines the figure format. `title` Optional figure title. `xlabel` Energy-axis label. `ylabel` Absorption-axis label. `xmin` Optional minimum energy. `xmax` Optional maximum energy. `ymax` Optional maximum absorption. `fermi_position` Energy at which to draw the optional Fermi marker. | pathlib.Path: Path to the saved figure. |
| `plot_sites(spectra, output, *, observed=None, xmin=None, xmax=None, ymax=None, fermi=False, fermi_position=None, extra_formats=False)` | `spectra` Computed spectra as energy, intensity, label tuples. `output` Destination path for the figure. `observed` Optional Athena spectra for the upper panel. `xmin` Optional lower limit of the energy axis. `xmax` Optional upper limit of the energy axis. `ymax` Optional upper limit of the absorption axis. `fermi` Whether the energy axis is Fermi-relative. `fermi_position` Energy of the vertical Fermi marker. `extra_formats` Also save EPS, PDF, and PNG. | pathlib.Path: Destination of the saved figure. |
| `plot_experiment_comparison(calculated_energy, calculated_absorption, observed_energy, observed_absorption, output, *, xmin=None, xmax=None, ymin=0.0, ymax=None)` | `calculated_energy` Calculated photon energies in eV. `calculated_absorption` Calculated absorption intensity. `observed_energy` Experimental photon energies in eV. `observed_absorption` Normalized experimental absorption. `output` Destination PDF or image filename. `xmin` Optional minimum photon energy in eV. `xmax` Optional maximum photon energy in eV. `ymin` Optional minimum absorption value. `ymax` Optional maximum absorption value. | pathlib.Path: Saved figure filename. |
| `plot_composite(spectra, output, *, observed=None, dos=(), xlabel='Photon Energy [eV]', ylabel='Absorption [arb. unit]', xmin=None, xmax=None, ymax=None, dmax=None, fermi_position=None, extra_formats=False, show=False)` | `spectra` Calculated spectrum tuples of energy, intensity, and label. `output` Main output filename. `observed` Optional measured energy, absorption, and label tuple. `dos` Optional LDOS tuples of energy, density, and label. `xlabel` Label of the bottom energy axis. `ylabel` Label of the calculated absorption axis. `xmin` Lower common energy limit. `xmax` Upper common energy limit. `ymax` Upper calculated absorption limit. `dmax` Upper LDOS limit. `fermi_position` Optional Fermi marker on calculated panels, in eV. `extra_formats` Also save EPS, PNG and PDF. `show` Display the figure using the active Matplotlib backend. | pathlib.Path: Main figure path. |

**Example**

```python
from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas
from fdmnes_util.fdm_conv import FdmConv

conv = FdmConv("Fe_conv.txt")
output = PlotFdmXas().plot([(conv.get_eng(), conv.get_xas(), "Fe")], "Fe_XAS.pdf")
```

### `PlotFdmDos`

`from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos`

Create density-of-states figures without parsing an SD file.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `plot_local(reader, output, *, orbit=1, integrated=False)` | `reader` SD reader. `output` Figure path. `orbit` Orbital angular momentum index. `integrated` Plot integrated LDOS. Uses the SAE `fdLDOS.py` layout. | Path to the saved figure. |
| `plot_single_orbital(reader, output, *, orbital='p', emin=None, emax=None, dmax=None, edge_offset=0.0, fermi_position=0.0, divisor=None, extra_outputs=())` | `reader` SD reader or sequence of site readers. `output` Destination image path. Matplotlib infers its format. `orbital` Orbital channel to plot, such as `p`. `emin` Optional minimum energy for the horizontal axis. `emax` Optional maximum energy for the horizontal axis. `dmax` Optional maximum density for the vertical axis. `edge_offset` Offset added to the computed energy axis (eV). `fermi_position` Position of the vertical Fermi marker (eV). `divisor` Optional divisor of the site sum. `extra_outputs` Additional save paths. | pathlib.Path: The generated image file. |
| `plot_occupied_ldos(reader, output, *, orbital='p', edge_offset=0.0, fermi_position=0.0, emin=None, emax=None, dmax=None)` | `reader` FDMNES SD object for the selected format year. `output` Destination figure path. `orbital` Orbital channel whose LDOS is plotted. `edge_offset` Energy offset added to SD energies, in eV. `fermi_position` Fermi level in the shifted energy axis, in eV. `emin` Optional lower energy limit, in eV. `emax` Optional upper energy limit, in eV. `dmax` Optional upper density limit. | pathlib.Path: Destination of the saved figure. |
| `plot(reader, output, orbitals=('s', 'p', 'd'), *, integrated=False)` | `reader` A version-specific SD reader exposing the `get_*dos` API. `output` Path of the output image or PDF. `orbitals` Orbital channels to draw in the requested order. `integrated` Plot integrated LDOS instead of LDOS when True. | pathlib.Path: Path to the figure written to disk. |
| `save_multiple_formats(readers, labels, output_prefix, *, formats=('eps', 'pdf', 'png'), edge_energy, fermi_energy, orbital='p', emin=None, emax=None)` | `readers` Exactly three year-specific SD reader objects. `labels` Three site labels in the same order as the readers. `output_prefix` Output path without a filename extension. `formats` Sequence of image extensions supported by Matplotlib. `edge_energy` Absorption-edge energy in eV. `fermi_energy` Fermi energy relative to the edge in eV. `orbital` Orbital channel to plot. `emin` Optional minimum photon energy in eV. `emax` Optional maximum photon energy in eV. | list[pathlib.Path]: Paths to the generated image files. |
| `plot_multiple_sites(readers, labels, output, *, edge_energy, fermi_energy, orbital='p', emin=None, emax=None)` | `readers` Three version-specific SD reader instances. `labels` Three labels corresponding to the SD files. `output` Path of the image to save. `edge_energy` Absorption-edge energy in eV. `fermi_energy` Fermi energy relative to the absorption edge in eV. `orbital` Orbital channel to display, defaulting to p. `emin` Optional lower photon-energy limit in eV. `emax` Optional upper photon-energy limit in eV. | pathlib.Path: Path of the saved figure. |
| `plot_three_calculations(readers, fermi_energies, labels, output, *, orbital='p', emin=None, emax=None, density_max=5.0, extra_outputs=())` | `readers` Three SD readers, one per calculation. `fermi_energies` Three Fermi energies from the corresponding `FdmTxt` objects, expressed in the SD energy reference. `labels` Labels for the three independent calculations. `output` Destination image path. `orbital` LDOS channel to plot. `emin` Optional minimum Fermi-relative energy in eV. `emax` Optional maximum Fermi-relative energy in eV. `density_max` Upper bound of the LDOS axis. `extra_outputs` Additional save paths. | pathlib.Path: Path to the saved figure. |
| `plot_composite(reader, output, *, groups, spins=(0,), spin_labels=('', ''), projected=False, integrated=False, xas=(), shift=0.0, fermi_position=0.0, xlabel='Photon Energy [eV]', limits=(None, None), density_max=None, orbital_max=None, xas_max=None, label='0', extra_formats=False, show=False, shade_occupied=False)` | `reader` SD reader supplying densities on its own energy grid. `output` Main figure filename. `groups` Bottom-to-top groups of orbital names. Use ("total",) for a total DOS panel. `spins` Spin channel order within each group, from bottom to top. `spin_labels` Label suffixes indexed by spin channel. `projected` Use individual orbital projections (PDOS). `integrated` Add stored integral curves on right-hand axes. `xas` Energy, intensity and label tuples for the absorption panel. `shift` Reference-frame shift applied only to the SD grid, in eV. `fermi_position` Position of the vertical energy marker, in eV. `xlabel` Energy reference label shown on the bottom axis. `limits` Lower and upper energy limits, with None for SD bounds. `density_max` Default upper limit on DOS magnitudes. `orbital_max` Optional mapping of group names to DOS limits. `xas_max` Maximum intensity on the absorption panel. `label` Site or material label used on the DOS curves. `extra_formats` Also save PDF, EPS, and PNG. `show` Display the figure after saving. `shade_occupied` Shade LDOS below the Fermi level. | pathlib.Path: Main saved figure. |

**Example**

```python
from fdmnes_util.plot.plot_fdm_dos import PlotFdmDos
from fdmnes_util.fdm_sd_2020 import FdmSd2020

sd = FdmSd2020("Fe_sd0.txt")
output = PlotFdmDos().plot_single_orbital(sd, "Fe_LDOS.pdf", orbital="p")
```

### `PlotFdmXasLdos`

`from fdmnes_util.plot.plot_fdm_xas_ldos import PlotFdmXasLdos`

Draw XAS and orbital-resolved LDOS using prepared numerical arrays.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `plot(xas, orbital_spectra, output, *, fermi_position=None, fermi=False)` | `xas` Tuple of energy and absorption arrays. `orbital_spectra` Iterable of (orbital, energy, LDOS) tuples. `output` Output file path. `fermi_position` Reference energy marker on every axis, when known. `fermi` Whether the energy axis is relative to the Fermi level. | pathlib.Path: Path to the generated figure. |
| `plot_experiment_ldos(*, calculated_energy, calculated_absorption, raw_energy, raw_absorption, observed_energy, observed_absorption, ldos_energy, ldos_density, fermi_energy, output, xmin=None, xmax=None)` | `calculated_energy` Photon energies of broadened XAS. `calculated_absorption` Broadened absorption values. `raw_energy` Photon energies of unbroadened XAS. `raw_absorption` Unbroadened absorption values. `observed_energy` Experimental photon energies. `observed_absorption` Scaled and shifted experimental XAS. `ldos_energy` Photon energies corresponding to the LDOS grid. `ldos_density` p-orbital LDOS values. `fermi_energy` Fermi level in photon-energy coordinates. `output` Destination figure filename. `xmin` Optional lower photon-energy limit. `xmax` Optional upper photon-energy limit. | pathlib.Path: Saved figure path. |

**Example**

```python
from fdmnes_util.plot.plot_fdm_xas_ldos import PlotFdmXasLdos
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.fdm_sd_2020 import FdmSd2020

conv, sd = FdmConv("Fe_conv.txt"), FdmSd2020("Fe_sd0.txt")
xas = (conv.get_eng(), conv.get_xas())
ldos = [("p", sd.get_eng(), sd.get_ldos("p"))]
output = PlotFdmXasLdos().plot(xas, ldos, "Fe_XAS_LDOS.pdf")
```

### `PlotFdmAverage`

`from fdmnes_util.plot.plot_fdm_average import PlotFdmAverage`

Draw averaged FDMNES orbital projections and absorption spectra.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `plot(orbital_data, output, *, xas_data=None, raw_xas_data=None, emin=None, emax=None, dmax=None, ymax=None, energy_offset=0.0, orbital_groups=None, fermi_position=None, xlabel='Photon Energy [eV]', extra_formats=False, show=False)` | `orbital_data` Sequence of (label, energy, DOS) records. `output` Destination image filename. `xas_data` Optional (energy, absorption) pair after broadening. `raw_xas_data` Optional (energy, absorption) pair before broadening. `emin` Optional minimum energy. `emax` Optional maximum energy. `dmax` Optional upper bound for each PDOS panel. `ymax` Optional upper bound for the XAS panel. `energy_offset` Energy shift in eV applied to every plotted curve. `orbital_groups` Optional orbital-name groups. Each group is plotted in one panel, following the SAE orbital block layout. `fermi_position` Fermi level in the displayed energy reference (eV), drawn on every panel when supplied. `xlabel` Energy-axis label. `extra_formats` Also save EPS, PDF, and PNG. `show` Display the figure. | pathlib.Path: Path to the generated figure. |

**Example**

```python
from fdmnes_util.plot.plot_fdm_average import PlotFdmAverage
from fdmnes_util.analyze_fdm_average import AnalyzeFdmAverage
from fdmnes_util.fdm_sd_2020 import FdmSd2020

readers = [FdmSd2020("Fe_1_sd0.txt"), FdmSd2020("Fe_2_sd0.txt")]
energy, density = AnalyzeFdmAverage().average(readers, "get_pdos", lm="p_z")
output = PlotFdmAverage().plot([("p_z", energy, density)], "Fe_PDOS_mean.pdf")
```

## Result file operations and convolution job preparation

### `SiteConvolutionJobPreparer`

`from fdmnes_util.util.site_convolution_job_preparer import SiteConvolutionJobPreparer`

Prepare site-by-site convolution jobs by selecting numbered raw XAS spectra in filename order and writing one input per spectrum plus a shared job list. `FDmakeCconvAllsite.py` uses this utility.

With input files `Fe_1.txt` and `Fe_2.txt`, the example writes `conv_1.inp`, `conv_2.inp`, and `fdmfile.txt` in `convolution_jobs/`.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `write(filout, output_dir='.')` | `filout` FDMNES output prefix, optionally including a directory. `output_dir` Directory receiving the jobs and serving as the working directory when FDMNES runs them. | list[str]: Input filenames in lexicographic order of source spectra. |

**Example**

```python
from fdmnes_util.util.site_convolution_job_preparer import SiteConvolutionJobPreparer
jobs = SiteConvolutionJobPreparer().write("Fe", output_dir="convolution_jobs")
print(jobs)
```

### `ResultFileOperations`

`from fdmnes_util.util.result_file_operations import ResultFileOperations`

Find, clean, rename, or archive files associated with a Filout prefix.

| Method and parameter defaults | Parameter meanings | Return value |
| --- | --- | --- |
| `__init__(filout: str \| Path)` | `filout` Filename prefix, optionally preceded by a directory. | None. |
| `outputs()` | — | list[Path]. Existing result and auxiliary files. |
| `move_outputs()` | — | list[Path]. Existing XAS, BAV, convolution, and SD files eligible for relocation. |
| `clean()` | — | list[Path]. Paths that were deleted. |
| `move(destination: str \| Path)` | `destination` Directory to create or use for the archive. | list[Path]. Paths in the archive directory. |
| `rename(destination: str \| Path)` | `destination` New prefix, optionally preceded by an existing directory. | list[Path]. Destination paths in result order. A collision raises FileExistsError. |

**Example**

```python
from fdmnes_util.util.result_file_operations import ResultFileOperations
results = ResultFileOperations("Fe")
print(results.outputs())
```

## Python examples

### Extract orbital density from SD

```python
from fdmnes_util.fdm_sd import FdmSd

sd = FdmSd("Fe_sd0.txt", format_year=None).select_reader()
energy = sd.get_eng()
p_ldos = sd.get_ldos("p")
pz_pdos = sd.get_pdos(lm="p_z")
```

### Export a calculation cluster from BAV to XYZ

```python
from fdmnes_util.fdm_bav import FdmBav
from fdmnes_util.xyz import Xyz

bav = FdmBav("Fe_bav.txt").select_reader()
symbols = bav.get_atoms_index_j()
positions = bav.get_position()
Xyz.write(symbols, positions, "Fe_cluster.xyz")
```

### Plot the mean XAS across sites

```python
from fdmnes_util.analyze_fdm_average import AnalyzeFdmAverage
from fdmnes_util.fdm_conv import FdmConv
from fdmnes_util.plot.plot_fdm_xas import PlotFdmXas

spectra = [FdmConv("Fe_1_conv.txt"), FdmConv("Fe_2_conv.txt")]
energy, intensity = AnalyzeFdmAverage().average(spectra, "get_xas")
PlotFdmXas().plot([(energy, intensity, "Fe mean")], "Fe_mean.pdf")
```
