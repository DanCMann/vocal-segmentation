### Python version 3.9.5
import subprocess
import os
import difflib

wd = os.getcwd()
os.chdir("..")

# Test one
## Make sure segment boundaries for a single budgie syllable match with original

wav_path ="examples/budgie_single.wav"
textgrid_path = "examples/budgie_single.Textgrid"

subprocess.call(["/usr/bin/praat", "--run", "run_program.praat", wav_path, "Default", "Create textgrid", textgrid_path, "1", "phrase", "Single", "Budgerigar", "CSV file", "./testing/output.csv"])


model_fname = 'testing/single_budgie1.csv'
out_fname = 'testing/output.csv'
  
with open(model_fname) as model:
    model_text = model.readlines()
  
with open(out_fname) as output:
    output_text = output.readlines()

diffs = difflib.unified_diff(model_text, output_text, fromfile=model_fname, tofile='out_fname', lineterm='')
diff_count = 0
for line in diffs:
    diff_count += 1
    print(line)

print("Number of line differences: {}".format(diff_count))
