# SAE FD*/fd* command audit — 28 scripts

PARTIAL means functionality differs from the source: options and numerical/plot semantics not fully verified. None is marked complete.

- `FDbav2xyz.py`: SAE input option, Cu default and single-file discovery, and identical ten-decimal XYZ on stdout or disk. Multi-log discovery requires explicit selection.
- `FDcif2fdm.py`: EXTENDED FROM BUG-ONLY ORIGINAL (`scripts/FDcif2fdm.py`; original only read CIF and printed "bug version")
- `FDclean.py`: Explicit or positional input, first batch job, and default input selection. File cleanup is scoped to the selected Filout directory.
- `FDconv_e2photoe.py`: PARTIAL (`scripts/FDconv_e2photoe.py`)
- `FDfdm2vasp.py`: Crystal and six-, two-, and one-parameter Molecule inputs are supported. Configurable vacuum padding is an extension replacing the original molecular cell-scaling issue. ASE writes a single POSCAR.
- `FDgetfermi.py`: Explicit input, first batch job, and default input selection are covered by regression tests. The output-prefix override also works without an input file, as in the pre-beta project.
- `FDmakeCconvAllsite.py`: SAE input fallback and lexicographic numbered-spectrum ordering. The job generator uses paths relative to the job directory. The arm64 build of FDMNES 2022 consumed the generated job and wrote the selected site result outside the job directory.
- `FDmove.py`: SAE one- and two-prefix positional syntax. A destination collision is rejected before moving files. The archive-directory flag is a project extension.
- `FDpbd2fdm.py`: PARTIAL (`scripts/FDpbd2fdm.py`)
- `FDplot_LDOS.py`: Restored SAE s/p/d/f and total panels, spin order and inversion, integral axes, independently weighted raw/broadened XAS, limits and labels, PDF/EPS/PNG, and native display control.
- `FDplot_PDOS.py`: Restored SAE s/p/d projection blocks (including the split p block), spin panels, weighted XAS overlay, limits and labels, PDF/EPS/PNG, and native display control.
- `FDplot_XAS.py`: Restored raw/broadened XAS, optional Athena and s/p-LDOS panels, independent energy grids, site averaging and `_0*` tables, named L2/L3 raw columns, axis limits, PDF/EPS/PNG, and native display control.
- `FDplot_XAS_LDOS.py`: PARTIAL (`scripts/FDplot_XAS_LDOS.py`; stacked XAS/LDOS PDF, explicit verified SD layout required)
- `FDplot_XASs.py`: PARTIAL (`scripts/FDplot_XASs.py`, convolved site series and observed Athena overlay; remaining options not fully verified)
- `FDvasp2fdm.py`: PARTIAL (`scripts/FDvasp2fdm.py`)
- `FDvasp2fdm_BUG.py`: HISTORICAL FROZEN (`scripts/FDvasp2fdm_BUG.py`; original conversion disabled after critical bug; non-converting behavior preserved)
- `FDvasp2fdm_NEW_20151125_BUGversion.py`: HISTORICAL FROZEN (`scripts/FDvasp2fdm_NEW_20151125_BUGversion.py`; original conversion disabled after critical bug; non-converting behavior preserved)
- `FDxyz2fdm.py`: PARTIAL (`scripts/FDxyz2fdm.py`)
- `fdExp_comp_XAS.py`: PARTIAL (`scripts/fdExp_comp_XAS.py`; experimental comparison with photon-energy conversion)
- `fdLDOS.py`: PARTIAL (`scripts/fdLDOS.py`)
- `fdLDOS0_specified.py`: PARTIAL (`scripts/fdLDOS0_specified.py`, original axis-limit flags and p-LDOS output; hard-coded Pd6 path replaced by input Filout)
- `fdLDOS_color.py`: PARTIAL (`scripts/fdLDOS_color.py`; occupied-state LDOS shading only)
- `fdLDOSmulti.py`: PARTIAL (`scripts/fdLDOSmulti.py`; three-site plot implemented; EPS/PDF/PNG batch export available via --all-formats; interactive display pending)
- `fdMulti_2_XAS+LDOS+EXP.py`: PARTIAL (`scripts/fdMulti_2_XAS+LDOS+EXP.py`; XAS/LDOS/experiment two-panel figure)
- `fdMulti_3.py`: PARTIAL (`scripts/fdMulti_3.py`; three independent Fermi-aligned p-LDOS panels and EPS/PDF/PNG output; SAE layout and interactive display remain incomplete)
- `fdPDOS_XAS_av.py`: PARTIAL (`scripts/fdPDOS_XAS_av.py`; averaged PDOS and optional averaged convolved XAS; raw/convolved XAS overlay available via --raw-xas-files; original energy offsets and other display options pending)
- `fdXAS.py`: PARTIAL (`scripts/fdXAS.py`)
- `fdXAS_specified.py`: PARTIAL (`scripts/fdXAS_specified.py`; Fermi-relative convolved XAS, original plot styling not fully reproduced)

