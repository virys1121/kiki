@echo off
echo Setting up virtual environment...
python -m venv venv
echo Activating...
call venv\Scripts\activate
echo Installing...
pip install -r requirements.txt
pip install Pillow
if not exist database.db (
    sqlite3 database.db < init_db.sql
)
echo Running...
python app.py
pause