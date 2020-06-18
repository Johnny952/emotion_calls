from pydub import AudioSegment
import numpy as np
import os
import glob
import shutil

def split_ravdess(input_path,output_path,step_size,skip_first=False):
	#path = "./RAVDESS/speech_by_class/"
	#output_path = "./ravdess/"
	path = input_path
	subdir_paths = glob.glob(output_path+"*")
	if len(subdir_paths) != 0:
		for folder_path in subdir_paths:
			shutil.rmtree(folder_path)
	class_folders = glob.glob(path+"*")
	for folder in class_folders:
		os.mkdir(output_path+folder.split("/")[-1])

	audio_paths = glob.glob(path+"**/*.wav")
	step_size = step_size

	for path in audio_paths:
		filename = path.split("/")[-1].split(".")[0]
		print("SPLITTING ",filename)
		label = path.split("/")[-2]
		audio = AudioSegment.from_wav(path) 
		if(skip_first):
			t = 1000
		else:
			t = 0
		window_counter = 0
		has_length = True
		while(has_length):
			audio_window = audio[t:t+step_size]
			if(len(audio_window)==step_size):
				audio_window.export(output_path+"/"+label+"/"+filename+"_"+str(window_counter)+".wav",format='wav')
				window_counter +=1
				t += step_size
			else:
				has_length=False

if __name__ == '__main__':
	split_ravdess("./RAVDESS/speech_by_class/","./ravdess/",1000,skip_first=True)







