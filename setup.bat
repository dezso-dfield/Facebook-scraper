:: setup.bat

@echo off
setlocal

set "VENV_DIR=venv"

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Creating virtual environment in "%VENV_DIR%"...
    python -m venv "%VENV_DIR%"
) else (
    echo Virtual environment already exists.
)

echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

echo Upgrading pip...
pip install --upgrade pip

echo Installing requirements.txt...
pip install -r requirements.txt

echo Installing Playwright...
pip install playwright

echo Installing Playwright browsers (this may take a moment)...
playwright install

echo.
echo Setup complete!
endlocal
