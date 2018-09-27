# -*- mode: python -*-

block_cipher = None


a = Analysis(['Aurora_Copy_database.py'],
             pathex=['E:\\code\\DB_Script\\Copy_Database'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Aurora_Copy_database',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
