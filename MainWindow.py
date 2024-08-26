from MainFrame.Resources.lib import *
from main_functions import MainWindowFunctions

class MainWindow(MainWindowFunctions):
    def __init__(self):
        super(MainWindow, self).__init__()

        start_time = time.time()

        # Log initial memory usage before UI loads
        self.log_memory_usage("Before UI load")

        ui_file = self.resource_path("MainFrame/Resources/UI/Main.ui")
        loadUi(ui_file, self)

        # Log memory usage after UI loads
        self.log_memory_usage("After UI load")

        self.setFixedSize(800, 600)
        self.initialize_widgets()
        self.setup_connections()
        self.setup_page_buttons()
        self.load_fonts()

        self.log_memory_usage("After initialization")

        def keyPressEvent(self, event):
            MainWindowFunctions.keyPressEvent(self, event)


if __name__ == "__main__":
    start_time = time.time()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())