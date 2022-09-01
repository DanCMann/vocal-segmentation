import parselmouth
import numpy as np
from scipy.stats.mstats import gmean

class Intensity:
    def __init__(self, minimum_pitch=100, time_step:float=None, subtract_mean:bool= True):
        self._minimum_pitch = minimum_pitch
        self._time_step = time_step
        self._subtract_mean = subtract_mean
        self.contour = None
        self.time = None
        
        self._intensity = None
        
        # This should help pass the error along
        # there should be a better way to do this
        self.error = None

    def get_intensity_contour(self, sound):
        try:
            self._intensity = sound.to_intensity(self._minimum_pitch, self._time_step, self._subtract_mean)
            self.contour = self._intensity.values.T # the dimensions might need to be resized? 
            self.time = self._intensity.xs() # check to make sure this is appropriate
            self.error = None
        except Exception as e:
            self.error = e

    @property
    def minimum_pitch(self):
        return self._minimum_pitch
    @minimum_pitch.setter
    def minimum_pitch(self, new_minimum_pitch):
        self._minimum_pitch = new_minimum_pitch
    
    @property
    def time_step(self):
        return self._time_step
    @time_step.setter
    def time_step(self):
        self._time_step = new_time_step
    
    @property
    def subtract_mean(self):
        return self._subtract_mean
    @subtract_mean.setter
    def subtract_mean(self, new_subtract_mean):
        self._subtract_mean = new_subtract_mean

class F0:
    def __init__(self, time_step = None, pitch_floor: float = 500, max_num_of_candidates: int = 15, 
            very_accurate:bool = False, silence_threshold: float = 0.03, voicing_threshold: float = 0.45,
            octave_cost: float = 0.01, octave_jump_cost: float = 0.35,voiced_unvoiced_cost: float = 0.14,
            pitch_ceiling: float = 15000.0):

        self._time_step = time_step
        self._pitch_floor = pitch_floor
        self._max_num_of_candidates = max_num_of_candidates
        self._very_accurate = very_accurate
        self._silence_threshold = silence_threshold
        self._voicing_threshold = voicing_threshold
        self._octave_cost = octave_cost
        self._octave_jump_cost = octave_jump_cost
        self._voiced_unvoiced_cost = voiced_unvoiced_cost
        self._pitch_ceiling = pitch_ceiling

        self._f0 = None
        
        self.contour = None
        self.time = None
        
        self.error = None

    def get_f0_contour(self, sound):
        try:
            self._f0 = sound.to_pitch_ac(time_step = self._time_step, pitch_floor = self._pitch_floor,
                    max_number_of_candidates = self._max_num_of_candidates,very_accurate = self._very_accurate,
                    silence_threshold = self._silence_threshold,voicing_threshold = self._voicing_threshold,
                    octave_cost = self._octave_cost, octave_jump_cost = self._octave_jump_cost,
                    voiced_unvoiced_cost = self._voiced_unvoiced_cost,pitch_ceiling = self._pitch_ceiling
                    )
            pitch_values = self._f0.selected_array['frequency']
            pitch_values[pitch_values==0] = np.nan
            self.contour = pitch_values
            self.time = self._f0.xs()
            self.error = None
        except Exception as e:
            self.error = e
            print(e)

    @property
    def time_step(self):
        return self._time_step
    @time_step.setter
    def time_step(self, new_time_step):
        self._time_step = new_time_step
    
    @property
    def pitch_floor(self):
        return self._pitch_floor
    @pitch_floor.setter
    def pitch_floor(self, new_pitch_floor):
        self._pitch_floor = new_pitch_floor
    
    @property
    def max_num_of_candidates(self):
        return self._max_num_of_candidates
    @max_num_of_candidates.setter
    def max_num_of_candidates(self, new_max_num_cand):
        self._max_num_of_candidates = new_max_num_cand
    
    @property
    def very_accurate(self):
        return self._very_accurate
    @very_accurate.setter
    def very_accurate(self, new_very_accurate):
        self._very_accurate = new_very_accurate

    @property
    def silence_threshold(self):
        return self._silence_threshold
    @silence_threshold.setter
    def silence_threshold(self, new_silence_threshold):
        self._silence_threshold = new_silence_threshold

    @property
    def voicing_threshold(self):
        return self._voicing_threshold
    @voicing_threshold.setter
    def voicing_threshold(self, new_voicing_threshold):
        self._voicing_threshold = new_voicing_threshold
    
    @property
    def octave_cost(self):
        return self._octave_cost
    @octave_cost.setter
    def octave_cost(self, new_octave_cost):
        self._octave_cost = new_octave_cost

    @property
    def octave_jump_cost(self):
        return self._octave_jump_cost
    @octave_jump_cost.setter
    def octave_jump_cost(self, new_octave_jump_cost):
        self._octave_jump_cost = new_octave_jump_cost
    
    @property
    def voiced_unvoiced_cost(self):
        return self._voiced_unvoiced_cost
    @voiced_unvoiced_cost.setter
    def voiced_unvoiced_cost(self, new_voiced_unvoiced_cost):
        self._voiced_unvoiced_cost = new_voiced_unvoiced_cost
    
    @property
    def pitch_ceiling(self):
        return self._pitch_ceiling
    @pitch_ceiling.setter
    def pitch_ceiling(self, new_pitch_ceiling):
        self._pitch_ceiling = new_pitch_ceiling

