# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Great Pacific Cleanup.

Build with:
    pyinstaller great_pacific_cleanup.spec

Output goes to dist/GreatPacificCleanup/
"""

import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('sounds', 'sounds'),
        ('firebase_config.py', '.'),
    ],
    hiddenimports=[
        'pyrebase',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GreatPacificCleanup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No terminal window
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GreatPacificCleanup',
)
