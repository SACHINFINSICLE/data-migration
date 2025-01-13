import PyInstaller.__main__
import os
import platform
from pathlib import Path

def build_app():
    """Build the desktop application"""
    # Get the current directory
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Determine the correct path separator based on OS
    separator = ';' if platform.system() == 'Windows' else ':'
    
    # Build the application directly without spec file
    PyInstaller.__main__.run([
        'app.py',
        '--name=Header Mapping Tool',
        '--onefile',
        f'--add-data=utils{separator}utils',
        f'--add-data=README.md{separator}.',
        '--hidden-import=streamlit',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--hidden-import=streamlit_option_menu',
        '--clean',
    ])

if __name__ == "__main__":
    build_app()
