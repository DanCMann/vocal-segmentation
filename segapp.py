import sys
import os
import random
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class App(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = "Segmentation"

        self.left = 0
        self.top = 0
        self.width = 800
        self.height = 600
        
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
        
        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.define_tabs()
        self.define_widgets()

        self.init_UI()

    def define_tabs(self):
        self.tabs = QtWidgets.QTabWidget()
        self.main_tab = QtWidgets.QWidget()
        self.amp_tab = QtWidgets.QWidget()
        self.f0_tab = QtWidgets.QWidget()
        self.spect_tab = QtWidgets.QWidget()
    
    def define_widgets(self):
        self.canvas_amp = MplCanvas(self, width=10, height=8, dpi=100)
        self.canvas_f0 = MplCanvas(self, width=10, height=8, dpi=100)
        self.canvas = MplCanvas(self, width=10, height=8, dpi=100)
        self.update_button = QtWidgets.QPushButton("Update")
        self.filename_text = QtWidgets.QLineEdit()
        self.browse_button = QtWidgets.QPushButton("Browse")
        self.segment_button = QtWidgets.QPushButton("Segment")
    
    def init_UI(self):
        self.add_tabs()
        self.filename_text.setPlaceholderText("/path/to/audio/file/syllable.wav")
        self.click_connections()
        self.add_widgets()
        self.set_data()
        #self.show()
        self.set_layout()

    def add_tabs(self):
        self.tabs.addTab(self.main_tab, "Load")
        self.tabs.addTab(self.amp_tab, "Adjust Amplitude")
        self.tabs.addTab(self.f0_tab, "Adjust F0")
        self.tabs.addTab(self.spect_tab, "Perform segmentation")

        self.main_tab.grid = QtWidgets.QGridLayout(self)
        self.spect_tab.grid = QtWidgets.QGridLayout(self)
        self.amp_tab.grid = QtWidgets.QGridLayout(self)
        self.f0_tab.grid = QtWidgets.QGridLayout(self)

    def click_connections(self):
        self.update_button.clicked.connect(self.update_plot)
        self.browse_button.clicked.connect(self.browse_file)
        self.segment_button.clicked.connect(self.segment_syllable)
       
    def add_widgets(self):
        # Main tab widgets
        self.main_tab.grid.addWidget(self.browse_button, 0, 1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.main_tab.grid.addWidget(self.filename_text, 0, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
       
        # Amplitude widgets
        self.amp_tab.grid.addWidget(self.canvas_amp, 0, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        # F0 widgets
        self.f0_tab.grid.addWidget(self.canvas_f0, 0, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        # Segmentation tab widgets
        self.spect_tab.grid.addWidget(self.canvas, 0, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.spect_tab.grid.addWidget(self.update_button, 0, 1, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.spect_tab.grid.addWidget(self.segment_button, 1, 1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
   
    def set_data(self):
        n_data = 10 
        self.xdata = list(range(n_data))
        self.ydata = [random.randint(0, 10) for i in range(n_data)]

        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.
        self._plot_ref = None
        #self.update_plot()

        ## load sound file here? or outside?
        # probably here for first spect
        
    def set_layout(self):
        self.main_tab.setLayout(self.main_tab.grid)
        self.amp_tab.setLayout(self.amp_tab.grid)
        self.f0_tab.setLayout(self.f0_tab.grid)
        self.spect_tab.setLayout(self.spect_tab.grid)
        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def update_plot(self):
        # Drop off the first y element, append a new one.
        self.ydata = self.ydata[1:] + [random.randint(0, 10)]

        # Note: we no longer need to clear the axis.
        if self._plot_ref is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refs = self.canvas.axes.plot(self.xdata, self.ydata, 'r')
            self._plot_ref = plot_refs[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_ref.set_ydata(self.ydata)

        # Trigger the canvas to update and redraw.
        self.canvas.draw()
   
    def plot_spectrogram(self):
        pass

    def browse_file(self):
        file_filter = 'Audio file (*.wav)'
        response = QtWidgets.QFileDialog.getOpenFileName( 
                parent=self,
                caption='select a sound file',
                directory=os.getcwd(),
                filter=file_filter,
                initialFilter='Audio file (*.wav)'
                )
        self.filename_text.setText(response[0])
    
    def load_sound(self):
        pass

    def segment_syllable(self):
        print("segment")

if __name__ == '__main__':
    app=QtWidgets.QApplication(sys.argv)

    window = App()
    window.show()
    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("closing window...")

