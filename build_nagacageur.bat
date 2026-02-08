@echo off
echo ================================
echo Building NagaCageur - Database Maintenance Tool
echo ================================
echo.

echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist\NagaCageur.exe del /q dist\NagaCageur.exe

echo.
echo Building executable with PyInstaller...
py -m PyInstaller --clean NagaCageur.spec

echo.
if exist dist\NagaCageur.exe (
    echo ================================
    echo Build Successful!
    echo ================================
    echo Executable location: dist\NagaCageur.exe
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
