## adjust_segmentation_settings.praat

selectObject: "Table segmentation_settings"
segmentation_settings = selected("Table")
## Initialize defaults
amp_tipping_point = Get value: 1, "value"
pitch_tipping_point = Get value: 2, "value"
we_tipping_point = Get value: 3, "value"	
amp_threshold = Get value: 4, "value"
pitch_threshold = Get value: 5, "value"
we_threshold = Get value: 6, "value"
noise_threshold = Get value: 7, "value"
noise_echo = Get value: 8, "value"


beginPause: "Fill attributes"
	comment: "Adjust segmentation settings"
	comment: "Tipping point:"
	comment: "Percent change from frame n to n+1 greater than input marks a segment boundary"
	positive: "Amp tipping point", amp_tipping_point
	positive: "Pitch tipping point", pitch_tipping_point
	positive: "Wiener entropy tipping point", we_tipping_point
	comment: "Threshold:"
	comment: "Segment boundary if percent change from frame n to n+1 is greater than input values for multiple acoustic values" 
	positive: "Amp threshold", amp_threshold
	positive: "Pitch threshoold", pitch_threshold
	positive: "Wiener entropy threshold", we_threshold
	comment: "Correct for background noise"
	comment: "Relative to RMS pressure, values below are considered silence"
	positive: "Noise threshold", noise_threshold
	comment: "Corrects for echo"
	boolean: "Noise echo", noise_echo
	
endPause: "Continue", 1

selectObject: pitch_settings
Set numeric value: 1, "value", amp_tipping_point
Set numeric value: 2, "value", pitch_tipping_point 
Set numeric value: 3, "value", wiener_entropy_tipping_point 
Set numeric value: 4, "value", amp_threshold
Set numeric value: 5, "value", pitch_threshold
Set numeric value: 6, "value", wiener_entropy_threshold
Set numeric value: 7, "value", noise_threshold
Set numeric value: 8, "value", noise_echo
