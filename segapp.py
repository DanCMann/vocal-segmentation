import sys
import os
import random
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import parselmouth
import numpy as np

from scripts.syllable import Syllable

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=10, height=7, dpi=300):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

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

class TabStruct(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.canvas = MplCanvas(self)
        self.canvas.axes.contour_ax = self.canvas.axes.twinx()
    

    def define_widgets(self):
        pass

    def click_connections(self):
        pass

    def add_widgets(self):
        pass

class TableWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
        self.syllable = None

        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.define_tabs()
        self.define_widgets()

        self.init_UI()

    def define_tabs(self):
        self.tabs = QtWidgets.QTabWidget()
        self.main_tab = QtWidgets.QWidget()
        self.amp_tab = QtWidgets.QWidget()
        self.f0_tab = QtWidgets.QWidget()
        self.seg_tab = QtWidgets.QWidget()
    
    def define_widgets(self):
        # Canvas
        self.canvas_amp = MplCanvas(self)
        self.canvas_amp.axes.contour_ax = self.canvas_amp.axes.twinx()
        
        self.canvas_f0 = MplCanvas(self)
        self.canvas_f0.axes.contour_ax = self.canvas_f0.axes.twinx()
        
        self.canvas_seg = MplCanvas(self)
        self.canvas_seg.axes.contour_ax = self.canvas_seg.axes.twinx()

        # Main
        self.filename_text = QtWidgets.QLineEdit()
        self.browse_button = QtWidgets.QPushButton("Browse")
        
        # Amp
        self.amp_button = QtWidgets.QPushButton("Plot")
        
        self.min_pitch_label = QtWidgets.QLabel("Minimum Pitch")

        self.min_pitch_slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
        self.min_pitch_slider.setMinimum(10)
        self.min_pitch_slider.setMaximum(2000)
        self.min_pitch_slider.setValue(400)
        self.min_pitch_slider.setTickPosition(QtWidgets.QSlider.TicksRight)
        self.min_pitch_slider.setTickInterval(10)

        self.amp_time_step_label = QtWidgets.QLabel("Time Step")

        self.amp_time_step = QtWidgets.QDoubleSpinBox()
        self.amp_time_step.setRange(0, 1000)
        self.amp_time_step.setValue(0)
        self.amp_time_step.setSingleStep(1)

        # F0
        self.f0_button = QtWidgets.QPushButton("Plot")
        '''
        self.f0_time_step_label = QtWidgets.QLabel("Time Step")
        self.f0_time_step = QtWidgets.QDoubleSpinBox()
        self.f0_time_step.setRange(0, 1000) 
        self.f0_time_step.setValue(0)
        self.f0_time_step.setSingleStep(1)
        '''
        self.f0_pitch_floor_label = QtWidgets.QLabel("Pitch Floor")
        self.f0_pitch_floor = QtWidgets.QSpinBox()
        self.f0_pitch_floor.setRange(50, 5000)
        self.f0_pitch_floor.setValue(500)
        self.f0_pitch_floor.setSingleStep(10)
       
        self.f0_max_n_cand_label = QtWidgets.QLabel("Maximum Number of Candidates")
        self.f0_max_n_cand = QtWidgets.QSpinBox()
        self.f0_max_n_cand.setRange(1, 15)
        self.f0_max_n_cand.setSingleStep(1)
        self.f0_max_n_cand.setValue(15)
        
        # very accurate widget
        
        self.f0_sil_threshold_label = QtWidgets.QLabel("Silence Threshold")
        self.f0_sil_threshold = QtWidgets.QDoubleSpinBox()
        self.f0_sil_threshold.setRange(0, 10)
        self.f0_sil_threshold.setSingleStep(0.05)
        self.f0_sil_threshold.setValue(0.03)

        self.f0_voicing_threshold_label = QtWidgets.QLabel("Voicing Threshold")
        self.f0_voicing_threshold = QtWidgets.QDoubleSpinBox()
        self.f0_voicing_threshold.setRange(0, 10)
        self.f0_voicing_threshold.setSingleStep(0.1)
        self.f0_voicing_threshold.setValue(0.45)
        
        self.f0_octave_cost_label = QtWidgets.QLabel("Octave Cost")
        self.f0_octave_cost = QtWidgets.QDoubleSpinBox()
        self.f0_octave_cost.setRange(0, 10) 
        self.f0_octave_cost.setSingleStep(0.01) 
        self.f0_octave_cost.setValue(0.001)

        self.f0_octave_jump_cost_label = QtWidgets.QLabel("Octave Jump Cost")
        self.f0_octave_jump_cost = QtWidgets.QDoubleSpinBox()
        self.f0_octave_jump_cost.setRange(0, 10)
        self.f0_octave_jump_cost.setSingleStep(0.1)
        self.f0_octave_jump_cost.setValue(0.05)
    
        self.f0_voiced_unvoiced_cost_label = QtWidgets.QLabel("Voiced/Unvoiced Cost")
        self.f0_voiced_unvoiced_cost = QtWidgets.QDoubleSpinBox()
        self.f0_voiced_unvoiced_cost.setRange(0, 10)
        self.f0_voiced_unvoiced_cost.setSingleStep(0.1)
        self.f0_octave_jump_cost.setValue(0.14)
        
        self.f0_pitch_ceiling_label = QtWidgets.QLabel("Pitch Ceiling")
        self.f0_pitch_ceiling = QtWidgets.QDoubleSpinBox()
        self.f0_pitch_ceiling.setRange(20, 50000)
        self.f0_pitch_ceiling.setSingleStep(100)
        self.f0_pitch_ceiling.setValue(15000)

        # Segment
        self.seg_plot_button = QtWidgets.QPushButton("Plot")
        #self.update_button = QtWidgets.QPushButton("Update")
        self.segment_button = QtWidgets.QPushButton("Segment")

    def init_UI(self):
        self.add_tabs()
        self.filename_text.setPlaceholderText("/examples/budgie_single.wav")
        self.click_connections()
        self.add_widgets()
        #self.set_data()
        #self.show()
        self.set_layout()

    def add_tabs(self):
        self.tabs.addTab(self.main_tab, "Load")
        self.tabs.addTab(self.amp_tab, "Adjust Amplitude")
        self.tabs.addTab(self.f0_tab, "Adjust F0")
        self.tabs.addTab(self.seg_tab, "Perform segmentation")

        self.main_tab.grid = QtWidgets.QGridLayout(self)
        self.amp_tab.grid = QtWidgets.QGridLayout(self)
        self.f0_tab.grid = QtWidgets.QGridLayout(self)
        self.seg_tab.grid = QtWidgets.QGridLayout(self)

    def click_connections(self):
        # Main tab widgets connections
        self.browse_button.clicked.connect(self.browse_file)
        
        # Amp tab widget connections
        self.amp_button.clicked.connect(lambda: self.update_spectrogram(self.canvas_amp))
        self.min_pitch_slider.valueChanged.connect(lambda: self.change_intensity(minimum_pitch = self.min_pitch_slider.value()))

        # F0 tab widget connections
        self.f0_button.clicked.connect(lambda: self.update_spectrogram(self.canvas_f0, overlay = "f0"))
        #self.f0_time_step.valueChanged.connect(lambda: self.change_f0(time_step = self.f0_time_step.value()))
        self.f0_pitch_floor.valueChanged.connect(lambda: self.change_f0(pitch_floor = self.f0_pitch_floor.value()))
        self.f0_max_n_cand.valueChanged.connect(lambda: self.change_f0(max_num_of_candidates = self.f0_max_n_cand.value()))
        self.f0_sil_threshold.valueChanged.connect(lambda: self.change_f0(silence_threshold = self.f0_sil_threshold.value())) 
        self.f0_voicing_threshold.valueChanged.connect(lambda: self.change_f0(voicing_threshold = self.f0_voicing_threshold.value()))
        self.f0_octave_cost.valueChanged.connect(lambda: self.change_f0(octave_cost = self.f0_octave_cost.value()))
        self.f0_octave_jump_cost.valueChanged.connect(lambda: self.change_f0(octave_jump_cost = self.f0_octave_jump_cost.value()))
        self.f0_voiced_unvoiced_cost.valueChanged.connect(lambda: self.change_f0(voiced_unvoiced_cost = self.f0_voiced_unvoiced_cost.value()))
        self.f0_pitch_ceiling.valueChanged.connect(lambda: self.change_f0(pitch_ceiling = self.f0_pitch_ceiling.value()))
        
        # Segmentation tab widget connections
        self.seg_plot_button.clicked.connect(lambda: self.update_spectrogram(self.canvas_seg, overlay = 'seg'))
        #self.update_button.clicked.connect(self.update_plot)
        self.segment_button.clicked.connect(self.segment_syllable)

    def add_widgets(self):
        # Main tab widgets
        self.main_tab.grid.addWidget(self.browse_button, 0, 1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.main_tab.grid.addWidget(self.filename_text, 0, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
       
        # Amplitude widgets
        self.amp_tab.grid.addWidget(self.canvas_amp, 0, 0, 3, 3, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.amp_tab.grid.addWidget(self.amp_button, 5, 5, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.amp_tab.grid.addWidget(self.min_pitch_label, 0, 4, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.amp_tab.grid.addWidget(self.min_pitch_slider, 0, 5, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.amp_tab.grid.addWidget(self.amp_time_step_label, 1, 4, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.amp_tab.grid.addWidget(self.amp_time_step, 1, 5, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        # F0 widgets
        self.f0_tab.grid.addWidget(self.canvas_f0, 0, 0, 9, 3, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_button, 6, 6, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        # Removed because it causes hard to catch crashes and there's an auto calc of the time step anyway
        #self.f0_tab.grid.addWidget(self.f0_time_step_label, 0, 4, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        #self.f0_tab.grid.addWidget(self.f0_time_step, 0, 5, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        self.f0_tab.grid.addWidget(self.f0_pitch_floor_label, 1, 4, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_pitch_floor, 1, 5, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        self.f0_tab.grid.addWidget(self.f0_max_n_cand_label, 2, 4, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_max_n_cand, 2, 5, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

        self.f0_tab.grid.addWidget(self.f0_sil_threshold_label, 3, 4, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_sil_threshold, 3, 5, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        self.f0_tab.grid.addWidget(self.f0_voicing_threshold_label, 4, 4, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_voicing_threshold, 4, 5, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        self.f0_tab.grid.addWidget(self.f0_octave_cost_label, 5, 4, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_octave_cost, 5, 5, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        self.f0_tab.grid.addWidget(self.f0_octave_jump_cost_label, 6, 4, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_octave_jump_cost, 6, 5, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        self.f0_tab.grid.addWidget(self.f0_voiced_unvoiced_cost_label, 7, 4, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_voiced_unvoiced_cost, 7, 5, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        self.f0_tab.grid.addWidget(self.f0_pitch_ceiling_label, 8, 4, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_pitch_ceiling, 8, 5, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        # Segmentation tab widgets
        self.seg_tab.grid.addWidget(self.seg_plot_button, 1, 1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.seg_tab.grid.addWidget(self.canvas_seg, 0, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        #self.seg_tab.grid.addWidget(self.update_button, 0, 1, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.seg_tab.grid.addWidget(self.segment_button, 2, 2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
   
    def set_data(self):
        n_data = 10
        #self.xdata = list(range(n_data))
        self.xdata = [random.uniform(0, self.syllable.duration) for i in range(n_data)]
        print(self.xdata)
        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.
        #self._plot_ref = None
        #self.update_plot()
        self.canvas_seg.axes.contour_ax.vlines(x = self.xdata, ymin = 0, ymax = 10000, colors= 'r')
        
    def set_layout(self):
        self.main_tab.setLayout(self.main_tab.grid)
        self.amp_tab.setLayout(self.amp_tab.grid)
        self.f0_tab.setLayout(self.f0_tab.grid)
        self.seg_tab.setLayout(self.seg_tab.grid)
        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def update_plot(self):
        # Drop off the first y element, append a new one.
        self.xdata = self.xdata[1:] + [random.uniform(0, self.syllable.duration)]

        # Note: we no longer need to clear the axis.
        if self._plot_ref is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            self.canvas_seg.axes.vlines(x = self.xdata, ymin = 0, ymax = 10000, colors= 'r')
            #self._plot_ref = plot_refs[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_ref.set_xdata(self.xdata)

        # Trigger the canvas to update and redraw.
        self.canvas_seg.draw()
   
    def update_spectrogram(self, canvas, overlay = "intensity"):

        if(canvas.axes.has_data()):
            canvas.axes.clear()
            canvas.axes.contour_ax.clear()
        else:
            if(self.syllable is None):
                self.load_sound()
        
        self.syllable.draw_spectrogram(canvas.axes) 
        if(overlay == "intensity"):
            self.syllable.draw_intensity(canvas.axes.contour_ax)
        elif(overlay == "f0"):
            self.syllable.draw_f0(canvas.axes.contour_ax)
        else:
            self.set_data()

        canvas.axes.contour_ax.set_xlim([self.syllable.sound.xmin, self.syllable.sound.xmax])
        canvas.draw()
        #print(f'axes -> {hex(id(canvas.axes))}')
        #print(f'_ax2 -> {hex(id(canvas.axes.ax2))}')

    def change_f0(self, **kwargs):
        if(self.syllable is None):
            self.load_sound()
        else:

            self.syllable.update_f0(**kwargs)
            if not self.syllable.f0.error:
                self.update_spectrogram(self.canvas_f0, overlay = "f0")
            else:
                # Change this to write in a message box
                print(self.syllable.f0.error)

    def change_intensity(self, **kwargs):
        if(self.syllable is None):
            self.load_sound()
        
        else:
            self.syllable.update_intensity(**kwargs)
            if not self.syllable.intensity.error:
                self.update_spectrogram(self.canvas_amp, overlay = "intensity")
            else:
                # Change to write in a message box
                print(self.syllable.intensity.error)

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
        self.filename = self.filename_text.text()
        #self.syllable = Syllable(self.filename)
        self.syllable = Syllable("./examples/budgie_single.wav")
        #Raise an error here if there is no filename

    def segment_syllable(self):
        #print("segment")
        n_data = 10
        self.xdata = [random.uniform(0, self.syllable.duration) for i in range(n_data)]
        print(self.xdata)
        self.canvas_seg.axes.contour_ax.vlines(x = self.xdata, ymin = 0, ymax = 10000, colors= 'r')
 
if __name__ == '__main__':
    app=QtWidgets.QApplication(sys.argv)

    window = App()
    window.show()
    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("closing window...")

