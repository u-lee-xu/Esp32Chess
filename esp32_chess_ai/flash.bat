@echo off
REM ESP32 Chess AI Flash Script
REM This script flashes the firmware to ESP32-P4

echo ========================================
echo ESP32-P4 Chess AI Flash Script
echo ========================================
echo.

REM Set ESP-IDF path
set IDF_PATH=C:\Users\Mia\Documents\esp32chess\esp-idf-v5.5.2

echo ESP-IDF Path: %IDF_PATH%
echo.

REM Check if ESP-IDF exists
if not exist "%IDF_PATH%" (
    echo ERROR: ESP-IDF not found at %IDF_PATH%
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

REM Check for connected device
echo Checking for ESP32-P4 device...
echo.
echo Available COM ports:
mode
echo.

echo.
echo Flashing firmware to COM19...
echo.

REM Flash and monitor
idf.py -p COM19 flash monitor

if errorlevel 1 (
    echo.
    echo ERROR: Flash/Monitor failed
    echo Please check:
    echo 1. ESP32-P4 is connected
    echo 2. Correct COM port is selected
    echo 3. Drivers are installed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Flash completed successfully!
echo ========================================
echo.

pause