from colored_text import green, red
from commands import do_command
from sound import Sound
from sound_effects import SoundEffects


def interactive_mode(filename: str):
    print("Вводите команды. Команда 'commands' выведет список доступных операций")
    snd = Sound(filename)
    effects = SoundEffects(snd)
    while True:
        do_command(input(), effects)