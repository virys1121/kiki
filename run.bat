@echo off
setlocal enabledelayedexpansion

echo Checking for Python...
set PYTHON_CMD=python
%PYTHON_CMD% --version >nul 2>&1
if !errorlevel! neq 0 (
    set PYTHON_CMD=py
    !PYTHON_CMD! --version >nul 2>&1
    if !errorlevel! neq 0 (
        echo ERROR: Python not found. Please install Python and add it to your PATH.
        pause
        exit /b 1
    )
)

echo Using !PYTHON_CMD!

if not exist venv (
    echo Creating virtual environment...
    !PYTHON_CMD! -m venv venv
    if !errorlevel! neq 0 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: venv\Scripts\activate.bat not found.
    pause
    exit /b 1
)

echo Upgrading pip and installing requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install Pillow

if not exist database.db (
    echo Initializing database...
    python -c "import sqlite3; conn = sqlite3.connect('database.db'); f = open('init_db.sql', 'r', encoding='utf-8'); conn.executescript(f.read()); conn.close(); f.close(); print('Database initialized successfully.')"
)

echo Starting the application...
python app.py

pause