class WienerEntropy:
    def __init__(self, window_size = 0.002, time_step = 0.001, min_freq = 500, max_freq = 10000):
        
        self.window_size = window_size
        self.time_step = time_step
        self.min_freq = min_freq
        self.max_freq = max_freq

        self.contour = None
        self.time = None
        
        self.error = None

    def get_we_contour(self, sound):
        try:
            ###!!! Preallocate sizes

            period = parselmouth.praat.call(sound, "Get sampling period")
            duration = parselmouth.praat.call(sound, "Get total duration")
            start_time = parselmouth.praat.call(sound, "Get time from sample number", 1)
            frames = int(np.floor((((duration)- self.window_size)/self.time_step) + 1))
            print(period, duration, start_time, frames)
            #time = []
            time = np.zeros(frames)
            #wiener_entropy = []
            wiener_entropy = np.zeros(frames)

            for frame in range(frames):
                ### take sound slices and get 
                time_point = start_time + (self.window_size/2)
                #time.append(time_point)
                time[frame] = time_point
                sound_slice = sound.extract_part(
                    from_time = start_time,
                    to_time = start_time + self.window_size,
                    window_shape = 'GAUSSIAN1',
                    relative_width = 1,
                    preserve_times = True)
                spect = sound_slice.to_spectrum(fast = False)
                start_bin = round(spect.get_bin_number_from_frequency(self.min_freq))
                end_bin = round(spect.get_bin_number_from_frequency(self.max_freq))
                start_time = start_time + self.time_step
                #magnitude = []
                magnitude = np.zeros(end_bin - start_bin)
                for bin in range(start_bin, end_bin):
                    ### calculate magnitude
                    count = bin - start_bin
                    real = spect.get_real_value_in_bin(bin)
                    imag = spect.get_imaginary_value_in_bin(bin)
                    #magnitude.append(((real/period)**2) + ((imag/period)**2))
                    magnitude[bin - start_bin] = ((real/period)**2) + ((imag/period)**2)

                arithmetic_mean = np.mean(magnitude)
                geometric_mean = gmean(magnitude)
                #wiener_entropy.append(np.log(geometric_mean/arithmetic_mean))
                wiener_entropy[frame] = np.log(geometric_mean/arithmetic_mean)
            self.time = time
            self.contour = wiener_entropy
            self.error = None
        except Exception as e:
            self.error = e

class Syllable(parselmouth.Sound):
    def __init__(self, filename, *args, **kwargs):
        super().__init__(filename, *args, **kwargs)
        self.filename = filename
        self.sound = parselmouth.Sound(self.filename)
        self.spectrogram = self.sound.to_spectrogram()
        
        intensity = Intensity(minimum_pitch = 400)
        intensity.get_intensity_contour(self.sound)
        self.intensity = intensity

        f0 = F0()
        f0.get_f0_contour(self.sound)
        self.f0 = f0

        wiener_entropy = WienerEntropy()
        wiener_entropy.get_we_contour(self.sound)
        self.wiener_entropy = wiener_entropy 

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
    '''
    print(syllable.wiener_entropy.contour)
    print(syllable.wiener_entropy.time)
 
