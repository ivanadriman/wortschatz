@echo off
setlocal enabledelayedexpansion
title Push Wortschatz to GitHub Pages
cd /d "%~dp0"

echo ==============================================
echo   Pushing Wortschatz Web to GitHub Pages
echo ==============================================
echo.

REM 1. Verify Git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git is not found in your system PATH!
    echo Please install Git from https://git-scm.com/
    echo.
    pause
    exit /b 1
)

REM 2. Check if git repository is initialized
if not exist ".git" (
    echo [*] Initializing local git repository in this folder...
    git init
    git remote add origin https://github.com/ivanadriman/wortschatz.git
    git branch -M main
    echo [*] Git repo initialized and linked to ivanadriman/wortschatz.
    echo.
)

REM 3. Verify remote origin exists and is correct
git remote get-url origin >nul 2>nul
if %errorlevel% neq 0 (
    git remote add origin https://github.com/ivanadriman/wortschatz.git
)

REM 4. Stage all changes
echo [*] Staging all files and audio clips...
git add -A

REM 5. Prompt for commit message
set "commit_msg="
set /p "commit_msg=Enter commit message (or press Enter for 'Update Wortschatz web app'): "
if not defined commit_msg set "commit_msg=Update Wortschatz web app"

REM Attempt commit (safe if nothing changed)
git commit -m "!commit_msg!" 2>nul
if %errorlevel% neq 0 (
    echo [*] No uncommitted changes detected. Proceeding to push...
)

echo.
echo [*] Pushing to GitHub (main branch)...
echo (Uploading ~6 MB of neural audio and web files...)
echo.

git push -u origin main --force
set "PUSH_STATUS=%errorlevel%"

echo.
if %PUSH_STATUS% equ 0 (
    echo ==============================================
    echo   [SUCCESS] Your updates and audio are live on GitHub!
    echo   Visit your app:
    echo   https://ivanadriman.github.io/wortschatz/
    echo ==============================================
) else (
    echo ==============================================
    echo   [ERROR] Push failed with code %PUSH_STATUS%.
    echo   Common causes:
    echo   1. Network issue / DNS (Could not resolve host)
    echo   2. GitHub login credentials required.
    echo ==============================================
)

echo.
pause
