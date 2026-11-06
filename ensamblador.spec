# -*- mode: python ; coding: utf-8 -*-
# Genera ensamblador.exe (un solo archivo, sin consola). Se compila con compilar_exe.bat.

a = Analysis(
    ['principal.py'],
    excludes=[
        'unittest', 'email', 'http', 'xml', 'pydoc', 'asyncio',
        'multiprocessing', 'sqlite3', 'ssl', 'bz2', 'lzma',
        'doctest', 'pdb', 'difflib', 'hashlib', '_hashlib',
        'decimal', '_decimal', 'socket', '_socket', 'select',
        'concurrent', 'inspect', 'ast',
        'dis', 'opcode', 'calendar', 'datetime', 'argparse',
        'pickle', '_compat_pickle', 'codeop', 'subprocess',
        'zipfile', 'tarfile', 'gzip', 'csv', 'shutil', 'tempfile', 'unicodedata',
    ],
    optimize=2,
)

BINARIOS_SOBRANTES = {'unicodedata.pyd', 'libcrypto-1_1.dll', 'libcrypto-3.dll', '_hashlib.pyd',
                      '_decimal.pyd', '_socket.pyd', 'select.pyd'}
a.binaries = [x for x in a.binaries if x[0] not in BINARIOS_SOBRANTES]


def dato_sobrante(destino):
    """Datos de Tcl/Tk que el programa no usa: zonas horarias, traducciones, imágenes, etc."""
    ruta = destino.replace('\\', '/')
    if ruta.startswith('_tcl_data/encoding/'):
        return not ruta.endswith('/cp1252.enc')          # codificación de Windows en español
    return ruta.startswith(('_tcl_data/tzdata/', '_tcl_data/msgs/', '_tcl_data/http1.0/',
                            '_tk_data/images/', '_tk_data/msgs/', 'tcl8/8.4/', 'tcl8/8.6/')) \
        or 'tcltest' in ruta


a.datas = [x for x in a.datas if not dato_sobrante(x[0])]

pyz = PYZ(a.pure, optimize=2)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ensamblador',
    upx=True,
    console=False,
)
