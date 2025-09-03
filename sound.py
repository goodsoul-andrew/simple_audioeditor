import itertools
import os
import struct
import uuid
import wave
import ffmpeg
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TDRC, TRCK, APIC, PictureType
from mutagen.mp3 import MP3

from converters import mp3_to_wav, wav_to_mp3


class Sound:
    def __init__(self, filename):
        self.filename = filename
        if filename[-4:] == ".wav":
            Sound._from_wave(self, filename)
        elif filename[-4:] == ".mp3":
            Sound._from_mp3(self, filename)
        else:
            raise ValueError("Неподдерживаемый формат аудио!")

    def _from_mp3(self, filename):
        tmp_name = str(uuid.uuid4()) + ".wav"
        mp3_to_wav(filename, tmp_name)
        Sound._from_wave(self, tmp_name)
        os.remove(tmp_name)
        self._get_mp3_tags()

    def _get_mp3_tags(self):
        metadata = {}
        audio = MP3(self.filename, ID3=ID3)
        if audio.tags is None:
            self.mp3_metadata = {}
        # print(audio.tags)
        if 'TIT2' in audio.tags: metadata['title'] = audio.tags['TIT2'].text[0] if audio.tags['TIT2'].text else None
        if 'TPE1' in audio.tags: metadata['artist'] = audio.tags['TPE1'].text[0] if audio.tags['TPE1'].text else None
        if 'TALB' in audio.tags: metadata['album'] = audio.tags['TALB'].text[0] if audio.tags['TALB'].text else None
        if 'TCON' in audio.tags: metadata['genre'] = audio.tags['TCON'].text[0] if audio.tags['TCON'].text else None
        if 'TRCK' in audio.tags: metadata['track_number'] = audio.tags['TRCK'].text[0] if audio.tags[
            'TRCK'].text else None
        if 'TDRC' in audio.tags: metadata['year'] = audio.tags['TDRC'].text[0] if audio.tags[
            'TDRC'].text else None
        if 'APIC:cover' in audio.tags:
            metadata['cover_mime'] = audio.tags['APIC:cover'].mime
            metadata['cover_data'] = audio.tags['APIC:cover'].data
        self.mp3_metadata = metadata

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
                    byte1, byte2, byte3 = struct.unpack('<BBB', frames[i:i + 3])
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
            raise ValueError("Конечный файл должен иметь расширение wav!")
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
        audio = MP3(filename)
        for tag_name, tag_value in self.mp3_metadata.items():
            if tag_value is None:
                continue
            if tag_name == 'title':
                audio.tags.add(TIT2(encoding=3, text=tag_value))
            elif tag_name == 'artist':
                audio.tags.add(TPE1(encoding=3, text=tag_value))
            elif tag_name == 'album':
                audio.tags.add(TALB(encoding=3, text=tag_value))
            elif tag_name == 'genre':
                audio.tags.add(TCON(encoding=3, text=tag_value))
            elif tag_name == 'track_number':
                audio.tags.add(TRCK(encoding=3, text=str(tag_value)))
            elif tag_name == 'year':
                audio.tags.add(TDRC(encoding=3, text=str(tag_value)))
            elif tag_name == 'cover_path' and tag_value and os.path.exists(tag_value):
                with open(tag_value, 'rb') as f:
                    cover_data = f.read()
                if tag_value.lower().endswith('.png'):
                    mime_type = 'image/png'
                elif tag_value.lower().endswith('.gif'):
                    mime_type = 'image/gif'
                audio.tags.add(APIC(
                    encoding=3,  # UTF-8
                    mime=mime_type,
                    type=3,  # Front Cover
                    desc='Front Cover',
                    data=cover_data
                ))
            elif tag_name == 'cover_data':
                audio.tags.add(APIC(
                    encoding=3,  # UTF-8
                    mime=self.mp3_metadata['cover_mime'],
                    type=3,  # Front Cover
                    desc='Front Cover',
                    data=self.mp3_metadata['cover_data']
                ))
        audio.save()
