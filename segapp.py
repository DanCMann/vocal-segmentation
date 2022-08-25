import sys
import os
import random
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from scripts.syllable import Syllable
from scripts.tabs import MainTab, AmpTab, F0Tab, SegTab

class App(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = "Segmentation"

        self.left = 0
        self.top = 0
        self.width = 1200
        self.height = 1000
        
        self.table_widget = TableWidget(self)

        self.initUI()
        
    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)

        self.setCentralWidget(self.table_widget)
        self.show()

class TableWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
        self.syllable = None
        self.layout = QtWidgets.QVBoxLayout(self)
        self.define_tabs()
        self.init_UI()

    def define_tabs(self):
        self.tabs = QtWidgets.QTabWidget()
        self.main_tab = MainTab() 
        self.amp_tab = AmpTab()
        self.f0_tab = F0Tab()
        self.seg_tab = SegTab()
    
    def init_UI(self):
        self.add_tabs()
        self.main_tab.filename_text.setPlaceholderText("/examples/budgie_single.wav")
        self.set_layout()

    def add_tabs(self):
        self.tabs.addTab(self.main_tab, "Load")
        self.tabs.addTab(self.amp_tab, "Adjust Amplitude")
        self.tabs.addTab(self.f0_tab, "Adjust F0")
        self.tabs.addTab(self.seg_tab, "Perform segmentation")

    def set_layout(self):
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)


if __name__ == '__main__':
    app=QtWidgets.QApplication(sys.argv)

    window = App()
    window.show()
    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("closing window...")

