	
procedure wiener_entropy: wiener_entropy.sound_object, wiener_entropy.window_size
..., wiener_entropy.time_step, wiener_entropy.minimum_frequency, wiener_entropy.maximum_frequency
### Wiener Entropy
### Calculates wiener entropy values for a sound. Outputs a table with wiener entropy values for points
###	... along the sound.  

#wiener_entropy.praat(sound_we, window_size_we, time_step_we, minimum_frequency_we, maximum_frequency_we)

### Arguments

# Needs sound, window size, time step, minimum frequency, and maximum frequency 
	
	we_window_size_check = variableExists ("wiener_entropy.window_size")
		if we_window_size_check = 0
			beginPause: "Error: Window size not defined"
				comment: "please exit and define"
			endPause: "Continue", 1
		else
		endif
	time_step_we_check = variableExists ("wiener_entropy.time_step")
		if time_step_we_check = 0
			beginPause: "Error: Window size not defined"
				comment: "please exit and define"
			endPause: "Continue", 1
		else
		endif
	minimum_frequency_we_check = variableExists ("wiener_entropy.minimum_frequency")
		if minimum_frequency_we_check = 0
			beginPause: "Error: Window size not defined"
				comment: "please exit and define"
			endPause: "Continue", 1
		else
		endif
	maximum_frequency_we_check = variableExists ("wiener_entropy.maximum_frequency")
		if maximum_frequency_we_check = 0
			beginPause: "Error: Window size not defined"
				comment: "please exit and define"
			endPause: "Continue", 1
		else
		endif

######Inputs
	selectObject: wiener_entropy.sound_object
	period = Get sampling period
	duration = Get total duration
	start_time = Get time from sample number: 1
	frames = floor((((duration)-wiener_entropy.window_size)/wiener_entropy.time_step) + 1)


##### Output

	#table_we = Create Table with column names: "WE_Table", frames, "Time WE Difference Change PercentChange MidPoint"
	table_we = Create Table with column names: "WE_Table", frames, "Time Wiener_Entropy"
##### Function

	
	wiener_entropy= 0

	
	for i.frame_we from 1 to frames
		selectObject: wiener_entropy.sound_object
		time = start_time + (wiener_entropy.window_size/2)

		Extract part: start_time, start_time + wiener_entropy.window_size, "Gaussian1", 1, "yes"
		sound_slice = selected("Sound")
		start_time = start_time + wiener_entropy.time_step

		spect = To Spectrum: "no"
		start_bin = Get bin number from frequency: wiener_entropy.minimum_frequency
		start_bin = round(start_bin)
		end_bin = Get bin number from frequency: wiener_entropy.maximum_frequency
		end_bin = round(end_bin)
		table_slice = Create Table with column names: "table", end_bin-start_bin + 1, "Frequency Magnitude"
		selectObject: spect
		for i.bin_we from start_bin to end_bin
			frequency = Get frequency from bin number: i.bin_we
			real = Get real value in bin: i.bin_we
			imag = Get imaginary value in bin: i.bin_we	
				#mag = sqrt(((real/period)^2) + ((imag/period)^2))
			mag = ((real/period)^2) + ((imag/period)^2)
			selectObject: table_slice
			Set numeric value: -start_bin + (i.bin_we + 1) , "Frequency", frequency
			Set numeric value: -start_bin + (i.bin_we + 1), "Magnitude", mag
			selectObject: spect
		endfor
		selectObject: table_slice
		nrows = Get number of rows
		log_sum = 0
		sum = 0
		for i.row_we from 1 to nrows
			magnitude = Get value: i.row_we, "Magnitude"
			sum = magnitude + sum
			log_magnitude = ln(magnitude)
			log_sum = log_sum + log_magnitude
		endfor
		arithmetic_mean = sum/nrows
		geometric_mean = exp(log_sum/nrows)
		wiener_entropy_slice = ln(geometric_mean/arithmetic_mean)
		selectObject: table_we
		Set numeric value: i.frame_we, "Time", time
		Set numeric value: i.frame_we, "Wiener_Entropy", wiener_entropy_slice
		
		#wiener_entropy = wiener_entropy + wiener_entropy_slice
		selectObject: sound_slice
		plusObject: spect
		plusObject: table_slice
		Remove
	endfor



	##### Output

	selectObject: table_we
	table_we_narm = Extract rows where column (text): "Wiener_Entropy", "is not equal to", "--undefined--"
	selectObject: table_we
	Remove
	.output = selectObject: table_we_narm

endproc	