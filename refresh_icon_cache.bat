@echo off
echo ========================================
echo  Refresh Windows Icon Cache
echo ========================================
echo.
echo Clearing icon cache...
echo.

rem Delete icon cache files
taskkill /F /IM explorer.exe >nul 2>&1
timeout /t 2 /nobreak >nul

del /a /q "%localappdata%\IconCache.db" >nul 2>&1
del /a /f /q "%localappdata%\Microsoft\Windows\Explorer\iconcache*" >nul 2>&1

echo Icon cache cleared.
echo.
echo Restarting Windows Explorer...
start explorer.exe

timeout /t 2 /nobreak >nul
echo.
echo ========================================
echo  Done! Icon should now be refreshed.
echo ========================================
echo.
pause
