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
        self.original_data = []
        self.filtered_data = self.original_data.copy()

    def setup_initial_state(self):
        self.btnFilter.setVisible(False)
        self.btnCheckSched.setVisible(False)

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
            self.btnImport.clicked.connect(self.populateComboBox.import_dat_file)
            self.btnTimeSheet.clicked.connect(self.buttonFunctions.createTimeSheet)
            self.btnCheckSched.clicked.connect(self.buttonFunctions.CheckSched)
            self.TimeListTable.cellDoubleClicked.connect(self.buttonFunctions.CheckSched)

            self.searchBioNum.textChanged.connect(self.searchFunction.search_bioNum)

            # self.btnFilter.clicked.connect(self.filteringFunction.filterModal)

            self.original_data = []
            self.filtered_data = self.original_data.copy()

        except Exception as e:
            logging.error(f"Error in setupTimecardUI: {e}")
            QMessageBox.critical(self, "Error", f"Failed to set up Timecard UI: {str(e)}")