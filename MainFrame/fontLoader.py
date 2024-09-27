from MainFrame.Resources.lib import *
from PIL import ImageFont
from MainFrame.systemFunctions import globalFunction


def load_fonts():
    font_dir = (globalFunction.resource_path("MainFrame\\Resources\\Fonts"))

    # List all font files in the directory
    font_files = [os.path.join(font_dir, f) for f in os.listdir(font_dir) if f.endswith('.ttf') or f.endswith('.otf')]
    print(font_files)

    loaded_fonts = {}

    for font_file in font_files:
        try:
            font_name = os.path.basename(font_file)
            font = ImageFont.truetype(font_file, size=5)
            loaded_fonts[font_name] = font
            print(f"Loaded font: {font_name}")
        except Exception as e:
            print(f"Failed to load font: {font_file}, Error: {e}")

    print("Fonts loaded successfully.")
    return loaded_fonts