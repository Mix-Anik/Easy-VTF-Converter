import os
import shutil

import PyInstaller.__main__

from pathlib import Path


exe_name = 'VTFChanger'
root_folder = Path(__file__).parent

PyInstaller.__main__.run([
    '--onefile',
    '--noconsole',
    '--clean',
    '-n',
    exe_name,
    'src/gui.py'
])


# cleanup
try:
    os.remove(f'{root_folder}\\{exe_name}.spec')
except OSError as e:
    print(f'Error: {e}')

try:
    shutil.rmtree(f'{root_folder}\\build')
except OSError as e:
    print(f'Error: {e}')
