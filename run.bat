@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo       Wortschatz - German Flashcards
echo ==========================================
echo.

where python >nul 2>&1
if errorlevel 1 goto :no_python

python -c "import customtkinter" >nul 2>&1
if errorlevel 1 goto :install_deps

:launch
echo Starting Wortschatz...
start "" pythonw wortschatz_app.py
if errorlevel 1 (
    python wortschatz_app.py
)
exit /b 0

:install_deps
echo Installing required packages...
python -m pip install -r requirements.txt
if errorlevel 1 goto :deps_failed
goto :launch

:no_python
echo [ERROR] Python was not found on your system!
echo Please ensure Python is installed and added to PATH.
echo.
pause
exit /b 1

:deps_failed
echo.
echo [ERROR] Failed to install required packages.
pause
exit /b 1
