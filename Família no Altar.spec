# -*- mode: python ; coding: utf-8 -*-


from PyInstaller.utils.hooks import collect_all

datas_pyqt, binaries_pyqt, hiddenimports_pyqt = collect_all('PySide6')

a = Analysis(
    ['main.py'],
    pathex=['src'],
    binaries=binaries_pyqt,
    datas=[
        ('assets\\icone.ico', 'assets'),
        ('imagens\\logo-ipbsg.png', 'imagens')
    ] + datas_pyqt,
    hiddenimports=hiddenimports_pyqt,
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
    a.zipfiles,
    a.datas,
    [],
    name='Família no Altar',
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
    icon=['assets\\icone.ico'],
)
