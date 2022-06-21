## adjust_pitch_settings.praat

selectObject: "Table pitch_settings_Manually_adjust_settings"
pitch_settings = selected("Table")
## Initialize defaults
max_species_freq = Get value: 1, "value"
min_species_pitch = Get value: 2, "value"
voicing_threshold = Get value: 3, "value"
octave_cost = Get value: 4, "value"
octave_jump_cost = Get value: 5, "value"
voiced_unvoiced_cost = Get value: 6, "value"
pitch_ceiling = Get value: 7, "value"


beginPause: "Fill attributes"
	comment: "Adjust pitch settings"
	positive: "Maximum frequency (Hz)", max_species_freq
	positive: "Minimum pitch (Hz)", min_species_pitch
	real: "Voicing threshold", voicing_threshold
	real: "Octave cost", octave_cost
	real: "Octave jump cost", octave_jump_cost
	real: "Voiced unvoiced cost", voiced_unvoiced_cost
	real: "Pitch ceiling", pitch_ceiling
	
endPause: "Continue", 1

selectObject: pitch_settings
Set numeric value: 1, "value", maximum_frequency
Set numeric value: 2, "value", minimum_pitch
Set numeric value: 3, "value", voicing_threshold
Set numeric value: 4, "value", octave_cost
Set numeric value: 5, "value", octave_jump_cost
Set numeric value: 6, "value", voiced_unvoiced_cost
Set numeric value: 6, "value", pitch_ceiling