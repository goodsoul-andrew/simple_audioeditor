import numpy as np
from sound import Sound


class SoundEffects:
    def __init__(self, sound: Sound):
        self.sound = sound
        self.history = []
        self.original_frames = np.copy(self.sound.frames)
        self.original_nchannels = self.sound.nchannels
        self.original_framerate = self.sound.framerate
        self.fr_start = 0
        self.fr_end = self.sound.nframes
        self.fragment_reset = False
        self.last = {}
        self._rebuilding = False

    def __record(self, operation: str, **kwargs):
        if getattr(self, "_rebuilding", False): return
        self.history.append({"operation": operation, **kwargs})

    def __update_fragment(self):
        if self.fr_end > self.sound.frames.shape[1]:
            self.fragment_reset = True
            self.fr_end = self.sound.frames.shape[1]
        if self.fr_start >= self.fr_end:
            self.fragment_reset = True
            self.fr_start = 0

    def __rebuild_sound(self, history):
        self.return_to_original()
        self._rebuilding = True
        for op in history:
            if op["operation"] == "change_volume":
                self.change_volume(op["factor"])
            elif op["operation"] == "change_speed":
                self.change_speed(op["factor"])
            elif op["operation"] == "cut":
                self.cut_fragment(op["start_sec"], op["end_sec"])
            elif op["operation"] == "concat":
                self.concat(op["other"])
            elif op["operation"] == "trim":
                self.trim(op["start_sec"], op["end_sec"])
            elif op["operation"] == "select_fragment":
                self.select_fragment(op["start_sec"], op["end_sec"])
        self._rebuilding = False

    def change_volume(self, factor: float):
        amplified_frames = self.sound.frames[:, self.fr_start:self.fr_end] * factor
        clipped_frames = np.clip(amplified_frames, -1.0, 1.0)
        self.sound.frames[:, self.fr_start:self.fr_end] = clipped_frames
        self.__record("change_volume", factor=factor, fragment=(self.fr_start, self.fr_end))
        return self

    def change_speed(self, factor: float):
        # factor > 1 - ускорение
        # factor < 1 - замедление
        if factor <= 0:
            raise ValueError("Фактор должен быть > 0!")
        old_len = self.fr_end - self.fr_start
        new_len = int(old_len / factor)
        if new_len <= 0:
            raise ValueError("Слишком большое ускорение!")
        indices = np.floor(np.arange(new_len) * factor).astype(int)
        indices = np.clip(indices, 0, old_len - 1)
        # self.sound.frames[:, self.fr_start:self.fr_end] = self.sound.frames[:, indices]
        indices += self.fr_start
        self.sound.frames = np.hstack((self.sound.frames[:, 0:self.fr_start], self.sound.frames[:, indices],
                                       self.sound.frames[:, self.fr_end:self.sound.nframes]))
        self.__record("change_speed", factor=factor, fragment=(self.fr_start, self.fr_end))
        self.__update_fragment()
        return self

    def cut_fragment(self, start_sec: float, end_sec: float):
        start_idx = int(start_sec * self.sound.framerate)
        end_idx = int(end_sec * self.sound.framerate)
        indices_to_keep = np.concatenate((np.arange(start_idx), np.arange(end_idx, self.sound.frames.shape[1])))
        self.sound.frames = self.sound.frames[:, indices_to_keep]
        self.__update_fragment()
        self.__record("cut", start_sec=start_sec, end_sec=end_sec)
        return self

    def trim(self, start_sec: float, end_sec: float):
        start_idx = int(start_sec * self.sound.framerate)
        end_idx = int(end_sec * self.sound.framerate)
        self.sound.frames = self.sound.frames[:, start_idx:end_idx]
        self.fr_start = min(self.fr_start, self.sound.nframes)
        self.fr_end = min(self.fr_end, self.sound.nframes)
        self.__update_fragment()
        self.__record("trim", start_sec=start_sec, end_sec=end_sec)
        return self

    def concat(self, other: Sound):
        if self.sound.nchannels != other.nchannels or self.sound.framerate != other.framerate:
            raise ValueError("Разные расширения! Чтобы склеить, необходимо иметь одинаковый формат")
        self.sound.frames = np.concatenate((self.sound.frames, other.frames), axis=1)
        self.__record("concat", other=other)
        return self

    def select_fragment(self, start_sec: float, end_sec: float):
        self.fr_start = int(start_sec * self.sound.framerate)
        self.fr_end = int(end_sec * self.sound.framerate)
        if self.fr_end > self.sound.nframes or self.fr_start < 0 or self.fr_start >= self.fr_end:
            raise ValueError("Некорректные границы фрагмента!")
        self.__record("select_fragment", start_sec=start_sec, end_sec=end_sec)
        return self

    def undo_last(self):
        if not self.history: raise ValueError("История пуста!")
        self.last = self.history.pop()
        self.__rebuild_sound(self.history)
        return self

    def return_to_original(self):
        self.sound.frames = np.copy(self.original_frames)
        self.sound.framerate = self.original_framerate
        self.sound.nchannels = self.original_nchannels

    # выполнить первые count операций из истории
    def replay_operation(self, count=None):
        history = self.history[:count] if count else self.history
        self.__rebuild_sound(history)

    def show_effects_history(self):
        for i, op in enumerate(self.history, 1):
            print(f"{i}: {op}")
