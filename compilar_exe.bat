@echo off
rem Genera ensamblador.exe. Usa Python 3.10 con tkinter si esta instalado (el .exe pesa menos).
set PY=python
py -3.10 -c "import tkinter" >nul 2>&1 && set PY=py -3.10
%PY% -m pip install -q pyinstaller
rem UPX (si esta instalado) comprime el .exe
set UPX=--lzma
%PY% -m PyInstaller --clean --noconfirm ensamblador.spec
if exist dist\ensamblador.exe (
    copy /Y dist\ensamblador.exe ensamblador.exe
    echo Listo: ensamblador.exe
) else (
    echo No se pudo generar el ejecutable.
)
pause
