# SAE FD*/fd* command audit — 28 scripts

PARTIAL means functionality differs from the source: options and numerical/plot semantics not fully verified. None is marked complete.

- `FDbav2xyz.py`: PARTIAL (`scripts/FDbav2xyz.py`)
- `FDcif2fdm.py`: EXTENDED FROM BUG-ONLY ORIGINAL (`scripts/FDcif2fdm.py`; original only read CIF and printed "bug version")
- `FDclean.py`: PARTIAL (`scripts/FDclean.py`)
- `FDconv_e2photoe.py`: PARTIAL (`scripts/FDconv_e2photoe.py`)
- `FDfdm2vasp.py`: NOT YET REBUILT
- `FDgetfermi.py`: PARTIAL (`scripts/FDgetfermi.py`)
- `FDmakeCconvAllsite.py`: PARTIAL (`scripts/FDmakeCconvAllsite.py`)
- `FDmove.py`: PARTIAL (`scripts/FDmove.py`)
- `FDpbd2fdm.py`: PARTIAL (`scripts/FDpbd2fdm.py`)
- `FDplot_LDOS.py`: PARTIAL (`scripts/FDplot_LDOS.py`)
- `FDplot_PDOS.py`: PARTIAL (`scripts/FDplot_PDOS.py`)
- `FDplot_XAS.py`: PARTIAL (`scripts/FDplot_XAS.py`)
- `FDplot_XAS_LDOS.py`: PARTIAL (`scripts/FDplot_XAS_LDOS.py`; stacked XAS/LDOS PDF, explicit verified SD layout required)
- `FDplot_XASs.py`: PARTIAL (`scripts/FDplot_XASs.py`, convolved site series and observed Athena overlay; remaining options not fully verified)
- `FDvasp2fdm.py`: PARTIAL (`scripts/FDvasp2fdm.py`)
- `FDvasp2fdm_BUG.py`: NOT YET REBUILT
- `FDvasp2fdm_NEW_20151125_BUGversion.py`: NOT YET REBUILT
- `FDxyz2fdm.py`: PARTIAL (`scripts/FDxyz2fdm.py`)
- `fdExp_comp_XAS.py`: PARTIAL (`scripts/fdExp_comp_XAS.py`; experimental comparison with photon-energy conversion)
- `fdLDOS.py`: PARTIAL (`scripts/fdLDOS.py`)
- `fdLDOS0_specified.py`: PARTIAL (`scripts/fdLDOS0_specified.py`, original axis-limit flags and p-LDOS output; hard-coded Pd6 path replaced by input Filout)
- `fdLDOS_color.py`: NOT YET REBUILT
- `fdLDOSmulti.py`: PARTIAL (`scripts/fdLDOSmulti.py`; three-site plot implemented; EPS/PDF/PNG batch export available via --all-formats; interactive display pending)
- `fdMulti_2_XAS+LDOS+EXP.py`: NOT YET REBUILT
- `fdMulti_3.py`: NOT YET REBUILT
- `fdPDOS_XAS_av.py`: NOT YET REBUILT
- `fdXAS.py`: PARTIAL (`scripts/fdXAS.py`)
- `fdXAS_specified.py`: PARTIAL (`scripts/fdXAS_specified.py`; Fermi-relative convolved XAS, original plot styling not fully reproduced)

