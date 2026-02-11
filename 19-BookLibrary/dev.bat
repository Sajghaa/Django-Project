@echo off
title Django Dev Launcher

REM ==============================
REM CONFIG
REM ==============================
set PROJECT_ROOT=D:\Coding_Projects\100 Django Projects\19-BookLibrary
set PROJECT_DIR=%PROJECT_ROOT%\quiz_project

REM ==============================
REM AUTO-DETECT VENV
REM ==============================
if exist "%PROJECT_ROOT%\ss_venv\Scripts\activate.bat" (
    set VENV_ACTIVATE=%PROJECT_ROOT%\ss_venv\Scripts\activate.bat
) else if exist "%PROJECT_ROOT%\venv\Scripts\activate.bat" (
    set VENV_ACTIVATE=%PROJECT_ROOT%\venv\Scripts\activate.bat
) else (
    echo ❌ No virtual environment found!
    pause
    exit /b
)

echo ✅ Using venv:
echo %VENV_ACTIVATE%
echo.

REM ==============================
REM OPEN WINDOWS TERMINAL TABS
REM ==============================
wt -w 0 ^
nt cmd /k "title SERVER && cd /d %PROJECT_DIR% && call \"%VENV_ACTIVATE%\" && python manage.py runserver" ^
; nt cmd /k "title MIGRATIONS && cd /d %PROJECT_DIR% && call \"%VENV_ACTIVATE%\"" ^
; nt cmd /k "title TESTS && cd /d %PROJECT_DIR% && call \"%VENV_ACTIVATE%\"" ^
; nt cmd /k "title GIT && cd /d %PROJECT_ROOT% && call \"%VENV_ACTIVATE%\" && if exist .git\index.lock del .git\index.lock && echo ✅ index.lock removed if it existed && git status"

exit
