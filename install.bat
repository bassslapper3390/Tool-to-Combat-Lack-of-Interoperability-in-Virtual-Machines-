@echo off
echo Installing VM Interoperability Tool...

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Install the package
echo Installing package...
pip install -e .

:: Create necessary directories
echo Creating directories...
mkdir captures 2>nul
mkdir converted 2>nul
mkdir temp 2>nul

:: Create default config
echo Creating configuration...
python -c "from vm_interop.config import Config; Config().save_config()"

echo Installation complete!
echo.
echo To run the GUI:
echo 1. Activate the virtual environment: venv\Scripts\activate
echo 2. Run: python run_gui.py
echo.
echo To run the command-line tool:
echo 1. Activate the virtual environment: venv\Scripts\activate
echo 2. Run: vm-interop --help 