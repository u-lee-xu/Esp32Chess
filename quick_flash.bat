@echo off
set IDF_PATH=C:\Users\Mia\Documents\esp32chess\esp-idf-v5.5.2
set PYTHON=C:\Users\Mia\.espressif\python_env\idf5.5_py3.11_env\Scripts\python.exe
set IDF_PYTHON_ENV_PATH=C:\Users\Mia\.espressif\python_env\idf5.5_py3.11_env
set PATH=C:\Users\Mia\.espressif\tools\cmake\3.28.1\bin;C:\Users\Mia\.espressif\tools\ninja\1.12.1;C:\Users\Mia\.espressif\tools\riscv32-esp-elf\esp-14.2.0_20251107\riscv32-esp-elf\bin;C:\Users\Mia\.espressif\tools\esptool_py\11.6.1;%PATH%
set ESP_ROM_ELF_DIR=C:\Users\Mia\.espressif\tools\esp-rom-elfs\20241011

cd C:\Users\Mia\Documents\esp32chess\esp32_chess_ai

echo Building Chess AI...
call %PYTHON% %IDF_PATH%\tools\idf.py build
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo Flashing to COM19...
call %PYTHON% %IDF_PATH%\tools\idf.py -p COM19 flash
if errorlevel 1 (
    echo ERROR: Flash failed
    pause
    exit /b 1
)

echo Done!
pause