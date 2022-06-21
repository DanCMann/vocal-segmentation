procedure create_wienerentropy_table: cwt.wiener_entropy_data, cwt.we_threshold, cwt.we_tipping_point

#""" Takes a Wiener Entropy data table and modifieds the table. Table includes Wiener Entropy at each time point.
#""" Function also calculates the difference and the percent change of W.E. at time point t and time point t + 1.  
#""" Function also includes a value for each time point, "Change". This value is either 0, 1, or 2. 
#""" 0 indicates that the percent change was not greater than either user specified threshold value. 
#""" 1 indicates that the percent change is larger than the user specified "we_threshold" value. This 
#""" value is used to check correlated changes between W.E. and amplitude. 2 means the percent change is greater
#""" that the user specified "we_tipping_point" value. This value means that there was a large enough change 
#""" in W.E. values that W.E.alone marks a boundary. 
	selectObject: cwt.wiener_entropy_data
	
	Append column: "Difference"
	Append column: "Change"
	Append column: "PercentChange"
	Append column: "MidPoint"
	Set column label (label): "Wiener_Entropy", "WE"

	frames = Get number of rows

	mean = Get mean: "WE"
	
	time.1 = Get value: 1, "Time"
	time.2 = Get value: 2, "Time"
	time_difference = time.2 - time.1
	for i from 1 to frames-1
		value.1 = Get value: i, "WE"
		value.2 = Get value: i + 1, "WE"
		time = Get value: i, "Time"
		difference = value.2 - value.1
		midpoint = time + (time_difference/2)
		Set numeric value: i, "Difference", difference
		#$#$#
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
		if value > cwt.we_threshold
			Set numeric value: i, "Change", 1
		else
			Set numeric value: i, "Change", 0 
		endif
		value = abs(value)
		if value > cwt.we_tipping_point
			Set numeric value: i, "Change", 2
		else
			i = i
		endif
	endfor
.output = selected("Table")
endproc