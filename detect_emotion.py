import os
import glob
import numpy as np
import shutil 
from pydub import AudioSegment
from tqdm import tqdm
import pandas as pd
from joblib import dump, load
import matplotlib.pyplot as plt

mw = "1.0"
ms = "1.0"
sw = "0.050"
ss = "0.050"
EMOTIONS = ["neutral", "calm","happy", "sad", "angry", "fearful", "disgust", "surprised"]

def split_audio(audiofile, step_size):
	output_dir = "/".join(audiofile.split("/")[:-1]) + "/splits"
	if(os.path.isdir(output_dir)): 
		shutil.rmtree(output_dir)
		os.mkdir(output_dir)
	else:
		os.mkdir(output_dir)

	filename = audiofile.split("/")[-1].split(".")[0] 
	audio = AudioSegment.from_wav(audiofile) 
	t = 0
	window_counter = 1
	has_length = True
	while(has_length):
		audio_window = audio[t:t+step_size]
		if(len(audio_window)==step_size):
			audio_window.export(output_dir + "/"+ filename+"_"+str(window_counter)+".wav",format='wav')
			window_counter += int(step_size/1000)
			t += step_size
		else:
			has_length=False
	return output_dir

def preprocess_audio(audio_dir):
	os.system('python3 ./pyAudioAnalysis/pyAudioAnalysis/audioAnalysis.py featureExtractionDir -i {} -mw {} -ms {} -sw {} -ss {}'.format(audio_dir, mw, ms, sw, ss))
	filenames = glob.glob(audio_dir+"/*.npy")
	df = []
	clf = load("./models/emotion_clf.joblib")
	for filepath_idx in tqdm(range(len(filenames))):
		filepath = filenames[filepath_idx]
		second = filepath.split("/")[-1].split(".")[0].split("_")[-1]
		data = np.load(filepath).flatten()
		df.append([second,data])
	df = pd.DataFrame(df,columns=['second','feats']).dropna()
	invalid_rows = []
	for index,row in df.iterrows():
		feats = np.array(row['feats'])
		if(not np.all(np.isfinite(feats)) or not np.all(np.isfinite(feats))):
			invalid_rows.append(index)
	df = df.drop(invalid_rows)
	return df

def predict_audio(preprocessed):
	
	global EMOTIONS
	clf = load("./models/emotion_clf.joblib")
	df = preprocessed
	predictions = clf.predict_proba(df['feats'].to_list())
	display_table = pd.DataFrame(predictions, columns = EMOTIONS)*100
	display_table = display_table.round(decimals=1)
	display_table["second"] = list(map(int, df["second"]))
	display_table = display_table.sort_values(by=["second"]).reset_index(drop=True)
	return display_table


def main(path):
	audio_dir = split_audio(path, float(mw)*1000)
	preprocessed = preprocess_audio(audio_dir)
	table = predict_audio(preprocessed)

	table.iloc[::5,:].plot(x="second", y=EMOTIONS, kind="line",linewidth=2)
	plt.title("{} emotions".format(path.split("/")[-1].split(".")[0]))
	plt.xlabel("Tiempo [segundos]")
	plt.ylabel("Porcentaje")
	plt.show()
	return table


if __name__ == '__main__':
	thunderstrack = "./test_audios/thunderstrack.wav"
	seu_jorge = "./test_audios/seu_jorge.wav"
	results_thunderstrack = main(thunderstrack)
