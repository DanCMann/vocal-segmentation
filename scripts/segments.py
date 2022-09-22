import random

## maybe this should be a subclass of contour???
class SegmentBoundaries:
    def __init__(
            self,
            amp_threshold = None,
            f0_threshold = None,
            we_threshold = None,
            correlated_threshold = None,
            boundary_buffer = None,
            window_size = None
            ): 

        self._amp_threshold = amp_threshold
        self._f0_threshold = f0_threshold
        self._we_threshold = we_threshold
        self._correlated_threshold = correlated_threshold
        self._boundary_buffer = boundary_buffer
        self._window_size = window_size
        
        self.boundaries = None
        
        self.error = None

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
 
    def get_segment_boundaries(self, sound):
        n_data = 10
        self.boundaries = [random.uniform(0, sound.duration) for i in range(n_data)]

if __name__ == '__main__':
    pass

