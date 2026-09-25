@echo off
setlocal enabledelayedexpansion
title Push Wortschatz to GitHub Pages
cd /d "%~dp0"

echo ==============================================
echo   Pushing Wortschatz Web to GitHub Pages
echo ==============================================
echo.

where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in PATH!
    pause
    exit /b 1
)

if not exist ".git" (
    git init
    git remote add origin https://github.com/ivanadriman/wortschatz.git
    git branch -M main
)

git remote get-url origin >nul 2>nul
if %errorlevel% neq 0 (
    git remote add origin https://github.com/ivanadriman/wortschatz.git
)

echo [*] Staging changes...
git add -A

set "commit_msg="
set /p "commit_msg=Enter commit message (or press Enter for 'Update Wortschatz'): "
if not defined commit_msg set "commit_msg=Update Wortschatz"

git commit -m "!commit_msg!" >nul 2>&1

echo.
echo [*] Pushing to GitHub...
echo.

git push -u origin main --force
if %errorlevel% neq 0 goto :on_error

:on_success
echo.
echo ==============================================
echo   [SUCCESS] Live on GitHub Pages!
echo   https://ivanadriman.github.io/wortschatz/
echo ==============================================
echo.
pause
exit /b 0

:on_error
echo.
echo ==============================================
echo   [ERROR] Push failed! Check your connection.
echo ==============================================
echo.
pause
exit /b 1
