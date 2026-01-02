@echo off
setlocal

echo Setting up environment...

set IDF_PATH=C:\Users\Mia\Documents\esp32chess\esp-idf-v5.5.2
set PYTHON=C:\Users\Mia\.espressif\python_env\idf5.5_py3.11_env\Scripts\python.exe
set PATH=C:\Users\Mia\.espressif\python_env\idf5.5_py3.11_env\Scripts;C:\Users\Mia\.espressif\tools\cmake\3.19.5\bin;C:\Users\Mia\.espressif\tools\ninja\1.12.1;C:\Users\Mia\.espressif\tools\riscv32-esp-elf\esp-14.2.0_20251107\riscv32-esp-elf\bin;%PATH%

echo IDF_PATH=%IDF_PATH%
echo.

cd C:\Users\Mia\Documents\esp32chess\esp32_chess_ai\build

echo Running CMake...
cmake -G Ninja -DCMAKE_TOOLCHAIN_FILE="%IDF_PATH%\tools\cmake\toolchain-esp32p4.cmake" -DIDF_TARGET=esp32p4 ..

if errorlevel 1 (
    echo CMake failed!
    pause
    exit /b 1
)

echo.
echo Running Ninja...
ninja

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
pause