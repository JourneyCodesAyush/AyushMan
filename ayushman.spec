a = Analysis(
    ['src/ayushman/__main__.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('src/ayushman', 'ayushman'),
    ],
    hiddenimports=['ayushman', 'importlib.metadata'],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='ayushman',
    console=True,
    onefile=True,
)
