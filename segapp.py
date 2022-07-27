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

class Syllable(parselmouth.Sound):
    def __init__(self, filename, *args, **kwargs):
        super().__init__(filename, *args, **kwargs)
        self.filename = filename
        self.sound = parselmouth.Sound(self.filename)
        self.spectrogram = self.sound.to_spectrogram()
        
        self.intensity = self.sound.to_intensity(minimum_pitch = 400)
        self._time_step = None
        self._pitch_floor = 500 
        self._max_num_of_candidates = 15
        self._very_accurate = False
        self._silence_threshold = 0.03
        self._voicing_threshold = 0.45
        self._octave_cost = 0.01
        self._octave_jump_cost = 0.35
        self._voiced_unvoiced_cost = 0.14
        self._pitch_ceiling = 15000
        
        self.get_f0()

    def get_f0(self):
        self.f0 = self.sound.to_pitch_ac(time_step = self._time_step, 
                pitch_floor = self._pitch_floor,
                max_number_of_candidates = self._max_num_of_candidates,
                #very_accurate = self._very_accurate,
                silence_threshold = self._silence_threshold,
                voicing_threshold = self._voicing_threshold,
                octave_cost = self._octave_cost,
                octave_jump_cost = self._octave_jump_cost,
                voiced_unvoiced_cost = self._voiced_unvoiced_cost,
                pitch_ceiling = self._pitch_ceiling
                )
        #print(self.f0)
        print(self._time_step)
        print(self._pitch_floor)
        print(self._pitch_ceiling)

    @property
    def time_step(self):
        return self._time_step
    # using time_step.setter caused problems with the pyqt5 connect function
    #  you can't assign in connect
    # this seems to work for now but I'm sure it'll fuck me over down the line
    def time_step(self, new_time_step):
        self._time_step = new_time_step
        self.get_f0()
    
    @property
    def pitch_floor(self):
        return self._pitch_floor

    def pitch_floor(self, new_pitch_floor):
        self._pitch_floor = new_pitch_floor
        self.get_f0()
    
    @property
    def max_num_of_candidates(self):
        return self._max_num_of_candidates
    
    def max_num_of_candidates(self, new_max_num_cand):
        self._max_num_of_candidates = new_max_num_cand
        self.get_f0()
    
    @property
    def very_accurate(self):
        return self._very_accurate

    def very_accurate(self, new_very_accurate):
        self._very_accurate = new_very_accurate
        self.get_f0()

    @property
    def silence_threshold(self):
        return self._silence_threshold
    
    def silence_threshold(self, new_silence_threshold):
        self._silence_threshold = new_silence_threshold
        self.get_f0()

    @property
    def voicing_threshold(self):
        return self._voicing_threshold

    def voicing_threshold(self, new_voicing_threshold):
        self._voicing_threshold = new_voicing_threshold
        self.get_f0()
    
    @property
    def octave_cost(self):
        return self._octave_cost
    
    def octave_cost(self, new_octave_cost):
        self._octave_cost = new_octave_cost
        self.get_f0()

    @property
    def octave_jump_cost(self):
        return self._octave_jump_cost
    
    def octave_jump_cost(self, new_octave_jump_cost):
        self._octave_jump_cost = new_octave_jump_cost
        self.get_f0()
    
    @property
    def voiced_unvoiced_cost(self):
        return self._voiced_unvoiced_cost

    def voiced_unvoiced_cost(self, new_voiced_unvoiced_cost):
        self._voiced_unvoiced_cost = new_voiced_unvoiced_cost
        self.get_f0()
    
    @property
    def pitch_ceiling(self):
        return self._pitch_ceiling
    
    def pitch_ceiling(self, new_pitch_ceiling):
        self._pitch_ceiling = new_pitch_ceiling
        self.get_f0()
 
    def update_intensity(self, *args, **kwargs):
        self.intensity = self.sound.to_intensity(*args, **kwargs)

    def update_f0(self, *args, **kwargs):
        '''
        with both this and intensity, I might need to make things explicit so that I don't unknowingly use defaults. 

        '''
        self.f0 = self.sound.to_pitch_ac(*args, **kwargs)

    def draw_spectrogram(self, canvas_axes, dynamic_range=70):
        '''
        The best way I could figure out to do this was to pass the actual matplotlib.axes object as an arg. 
        Probably a better way, but honestly it might just be fine to test on normal figures and make sure
          that it would also plot on a noncanvas object. 
        '''
        X, Y = self.spectrogram.x_grid(), self.spectrogram.y_grid()
        sg_db = 10 * np.log10(self.spectrogram.values)
        canvas_axes.pcolormesh(
                X, Y, sg_db, 
                vmin=sg_db.max() - dynamic_range, 
                facecolor = 'white',
                edgecolors = 'face', 
                alpha = 0.5,
                shading='flat', 
                snap = True,
                rasterized = True,
                cmap='binary')
        canvas_axes.set_ylim([self.spectrogram.ymin, self.spectrogram.ymax])
        canvas_axes.set_xlabel("time [s]")
        canvas_axes.set_ylabel("frequency [Hz]")

    def draw_intensity(self, canvas_axes):
        canvas_axes.plot(self.intensity.xs(), self.intensity.values.T, linewidth=3, color='w')
        canvas_axes.plot(self.intensity.xs(), self.intensity.values.T, linewidth=1)
        canvas_axes.grid(False)
        canvas_axes.set_ylim(0)
        canvas_axes.set_ylabel("intensity [dB]")
    
    def draw_f0(self, canvas_axes):
        pitch_values = self.f0.selected_array['frequency']
        print(pitch_values)
        pitch_values[pitch_values==0] = np.nan
        canvas_axes.plot(self.f0.xs(), pitch_values, 'o', markersize=5, color='w')
        canvas_axes.plot(self.f0.xs(), pitch_values, 'o', markersize=2)
        canvas_axes.grid(False)
        canvas_axes.set_ylim(0, self.spectrogram.ymax)
        canvas_axes.set_ylabel("fundamental frequency [Hz]")

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=11, height=8, dpi=300):
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
        self.spect_tab = QtWidgets.QWidget()
    
    def define_widgets(self):
        # Canvas
        self.canvas_amp = MplCanvas(self)
        self.canvas_f0 = MplCanvas(self)
        self.canvas = MplCanvas(self)
        
        # Main
        self.filename_text = QtWidgets.QLineEdit()
        self.browse_button = QtWidgets.QPushButton("Browse")
        
        # Amp
        self.amp_button = QtWidgets.QPushButton("Plot")
        self.min_pitch_slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
        self.min_pitch_slider.setMinimum(10)
        self.min_pitch_slider.setMaximum(2000)
        self.min_pitch_slider.setValue(400)
        self.min_pitch_slider.setTickPosition(QtWidgets.QSlider.TicksRight)
        self.min_pitch_slider.setTickInterval(10)

        # F0
        self.f0_button = QtWidgets.QPushButton("Plot")
        
        self.f0_time_step = QtWidgets.QDoubleSpinBox()
        self.f0_time_step.setRange(0, 1000) 
        self.f0_time_step.setValue(0)
        self.f0_time_step.setSingleStep(1)

        self.f0_pitch_floor = QtWidgets.QSpinBox()
        self.f0_pitch_floor.setRange(50, 5000)
        self.f0_pitch_floor.setValue(500)
        self.f0_pitch_floor.setSingleStep(10)
        
        self.f0_max_n_cand = QtWidgets.QSpinBox()
        self.f0_max_n_cand.setRange(1, 15)
        self.f0_max_n_cand.setSingleStep(1)
        self.f0_max_n_cand.setValue(15)
        
        # very accurate widget

        self.f0_sil_threshold = QtWidgets.QDoubleSpinBox()
        self.f0_sil_threshold.setRange(0, 10)
        self.f0_sil_threshold.setSingleStep(0.05)
        self.f0_sil_threshold.setValue(0.03)

        self.f0_voicing_threshold = QtWidgets.QDoubleSpinBox()
        self.f0_voicing_threshold.setRange(0, 10)
        self.f0_voicing_threshold.setSingleStep(0.1)
        self.f0_voicing_threshold.setValue(0.45)
        
        self.f0_octave_cost = QtWidgets.QDoubleSpinBox()
        self.f0_octave_cost.setRange(0, 10) 
        self.f0_octave_cost.setSingleStep(0.01) 
        self.f0_octave_cost.setValue(0.001)

        self.f0_octave_jump_cost = QtWidgets.QDoubleSpinBox()
        self.f0_octave_jump_cost.setRange(0, 10)
        self.f0_octave_jump_cost.setSingleStep(0.1)
        self.f0_octave_jump_cost.setValue(0.05)

        self.f0_voiced_unvoiced_cost = QtWidgets.QDoubleSpinBox()
        self.f0_voiced_unvoiced_cost.setRange(0, 10)
        self.f0_voiced_unvoiced_cost.setSingleStep(0.1)
        self.f0_octave_jump_cost.setValue(0.14)

        self.f0_pitch_ceiling = QtWidgets.QDoubleSpinBox()
        self.f0_pitch_ceiling.setRange(20, 50000)
        self.f0_pitch_ceiling.setSingleStep(100)
        self.f0_pitch_ceiling.setValue(15000)

        # Segment
        self.update_button = QtWidgets.QPushButton("Update")
        self.segment_button = QtWidgets.QPushButton("Segment")

    def init_UI(self):
        self.add_tabs()
        self.filename_text.setPlaceholderText("/examples/budgie_single.wav")
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
        # Main tab widgets connections
        self.browse_button.clicked.connect(self.browse_file)
        
        # Amp tab widget connections
        self.amp_button.clicked.connect(lambda: self.update_spectrogram(self.canvas_amp))
        self.min_pitch_slider.valueChanged.connect(lambda: self.change_intensity(minimum_pitch = self.min_pitch_slider.value()))

        # F0 tab widget connections
        self.f0_button.clicked.connect(lambda: self.update_spectrogram(self.canvas_f0, overlay = "f0"))
        self.f0_time_step.valueChanged.connect(lambda: self.syllable.time_step(self.f0_time_step.value()))
        self.f0_pitch_floor.valueChanged.connect(lambda: self.syllable.pitch_floor(self.f0_pitch_floor.value()))
        self.f0_max_n_cand.valueChanged.connect(lambda: self.syllable.max_num_of_candidates(self.f0_max_n_cand.value()))
        self.f0_sil_threshold.valueChanged.connect(lambda: self.syllable.silence_threshold(self.f0_sil_threshold.value())) 
        self.f0_voicing_threshold.valueChanged.connect(lambda: self.syllable.voicing_threshold(self.f0_voicing_threshold.value()))
        self.f0_octave_cost.valueChanged.connect(lambda: self.syllable.octave_cost(self.f0_octave_cost.value()))
        self.f0_octave_jump_cost.valueChanged.connect(lambda: self.syllable.octave_jump_cost(self.f0_octave_jump_cost.value()))
        self.f0_voiced_unvoiced_cost.valueChanged.connect(lambda: self.syllable.voiced_unvoiced_cost(self.f0_voiced_unvoiced_cost.value()))
        self.f0_pitch_ceiling.valueChanged.connect(lambda: self.syllable.pitch_ceiling(self.f0_pitch_ceiling.value()))
        
        # Segmentation tab widget connections
        self.update_button.clicked.connect(self.update_plot)
        self.segment_button.clicked.connect(self.segment_syllable)

    def add_widgets(self):
        # Main tab widgets
        self.main_tab.grid.addWidget(self.browse_button, 0, 1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.main_tab.grid.addWidget(self.filename_text, 0, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
       
        # Amplitude widgets
        self.amp_tab.grid.addWidget(self.canvas_amp, 0, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.amp_tab.grid.addWidget(self.amp_button, 1, 1, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.amp_tab.grid.addWidget(self.min_pitch_slider, 0, 1, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        # F0 widgets
        self.f0_tab.grid.addWidget(self.canvas_f0, 0, 0, 3, 3, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_button, 4, 4, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_time_step, 0, 3, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_pitch_floor, 1, 3, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_max_n_cand, 2, 3, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

        self.f0_tab.grid.addWidget(self.f0_sil_threshold, 3, 3, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_voicing_threshold, 4, 3, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_octave_cost, 5, 3, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_octave_jump_cost, 6, 3, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_voiced_unvoiced_cost, 7, 3, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.f0_tab.grid.addWidget(self.f0_pitch_ceiling, 8, 3, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
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
   
    def update_spectrogram(self, canvas, overlay = "intensity"):

        if(canvas.axes.has_data()):
            canvas.axes.clear()
            canvas.axes._ax2.clear()
        else:
            if(self.syllable is None):
                self.load_sound()
        
        self.syllable.draw_spectrogram(canvas.axes) 
        canvas.axes._ax2 = canvas.axes.twinx()
        if(overlay == "intensity"):
            self.syllable.draw_intensity(canvas.axes._ax2)
        elif(overlay == "f0"):
            self.syllable.draw_f0(canvas.axes._ax2)
        
        canvas.axes._ax2.set_xlim([self.syllable.sound.xmin, self.syllable.sound.xmax])
        canvas.draw()

    def change_f0(self, *args, **kwargs):
        if(self.syllable is None):
            self.load_sound()

        #self.syllable.update_f0(*args, **kwargs)
        
        self.update_spectrogram(self.canvas_f0, overlay = "f0")

    def change_intensity(self, *args, **kwargs):
        if(self.syllable is None):
            self.load_sound()
            
        self.syllable.update_intensity(*args, **kwargs)
        self.update_spectrogram(self.canvas_amp, overlay = "intensity")

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
        print("segment")

if __name__ == '__main__':
    app=QtWidgets.QApplication(sys.argv)

    window = App()
    window.show()
    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("closing window...")
