import PyInstaller.__main__

PyInstaller.__main__.run([
   'sticky_notes.py',
   '--onefile',
   '--windowed',
   "--icon=sticky_notes.ico"
])