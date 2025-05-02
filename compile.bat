@echo off
cd %~dp0

if not exist "venv" (
    echo Virtual environment not found.
    echo Please run setup.py to create the virtual environment.
    pause
    exit /b
)

call venv\Scripts\activate

for /f "delims=" %%a in ('python update_version.py') do set "version=%%a"

pyinstaller --noconsole app.py

python create_archive.py "%version%"

pause