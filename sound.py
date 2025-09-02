import struct
import wave


class Sound:
    def from_wave(self, filename: str):
        with wave.open(filename, "r") as file:
            self.nchannels = file.getnchannels()
            self.nframes = file.getnframes()
            self.sampwidth = file.getsampwidth()
            self.framerate = file.getframerate()
            frames = file.readframes(self.nframes)

            if self.sampwidth == 1:
                self._min_val = 0
                self._max_val = 255
            else:
                self._min_val = -(2 ** (self.sampwidth - 1))
                self._max_val = -self._min_val - 1
            fmt_chars = ["B", "h", "?", "i"]
            self._fmt_char = fmt_chars[self.sampwidth - 1]
            if self.sampwidth != 3:
                frames = list(struct.unpack("<" + self._fmt_char * (len(frames) // self.sampwidth), frames))
            else:
                unpacked_frames = []
                for i in range(0, len(frames) // self.sampwidth, 3):
                    byte1, byte2, byte3 = struct.unpack('<BBB', frames[i:i+3])
                    sample = (byte3 << 16) | (byte2 << 8) | byte1
                    if sample & (1 << 23):  # Если 24-й бит установлен (самый старший в 24 битах)
                        sample -= (1 << 24)  # Вычитаем 2^24 для получения отрицательного значения
                    unpacked_frames.append(sample)
                frames = unpacked_frames
                del unpacked_frames
            for i in range(len(frames)):
                if self.sampwidth == 1:
                    frames[i] = frames[i] / self._max_val * 2 - 1
                else:
                    frames[i] = frames[i] / -self._min_val

            if self.nchannels == 2:
                self.frames = [[], []]
                for i in range(len(frames)):
                    self.frames[i % 2].append(frames[i])
            else:
                self.frames = [frames[:]]
            del frames



