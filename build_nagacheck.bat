@echo off
echo ================================
echo Building nagacheck - Database Maintenance Tool
echo ================================
echo.

echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist\nagacheck.exe del /q dist\nagacheck.exe

echo.
echo Building executable with PyInstaller...
py -m PyInstaller --clean nagacheck.spec

echo.
if exist dist\nagacheck.exe (
    echo ================================
    echo Build Successful!
    echo ================================
    echo Executable location: dist\nagacheck.exe
    echo.
    echo File ready for distribution!
    echo.
) else (
    echo ================================
    echo Build Failed!
    echo ================================
    echo Please check the error messages above.
    echo.
)

pause
