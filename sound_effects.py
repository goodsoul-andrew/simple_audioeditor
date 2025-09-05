import numpy as np
from sound import Sound


class SoundEffects:
    def __init__(self, sound: Sound):
        self.sound = sound
        self.effects_history = []
        self.original_frames = np.copy(self.sound.frames)
        self.original_nchannels = self.sound.nchannels
        self.original_framerate = self.sound.framerate

    def __record(self, operation: str, **kwargs):
        self.effects_history.append({"operation": operation, **kwargs})

    def change_volume(self, factor: float):
        amplified_frames = self.sound.frames * factor
        clipped_frames = np.clip(amplified_frames, -1.0, 1.0)
        self.sound.frames = clipped_frames
        self.__record("change_volume", factor=factor)
        return self

    def change_speed(self, factor: float):
        # factor > 1 - ускорение
        # factor < 1 - замедление
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
        self.__record("change_speed", factor=factor)
        return self

    def cut_fragment(self, start_sec: float, end_sec: float):
        start_idx = int(start_sec * self.sound.framerate)
        end_idx = int(end_sec * self.sound.framerate)
        indices_to_keep = np.concatenate((np.arange(start_idx), np.arange(end_idx, self.sound.frames.shape[1])))
        self.sound.frames = self.sound.frames[:, indices_to_keep]
        # self.sound.frames = self.sound.frames[:, start_idx:end_idx]
        self.sound.nframes = self.sound.frames.shape[1]
        self.__record("cut", start_sec=start_sec, end_sec=end_sec)
        return self

    def trim(self, start_sec: float, end_sec: float):
        start_idx = int(start_sec * self.sound.framerate)
        end_idx = int(end_sec * self.sound.framerate)
        self.sound.frames = self.sound.frames[:, start_idx:end_idx]
        self.sound.nframes = self.sound.frames.shape[1]
        self.__record("trim", start_sec=start_sec, end_sec=end_sec)
        return self

    def concat(self, other: Sound):
        if self.sound.nchannels != other.nchannels or self.sound.framerate != other.framerate:
            raise ValueError("Разные расширения! Чтобы склеить, необходимо иметь одинаковый формат")
        self.sound.frames = np.concatenate((self.sound.frames, other.frames), axis=1)
        self.sound.nframes = self.sound.frames.shape[1]
        self.__record("concat", other=other)
        return self

    def take_fragment(self, start_sec: float, end_sec: float):
        start_idx = int(start_sec * self.sound.framerate)
        end_idx = int(end_sec * self.sound.framerate)
        new_frames = np.copy(self.sound.frames[:, start_idx:end_idx])
        fragment = Sound.__new__(Sound)
        fragment.frames = new_frames
        fragment.nframes = new_frames.shape[1]
        fragment.nchannels = self.sound.nchannels
        fragment.framerate = self.sound.framerate
        fragment.sampwidth = self.sound.sampwidth
        fragment.path = None
        self.__record("take_fragment", start_sec=start_sec, end_sec=end_sec)
        return SoundEffects(fragment)

    def return_to_original(self):
        self.sound.frames = np.copy(self.original_frames)
        self.sound.framerate = self.original_framerate
        self.sound.nchannels = self.original_nchannels

    # выполнить первые count операций из истории
    def replay_operation(self, count=None):
        self.return_to_original()
        for op in (self.effects_history[:count] if count else self.effects_history):
            if op["operation"] == "change_volume":
                self.change_volume(op["factor"])
            elif op["operation"] == "change_speed":
                self.change_speed(op["factor"])
            elif op["operation"] == "cut":
                self.cut_fragment(op["start_sec"], op["end_sec"])
            elif op["operation"] == "concat":
                self.concat(op["other"])

    def show_effects_history(self):
        for i, op in enumerate(self.effects_history, 1):
            print(f"{i}: {op}")
