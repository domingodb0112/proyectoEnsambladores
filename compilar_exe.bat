@echo off
rem Genera ensamblador.exe con PyInstaller (requiere Python 3.10+ en el PATH)
python -m pip install pyinstaller
python -m PyInstaller --clean ensamblador.spec
if exist dist\ensamblador.exe (
    copy /Y dist\ensamblador.exe ensamblador.exe
    echo.
    echo Listo: ensamblador.exe
) else (
    echo.
    echo No se pudo generar el ejecutable.
)
pause
