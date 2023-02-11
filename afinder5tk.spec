# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['afinder5tk.py'],
             pathex=[],
             binaries=[],
             datas=[
                 ('./data/computers.db', 'data'), 
                 ('./log/afv5.log', 'log'),
                 ('./images/afinder_icon.png', 'images'),
                 ('./.env','.')
             ],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
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
          name='afinder5tk',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='images/afinder_icon.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='afinder5tk')
app = BUNDLE(coll,
             name='afinder5tk.app',
             icon='./images/afinder_icon.icns',
             bundle_identifier=None)
