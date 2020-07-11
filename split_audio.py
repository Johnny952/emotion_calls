from pydub import AudioSegment
import os
import shutil

from model import classify

class Audio:
    def __init__(self, audio_path, window_len, windows_dir='temp', overlap=0, skip_head=False, skip_time=0):
        assert(overlap < window_len)
        self.audio_path = audio_path
        self.windows_dir = windows_dir
        self.window_len = window_len
        self.overlap = overlap
        self.skip_head = skip_head
        self.skip_time = skip_time
        self.windows_path = []

    def split(self):
        self.windows_path = []
        if not os.path.exists(self.windows_dir):
            os.makedirs(self.windows_dir)

        audio = AudioSegment.from_wav(self.audio_path) 

        count = 0
        t = 0
        if self.skip_head:
            t += self.skip_time

        while t + self.window_len - self.overlap < len(audio):
            window = audio[t: t + self.window_len]
            window_name = "{}/{}.wav".format(self.windows_dir, count)
            window.export(window_name, format='wav')
            self.windows_path.append(window_name)
            count += 1
            t += self.window_len - self.overlap

    def delete_temp(self):
        try:
            shutil.rmtree(self.windows_dir)
        except OSError as e:
            print("Error: %s : %s" % (self.windows_dir, e.strerror))

    def classify_windows(self):
        detections = []
        for audio in self.windows_path:
            detections.append(classify(audio))
        return detections

    def split_classif(self):
        self.split()
        detections = self.classify_windows()
        self.delete_temp()
        return detections