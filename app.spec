# -*- mode: python ; coding: utf-8 -*-

datas = [
    ('src/assets', 'src/assets'),
    ('src/components', 'src/components'),
    ('src/config', 'src/config'),
    ('src/controller', 'src/controller'),
    ('src/interface', 'src/interface'),
    ('src/models', 'src/models'),
    ('src/service', 'src/service'),
    ('src/utils', 'src/utils'),
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'flet',
        'openpyxl',
        'pandas',
        'lxml'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(  
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='Extrator CF-e',
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
    icon='src/assets/icone.ico',
    onefile=True
)

