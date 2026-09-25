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

REM 4. Stage all changes
git add .

REM Check if there are changes to commit
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo [*] Working tree clean. Preparing to push...
) else (
    set /p commit_msg="Enter commit message (or press Enter for 'Update Wortschatz web app'): "
    if "%commit_msg%"=="" set commit_msg=Update Wortschatz web app
    git commit -m "%commit_msg%"
)

echo.
echo [*] Syncing with remote repository...
REM Pull remote changes with allow-unrelated-histories to reconcile initial commits
git pull origin main --rebase --allow-unrelated-histories 2>nul
if %errorlevel% neq 0 (
    echo [*] Reconciling branch heads...
    git pull origin main --no-rebase --allow-unrelated-histories -X ours --no-edit 2>nul
)

echo.
echo [*] Pushing to GitHub (main branch)...
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo [!] Standard push rejected. Remote has different commit history.
    set /p do_force="Overwrite GitHub with these local files? (Recommended for first deploy) (y/n): "
    if /i "%do_force%"=="y" (
        echo [*] Force pushing to main branch...
        git push -u origin main --force
    )
)

echo.
echo ==============================================
echo   Done! Your updates are on GitHub.
echo   Check your live site in 1-2 minutes:
echo   https://ivanadriman.github.io/wortschatz/
echo ==============================================
pause
