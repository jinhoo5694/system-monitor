# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['system_monitor.py'],
    pathex=[],
    binaries=[],
    datas=[('ironman/cache', 'ironman/cache')],
    hiddenimports=['PIL._tkinter_finder', 'psutil'],
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
    [],
    exclude_binaries=True,
    name='JarvisMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JarvisMonitor',
)
app = BUNDLE(
    coll,
    name='JarvisMonitor.app',
    icon=None,
    bundle_identifier=None,
)
