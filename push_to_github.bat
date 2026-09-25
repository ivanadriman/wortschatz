@echo off
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

REM 3. Verify remote origin exists
git remote get-url origin >nul 2>nul
if %errorlevel% neq 0 (
    git remote add origin https://github.com/ivanadriman/wortschatz.git
)

REM 4. Show current status
echo [Current Git Status]
git status --short
echo.

REM 5. Stage all changes
git add .

REM Check if there are changes to commit
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo [*] No new changes to commit.
    echo.
    set /p force_push="Do you want to force push current state to GitHub anyway? (y/n): "
    if /i "%force_push%"=="y" (
        git push -u origin main
    )
    goto finish
)

REM 6. Get commit message
set /p commit_msg="Enter commit message (or press Enter for 'Update Wortschatz web app'): "
if "%commit_msg%"=="" set commit_msg=Update Wortschatz web app

git commit -m "%commit_msg%"
echo.
echo [*] Pushing to GitHub (main branch)...
git push -u origin main

:finish
echo.
echo ==============================================
echo   Done! Your updates are on GitHub.
echo   Check your live site in 1-2 minutes:
echo   https://ivanadriman.github.io/wortschatz/
echo ==============================================
pause
