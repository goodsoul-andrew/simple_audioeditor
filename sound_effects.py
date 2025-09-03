import sound
from sound import Sound


class SoundEffects:
    def __init__(self, sound: "Sound"):
        self.sound = sound

    def change_volume(self, factor: float):
        for ch in range(self.sound.nchannels):
            self.sound.frames[ch] = [
                max(-1.0, min(1.0, s * factor)) for s in self.sound.frames[ch]
            ]
        return self

    def change_speed(self, factor: float):
        if factor <= 0:
            raise ValueError("Factor must be > 0")
        old_len = len(self.sound.frames[0])
        new_len = int(old_len / factor)
        for ch in range(self.sound.nchannels):
            self.sound.frames[ch] = [
                self.sound.frames[ch][min(int(i * factor), old_len - 1)]
                for i in range(new_len)
            ]
        self.sound.nframes = new_len
        return self

    def cut(self, start_sec: float, end_sec: float):
        start_idx = int(start_sec * self.sound.framerate)
        end_idx = int(end_sec * self.sound.framerate)
        for ch in range(self.sound.nchannels):
            self.sound.frames[ch] = self.sound.frames[ch][start_idx:end_idx]
        self.sound.nframes = len(self.sound.frames[0])
        return self

    def concat(self, other: "Sound"):
        if self.sound.nchannels != other.nchannels or self.sound.framerate != other.framerate:
            raise ValueError("Разные расширения! Чтобы склеить, необходимо иметь одинаковый формат")
        for ch in range(self.sound.nchannels):
            self.sound.frames[ch].extend(other.frames[ch])
        self.sound.nframes = len(self.sound.frames[0])
        return self
