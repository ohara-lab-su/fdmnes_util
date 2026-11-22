"""Check the SCF records added by the explicit 2026 BAV reader."""

from fdmnes_util.fdm_bav_2020 import FdmBav2020
from fdmnes_util.fdm_bav_2026 import FdmBav2026


def test_reads_scf_records_and_ignores_other_numbers(tmp_path):
    """Read the reported cycle and energy from the 2026 SCF line forms."""
    log = tmp_path / "Fe_SCF_bav.txt"
    log.write_text(
        " FDMNES program, Revision 5th of November 2026\n"
        " Threshold: Iron K1 edge\n"
        " Self consistent calculation\n"
        " Maximum number of iteration = 30\n"
        " Excited atom total energy = -2.74438E+04 eV\n"
        " Cycle   1,  Fermi energy = -9.371 eV, Occupancy val abs = 3.492\n"
        " Cycle   2,  Fermi energy = -10.211 eV, Occupancy val abs = 6.430\n"
        " Total energy = -4.38755D+04 eV, Delta energy = 1329.203 > 0.700 eV\n"
        " Cycle   8,  Fermi energy = -10.115 eV, Occupancy val abs = 6.127\n"
        " Total energy = -43792.8 eV, Delta energy = 0.678 < 0.700 eV\n"
        " Weight = 0.02500. Converged !\n"
        " Last cycle, XANES calculation\n"
    )

    reader = FdmBav2026(log)
    base = FdmBav2020(log)
    assert reader.get_edge() == base.get_edge() == "Iron K1 edge"
    assert reader.get_max_scf_iterations() == base.get_max_scf_iterations() == 30
    assert reader.get_n_scf_loop() == 8
    assert reader.get_scf_toten() == [-43875.5, -43792.8]
    assert base.get_n_scf_loop() == 0
    assert base.get_scf_toten() == []


def test_leaves_non_scf_fermi_cycle_out_of_scf_history(tmp_path):
    """A Fermi-only calculation can have a cycle entry without an SCF run."""
    log = tmp_path / "Ni_bav.txt"
    log.write_text(
        " FDMNES program, Revision 5th of November 2026\n"
        " Magnetic calculation without spin-orbit interaction\n"
        " Cycle   1, Fermi Energy = -11.054 eV\n"
    )

    reader = FdmBav2026(log)
    assert reader.get_nspin() == 2
    assert reader.get_n_scf_loop() == 0
    assert reader.get_scf_toten() == []


def test_retains_support_for_the_existing_scf_records(tmp_path):
    """Keep the inherited behavior for the older SCF marker spellings."""
    log = tmp_path / "older_bav.txt"
    log.write_text(
        " Self consistent calculation\n"
        " Begining of cycle 3\n"
        " Unit cell energy = -1200 eV\n"
    )

    reader = FdmBav2026(log)
    assert reader.get_n_scf_loop() == 3
    assert reader.get_scf_toten() == [-1200.0]
