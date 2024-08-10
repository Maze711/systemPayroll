from MainFrame.Resources.lib import *
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_fonts():
    font_dir = (resource_path("MainFrame\\Resources\\Fonts"))
    font_db = QFontDatabase()

    # List all font files in the directory
    font_files = [os.path.join(font_dir, f) for f in os.listdir(font_dir) if f.endswith('.ttf') or f.endswith('.otf')]

    #print(font_files)
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
