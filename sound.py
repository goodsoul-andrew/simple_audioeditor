import itertools
import os
import struct
import uuid
import wave

import ffmpeg
import pydub
import numpy as np
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TDRC, TRCK, APIC
from mutagen.mp3 import MP3

from converters import mp3_to_wav, wav_to_mp3


class Sound:
    def __init__(self, filename):
        self.filename = filename
        if filename[-4:] == ".wav":
            Sound._from_wav(self, filename)
        elif filename[-4:] == ".mp3":
            Sound._from_mp3(self, filename)
        else:
            raise ValueError("Неподдерживаемый формат аудио!")

    '''def _from_mp3(self, filename):
        tmp_name = str(uuid.uuid4()) + ".wav"
        mp3_to_wav(filename, tmp_name)
        Sound._from_wave(self, tmp_name)
        os.remove(tmp_name)
        self._get_mp3_tags()'''

    def _from_mp3(self, filename):
        probe = ffmpeg.probe(filename)
        audio_stream_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
        self.framerate = int(audio_stream_info['sample_rate'])
        self.nchannels = int(audio_stream_info['channels'])
        stream = ffmpeg.input(filename, loglevel="quiet")
        output_args = {'f': 's16le', 'acodec': 'pcm_s16le'}
        process = ffmpeg.output(stream, '-', **output_args)
        output_raw_bytes = process.run(capture_stdout=True, capture_stderr=True)[0]
        self._fmt_char = "h"
        self.sampwidth = 2
        self._min_val = -(2 ** (8 * self.sampwidth - 1))
        self._max_val = -self._min_val - 1
        bytes_per_sample = 2 * self.nchannels
        num_samples = len(output_raw_bytes) // bytes_per_sample
        format_string = '<' + 'h' * self.nchannels * num_samples
        unpacked_samples = struct.unpack(format_string, output_raw_bytes)
        audio_data_list = [[] for _ in range(self.nchannels)]
        for i in range(num_samples):
            for ch in range(self.nchannels):
                sample = unpacked_samples[i * self.nchannels + ch]
                audio_data_list[ch].append(sample)
        self.frames = self._normalize_frames(np.array(audio_data_list))
        self.nframes = len(self.frames[0])
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

    def _from_wav(self, filename: str):
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
            # fmt = {1: np.uint8, 2: np.int16, 3: np.int32, 4: np.int32}
            dtypes = [np.uint8, np.int16, np.int32, np.int32]
            self._dtype = dtypes[self.sampwidth - 1]
            arrays = np.frombuffer(frames, dtype=dtypes[self.sampwidth - 1])
            if self.sampwidth == 3:
                arrays = self._convert_24bit(arrays)
            arrays = self._normalize_frames(arrays)
            self.frames = self._split_channels(arrays)

    def _convert_24bit(self, arrays):
        expanded = np.zeros(arrays.shape[0] // 3, dtype=np.int32)
        for i in range(0, len(arrays), 3):
            sample = (arrays[i + 2] << 16) | (arrays[i + 1] << 8) | arrays[i]
            if sample & (1 << 23):
                sample -= (1 << 24)
            expanded[i // 3] = sample
        return expanded

    def _normalize_frames(self, frames):
        norm_factor = -self._min_val if self.sampwidth != 1 else self._max_val
        frames = frames / norm_factor
        return np.clip(frames, -1.0, 1.0)

    def _split_channels(self, frames):
        if self.nchannels == 2:
            return np.array([frames[i::2] for i in range(2)])
        else:
            return np.array([frames])

    def save_to_wav(self, filename):
        if filename[-4:] != ".wav":
            raise ValueError("Конечный файл должен иметь расширение wav!")
        if self.nchannels == 2:
            frames = self.frames.T.ravel()
        else:
            frames = self.frames.ravel()
        if self.sampwidth == 1:
            frames = np.clip((frames + 1) * self._max_val, self._min_val, self._max_val).astype(np.uint8)
        else:
            frames = np.clip(frames * -self._min_val, self._min_val, self._max_val).astype(self._dtype)
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
