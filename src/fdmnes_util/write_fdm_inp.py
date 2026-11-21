#!/usr/bin/env python3
# Original SAE source: inp_writer.py
# SAE: Copyright Kengo NAKADA; SAE class library.
"""Write a complete FDMNES calculation input from structural information."""

from pathlib import Path

from fdmnes_util.write_fdm_structure import WriteFdmStructure


class WriteFdmInp:
    """Generate the calculation input used by the original FDvasp2fdm script.

    The structure writer supplies the Crystal/Molecule section. This class
    owns the calculation keywords, their order, and the input-file output.
    """

    def __init__(self, structure_writer: WriteFdmStructure) -> None:
        """Initialize the input writer.

        Args:
            structure_writer: Writer for the FDMNES structure section.
        """
        self.structure_writer = structure_writer

    def render(
        self,
        absorber: int = 1,
        fileout: str = "Cu",
        energy_range: str = "-15. 0.2  0. 0.5 10. 1. 45.",
        edge: str = "K",
        radius: float = 5,
        molecule: bool = False,
    ) -> str:
        """Construct a complete FDMNES input file.

        Args:
            absorber: Absorber number in the FDMNES input.
            fileout: Prefix for calculated output files.
            energy_range: Energy mesh definition in electronvolts.
            edge: Absorption edge, for example K or L3.
            radius: Cluster radius in angstroms.
            molecule: Select the Molecule keyword instead of Crystal.

        Returns:
            str: FDMNES input content including the structural section.
        """
        # Keep the keyword sequence and defaults of SAE's FDvasp2fdm.py.
        lines = [
            "! FDMNES indata file",
            "",
            "!Nonexc",
            "",
            " Absorber",
            f"  {absorber}",
            "! allsite",
            "",
            " Filout",
            f"  {fileout}",
            "",
            " Range                        ! Energy range of calculation (eV)",
            (
                f"  {energy_range}  ! first energy, step, intermediary "
                "energy, step ..., last energy "
            ),
            "! -15. 0.1 50. 1. 200.        !",
            "",
            "!Energpho",
            "",
            " Edge",
            f"  {edge}",
            "! L23",
            "",
            "!Quadrupole",
            "",
            " Relativism",
            "",
            " Convolution",
            "",
            "!No_Fermi",
            "!Efermi",
            "!  -6.0",
            "!Estart",
            "! -10.0",
            "",
            "!SCF",
            "!R_self",
            "! 5.0",
            "!N_self",
            "! 100",
            "!P_self",
            "! 0.05",
            "!Delta_E_conv",
            "! 0.01",
            "",
            "!Magnetism",
            "!SCF_mag_free",
            "",
            "!Hubbard",
            "! 0.0 6.3 0.0",
            "",
            "!TDDFT",
            "",
            "!Green",
            "",
            (
                " Radius                       ! Radius of the cluster "
                "where final state calculation is performed"
            ),
            (
                f"   {radius}  ! For a good calculation, this radius "
                "must be increased up to 6 or 7 Angstroems"
            ),
            "",
            " Memory_save",
            "",
        ]
        # The structure section is produced by its own file-format writer.
        structure_content = self.structure_writer.render(molecule=molecule)
        lines.extend(structure_content.rstrip("\n").splitlines())
        lines.extend(
            [
                "",
                "!Cif_file",
                "!  POSCAR.cif",
                "",
                " Density",
                "  state_all",
                "",
                "!Adimp",
                "! 0.20",
                "",
                " End",
                "",
            ]
        )
        return "\n".join(lines) + "\n"

    def write(self, filename: str | Path = "read_pdb.inp", **kwargs) -> Path:
        """Write a complete FDMNES calculation input.

        Args:
            filename: Destination filename.
            **kwargs: Calculation settings accepted by :meth:`render`.

        Returns:
            Path: Destination of the written input file.
        """
        destination = Path(filename)
        content = self.render(**kwargs)
        destination.write_text(content, encoding="utf-8")
        return destination
