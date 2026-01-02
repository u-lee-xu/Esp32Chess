@echo off
setlocal

echo ========================================
echo ESP32-P4 Chess AI - Rebuild Script
echo ========================================
echo.

REM Set ESP-IDF path
set IDF_PATH=C:\Users\Mia\Documents\esp32chess\esp-idf-v5.5.2
echo ESP-IDF Path: %IDF_PATH%
echo.

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

REM Configure project
echo Configuring project...
idf.py reconfigure

if errorlevel 1 (
    echo ERROR: Configuration failed
    pause
    exit /b 1
)

echo.
echo Configuration completed
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
pause