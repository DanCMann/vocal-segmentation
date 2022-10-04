import parselmouth
import numpy as np
import random
from scripts.contours import *

class Syllable(parselmouth.Sound):
    def __init__(
            self, 
            filename, 
            amp_threshold = None,
            f0_threshold = None,
            we_threshold = None,
            correlated_threshold = None,
            boundary_buffer = None,
            window_size = None,
            *args, 
            **kwargs
            ):
        super().__init__(filename, *args, **kwargs)
        self.filename = filename
        self.sound = parselmouth.Sound(self.filename)
        self.spectrogram = self.sound.to_spectrogram()

        self._amp_threshold = amp_threshold
        self._f0_threshold = f0_threshold
        self._we_threshold = we_threshold
        self._correlated_threshold = correlated_threshold
        self._boundary_buffer = boundary_buffer
        self._window_size = window_size
        
        self.segment_boundaries = None
        
        self.error = None

        intensity = Intensity(minimum_pitch = 400)
        intensity.get_intensity_contour(self.sound)
        self.intensity = intensity

        f0 = F0()
        f0.get_f0_contour(self.sound)
        self.f0 = f0

        wiener_entropy = WienerEntropy(time_step = 0.001)
        wiener_entropy.get_we_contour(self.sound)
        self.wiener_entropy = wiener_entropy 

        #segmentation = SegmentBoundaries()
        #segmentation.get_segment_boundaries()
        #self.segmentation = segmentation
        self.segment_boundaries = None
        self.get_segment_boundaries()

    @property
    def amp_threshold(self):
        return self._amp_threshold
    @amp_threshold.setter
    def amp_threshold(self, new_amp_threshold):
        self._amp_threshold = new_amp_threshold
  
    @property
    def f0_threshold(self):
        return self._f0_threshold
    @f0_threshold.setter
    def f0_threshold(self, new_f0_threshold):
        self._f0_threshold = new_f0_threshold
   
    @property
    def we_threshold(self):
        return self._we_threshold
    @we_threshold.setter
    def we_threshold(self, new_we_threshold):
        self._we_threshold = new_we_threshold
 
    @property
    def correlated_threshold(self):
        return self._correlated_threshold
    @correlated_threshold.setter
    def correlated_threshold(self, new_correlated_threshold):
        self._correlated_threshold = new_correlated_threshold
  
    @property
    def boundary_buffer(self):
        return self._boundary_buffer
    @boundary_buffer.setter
    def boundary_buffer(self, new_boundary_buffer):
        self._boundary_buffer = new_boundary_buffer
   
    @property
    def window_size(self):
        return self._window_size
    @window_size.setter
    def window_size(self, new_window_size):
        self._window_size = new_window_size
        
    def get_segment_boundaries(self):
        n_data = 10
        self.segment_boundaries = [random.uniform(0, self.sound.duration) for i in range(n_data)]

    def update_intensity(self, minimum_pitch = None, time_step = None, subtract_mean = None ):
        if minimum_pitch:
            self.intensity.minimum_pitch = minimum_pitch
        if time_step:
            self.intensity.time_step = time_step
        if subtract_mean:
            self.intensity.subtract_mean = subtract_mean

        self.intensity.get_intensity_contour(self.sound)

    def update_f0(self, time_step = None, pitch_floor = None, max_num_of_candidates = None, 
            very_accurate = None, silence_threshold = None, voicing_threshold = None,
            octave_cost = None, octave_jump_cost = None, voiced_unvoiced_cost = None, pitch_ceiling = None):
        if time_step:
            self.f0.time_step = time_step
        if pitch_floor:
            self.f0.pitch_floor = pitch_floor
        if max_num_of_candidates:
            self.f0.max_num_of_candidates = max_num_of_candidates
        if very_accurate:
            self.f0.very_accurate = very_accurate
        if silence_threshold:
            self.f0.silence_threshold = silence_threshold
        if voicing_threshold:
            self.f0.voicing_threshold = voicing_threshold
        if octave_cost:
            self.f0.octave_cost = octave_cost
        if octave_jump_cost:
            self.f0.octave_jump_cost = octave_jump_cost
        if voiced_unvoiced_cost:
            self.f0.voiced_unvoiced_cost = voiced_unvoiced_cost
        if pitch_ceiling:
            self.f0.pitch_ceiling = pitch_ceiling

        self.f0.get_f0_contour(self.sound)
    
    def update_wiener_entropy(self, time_step = None, window_size = None, min_freq = None, 
            max_freq = None):
        if time_step:
            self.wiener_entropy.time_step = time_step
        if window_size:
            self.wiener_entropy.window_size = window_size
        if min_freq:
            self.wiener_entropy.min_freq = min_freq
        if max_freq:
            self.wiener_entropy.max_freq = max_freq

        self.wiener_entropy.get_we_contour(self.sound)

    def update_segmentation(self, amp_threshold = None, f0_threshold = None, we_threshold = None,
            correlated_threshold = None, boundary_buffer = None, window_size = None):
        if amp_threshold:
            self.amp_threshold = amp_threshold
        if f0_threshold:
            self.f0_threshold = f0_threshold
        if we_threshold:
            self.we_threshold = we_threshold
        if correlated_threshold:
            self.correlated_threshold = correlated_threshold
        if boundary_buffer:
            self.boundary_buffer = boundary_buffer
        if window_size:
            self.window_size = window_size
        #n_data = 10
        #self.xdata = [random.uniform(0, self.duration) for i in range(n_data)]
        self.get_segment_boundaries()

    def draw_spectrogram(self, canvas_axes, dynamic_range=70):
        '''
        The best way I could figure out to do this was to pass the actual matplotlib.axes object as an arg. 
        Probably a better way, but honestly it might just be fine to test on normal figures and make sure
          that it would also plot on a noncanvas object. 
        '''
        X, Y = self.spectrogram.x_grid(), self.spectrogram.y_grid()
        print("length of X is {}, of Y is {}".format(len(X), len(Y)))
        print("------")
        print(X)
        print(Y)
        print("-------")
        print(self.spectrogram.values)
        sg_db = 10 * np.log10(self.spectrogram.values)
        canvas_axes.pcolormesh(
                # removes last element from X and Y
                # I'm not happywith this solution, but gouraud shading operates different from flat
                # the dimensions of C are treated differently it seems. 
                X[:-1], Y[:-1], sg_db, 
                vmin=sg_db.max() - dynamic_range, 
                facecolor = 'white',
                edgecolors = 'face', 
                #alpha = 0.5,
                shading='gouraud',
                #interpolate_grids=True,
                #allmatch=True,
                snap = True,
                rasterized = True,
                cmap='binary')
        #canvas_axes.set_ylim([self.spectrogram.ymin, self.spectrogram.ymax])
        
        canvas_axes.set_xlabel("time [s]")
        canvas_axes.set_ylabel("frequency [Hz]")
    
    def draw_wavform(self, canvas_axes):
        canvas_axes.plot(self.sound.xs(), self.sound.values.T, linewidth = 0.5)
        #canvas_axes.plot([self.sound.xmin, self.sound.xmax])
        canvas_axes.set_xlabel("time [s]")
        canvas_axes.set_ylabel("amplitude")

    def draw_intensity(self, canvas_axes):
        #canvas_axes.plot(self.intensity.xs(), self.intensity.values.T, linewidth=3, color='w')
        #canvas_axes.plot(self.intensity.xs(), self.intensity.values.T, linewidth=1)
        canvas_axes.plot(self.intensity.time, self.intensity.contour,linewidth=3, color='w')
        canvas_axes.plot(self.intensity.time, self.intensity.contour, linewidth=1)
        canvas_axes.grid(False)
        #canvas_axes.set_ylim(0)
        canvas_axes.set_ylabel("intensity [dB]")

    def draw_f0(self, canvas_axes):
        '''
        pitch_values = self.f0.selected_array['frequency']
        print(pitch_values)
        pitch_values[pitch_values==0] = np.nan
        canvas_axes.plot(self.f0.xs(), pitch_values, 'o', markersize=5, color='w')
        canvas_axes.plot(self.f0.xs(), pitch_values, 'o', markersize=2)
        '''
        canvas_axes.plot(self.f0.time, self.f0.contour, 'o', markersize=5, color='w')
        canvas_axes.plot(self.f0.time, self.f0.contour, linewidth=1)
        canvas_axes.grid(False)
        canvas_axes.set_ylim(0, self.spectrogram.ymax)
        canvas_axes.set_ylabel("fundamental frequency [Hz]")
    
    def draw_wiener_entropy(self, canvas_axes):
        canvas_axes.plot(self.wiener_entropy.time, self.wiener_entropy.contour, linewidth=3, color = 'w')
        canvas_axes.plot(self.wiener_entropy.time, self.wiener_entropy.contour, linewidth=1)
        canvas_axes.grid(False)
        canvas_axes.set_ylabel("Wiener Entropy")

    def draw_segments(self, canvas_axes):
        canvas_axes.grid(False)
        canvas_axes.axes.contour_ax.vlines(x = self.segment_boundaries, ymin = 0, ymax = 10000, colors= 'r')

if __name__ == '__main__':
    syllable = Syllable('./examples/budgie_single.wav')
    '''
    print(syllable.intensity.contour)
    print(syllable.intensity.time)
    syllable.update_intensity(minimum_pitch = 500)
    print(syllable.intensity.contour)
    print(syllable.intensity.time)
    print("\n--------\n")
    print(syllable.f0.contour)
    print(syllable.f0.time)
    syllable.update_f0(pitch_floor = 600)
    print(syllable.f0.contour)
    print(syllable.f0.time)
    
    print(syllable.wiener_entropy.contour)
    print(syllable.wiener_entropy.time)
    '''

    syllable.f0.threshold_detection(5)
    print(syllable.f0.boundaries)
    syllable.f0.buffer_check(0.005)
    print(syllable.f0.buffered_boundaries)
