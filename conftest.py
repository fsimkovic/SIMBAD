import mock
import os
import pytest
import sys

os.environ['PYTEST_SIMBAD_TEST'] = 'true'
os.environ['CCP4'] = os.environ['CCP4_SCR'] = '.'

mock_modules = [
    'cctbx',
    'cctbx.crystal',
    'cctbx.uctbx',
    'cctbx.xray',
    'iotbx',
    'iotbx.pdb',
    'iotbx.pdb.amino_acid_codes',
    'iotbx.pdb.fetch',
    'iotbx.reflection_file_utils',
    'mmtbx',
    'mmtbx.scaling',
    'mmtbx.scaling.matthews',
    'phaser',
    'pyrvapi',
]
for module in mock_modules:
    sys.modules[module] = mock.MagicMock()
