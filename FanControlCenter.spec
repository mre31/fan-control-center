# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Uygulama\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('Uygulama/src', 'src')],
    hiddenimports=['win32api', 'win32event', 'winerror', 'wmi', 'keyboard', 'PySide6'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FanControlCenter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Uygulama\\src\\assets\\app.ico'],
    manifest='Uygulama\\src\\app.manifest',
)
