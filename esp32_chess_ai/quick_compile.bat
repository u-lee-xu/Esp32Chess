@echo off
setlocal

set IDF_PATH=C:\Users\Mia\Documents\esp32chess\esp-idf-v5.5.2
set PATH=C:\Users\Mia\.espressif\tools\ninja\1.12.1;%PATH%
set PATH=C:\Users\Mia\.espressif\tools\cmake\3.23.2\bin;%PATH%
set PATH=C:\Users\Mia\.espressif\tools\riscv32-esp-elf\esp-14.2.0_20251107\riscv32-esp-elf\bin;%PATH%
set PATH=C:\Users\Mia\.espressif\python_env\idf5.5_py3.9_env\Scripts;%PATH%

echo Building project...
python %IDF_PATH%\tools\idf.py build

pause