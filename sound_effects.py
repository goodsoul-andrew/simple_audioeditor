import numpy as np

import sound
from sound import Sound


class SoundEffects:
    def __init__(self, sound: Sound):
        self.sound = sound

    def change_volume(self, factor: float):
        amplified_frames = self.sound.frames * factor
        clipped_frames = np.clip(amplified_frames, -1.0, 1.0)
        self.sound.frames = clipped_frames
        print("готово")
        return self

    def change_speed(self, factor: float):
        if factor <= 0:
            raise ValueError("Factor must be > 0")
        old_len = len(self.sound.frames[0])
        new_len = int(old_len / factor)
        new_frames = []
        for ch in range(self.sound.nchannels):
            frame = [
                self.sound.frames[ch][min(int(i * factor), old_len - 1)]
                for i in range(new_len)
            ]
            new_frames.append(frame)
        self.sound.frames = new_frames
        self.sound.nframes = new_len
        return self

    def cut(self, start_sec: float, end_sec: float):
        start_idx = int(start_sec * self.sound.framerate)
        end_idx = int(end_sec * self.sound.framerate)
        self.sound.frames = self.sound.frames[:, start_idx:end_idx]
        self.sound.nframes = self.sound.frames.shape[1]
        return self

    def concat(self, other: "Sound"):
        if self.sound.nchannels != other.nchannels or self.sound.framerate != other.framerate:
            raise ValueError("Разные расширения! Чтобы склеить, необходимо иметь одинаковый формат")
        for ch in range(self.sound.nchannels):
            self.sound.frames[ch].extend(other.frames[ch])
        self.sound.nframes = len(self.sound.frames[0])
        return self
