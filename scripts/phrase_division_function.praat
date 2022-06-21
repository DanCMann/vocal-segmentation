	
#############################################################################################
#############################################################################################
#
############################ PHRASE DIVISION ##########################################
#
#############################################################################################
#############################################################################################
#
#
#	This script takes a phrase and searches for discontinuities in the signal. 
#	It looks for sharp differences in frequency, amplitude, and spectral energy
#	Any drastic changes in those 3 (defined by the 'tipping_point' variables) are 
#	used to divide the phrase into segments. It also looks for less drastic modulations
#	that are correlated. Any changes larger than the threshold variables that are 
#	found in amplitude and frequency or amplitude or wiener entropy are also used 
#	to divide the phrase. 
#	
#
#
################




include ./scripts/create_pitch_table.praat
include ./scripts/create_intensity_table.praat
include ./scripts/wiener_entropy.praat
include ./scripts/create_wienerentropy_table.praat


procedure phrase_division: pd.audio
..., pd.amp_tipping_point, pd.pitch_tipping_point, pd.we_tipping_point
..., pd.amp_threshold, pd.pitch_threshold, pd.we_threshold
..., pd.noise_threshold, pd.noise_echo
..., pd.max_species_freq, pd.min_species_pitch, pd.voicing_threshold
..., pd.octave_cost, pd.octave_jump_cost, pd.voiced_unvoiced_cost, pd.pitch_ceiling 




	#phrase = selected("Sound")
	phrase = pd.audio

	### Acts as a sound duration minimum. Shifts will often span more than one frame so this prevents the algorithm from 
	### treating one shift as multiple. 
	buffer = 0.5/pd.min_species_pitch 
	### For correlated shifts. If there are shifts in acoustic parameters within this range they are considered to be the same. Same in diff acoustic parameters
	error_threshold = 0.5/pd.min_species_pitch 
	### Determines if the segment is a silent gap or if is actual segment

	rms_silent_interval_threshold = pd.noise_threshold
	rms_silent_interval_threshold_burst = pd.noise_threshold
	if pd.noise_echo  = 1
		rms_silent_interval_threshold_echo = pd.noise_threshold * 3
	else
		rms_silent_interval_threshold_echo = pd.noise_threshold
	endif

	### Time step for we measurements
	time_step_we = 0.01

	

	
	selectObject: phrase
