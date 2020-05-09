from os import listdir
import os
from datetime import date

train_path = "train_splits"
dev_path = "dev_splits_complete"
test_path = "output_repeated_splits_test"

train_sound_path = "train_sounds"
dev_sound_path = "dev_sounds"
test_sound_path = "test_sounds"

error_folder = "error"

def read_names(directory):
  return [directory+'/'+l for l in listdir(directory)]


import moviepy.editor

def extract_audio(video_path, sound_folder):
  # Read video
  video = moviepy.editor.VideoFileClip(video_path)
  # Extract audio
  audio = video.audio
  # Extract video name
  video_name = video_path.split("/")[-1].split(".")[0]
  sound_name = "{}/{}.mp3".format(sound_folder,video_name)

  # If the directory does not exist, it creates it
  if not os.path.exists(sound_folder):
      os.makedirs(sound_folder)

  # Write audio in a file
  audio.write_audiofile(sound_name)


def extract_every_audio(video_folder, sound_folder, error_folder):
  videos = read_names(video_folder)
  index = 1
  files_error = []
  for video in videos:
    print("Video {} de {}".format(index, len(videos)))
    try:
      extract_audio(video, sound_folder)
    except Exception:
      files_error.append(video)
    index += 1
  # If the directory does not exist, it creates it
  if not os.path.exists(error_folder):
    os.makedirs(error_folder)
  name = "{}/{}.csv".format(error_folder, video_folder.split("/")[-1])
  with open(name, "a") as file:
    file.write(date.today().strftime("%B %d, %Y"))
    file.write("\n")
    for error in files_error:
      file.write(error + "\n")

if __name__=="__main__":
	extract_every_audio(train_path, train_sound_path, error_folder)
	extract_every_audio(dev_path, dev_sound_path, error_folder)
	extract_every_audio(test_path, test_sound_path, error_folder)
