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

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
     
        ## Figure out how to deal with tabbed setup 
        self.tabs = QtWidgets.QTabWidget()

        self.canvas = MplCanvas(self, width=10, height=8, dpi=100)
        self.update_button = QtWidgets.QPushButton("Update")
        self.filename_text = QtWidgets.QLineEdit()
        self.browse_button = QtWidgets.QPushButton("Browse")
        self.segment_button = QtWidgets.QPushButton("Segment")

        self.iniUI()
      
    def iniUI(self):
        w = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(w)
        self.setCentralWidget(w)
        self.filename_text.setPlaceholderText("/path/to/audio/file/syllable.wav")

        self.update_button.clicked.connect(self.update_plot)
        self.browse_button.clicked.connect(self.browse_file)
        self.segment_button.clicked.connect(self.segment_syllable)

        grid.addWidget(self.canvas, 0, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        grid.addWidget(self.update_button, 0, 1, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        grid.addWidget(self.filename_text, 1, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        grid.addWidget(self.browse_button, 1, 1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        grid.addWidget(self.segment_button, 2, 2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

        self.set_data()
        self.show()

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

    window = MainWindow()
    window.show()
    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("closing window...")

