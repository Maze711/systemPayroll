from MainFrame.Resources.lib import *
from MainFrame.TimeKeeping.schedValidator.checkSched import chkSched
from MainFrame.TimeKeeping.timekeeper_functions.dialogFunctions import import_dat_file
from MainFrame.systemFunctions import globalFunction
from MainFrame.TimeKeeping.timekeeper_functions.timecardFunctions import populateList, buttonTimecardFunction, \
    searchBioNum, FilterDialog

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class timecard(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1442, 665)
        ui_file = globalFunction.resource_path("MainFrame\\Resources\\UI\\timecard.ui")
        loadUi(ui_file, self)

        self.populateComboBox = populateList(self)
        self.buttonFunctions = buttonTimecardFunction(self)
        self.searchFunction = searchBioNum(self)
        self.filteringFunction = FilterDialog(self)
        self.setupTimecardUI()
        self.setup_initial_state()

        # Initialize data attributes
        self.original_data = []  # Holds the initial data
        self.temp_data = []      # Holds updates made to the data
        self.filtered_data = []  # Current view data

    def setup_initial_state(self):
        self.btnFilter.setVisible(False)
        self.btnCheckSched.setVisible(True)

        # Ensure original_data is initialized
        self.original_data = []  # Initially empty, should be filled when data is imported
        self.filtered_data = self.original_data.copy()  # Should initially be empty too

    def setupTimecardUI(self):
        try:
            self.TimeListTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
            self.TimeListTable.horizontalHeader().setStretchLastSection(True)

            self.populateComboBox.populate_year_combo_box()
            self.populateComboBox.populateCostCenterBox()
            self.yearCC.currentTextChanged.connect(self.populateComboBox.populate_date_combo_boxes)
            self.dateFromCC.currentTextChanged.connect(self.populateComboBox.populate_table_loader)
            self.dateToCC.currentTextChanged.connect(self.populateComboBox.populate_table_loader)

            self.btnCCSched.clicked.connect(self.buttonFunctions.updateSchedule)
            self.btnExport.clicked.connect(self.buttonFunctions.export_to_excel)
            self.btnImport.clicked.connect(lambda: self.populateComboBox.import_dat_file(self))
            self.btnTimeSheet.clicked.connect(self.buttonFunctions.createTimeSheet)
            self.btnCheckSched.clicked.connect(self.buttonFunctions.CheckSched)
            self.TimeListTable.cellDoubleClicked.connect(self.buttonFunctions.CheckSched)

            self.searchBioNum.textChanged.connect(self.searchFunction.search_bioNum)

            # Initialize data attributes
            self.original_data = []
            self.temp_data = []
            self.filtered_data = self.original_data.copy()

        except Exception as e:
            logging.error(f"Error in setupTimecardUI: {e}")
            QMessageBox.critical(self, "Error", f"Failed to set up Timecard UI: {str(e)}")
