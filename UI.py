import sys
from PyQt5 import QtWidgets
import data_gather

class window(QtWidgets.QWidget):
    def __init__(self):
        super (window, self).__init__()
        self.setWindowTitle('QC meteo history')
        self.setGeometry(2330, 000, 500, 300)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.but = QtWidgets.QPushButton('Refresh locations')
        self.layout.addWidget(self.but)
        self.but.clicked.connect(self.update_json)

        self.lab = QtWidgets.QLabel('label')
        self.layout.addWidget(self.lab)
        self.get_json_date_created()

        self.stations_menu = QtWidgets.QComboBox()
        self.layout.addWidget(self.stations_menu)
        self.populate_stations_menu()


    def populate_stations_menu(self):
        self.stations_menu.insertItems(0, data_gather.get_json_info("stations"))

    def update_json(self):
        alert = QtWidgets.QMessageBox()
        alert.setText("Refresh meteo station locations?")
        alert.setInformativeText("This might take a few moments (from 30sec to 1.5 minutes or more "
                                 "depending on your internet connection")
        i = alert.buttonClicked
        alert.setStandardButtons(alert.Ok | alert.Cancel)
        ret = alert.exec()
        if ret == 4194304:
            print("Cancel")
        elif ret == 1024:
            print("Ok")
            data_gather.save_meteo_stations()
            self.get_json_date_created()

    def get_json_date_created(self):
        self.lab.setText("Last update of locations: {}".format(
            data_gather.get_json_info("date_created")))


if __name__ == '__main__' :
    app = QtWidgets.QApplication (sys.argv)
    wnd = window()
    wnd.show()
    sys.exit (app.exec_())