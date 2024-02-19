# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Livereader/main.py'],
             pathex=['/Users/josh/Projects/LiveReader 2'],
             binaries=[],
             datas=[("MIDI Remote Script", "MIDI Remote Script")],
             hiddenimports=["pynput.keyboard._darwin", "pynput.mouse._darwin"],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='LiveReader',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='LiveReader')
app = BUNDLE(coll,
             name='LiveReader.app',
             icon=None,
             bundle_identifier=None)
