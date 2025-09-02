import itertools
import os
import struct
import uuid
import wave

from converters import mp3_to_wav, wav_to_mp3


class Sound:
    def __init__(self, filename):
        if filename[-4:] == ".wav":
            Sound._from_wave(self, filename)
        elif filename[-4:] == ".mp3":
            Sound._from_mp3(self, filename)

    def _from_mp3(self, filename):
        tmp_name = str(uuid.uuid4()) + ".wav"
        mp3_to_wav(filename, tmp_name)
        Sound._from_wave(self, tmp_name)
        os.remove(tmp_name)

    def _from_wave(self, filename: str):
        with wave.open(filename, "rb") as file:
            self.nchannels = file.getnchannels()
            self.nframes = file.getnframes()
            self.sampwidth = file.getsampwidth()
            self.framerate = file.getframerate()
            frames = file.readframes(self.nframes)
            if self.sampwidth == 1:
                self._min_val = 0
                self._max_val = 255
            else:
                self._min_val = -(2 ** (8 * self.sampwidth - 1))
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
            if self.sampwidth == 1:
                for i in range(len(frames)):
                    frames[i] = frames[i] / self._max_val * 2 - 1
            else:
                for i in range(len(frames)):
                    frames[i] = frames[i] / -self._min_val
            if self.nchannels == 2:
                self.frames = [[], []]
                for i in range(len(frames)):
                    self.frames[i % 2].append(frames[i])
            else:
                self.frames = [frames[:]]
            del frames

    def save_to_wave(self, filename):
        if filename[-4:] != ".wav":
            raise ValueError("Not wav destination file")
        if self.nchannels == 2:
            frames = list(itertools.chain(*zip(self.frames[0], self.frames[1])))
        else:
            frames = self.frames[0][:]
        if self.sampwidth == 1:
            for i in range(len(frames)):
                frames[i] = (frames[i] + 1) * self._max_val
        else:
            for i in range(len(frames)):
                frames[i] = frames[i] * -self._min_val
        with wave.open(filename, "wb") as file:
            file.setnchannels(self.nchannels)
            file.setnframes(self.nframes)
            file.setframerate(self.framerate)
            file.setsampwidth(self.sampwidth)
            if self.sampwidth == 3:
                data = []
                for num in frames:
                    packed_num = struct.pack("i", int(num))
                    data.append(packed_num[:3])
            else:
                data = []
                for num in frames:
                    packed_num = struct.pack(self._fmt_char, int(num))
                    data.append(packed_num)
            file.writeframes(b''.join(data))
            del data

    def save_to_mp3(self, filename):
        tmp_name = str(uuid.uuid4()) + ".wav"
        self.save_to_wave(tmp_name)
        wav_to_mp3(tmp_name, filename)
        os.remove(tmp_name)