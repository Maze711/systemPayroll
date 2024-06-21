import os
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication

def load_fonts():
    font_dir = os.path.join(os.path.dirname(__file__), 'ResourceS', 'Fonts')
    font_db = QFontDatabase()

    # List all font files in the directory
    font_files = [os.path.join(font_dir, f) for f in os.listdir(font_dir) if f.endswith('.ttf') or f.endswith('.otf')]

    print(font_files)
    # Load each font file into the QFontDatabase
    for font_file in font_files:
        font_id = font_db.addApplicationFont(font_file)
        if font_id != -1:
            font_family = font_db.applicationFontFamilies(font_id)[0]
            font = QFont(font_family)
            font.setPointSize(12)  # Example: Set default point size
            QApplication.instance().setFont(font)
        else:
            print(f"Failed to load font: {font_file}")

    print("Fonts loaded successfully.")
