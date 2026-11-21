#!/usr/bin/env python3
"""Regression tests for all-site convolution job generation."""

from fdmnes_util.fdm_convolution_inputs import FdmConvolutionInputs


def test_allsite_convolution_inputs(tmp_path):
    """Create jobs only for numbered spectra and retain their names."""
    (tmp_path / "Fe_1.txt").write_text("sample", encoding="utf-8")
    (tmp_path / "Fe_2.txt").write_text("sample", encoding="utf-8")
    (tmp_path / "Fe_conv.txt").write_text("sample", encoding="utf-8")
    (tmp_path / "Fe_1_conv.txt").write_text("sample", encoding="utf-8")

    writer = FdmConvolutionInputs()
    inputs = writer.write(str(tmp_path / "Fe"), tmp_path)

    assert inputs == ["conv_1.inp", "conv_2.inp"]
    first_input = (tmp_path / "conv_1.inp").read_text(encoding="utf-8")
    assert "Fe_1.txt" in first_input
    assert "Fe_1_conv.txt" in first_input
    job_list = (tmp_path / "fdmfile.txt").read_text(encoding="utf-8")
    assert "2\nconv_1.inp\nconv_2.inp" in job_list
