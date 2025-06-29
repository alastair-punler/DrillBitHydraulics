@echo off

set VENV_NAME=.venv
set REQUIREMENTS=requirements.txt

echo Creating virtual environment...
python -m venv %VENV_NAME%

echo Activating virtual environment...
call %VENV_NAME%\Scripts\activate.bat

if exist %REQUIREMENTS% (
    echo Installing packages...
    python -m pip install -r %REQUIREMENTS%
)

echo Virtual environment setup complete. To activate, run "%VENV_NAME%\Scripts\activate.bat"

echo Creating .gitignore file...
echo # Virtual environment folder
echo %VENV_NAME%/ >> .gitignore

git config --global user.name  alastair-punler
git config --global user.email alastair.punler@woodside.com.au

echo .gitignore file created.


echo Running ipython kernel install...
::python m ipython kernel install --name %VENV_NAME% --user
python -m ipykernel install --user --name=%VENV_NAME%
echo Setup complete.
echo %VENV_NAME%
