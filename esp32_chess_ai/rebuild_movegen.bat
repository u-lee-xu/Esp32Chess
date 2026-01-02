@echo off
echo ========================================
echo ESP32 Chess AI - Rebuild with Move Generator
echo ========================================
echo.

REM Set ESP-IDF environment
set IDF_PATH=C:\Users\Mia\Documents\esp32chess\esp-idf-v5.5.2
set PATH=%IDF_PATH%\tools;%PATH%
set PATH=C:\Users\Mia\.espressif\tools\ninja\1.12.1;%PATH%
set PATH=C:\Users\Mia\.espressif\tools\cmake\3.23.2\bin;%PATH%
set PATH=C:\Users\Mia\.espressif\tools\riscv32-esp-elf\esp-14.2.0_20251107\riscv32-esp-elf\bin;%PATH%
set PATH=C:\Users\Mia\.espressif\python_env\idf5.5_py3.11_env\Scripts;%PATH%

echo Cleaning build...
if exist build (
    rmdir /s /q build
)

echo.
echo Configuring project...
mkdir build
cd build
cmake -G Ninja .. -DCMAKE_TOOLCHAIN_FILE=%IDF_PATH%\tools\cmake\toolchain-esp32p4.cmake -DIDF_TARGET=esp32p4

if errorlevel 1 (
    echo CMake configuration failed!
    pause
    exit /b 1
)

echo.
echo Building project...
ninja

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
pause