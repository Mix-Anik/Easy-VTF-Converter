import itertools
import pytest
import os
import re
import subprocess
import shutil

from pathlib import Path

from src.vtf_structs import VTFFile


SAMPLES_FOLDER_PATH = f'{Path(__file__).parent}\\samples'
SAMPLES_PATHS = [f'{absp}\\{fname}' for (absp, _, fnames) in os.walk(SAMPLES_FOLDER_PATH) for fname in fnames]
TEST_PARAM_LIST = [tuple([f, *v]) for v in itertools.product(range(6), repeat=2) for f in SAMPLES_PATHS]


class TestVTFChanger:

    def setup_class(self):
        self.VTFCMD_path = '<vtfcmd.exe absolute path here>'
        self.temp_fname = 'temp'

    @pytest.mark.parametrize('file_path,from_version,to_version', TEST_PARAM_LIST)
    def test_conversion(self, file_path: str, from_version: int, to_version: int):
        temp_file_path = f'{SAMPLES_FOLDER_PATH}\\{self.temp_fname}.vtf'
        shutil.copyfile(file_path, temp_file_path)
        self._convert_texture_to_version(temp_file_path, from_version)
        self._convert_texture_to_version(temp_file_path, to_version)
        self._validate_vtf(temp_file_path)

    def _convert_texture_to_version(self, texture_path: str, to_version: int):
        with open(texture_path, mode="r+b") as tex_file:
            bytelist = tex_file.read()

        vtf = VTFFile(bytelist)
        vtf.convert(to_version)

        with open(texture_path, 'wb') as tex_file:
            tex_file.write(vtf.compose())

    def _validate_vtf(self, vtf_abs_path: str):
        output = subprocess.check_output([self.VTFCMD_path, '-exportformat', 'tga', '-file', vtf_abs_path])
        is_successful = re.findall(rb'1/1 files completed.', output)

        assert is_successful, 'VTF ended up being corrupted during conversion'

    def teardown(self):
        # cleanup
        temp_file_path = f'{SAMPLES_FOLDER_PATH}\\{self.temp_fname}'

        try:
            os.remove(f'{temp_file_path}.vtf')
        except OSError:
            pass

        try:
            os.remove(f'{temp_file_path}.tga')
        except OSError:
            pass