### MAX SPECIES!
	filt = Filter (pass Hann band): pd.min_species_pitch, pd.max_species_freq, 100
	selectObject: phrase


	#update minimum pitch to specifics of file
	pitch =  To Pitch (ac): 0,  pd.min_species_pitch, 15, "no", 0.03
	..., pd.voicing_threshold, pd.octave_cost, pd.octave_jump_cost, pd.voiced_unvoiced_cost
	..., pd.pitch_ceiling

	minimum_freq = Get minimum: 0, 0, "Hertz", "Parabolic"
	Remove
	selectObject: phrase
	minimum_freq = minimum_freq * 0.95	
	pitch =  To Pitch (ac): 0,  minimum_freq, 15, "no", 0.03
	..., pd.voicing_threshold, pd.octave_cost, pd.octave_jump_cost, pd.voiced_unvoiced_cost
	..., pd.pitch_ceiling

	intensity_minimum = minimum_freq * 2

	selectObject: phrase

	intensity = To Intensity: intensity_minimum, 0, "yes"

	selectObject: phrase
	textgrid = To TextGrid: "Intensity Pitch WienEntropy Tip Combined", ""

	@create_pitch_table: pitch, pd.pitch_threshold, pd.pitch_tipping_point

	selectObject: phrase

	for i from 1 to frames-1
		selectObject: create_pitch_table.output
		value = Get value: i, "Change"
		if value = 1
			if i = 1
				i = i
			else
				time = Get value: i, "MidPoint"
				selectObject: textgrid
				Insert boundary: 2, time
				#Insert point: 1, time, ""
			endif
		elif value = 2
			time = Get value: i, "MidPoint"
			selectObject: textgrid
			Insert boundary: 4, time
		else
			i = i
		endif
	endfor


	@create_intensity_table: intensity, pd.amp_threshold, pd.amp_tipping_point

	selectObject: phrase

	for i from 1 to frames-1
		selectObject: create_intensity_table.output
		value = Get value: i, "Change"
		if value = 1
			if i = 1
				i = i
			else
				time = Get value: i, "MidPoint"
				selectObject: textgrid
				Insert boundary: 1, time
				#Insert point: 1, time, ""
			endif
		elif value = 2
			time = Get value: i, "MidPoint"
			selectObject: textgrid
			### checks to make sure there isn't already a boundary
			edge = Get interval edge from time: 4, time
			if edge <> 0
				i = i
			else  
				Insert boundary: 4, time
			endif


		else
			i = i
		endif
	endfor


	selectObject: phrase

	window_size_we = 1/minimum_freq
	time_step_we = 0.5/minimum_freq

	@wiener_entropy: phrase, window_size_we, time_step_we, pd.min_species_pitch, pd.max_species_freq

	table_we = selected("Table")
	@create_wienerentropy_table: table_we, pd.we_threshold, pd.we_tipping_point
	table_we = create_wienerentropy_table.output
	selectObject: phrase

	for i from 1 to frames-1
		selectObject: table_we
		value = Get value: i, "Change"
		if value = 1
			if i = 1
				i = i
			else
				time = Get value: i, "MidPoint"
				selectObject: textgrid
				Insert boundary: 3, time
				#Insert point: 1, time, ""
			endif
		elif value = 2
			time = Get value: i, "MidPoint"
			selectObject: textgrid
			### checks to make sure there isn't already a boundary
			edge = Get interval edge from time: 4, time
			if edge <> 0
				i = i
			else  
				Insert boundary: 4, time
			endif
		else
			i = i
		endif
	endfor

			
	#####################################################################
	#


	selectObject: textgrid

	n_tiers = Get number of tiers
	for i from 1 to n_tiers
		n_intervals[i] = Get number of intervals: i
	endfor

	###########################################################
	#
	## Set Large Modulations
	#
	#
	for i from 1 to n_intervals[4]
		start.1 = Get start point: 4, i		
		check = 0
		n_intervals[5] = Get number of intervals: 5
		for j from 1 to n_intervals[5]
			start.5 = Get start point: 5, j
			difference = start.1 - start.5
			difference = abs(difference)
			if difference < buffer
				check = check + 1
			else 
				j = j
			endif
		endfor
		if check = 0
			Insert boundary: 5, start.1
		else
			i = i
		endif
	endfor

	###########################################################
	#
	### Compare Amplitude with Frequency and Wiener Entropy

	for i from 1 to n_intervals[1]
		n_intervals = n_intervals[2] + n_intervals[3]
		count = 0
		start.1 = Get start point: 1, i
		for j from 1 to n_intervals
			if j <= n_intervals[2]
				compare_tier = 2
				interval = j
			elif j > n_intervals[2]
				compare_tier = 3
				interval = j - n_intervals[2]
			endif
			start.2 = Get start point: compare_tier, interval
			difference = start.1 - start.2
			difference = abs(difference)
			if difference < error_threshold
				count = count + 1
			else 
				j = j
			endif
			#appendInfoLine: i, "	", j, "	", difference, "	", count
		endfor
		if count >= 1 
			n_intervals[5] = Get number of intervals: 5
			check = 0
			for j from 1 to n_intervals[5]
				start.5 = Get start point: 5, j
				difference = start.1 - start.5
				difference = abs(difference)
				#writeInfoLine: start.1 difference
				if difference < buffer
					check = check + 1
				else 
					j = j
				endif
			endfor
			#writeInfoLine: check
			if check = 0
				Insert boundary: 5, start.1
			else
				i = i
			endif
		else
			i = i 
		endif
	endfor


	##########################################################################


	selectObject: phrase
	#$#$#
	phrase$ = selected$("Sound")
	start_phrase = Get start time
	end_phrase = Get end time
	rms = Get root-mean-square: 0, 0
	threshold = rms * rms_silent_interval_threshold
	#writeInfoLine: rms, "	", threshold
	selectObject: textgrid
	n_intervals = Get number of intervals: 5
	for i from 1 to n_intervals
		selectObject: textgrid
		start = Get starting point: 5, i
		end = Get end point: 5, i
		selectObject: phrase
		interval = Get maximum: start, end, "Sinc70"
		#appendInfoLine: interval
		if interval < threshold
			selectObject: textgrid
			Set interval text: 5, i, "silent"
			
		else
			i = i
		endif
	endfor
	

	### This checks for short, intense bursts of energy. Some silence intervals may have a short peak but overall be silent	
	for i from 1 to n_intervals
		selectObject: textgrid
		label$ = Get label of interval: 5, i
		if label$ <> "silent"
		####### NOTE START AND END POINTS	
		### Gets start points in textgrids
			start = Get starting point: 5, i
			end = Get end point: 5, i
							
				
	####### RMS

			selectObject: filt
			rms_phrase =  Get root-mean-square: start_phrase, end_phrase
			threshold = rms_phrase * rms_silent_interval_threshold_burst
			
			max = Get maximum: start, end, "Sinc70"
			min = Get minimum: start, end, "Sinc70"
			if abs(min) > max
				max_time = Get time of minimum: start, end, "Sinc70"
			else
				max_time = Get time of maximum: start, end, "Sinc70"
			endif
			
			#appendInfoLine: rms, "	", threshold, max, "	", min
	
	###### START TIME
			start_sample = Get sample number from time: start
			start_sample = floor(start_sample)
			end_sample = Get sample number from time: end
			end_sample = ceiling(end_sample)
			#$#$#
			sample = start_sample-1
			repeat
				#$#$#
				sample = sample + 1
				value = Get value at sample number: 1, sample
				value = abs(value)
			until value > threshold or sample >= end_sample

			start_time = Get time from sample number: sample

		###### END TIME
			#$#$#
			sample = end_sample+1
			repeat 
				#$#$#
				sample = sample - 1
				value = Get value at sample number: 1, sample
				value = abs(value)
				
			until value > threshold or sample <= start_sample

			end_time = Get time from sample number: sample

			duration = end_time - start_time
			if duration <= 0 
				selectObject: textgrid
				Set interval text: 5, i, "silent"
				#appendInfoLine: phrase$, "	", i, "	", duration, "	", start_time, "	", end_time	
			else
				duration = duration
			endif	
		endif
	endfor	

	
	selectObject: textgrid
	counter = 1
	repeat 
		label$ = Get label of interval: 5, counter
		counter = counter + 1
	until label$ <> "silent" or counter = n_intervals

	threshold = rms_phrase * rms_silent_interval_threshold_echo
	for i from counter to n_intervals
		selectObject: textgrid
		start = Get starting point: 5, i
		end = Get end point: 5, i

		selectObject: phrase
		interval = Get maximum: start, end, "Sinc70"
		#appendInfoLine: interval
		if interval < threshold
			selectObject: textgrid
			Set interval text: 5, i, "silent"
			
		else
			i = i
		endif
	endfor


	selectObject: textgrid

	n_segments = Count intervals where: 5, "is equal to", ""
	count = n_segments - 1
	n_intervals = Get number of intervals: 5
	for i from 1 to n_intervals
		label$ = Get label of interval: 5, i
		if label$ = ""
			new_label$ = string$(n_segments - count) 
			Set interval text: 5, i, new_label$
			count = count-1
		else
			i = i
		endif
	endfor

	selectObject: textgrid
	for i from 1 to 4
		Remove tier: 1
	endfor




	
	selectObject: create_intensity_table.output
	plusObject: create_pitch_table.output
	plusObject: table_we
	plusObject: intensity
	plusObject: pitch
	plusObject: filt

	Remove



	selectObject: textgrid

	n.intervals = Get number of intervals: 1
	Duplicate tier: 1, 2, "segment"
	for i.interval from 1 to n.intervals-1
		label$ = Get label of interval: 1, i.interval
		label_two$ = Get label of interval: 1, i.interval + 1
		if label$ = "silent" and label_two$ = "silent"
			end = Get end point: 1, i.interval
			Remove boundary at time: 2, end
			interval = Get interval at time: 2, end
			Set interval text: 2, interval, "silent"
		else
		endif
	endfor
	Remove tier: 1


endproc














