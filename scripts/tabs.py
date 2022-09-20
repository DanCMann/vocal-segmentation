import sys
import os
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from scripts.syllable import Syllable
from scripts.utils import DoubleSlider

TABROWS = 9
TABCOLS = 5

CANVAS_W = 10
CANVAS_H = 7

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=CANVAS_W, height=CANVAS_H, dpi=300):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class TabStruct(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.syllable = None

        self.canvas = MplCanvas(self)
        self.canvas.axes.contour_ax = self.canvas.axes.twinx()
        
        self.wav_canvas = MplCanvas(self, width = CANVAS_W, height = 1)
        
        self.contour_type = None

        # put above constructor??
        self.rows = TABROWS
        self.cols = TABCOLS

        self.set_ui()

    def set_ui(self):
        self.add_layout()
        self.define_widgets()
        self.click_connections()
        self.add_widgets()

    def define_widgets(self):
        self.plot_button = QtWidgets.QPushButton("Plot")

    def click_connections(self):
        self.plot_button.clicked.connect(lambda: self.update_spectrogram(self.canvas))

    def add_widgets(self):
        self.grid.addWidget(self.canvas, 0, 0, self.rows-1, self.cols-3, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.wav_canvas, self.rows-1, 0, 1, self.cols-3, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.plot_button, self.rows, self.cols, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

    def add_layout(self):
        self.grid =  QtWidgets.QGridLayout(self)

    def set_syllable(self, syllable):
        self.syllable = syllable

    def update_spectrogram(self, canvas):

        if(canvas.axes.has_data()):
            canvas.axes.clear()
            canvas.axes.contour_ax.clear()
        else:
            if(self.syllable is None):
                self.load_sound()
                self.syllable.draw_wavform(self.wav_canvas.axes)
                self.wav_canvas.draw() 
        self.syllable.draw_spectrogram(canvas.axes) 
        if(self.contour_type == "intensity"):
            self.syllable.draw_intensity(canvas.axes.contour_ax)
        elif(self.contour_type == "f0"):
            self.syllable.draw_f0(canvas.axes.contour_ax)
        elif(self.contour_type == "wiener_entropy"):
            self.syllable.draw_wiener_entropy(canvas.axes.contour_ax)
        else:
            #self.segment_syllable()
            self.syllable.draw_segments(canvas.axes)

        canvas.axes.contour_ax.set_xlim([self.syllable.sound.xmin, self.syllable.sound.xmax])
        canvas.draw()

    def change_contour(self, **kwargs):
        if(self.syllable is None):
            self.load_sound()
        else:
            ### abstract??
            if self.contour_type == "intensity":
                self.syllable.update_intensity(**kwargs)
                if not self.syllable.intensity.error:
                    self.update_spectrogram(self.canvas)
                else:
                    # Change to write in a message box
                    print(self.syllable.intensity.error)

            if self.contour_type == "f0":
                self.syllable.update_f0(**kwargs)
                if not self.syllable.f0.error:
                    self.update_spectrogram(self.canvas)
                else:
                    # Change this to write in a message box
                    print(self.syllable.f0.error)

            if self.contour_type == "wiener_entropy":
               self.syllable.update_wiener_entropy(**kwargs)
               if not self.syllable.wiener_entropy.error:
                   self.update_spectrogram(self.canvas)
               else:
                   print(self.syllable.wiener_entropy.error)
            if self.contour_type == "seg":
                self.syllable.update_segmentation(**kwargs)
                if not self.syllable.segmentation.error:
                    self.update_spectrogram(self.canvas)
                else:
                    print(self.syllable.segmentation.error)

    def load_sound(self, filename = "./examples/budgie_single.wav"):
        #self.filename = self.filename_text.text()
        self.filename = filename
        self.syllable = Syllable(self.filename)
        #Raise an error here if there is no filename

class MainTab(TabStruct):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def define_widgets(self):
        self.filename_text = QtWidgets.QLineEdit()
        self.browse_button = QtWidgets.QPushButton("Browse")
 
    def click_connections(self):
        self.browse_button.clicked.connect(lambda: self.browse_file())
    
    def add_widgets(self):
        self.grid.addWidget(self.browse_button, 0, 1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.filename_text, 0, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

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

class AmpTab(TabStruct):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.contour_type = 'intensity'

    def define_widgets(self):

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
        
        super().define_widgets()

    def click_connections(self):

        self.min_pitch_slider.valueChanged.connect(lambda: self.change_contour(minimum_pitch = self.min_pitch_slider.value()))
        super().click_connections()

    def add_widgets(self):
        self.grid.addWidget(self.min_pitch_label, 4, self.cols-2, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.min_pitch_slider, 4, self.cols-1, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.amp_time_step_label, 5, self.cols-2, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.amp_time_step, 5, self.cols-1, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        super().add_widgets()

class F0Tab(TabStruct):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        self.contour_type = 'f0'

    def define_widgets(self):
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

        super().define_widgets()

    def click_connections(self):
        
        #self.f0_time_step.valueChanged.connect(lambda: self.change_contour(time_step = self.f0_time_step.value()))
        self.f0_pitch_floor.valueChanged.connect(lambda: self.change_contour(pitch_floor = self.f0_pitch_floor.value()))
        self.f0_max_n_cand.valueChanged.connect(lambda: self.change_contour(max_num_of_candidates = self.f0_max_n_cand.value()))
        self.f0_sil_threshold.valueChanged.connect(lambda: self.change_contour(silence_threshold = self.f0_sil_threshold.value())) 
        self.f0_voicing_threshold.valueChanged.connect(lambda: self.change_contour(voicing_threshold = self.f0_voicing_threshold.value()))
        self.f0_octave_cost.valueChanged.connect(lambda: self.change_contour(octave_cost = self.f0_octave_cost.value()))
        self.f0_octave_jump_cost.valueChanged.connect(lambda: self.change_contour(octave_jump_cost = self.f0_octave_jump_cost.value()))
        self.f0_voiced_unvoiced_cost.valueChanged.connect(lambda: self.change_contour(voiced_unvoiced_cost = self.f0_voiced_unvoiced_cost.value()))
        self.f0_pitch_ceiling.valueChanged.connect(lambda: self.change_contour(pitch_ceiling = self.f0_pitch_ceiling.value()))
        
        super().click_connections()

    def add_widgets(self):
        
        # Removed because it causes hard to catch crashes and there's an auto calc of the time step anyway
        #self.grid.addWidget(self.f0_time_step_label, 0, 4, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        #self.grid.addWidget(self.f0_time_step, 0, 5, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        self.grid.addWidget(self.f0_pitch_floor_label, 1, self.cols-2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.f0_pitch_floor, 1, self.cols-1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        self.grid.addWidget(self.f0_max_n_cand_label, 2, self.cols-2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.f0_max_n_cand, 2, self.cols-1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

        self.grid.addWidget(self.f0_sil_threshold_label, 3, self.cols-2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.f0_sil_threshold, 3, self.cols-1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        self.grid.addWidget(self.f0_voicing_threshold_label, 4, self.cols-2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.f0_voicing_threshold, 4, self.cols-1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        self.grid.addWidget(self.f0_octave_cost_label, 5, self.cols-2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.f0_octave_cost, 5, self.cols-1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        self.grid.addWidget(self.f0_octave_jump_cost_label, 6, self.cols-2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.f0_octave_jump_cost, 6, self.cols-1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        self.grid.addWidget(self.f0_voiced_unvoiced_cost_label, 7, self.cols-2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.f0_voiced_unvoiced_cost, 7, self.cols-1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        self.grid.addWidget(self.f0_pitch_ceiling_label, 8, self.cols-2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.f0_pitch_ceiling, 8, self.cols-1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        super().add_widgets()

class WienTab(TabStruct):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.contour_type = "wiener_entropy"
    
    def define_widgets(self):
        self.min_freq_label = QtWidgets.QLabel("Minimum Frequency")

        self.min_freq_slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
        self.min_freq_slider.setMinimum(10)
        self.min_freq_slider.setMaximum(2000)
        self.min_freq_slider.setValue(400)
        self.min_freq_slider.setTickPosition(QtWidgets.QSlider.TicksRight)
        self.min_freq_slider.setTickInterval(10)

        self.max_freq_label = QtWidgets.QLabel("Maximum Frequency")

        self.max_freq_slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
        self.max_freq_slider.setMinimum(1000)
        self.max_freq_slider.setMaximum(30000)
        self.max_freq_slider.setValue(15000)
        self.max_freq_slider.setTickPosition(QtWidgets.QSlider.TicksRight)
        self.max_freq_slider.setTickInterval(1000)

        self.time_step_label = QtWidgets.QLabel("Time Step")

        self.time_step = QtWidgets.QDoubleSpinBox()
        self.time_step.setRange(0, 10)
        self.time_step.setValue(0)
        self.time_step.setSingleStep(0.001)
        
        self.window_size_label = QtWidgets.QLabel("Window Size")

        self.window_size = QtWidgets.QDoubleSpinBox()
        self.window_size.setRange(0, 10)
        self.window_size.setValue(0)
        self.window_size.setSingleStep(0.001)
        
        super().define_widgets()

    def click_connections(self):
        #self.plot_button.clicked.connect(lambda: self.update_spectrogram(self.canvas))
        self.min_freq_slider.valueChanged.connect(lambda: self.change_contour(min_freq = self.min_freq_slider.value()))
        self.max_freq_slider.valueChanged.connect(lambda: self.change_contour(max_freq = self.max_freq_slider.value()))
        self.time_step.valueChanged.connect(lambda: self.change_contour(time_step = self.time_step.value()))
        self.window_size.valueChanged.connect(lambda: self.change_contour(window_size = self.window_size.value()))

        super().click_connections()

    def add_widgets(self):
        self.grid.addWidget(self.min_freq_label, 1, self.cols-2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.min_freq_slider, 1, self.cols-1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.max_freq_label, 2, self.cols-2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.max_freq_slider, 2, self.cols-1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.time_step_label, 3, self.cols-2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.time_step, 3, self.cols-1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.window_size_label, 4, self.cols-2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.window_size, 4, self.cols-1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        
        super().add_widgets()

class SegTab(TabStruct):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.contour_type = 'seg'

    def define_widgets(self):
        self.segment_button = QtWidgets.QPushButton("Segment")
        
        self.buffer_slider = DoubleSlider(QtCore.Qt.Vertical)
        self.buffer_slider.setMinimum(0)
        self.buffer_slider.setMaximum(1)
        self.buffer_slider.setInterval(0.01)
        self.buffer_slider.setValue(0.05)
        self.buffer_slider.setTickPosition(QtWidgets.QSlider.TicksRight)
        self.buffer_slider.setTickInterval(0.01)

        super().define_widgets()

    def click_connections(self):
        #self.plot_button.clicked.connect(lambda: self.update_spectrogram(self.canvas))
        #self.update_button.clicked.connect(self.update_plot)
        self.segment_button.clicked.connect(lambda: self.update_spectrogram(self.canvas))
        self.buffer_slider.valueChanged.connect(lambda: self.change_contour(boundary_buffer = self.buffer_slider.value()))
        super().click_connections()

    def add_widgets(self):
        #self.grid.addWidget(self.update_button, 0, 1, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.segment_button, 2, 2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(self.buffer_slider, 1, self.cols-2, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        super().add_widgets()
    
    def change_segmentation(self):
        print("check")
        
if __name__ == '__main__':
    pass
