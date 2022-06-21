
	
procedure create_pitch_table: cpt.pitch_object, cpt.pitch_threshold, cpt.pitch_tipping_point

#""" Takes a pitch object and creates a table. Table includes F0 at each time point.
#""" Function also calculates the difference and the percent change of F0 at time point t and time point t + 1.  
#""" Function also includes a value for each time point, "Change". This value is either 0, 1, or 2. 
#""" 0 indicates that the percent change was not greater than either user specified threshold value. 
#""" 1 indicates that the percent change is larger than the user specified "pitch_threshold" value. This 
#""" value is used to check correlated changes between F0 and amplitude. 2 means the percent change is greater
#""" that the user specified "pitch_tipping_point" value. This value means that there was a large enough change 
#""" in F0 values that F0 alone marks a boundary. 

	selectObject: cpt.pitch_object
	frames = Get number of frames
	.output = Create Table with column names: "pitch_table", frames, "Time Pitch Difference Change PercentChange MidPoint"
		for i from 1 to frames
		selectObject: cpt.pitch_object
		value = Get value in frame: i, "Hertz"

		if value = undefined
			value = 1
		else
			value = value
		endif	
		time = Get time from frame number: i
		selectObject: .output 
		Set numeric value: i, "Pitch", value
		Set numeric value: i, "Time", time
	endfor

	selectObject: .output
	mean = Get mean: "Pitch"
	
	time.1 = Get value: 1, "Time"
	time.2 = Get value: 2, "Time"
	time_difference = time.2 - time.1
	for i from 1 to frames-1
		value.1 = Get value: i, "Pitch"
		value.2 = Get value: i + 1, "Pitch"
		time = Get value: i, "Time"
		difference = value.2 - value.1
		midpoint = time + (time_difference/2)
		Set numeric value: i, "Difference", difference
		percent_difference = abs((value.1 - value.2) / ((value.1 + value.2)/2) * 100)
		Set numeric value: i, "PercentChange", percent_difference
		Set numeric value: i, "MidPoint", midpoint
	endfor
	number_of_rows = Get number of rows
	Remove row: number_of_rows


	for i from 1 to frames-1
		value = Get value: i, "PercentChange"
		if value = undefined
			value = 0
		else
			value = value
		endif
		#writeInfoLine: value.1
		if value > cpt.pitch_threshold
			Set numeric value: i, "Change", 1
		else
			Set numeric value: i, "Change", 0 
		endif
		value = abs(value)
		if value > cpt.pitch_tipping_point
			Set numeric value: i, "Change", 2
		else
			i = i
		endif
	endfor
endproc