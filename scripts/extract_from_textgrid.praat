	



include ./scripts/phrase_division_function.praat

procedure extract_from_textgrid: et.audio, et.textgrid, et.tier, et.label$


selectObject: et.textgrid

n.phrase = Count intervals where: et.tier, "is equal to", et.label$
## put check in here? Previous version had a failsafe. 
	
n.tiers = Get number of tiers
Insert interval tier: n.tiers+ 1, "segmentation"
	
plusObject: et.audio
	
Extract intervals where: et.tier, "yes", "is equal to", et.label$
	
n.phrase = numberOfSelected("Sound")
for i.phrases from 1 to n.phrase
	phrase'i.phrases' = selected("Sound", i.phrases)
endfor


### get segmentation settings from txt files
selectObject: "Table segmentation_settings"
et.amp_tipping_point = Get value: 1, "value"
et.pitch_tipping_point = Get value: 2, "value"
et.we_tipping_point = Get value: 3, "value"	
et.amp_threshold = Get value: 4, "value"
et.pitch_threshold = Get value: 5, "value"
et.we_threshold = Get value: 6, "value"
et.noise_threshold = Get value: 7, "value"
et.noise_echo = Get value: 8, "value"


### get pitch settings from txt files
selectObject: "Table pitch_settings"
et.max_species_freq = Get value: 1, "value"
et.min_species_pitch = Get value: 2, "value"
et.voicing_threshold = Get value: 3, "value"
et.octave_cost = Get value: 4, "value"
et.octave_jump_cost = Get value: 5, "value"
et.voiced_unvoiced_cost = Get value: 6, "value"
et.pitch_ceiling = Get value: 7, "value"


for i.phrases from 1 to n.phrase

	selectObject: phrase'i.phrases'
	extracted_phrase = selected("Sound")
	phrase_name$ = selected$("Sound")
		


	@phrase_division: extracted_phrase
	..., et.amp_tipping_point, et.pitch_tipping_point, et.we_tipping_point
	..., et.amp_threshold, et.pitch_threshold, et.we_threshold
	..., et.noise_threshold, et.noise_echo
	..., et.max_species_freq, et.min_species_pitch, et.voicing_threshold
	..., et.octave_cost, et.octave_jump_cost, et.voiced_unvoiced_cost, et.pitch_ceiling


	phrase_textgrid = selected("TextGrid")
	selectObject: phrase_textgrid
	n.intervals = Get number of intervals: 1


	for i.segments from 1 to n.intervals
		selectObject: phrase_textgrid
		start = Get starting point: 1, i.segments
		### Praat automatically puts an interval boundary at 0 and the end of textgrid. 
		### This can cause problems when merging. 
		#if start = 0
		#	start = 0.0000001
		#else
		#	start = start
		#endif
		label$ = Get label of interval: 1, i.segments
		if i.segments = n.intervals
			end = Get end point: 1, i.segments
			total_duration = Get total duration
			### Praat automatically puts an interval boundary at 0 and the end of textgrid. 
			### This can cause problems when merging. 
		#	if end = total_duration
		#		end = end - 0.0000001
		#	else
		#		end = end
		#	endif
		else
			i.segments = i.segments
		endif

		selectObject: et.textgrid
		check = Get interval boundary from time: n.tiers + 1, start
		if check = 0
			double_check = Get interval edge from time: n.tiers + 1, start
			if double_check = 0
				Insert boundary: n.tiers + 1, start
			else
			endif
		else
		endif

		if i.segments = n.intervals
			#Insert boundary: n.tiers + 1, end
		else
			i.segments  = i.segments 
		endif
		interval = Get interval at time: n.tiers + 1, start
		Set interval text: n.tiers + 1, interval, label$
	endfor	
	selectObject: phrase_textgrid
	plusObject: extracted_phrase
	Remove
endfor

selectObject: et.audio, et.textgrid
endproc