## Static comparison of CLI option spellings

Compared the literal parser declarations in all 28 SAE scripts. The table lists spelling differences, including aliases. Shared spellings still require behavioral checks for defaults, value types, and output. Positional arguments and output layouts are tracked separately.

| Sample | Original flag spellings absent from the current parser |
| --- | --- |

| `FDplot_XAS_LDOS.py` | `--orbit`, `-l` |
| `FDvasp2fdm.py` | `--ipput` |
| `fdLDOS.py` | `--atom`, `-a`, `-l` |
| `fdLDOS_color.py` | `--atom`, `--bavname`, `--broad`, `--conv`, `--convname`, `--d`, `--dmax_d`, `--dmax_f`, `--dmax_p`, `--dmax_s`, `--dn`, `--dosweight`, `--down`, `--filbav`, `--filout`, `--filoutname`, `--head`, `--inpname`, `--intdos`, `--label`, `--name`, `--nw`, `--outsuffix`, `--p`, `--pdf`, `--s`, `--sd`, `--sdname`, `--sp`, `--spd`, `--spdf`, `--spin`, `--total`, `--txt`, `--txtname`, `--txtweight`, `--up`, `--weight`, `--xas`, `--xasweight`, `--ymax`, `-a`, `-b`, `-c`, `-f`, `-i`, `-s`, `-t`, `-x` |
| `fdMulti_2_XAS+LDOS+EXP.py` | `--input`, `-i` |
| `fdPDOS_XAS_av.py` | `--broad`, `--dosweight`, `--nw`, `--outsuffix`, `--xas`, `-a`, `-b`, `-x` |

## Composite XAS / LDOS / PDOS verification

- The sample parsers expose all of the original flag spellings: 48 for
  FDplot_XAS, 54 for FDplot_LDOS and 48 for FDplot_PDOS, counting aliases.
  SAE's `--pdf` adds EPS and PNG to the PDF. `--nw` saves without opening
  a window. The composite renderers use the active Matplotlib backend.
- Running the unmodified SAE commands and this project on the same supplied
  nonmagnetic Fe data gave matching panel bounds and curve arrays. The cases
  were the default XAS overlay and the DOS commands with `--xas --sp`.
  Automated cases also check the three-panel Athena/XAS/DOS figure, integral
  axes, the 2016 spin-pair inversion, site-normalization divisors, exported
  averages, and the three output file signatures.
- XAS site averaging now reads the absorption column and divides the sum by
  the specified weight or site count. Raw, convolved and SD families must
  agree internally on their grids, and are allowed to differ from each other.
  For input in photon coordinates, the Fermi-relative transform subtracts
  both the edge energy and E_Fermi. This corrects the inconsistent LDOS
  expression and unassigned PDOS expression in SAE. The Athena overlay
  retains its own energy values, as SAE did.
- Named L2/L3 selection applies to raw XAS. The convolved overlay uses its
  first intensity column as in SAE. Averages exported as raw XAS tables
  contain the first selected curve, with the first site's metadata.
  Edge-resolved spin selection is covered by format logic and synthetic
  cases, with real multi-edge magnetic spectra still to be checked.
- The selected DOS year comes from the companion BAV or explicit `--year`.
  Unknown BAV revisions, including 2022, require separate validation.
  The verified 2020 SD layout supports one spin channel. For PDOS only,
  `--intdos` remains a compatibility flag. SAE parsed it without drawing
  per-component integrals, and the verified 2020 SD format has none.
  PDOS `--total` adds a total panel and `--s` / `--p` select their named
  groups as extensions. The direct positional SD mode retains its prior
  single-figure behavior.
