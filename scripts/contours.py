import parselmouth
import numpy as np
from scipy.stats.mstats import gmean
import random
from scripts.segments import SegmentBoundaries

class Contour:
    def __init__(self, time_step:float=None):
        self._time_step = time_step
        self.time = None
        self.contour = None
        self.error = None

    @property
    def time_step(self):
        return self._time_step
    @time_step.setter
    def time_step(self, new_time_step):
        self._time_step = new_time_step
 
    def calc_percent_change(self) :
        # should I do percent change by frame or standardize by time?

        start_value = 0.0
        self.percent_change = np.zeros(len(self.contour)) 

        for i in range(0, len(self.contour)):
            row = self.contour[i]
            self.percent_change[i] = abs(((row - start_value) / start_value)) * 100
            #print(i, "::", start_value, row, "CHANGE:", self.percent_change[i])
            start_value = row

    def threshold_detection(self, threshold) :
        self.calc_percent_change()
        self.boundaries = [i for i in range(len(self.percent_change)) if self.percent_change[i] >= threshold]
        #self.boundaries = [1 if x >= threshold else 0 for x in self.percent_change]
        #breakpoint()
        #self.boundaries = [i for i in range(len(self.boundaries)) if self.boundaries[i] == 1]
        self.boundaries = self.time[self.boundaries] 
    
    def buffer_check(self, buffer):
        '''  create a new list by checking if there are 'clusters' of changes
        ''' 
        self.buffered_boundaries = np.zeros(len(self.boundaries))
        breakpoint()
        i = 0
        count = 0
        sum = 0

        while i < len(self.boundaries) - 1 :
            # check to make sure all are being evaluated
            #print(list[i])

            diff = abs(self.boundaries[i] - self.boundaries[i+1])
            #print(diff)
            if diff > buffer :
                if count != 0 :
                    count += 1
                    sum += self.boundaries[i]
                    #print(sum/count)
                    self.buffered_boundaries[i] = sum/count
                else:
                    self.buffered_boundaries[i] = self.boundaries[i]

                count = 0
                sum = 0
                i += 1
            else : 
                count += 1
                sum += self.boundaries[i]
                i += 1
                if count == len(self.boundaries)-1:
                    self.buffered_boundaries[i] = sum/count
                    #print("check")
        

class Intensity(Contour):
    def __init__(self, minimum_pitch=100, time_step: float=None, subtract_mean:bool= True):
        super().__init__(time_step)
        self._minimum_pitch = minimum_pitch
        self._subtract_mean = subtract_mean
        
        self._intensity = None
        
        # This should help pass the error along
        # there should be a better way to do this
        #self.error = None

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
    def subtract_mean(self):
        return self._subtract_mean
    @subtract_mean.setter
    def subtract_mean(self, new_subtract_mean):
        self._subtract_mean = new_subtract_mean

class F0(Contour):
    def __init__(self, time_step: float = None, pitch_floor: float = 500, max_num_of_candidates: int = 15, 
            very_accurate:bool = False, silence_threshold: float = 0.03, voicing_threshold: float = 0.45,
            octave_cost: float = 0.01, octave_jump_cost: float = 0.35,voiced_unvoiced_cost: float = 0.14,
            pitch_ceiling: float = 15000.0):

        super().__init__(time_step)
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

class WienerEntropy(Contour):
    def __init__(self, time_step: float=None, window_size = 0.002, min_freq = 500, max_freq = 10000):
        
        super().__init__(time_step) 
        self._window_size = window_size
        self._min_freq = min_freq
        self._max_freq = max_freq

    def get_we_contour(self, sound):
        try:
            ###!!! Preallocate sizes

            period = parselmouth.praat.call(sound, "Get sampling period")
            duration = parselmouth.praat.call(sound, "Get total duration")
            start_time = parselmouth.praat.call(sound, "Get time from sample number", 1)
            frames = int(np.floor((((duration)- self._window_size)/self._time_step) + 1))
            print(period, duration, start_time, frames)
            #time = []
            time = np.zeros(frames)
            #wiener_entropy = []
            wiener_entropy = np.zeros(frames)

            for frame in range(frames):
                ### take sound slices and get 
                time_point = start_time + (self._window_size/2)
                #time.append(time_point)
                time[frame] = time_point
                sound_slice = sound.extract_part(
                    from_time = start_time,
                    to_time = start_time + self._window_size,
                    window_shape = 'GAUSSIAN1',
                    relative_width = 1,
                    preserve_times = True)
                spect = sound_slice.to_spectrum(fast = False)
                start_bin = round(spect.get_bin_number_from_frequency(self._min_freq))
                end_bin = round(spect.get_bin_number_from_frequency(self._max_freq))
                start_time = start_time + self._time_step
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

    @property
    def window_size(self):
        return self._window_size
    @window_size.setter
    def window_size(self, new_window_size):
        self._window_size = new_window_size
    
    @property
    def min_freq(self):
        return self._min_freq
    @min_freq.setter
    def min_freq(self, new_min_freq):
        self._min_freq = new_min_freq

    @property
    def max_freq(self):
        return self._max_freq
    @max_freq.setter
    def max_freq(self, new_max_freq):
        self._max_freq = new_max_freq

if __name__ == '__main__':
    pass

