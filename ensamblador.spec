# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['principal.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'unittest', 'email', 'http', 'xml', 'pydoc', 'asyncio',
        'multiprocessing', 'sqlite3', 'ssl', 'bz2', 'lzma',
        'doctest', 'pdb', 'difflib', 'hashlib', '_hashlib',
        'decimal', '_decimal', 'socket', '_socket', 'select',
        'urllib', 'concurrent', 'inspect', 'ast',
        'dis', 'opcode', 'calendar', 'datetime', 'argparse',
        'pickle', '_compat_pickle', 'codeop', 'subprocess',
        'zipfile', 'tarfile', 'gzip', 'csv', 'shutil', 'tempfile'
    ],
    noarchive=False,
    optimize=2,
)

excluded_binaries = {'libcrypto-3.dll', '_hashlib.pyd', '_decimal.pyd', '_socket.pyd', 'select.pyd'}
a.binaries = [x for x in a.binaries if x[0] not in excluded_binaries]

pyz = PYZ(a.pure, optimize=2)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ensamblador',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
