@echo off
REM ESP32 Chess AI Build Script
REM This script sets up ESP-IDF environment and builds the project

echo ========================================
echo ESP32-P4 Chess AI Build Script
echo ========================================
echo.

REM Set ESP-IDF path
set IDF_PATH=C:\Users\Mia\Documents\esp32chess\esp-idf-v5.5.2

echo ESP-IDF Path: %IDF_PATH%
echo.

REM Check if ESP-IDF exists
if not exist "%IDF_PATH%" (
    echo ERROR: ESP-IDF not found at %IDF_PATH%
    echo Please download ESP-IDF first
    pause
    exit /b 1
)

REM Activate ESP-IDF environment
echo Activating ESP-IDF environment...
call "%IDF_PATH%\export.bat"

if errorlevel 1 (
    echo ERROR: Failed to activate ESP-IDF environment
    pause
    exit /b 1
)

echo.
echo ESP-IDF environment activated successfully
echo.

REM Set target to ESP32-P4
echo Setting target to ESP32-P4...
idf.py set-target esp32p4

if errorlevel 1 (
    echo ERROR: Failed to set target
    pause
    exit /b 1
)

echo.
echo Target set to ESP32-P4 successfully
echo.

REM Build the project
echo Building project...
idf.py build

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Connect ESP32-P4 to your computer
echo 2. Run: flash.bat to flash the firmware
echo.
pause