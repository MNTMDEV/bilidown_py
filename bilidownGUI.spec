# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['bilidownGUI.pyw'],
             pathex=[],
             binaries=[('*.dll', '.')],
             datas=[('assets', 'assets')],
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
          name='bilidownGUI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , version='bilidownGUI_version_info.txt', icon='assets\\image\\favicon.ico')

b = Analysis(['register_protocol.pyw'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz2 = PYZ(b.pure, b.zipped_data,
             cipher=block_cipher)

exe2 = EXE(pyz2,
          b.scripts, 
          [],
          exclude_binaries=True,
          name='register_protocol',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , version='register_version_info.txt', icon='assets\\image\\favicon.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               exe2,
               b.binaries,
               b.zipfiles,
               b.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='bilidownGUI')
