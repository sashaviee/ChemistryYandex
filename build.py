import os
import sys
import subprocess
import shutil


def build_executable():
    """Сборка приложения в исполняемый файл"""

    # Создание spec файла для PyInstaller
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_window.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('chemical_elements.db', '.'),
    ],
    hiddenimports=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ChemicalCalculator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='chemical_icon.ico',
)
"""

    # Запись spec файла
    with open('chemical_calculator.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)

    # Запуск PyInstaller
    try:
        subprocess.run(['pyinstaller', 'chemical_calculator.spec', '--onefile', '--windowed'], check=True)
        print("✅ Сборка завершена успешно!")
        print("📁 Исполняемый файл находится в папке 'dist'")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при сборке: {e}")
    except FileNotFoundError:
        print("❌ PyInstaller не найден. Установите его: pip install pyinstaller")


if __name__ == "__main__":
    build_executable()