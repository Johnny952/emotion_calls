import os
import glob
import numpy as np
import shutil 
from pydub import AudioSegment
from tqdm import tqdm
import pandas as pd
from joblib import dump, load
import matplotlib.pyplot as plt

import librosa
import librosa.display
from keras.models import model_from_json
import keras

# Parameters for audio feature extraction
mw = "2.5"
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
            audio_window.export(output_dir +"/"+ filename+"_"+str(window_counter)+".wav",format='wav')
            window_counter += 1#int(step_size/1000)
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
    mylist= os.listdir(audio_dir)
    print(mylist)
    df = []
    seconds = []
    for index,filepath in enumerate(mylist):
        X, sample_rate = librosa.load(audio_dir+"/"+filepath, res_type='kaiser_fast',duration=2.5,sr=22050*2,offset=0)
        sample_rate = np.array(sample_rate)
        data = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=13), axis=0)
        if len(data) < 216:
            data_pad = np.zeros(216)
            data_pad[:data[len]] = data
            data = data_pad
        second = int(filepath.split("/")[-1].split(".")[0].split("_")[-1])
        df.append(data)
        seconds.append(second)
    # Drops rows with null values
    df = pd.DataFrame(df).fillna(0)
    df["seconds"] = seconds
    df = df.sort_values(by=["seconds"]).reset_index(drop=True)
    df = df.drop(["seconds"],axis=1)
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

    # global EMOTIONS 
    # Loads trained classifications model
    json_file = open('./models/model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    clf = model_from_json(loaded_model_json)
    # load weights into new model
    clf.load_weights("./models/Emotion_Voice_Detection_Model.h5")
    opt = keras.optimizers.rmsprop(lr=0.00001, decay=1e-6)
    clf.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
    
    df = preprocessed
    X = np.array(df.iloc[:,:])
    x_cnn= np.expand_dims(X, axis=2)
    # Predicts a probability for each emotion in every audio sample
    p = clf.predict(x_cnn)
    predictions = []
    for raw in p:
        prediction = [raw[0]+raw[5],raw[1]+raw[6],raw[2]+raw[7],raw[3]+raw[8],raw[4]+raw[9]]
        predictions.append(prediction)
    display_table = pd.DataFrame(predictions)*100
    display_table = display_table.round(decimals=1)
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

    """
    if(display==True):
        # Displays emotions relative to time from audio in path
        table.iloc[::5,:].plot(x="second", y=EMOTIONS, kind="line",linewidth=2)
        plt.title("{} emotions".format(path.split("/")[-1].split(".")[0]))
        plt.xlabel("Tiempo [segundos]")
        plt.ylabel("Porcentaje")
        plt.show()
    return table
    """


if __name__ == '__main__':
    # Audio test samples
    thunderstrack = "./test_audios/thunderstrack.wav"
    seu_jorge = "./test_audios/seu_jorge.wav"
    results_thunderstrack = main(thunderstrack, display=True)
