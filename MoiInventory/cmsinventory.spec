# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_django.py'],
    pathex=['.'],  # Assuming you run PyInstaller from the project root
    binaries=[],
    datas=[
        # Dashboard app templates
        ('dashboard/templates', 'dashboard/templates'),
        
        # Authentication app templates
        ('authentication/templates', 'authentication/templates'),
        
        # SQLite database file
        ('db.sqlite3', '.'),
    ],
       hiddenimports=[
        'django.db.backends.mysql.base',
        'django.db.backends.oracle.base',
        'django.db.backends.postgresql.base',
        'django.db.backends.sqlite3.base',
        'django.contrib.sessions.templatetags',
        'django.contrib.auth.templatetags',
        'django.contrib.staticfiles.templatetags',
        'django.contrib.admin.context_processors',
        'django.contrib.sessions.context_processors',
        'django.contrib.messages.templatetags',
        'django.contrib.contenttypes.context_processors',
        'django.contrib.contenttypes.templatetags',
        'django.contrib.staticfiles.context_processors',
        'django.template.context_processors',
        'django.contrib.auth.context_processors',
        'django.contrib.sessions.context_processors',
        'django.contrib.staticfiles.templatetags',
        'dashboard.templatetags',
        'authentication.templatetags',
        'dashboard.context_processors',
        'authentication.context_processors',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MoiInventory',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
