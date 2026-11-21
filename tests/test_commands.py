from pathlib import Path
import shutil
import numpy as np
import pytest
from fdmnes_util.commands import fd_clean, fd_move, fd_conv_e2photoe, fd_getfermi
from fdmnes_util.commands import fd_make_conv_allsite, fd_bav2xyz, fd_xas, fd_ldos

F = Path(__file__).parent / 'fixtures'


def prepare(tmp_path):
    for name in ('Fe.txt', 'Fe_conv.txt', 'Fe_sd0.txt', 'Fe_bav.txt'):
        shutil.copy(F / name, tmp_path / name)
    (tmp_path / 'read_pdb.inp').write_text('Filout\n  Fe\nEND\n')


def test_getfermi_and_conversion(tmp_path, monkeypatch, capsys):
    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    fd_getfermi.main([])
    assert '7112.0' in capsys.readouterr().out
    fd_conv_e2photoe.main([])
    data = np.loadtxt('Fe_conv_photoe.txt')
    assert np.isclose(data[0, 0], 7097.0)


def test_clean(tmp_path, monkeypatch):
    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    fd_clean.main([])
    assert not (tmp_path / 'Fe_sd0.txt').exists()
    assert not (tmp_path / 'Fe.txt').exists()
    assert (tmp_path / 'read_pdb.inp').exists()


def test_move(tmp_path, monkeypatch):
    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    fd_move.main(['-d', 'archive'])
    assert (tmp_path / 'archive/Fe_bav.txt').is_file()
    assert not (tmp_path / 'Fe_bav.txt').exists()
    assert (tmp_path / 'read_pdb.inp').exists()


def test_bav2xyz_real_data(tmp_path, capsys):
    path = tmp_path/'Fe_bav.txt'
    shutil.copy(F/'Fe_bav.txt',path)
    fd_bav2xyz.main([str(path).removesuffix('_bav.txt')])
    xyz=tmp_path/'Fe.xyz'
    assert xyz.exists()
    lines=xyz.read_text().splitlines()
    assert lines[2].startswith('Fe ')
    assert lines[3].startswith('O ')


def test_convolution_allsite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path/'conv.inp').write_text('Filout\n Fe\nEND\n')
    for i in (1,2):(tmp_path/f'Fe_{i}.txt').write_text('data\n')
    fd_make_conv_allsite.main([])
    assert (tmp_path/'fdmfile.txt').exists()
    assert (tmp_path/'conv_2.inp').exists()


def test_plotting_cli(tmp_path, monkeypatch):
    pytest.importorskip('matplotlib')
    prepare(tmp_path)
    monkeypatch.chdir(tmp_path)
    fd_xas.main(['-i','Fe','-o','xas.pdf'])
    fd_ldos.main(['-i','Fe','--year','2020','-o','ldos.pdf'])
    assert (tmp_path/'xas.pdf').stat().st_size>100
    assert (tmp_path/'ldos.pdf').stat().st_size>100
