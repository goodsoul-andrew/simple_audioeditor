import numpy as np
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
        old_len = self.sound.nframes
        new_len = int(self.sound.frames.shape[1] / factor)
        if new_len <= 0:
            raise ValueError("Слишком большое ускорение!")
        indices = np.floor(np.arange(new_len) * factor).astype(int)
        indices = np.clip(indices, 0, old_len - 1)
        self.sound.nframes = new_len
        self.sound.frames = self.sound.frames[:, indices]
        return self

    def cut(self, start_sec: float, end_sec: float):
        start_idx = int(start_sec * self.sound.framerate)
        end_idx = int(end_sec * self.sound.framerate)
        self.sound.frames = self.sound.frames[:, start_idx:end_idx]
        self.sound.nframes = self.sound.frames.shape[1]
        return self

    def concat(self, other: Sound):
        if self.sound.nchannels != other.nchannels or self.sound.framerate != other.framerate:
            raise ValueError("Разные расширения! Чтобы склеить, необходимо иметь одинаковый формат")
        self.sound.frames = np.concatenate((self.sound.frames, other.frames), axis=1)
        self.sound.nframes = self.sound.frames.shape[1]
        return self
