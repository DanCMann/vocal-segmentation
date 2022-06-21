procedure create_intensity_table: cit.intensity_object, cit.intensity_threshold, cit.intensity_tipping_point 

#""" Takes an intensity object and creates a table. Table includes amplitude at each time point.
#""" Function also calculates the difference and the percent change of intensity at time point t and time point t + 1.  
#""" Function also includes a value for each time point, "Change". This value is either 0, 1, or 2. 
#""" 0 indicates that the percent change was not greater than either user specified threshold value. 
#""" 1 indicates that the percent change is larger than the user specified "intensity_threshold" value. This 
#""" value is used to check correlated changes between amplitude and F0 or Wiener entropy. 2 means the percent change is greater
#""" that the user specified "intensity_tipping_point" value. This value means that there was a large enough change 
#""" in amplitude values that amplitude alone marks a boundary. 
	
	selectObject: cit.intensity_object
	
	frames = Get number of frames

	.output= Create Table with column names: "intensity_table", frames, "Time Intensity Difference Change PercentChange MidPoint"
	for i from 1 to frames
		selectObject: cit.intensity_object
		value = Get value in frame: i
		#value = maximum_intensity - value
		#value = (value - minimum_intensity)/(maximum_intensity - minimum_intensity)* 100
		#value = 10^(value/20) * 0.0001
		#value = (value - minimum_intensity)/(maximum_intensity - minimum_intensity)
		time = Get time from frame number: i
		selectObject: .output
		Set numeric value: i, "Intensity", value
		Set numeric value: i, "Time", time
		
	endfor
	
	selectObject: .output
	mean = Get mean: "Intensity"
	time.1 = Get value: 1, "Time"
	time.2 = Get value: 2, "Time"
	time_difference = time.2 - time.1


	for i from 1 to frames-1
		value.1 = Get value: i, "Intensity"
		value.2 = Get value: i + 1, "Intensity"
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
			value = 1
		else
			value = value
		endif
		#writeInfoLine: value.1
		if value > cit.intensity_threshold
			Set numeric value: i, "Change", 1
		else
			Set numeric value: i, "Change", 0 
		endif
		#value = abs(value)
		if value > cit.intensity_tipping_point
			Set numeric value: i, "Change", 2
		else
			i = i
		endif
	endfor
endproc