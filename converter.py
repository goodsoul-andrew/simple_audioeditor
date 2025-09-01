import subprocess


def mp3_to_wav (filename: str, new_fname: str):
    if filename[-4:] != ".mp3":
        raise ValueError("Not mp3 file")
    if new_fname[-4:] != ".wav":
        raise ValueError("Not wav destination file")
    subprocess.call(['ffmpeg', '-i', filename, new_fname])


def wav_to_mp3 (filename: str, new_fname: str):
    if filename[-4:] != ".wav":
        raise ValueError("Not wav file")
    if new_fname[-4:] != ".mp3":
        raise ValueError("Not mp3 destination file")
    subprocess.call(['ffmpeg', '-i', filename, new_fname])


def int_list_to_bytearray(int_list: list[int], bytes_length: int = 0) -> bytearray:
    byte_array = bytearray()
    '''if bytes_length <= 0:
        bytes_length = (max(int_list).bit_length() + 7) // 8
    byte_array += bytes_length.to_bytes(1, 'little')'''
    for num in int_list:
        byte_array += num.to_bytes(bytes_length, 'little', signed=True)
    return byte_array
