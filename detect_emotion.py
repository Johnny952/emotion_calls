import os
import glob
import numpy as np
import shutil 
from pydub import AudioSegment
from tqdm import tqdm
import pandas as pd
from joblib import dump, load
import matplotlib.pyplot as plt

# Parameters for audio feature extraction
mw = "1.0"
ms = "1.0"
sw = "0.050"
ss = "0.050"
# Labels of emotions
EMOTIONS = ["neutral", "calm","happy", "sad", "angry", "fearful", "disgust", "surprised"]

def split_audio(audiofile, step_size):
	"""
	splits audio, located in path audiofile, in several segments of step_size [ms]
	length each
	--------------
	Arguments
	-------------
	audiofile: string
		path to audio file
	step_size: int
		length, in milliseconds, of each audio segment
	-------------
	Returns: string
		path to folder with audio segments
	"""

	output_dir = "/".join(audiofile.split("/")[:-1]) + "/splits"
	# Creates output directory for audio splits
	if(os.path.isdir(output_dir)): 
		shutil.rmtree(output_dir)
		os.mkdir(output_dir)
	else:
		os.mkdir(output_dir)

	filename = audiofile.split("/")[-1].split(".")[0] 
	audio = AudioSegment.from_wav(audiofile) 
	t = 0 
	window_counter = 1 # split id
	has_length = True 
	# Continues until entire length of audio file is segmented
	while(has_length):
		audio_window = audio[t:t+step_size] # audio split
		# checks whether audio split is of appropiate size
		if(len(audio_window)==step_size):
			audio_window.export(output_dir + "/"+ filename+"_"+str(window_counter)+".wav",format='wav')
			window_counter += int(step_size/1000)
			t += step_size
		# if audio split is smaller than step_size, breaks the loop
		else:
			has_length=False
	return output_dir

def preprocess_audio(audio_dir):
	"""
	extracts short-term and mid-term audio features from each split audio file in audio_dir 
	and returns as a pandas dataframe with time indications
	-------------
	Arguments
	-------------
	audio_dir: string
		path to folder with audio splits
	-------------
	Returns: DataFrame
		table with extracted audiofeatures according to their relative time in general audio file
	"""
	# Extracts short and mid term features of each audio file and stores
	# them in the same folder
	os.system('python3 ./pyAudioAnalysis/pyAudioAnalysis/audioAnalysis.py featureExtractionDir -i {} -mw {} -ms {} -sw {} -ss {}'.format(audio_dir, mw, ms, sw, ss))
	filenames = glob.glob(audio_dir+"/*.npy")
	df = []
	# Loads each feature matrix, flattens it and stores it alongside corresponding time
	for filepath_idx in tqdm(range(len(filenames))):
		filepath = filenames[filepath_idx]
		second = filepath.split("/")[-1].split(".")[0].split("_")[-1]
		data = np.load(filepath).flatten()
		df.append([second,data])
	df = pd.DataFrame(df,columns=['second','feats']).dropna()
	# Drops rows with null or infinite values
	invalid_rows = []
	for index,row in df.iterrows():
		feats = np.array(row['feats'])
		if(not np.all(np.isfinite(feats)) or not np.all(np.isfinite(feats))):
			invalid_rows.append(index)
	df = df.drop(invalid_rows)
	return df

def predict_audio(preprocessed):
	"""
	predicts emotions over each sample of preprocessed audio files
	-------------
	Arguments
	-------------
	preprocessed: DataFrame
		table were each row is a feature vector from an audio file and its
		correspoding time
	-------------
	Returns: DataFrame
		table were each row contains a vector with emotion predictions in percentages
		and the time relative to the general audio file
	"""
	
	global EMOTIONS
	# Loads trained classifications model
	clf = load("./models/emotion_clf.joblib")
	df = preprocessed
	# Predicts a probability for each emotion in every audio sample
	predictions = clf.predict_proba(df['feats'].to_list())
	# Arranges predictions as percentages and includes time relative to general
	# audio file
	display_table = pd.DataFrame(predictions, columns = EMOTIONS)*100
	display_table = display_table.round(decimals=1)
	display_table["second"] = list(map(int, df["second"]))
	display_table = display_table.sort_values(by=["second"]).reset_index(drop=True)
	return display_table


def main(path, display=False):
	"""
	main function for handling audio emotion prediction
	-------------
	Arguments
	-------------
	path: string
		path to audio file
	-------------
	Returns: DataFrame
		table with emotion predictions for each time step
	"""
	# Splits audio file into several audio segments of mw [s] of length
	audio_dir = split_audio(path, float(mw)*1000)
	# Extracts features for each audio segment
	preprocessed = preprocess_audio(audio_dir)
	# Predicts emotions for each audio segment
	table = predict_audio(preprocessed)

	if(display=True):
		# Displays emotions relative to time from audio in path
		table.iloc[::5,:].plot(x="second", y=EMOTIONS, kind="line",linewidth=2)
		plt.title("{} emotions".format(path.split("/")[-1].split(".")[0]))
		plt.xlabel("Tiempo [segundos]")
		plt.ylabel("Porcentaje")
		plt.show()
	return table


if __name__ == '__main__':
	# Audio test samples
	thunderstrack = "./test_audios/thunderstrack.wav"
	seu_jorge = "./test_audios/seu_jorge.wav"
	results_thunderstrack = main(thunderstrack, display=True)
