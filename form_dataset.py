from os import listdir
import os
import shutil

mw = "1.0"
ms = "1.0"
sw = "0.050"
ss = "0.050"

copy_files = False

db_path = "pyaudio"
data_path = "pyaudio/data"
labels_path = "pyaudio/labels.csv"

meld_subdirs = [
    "MELD.Sounds/dev_sounds",
    "MELD.Sounds/test_sounds",
    "MELD.Sounds/train_sounds"
]
meld_labels = [
    "MELD.Sounds/dev_sent_emo.csv",
    "MELD.Sounds/test_sent_emo.csv",
    "MELD.Sounds/train_sent_emo.csv",
]

ravdess_name = "ravdess"

features_fileExt = [".wav_st.csv", ".wav_st.npy"]

emotion_conv = {
    "neutral": "01", 
    "joy": "03", 
    "sadness": "04", 
    "anger": "05", 
    "surprise": "08", 
    "fear": "06", 
    "disgust": "07"
}

def progressBar(current, total, barLength = 20):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))

    print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')

def read_filenames(directory):
    return ["{}/{}".format(directory, l) for l in listdir(directory)]

def read_subdir(subdirs):
    files = []
    for subdir in subdirs:
        files += read_filenames(subdir)
    return files

def move_ravdess(audios, folder, labels_file, copy=True):
    total = len(audios)
    
    for index, audio in enumerate(audios):
        # Get audio name
        name = audio.split("/")[-1]
        progressBar(index, total)

        # Move csv and npy files
        if copy:
            shutil.copy("{}{}".format(audio, features_fileExt[0]), "{}/{}{}".format(folder, name, features_fileExt[0]))
            shutil.copy("{}{}".format(audio, features_fileExt[1]), "{}/{}{}".format(folder, name, features_fileExt[1]))
        else:
            os.rename("{}{}".format(audio, features_fileExt[0]), "{}/{}{}".format(folder, name, features_fileExt[0]))
            os.rename("{}{}".format(audio, features_fileExt[1]), "{}/{}{}".format(folder, name, features_fileExt[1]))
        
        # Get label
        label = name.split("-")[2]
        # Write label in labels file
        with open(labels_file, "a+") as csv:
            csv.write("{},{}\n".format(name, label))
    
    progressBar(total, total)

def move_meld(audios, folder, labels_path, labels, copy=True):
    total = len(audios)
    
    for index, audio in enumerate(audios):
        progressBar(index, total)
        # Get Dialogue_ID and Utterance_ID
        name = audio.split("/")[-1]
        name_split = name.split("_")
        dia = name_split[0].split("dia")[-1]
        utt = name_split[1].split("utt")[-1]

        found = False
        # Read audio label
        with open(labels, "r") as csv:
            for i, row in enumerate(csv):
                if i > 0:
                    splitted_row = row.split(",")
                    [emotion, _, row_dia, row_utt, season, episode] = splitted_row[-10: -4]
                    if [row_utt, row_dia] == [utt, dia]:
                        found = True
                        break
        
        name = "{}_{}_{}".format(audio.split("/")[-2], dia, utt)
        if found:
            # Write label in labels file
            with open(labels_path, "a+") as csv:
                csv.write("{},{}\n".format(name, emotion_conv[emotion]))

            # Move csv and npy files
            if copy:
                shutil.copy("{}{}".format(audio, features_fileExt[0]), "{}/{}{}".format(folder, name, features_fileExt[0]))
                shutil.copy("{}{}".format(audio, features_fileExt[1]), "{}/{}{}".format(folder, name, features_fileExt[1]))
            else:
                os.rename("{}{}".format(audio, features_fileExt[0]), "{}/{}{}".format(folder, name, features_fileExt[0]))
                os.rename("{}{}".format(audio, features_fileExt[1]), "{}/{}{}".format(folder, name, features_fileExt[1]))
    progressBar(total, total)

def extract_features():
    print("Extracting features")
    ravdess_subdirs = read_filenames(ravdess_name)
    subdirs = meld_subdirs + ravdess_subdirs

    for subdir in subdirs:
        print("Processing {}".format(subdir), end='\r')
        os.system('python3 audioAnalysis.py featureExtractionDir -i {} -mw {} -ms {} -sw {} -ss {}'.format(subdir, mw, ms, sw, ss))
        print("", end='\r')

def setUp():
    # Create database folder
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    if not os.path.exists(data_path):
        os.makedirs(data_path)

def process_ravdess():
    # Read file names of RAVDESS audios
    ravdess_dirs = read_filenames(ravdess_name)
    ravdess_files = read_subdir(ravdess_dirs)
    
    # Get audios names
    audios = list(set([file.split(".")[0] for file in ravdess_files]))
    # Copy files 
    move_ravdess(audios, data_path, labels_path, copy=copy_files)

def process_meld():
    for subdir, l_path in zip(meld_subdirs, meld_labels):
        print("\nMoving {}".format(subdir.split("/")[-1]))
        files = read_filenames(subdir)
        files = list(set([".".join(file.split(".")[0:2]) for file in files]))
        
        # Copy features files and write label
        move_meld(files, data_path, labels_path, l_path, copy=copy_files)

if __name__ == "__main__":
    extract_features()

    setUp()

    print("Moving features files of RAVDESS")
    process_ravdess()

    print("\n\nMoving features files of MELD")
    process_meld()