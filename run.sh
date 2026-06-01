#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install Pillow
if [ ! -f "database.db" ]; then
    sqlite3 database.db < init_db.sql
fi
python3 app.py
