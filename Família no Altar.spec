# -*- mode: python ; coding: utf-8 -*-


from PyInstaller.utils.hooks import collect_submodules

hidden = []
hidden += collect_submodules('PySide6')
hidden += ['win32com', 'win32com.client']

a = Analysis(
    ['main.py'],
    pathex=['src'],
    binaries=[],
    datas=[('dados', 'dados'), ('imagens', 'imagens')],
    hiddenimports=hidden,
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
    icon=['C:\\Users\\Myelin\\OneDrive\\Documentos\\icone.ico'],
)
