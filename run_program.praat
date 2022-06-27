form Fill attributes
	comment Sound file to segment
	sentence Sound_pathway ./examples/budgie_multiple.wav

	comment Choose the appropriate segmentation settings
	optionmenu Segmentation: 1
	  option Default
	  option Manually adjust settings

	comment Do you have an associated textgrid file?
	optionmenu Textgrid: 1
		option Yes
		option Create textgrid
	sentence Textgrid_pathway ./examples/budgie_multiple.Textgrid

	comment Which units should be segmented?
	comment Enter both the tier and the interval labels you want to segment
	positive Tier_to_segment: 1
	sentence Labels_to_segment: phrase
	
	comment Does the audio file contain multiple sounds to be segmented?
	comment (Not necessary if you input a preexisting textgrid file)
	optionmenu Number_of_sounds: 1
		option Single
		option Multiple

	comment Choose the appropriate pitch settings
	optionmenu Species: 2
		option Human
		option Budgerigar
		option Manually adjust settings
	comment 
    
endform



############################################################################################

include ./scripts/create_segmentation_textgrid.praat
include ./scripts/extract_from_textgrid.praat


### 	Load and manipulate settings for Segmentation	###################################

seg_settings_default = Read Table from tab-separated file: "./settings/segmentation_settings.txt"


if segmentation = 2
	runScript: "./scripts/adjust_segmentation_settings.praat"
else
	
endif


############################################################################################


### 	Load and manipulate settings for Pitch functions	############################

pitch_settings_default = Read Table from tab-separated file: "./settings/pitch_settings.txt"

pitch_settings = Extract rows where column (text): "species", "is equal to", species$
selectObject: pitch_settings_default
Remove
selectObject: pitch_settings
Rename: "pitch_settings"

if species = 3
	runScript: "./scripts/adjust_pitch_settings.praat"
else
	
endif

############################################################################################





### Run segmentation ######################################################################


audio = Read from file: sound_pathway$

### 	Read/Create textgrid	##########################################################

if textgrid = 1
	textgrid = Read from file: textgrid_pathway$
else
	@to_textgrid: audio
	textgrid = selected("TextGrid")
endif

plusObject: textgrid

@extract_from_textgrid: audio, textgrid, tier_to_segment, labels_to_segment$
textgrid = selected("TextGrid")
############################################################################################
### 	Clean object window	 ###########################################################
selectObject: pitch_settings
plusObject: seg_settings_default
Remove
selectObject: audio
plusObject: textgrid
View & Edit
############################################################################################