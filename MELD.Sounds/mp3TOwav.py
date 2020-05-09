from os import listdir
import os

def read_names(directory):
    return [directory+'/'+l for l in listdir(directory)]

def convert_mp3_wav(path):
    directory = "/".join(path.split("/")[:-1])
    new_name = path.split("/")[-1].split(".")[0]
    new_path = "{}/{}.wav".format(directory, new_name)
    os.rename(path, new_path)

def convert_dir(directory):
    files = read_names(directory)
    i = 1
    length = len(files)
    for file in files:
        print("Converting {}/{}: {}".format(i, length, file))
        convert_mp3_wav(file)
        i += 1

if __name__ == "__main__":
    convert_dir("test_sounds")
    convert_dir("dev_sounds")
    convert_dir("train_sounds")
