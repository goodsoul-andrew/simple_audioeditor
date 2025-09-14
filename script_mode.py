from colored_text import green, red
from commands import do_command
from sound import Sound
from sound_effects import SoundEffects

def script_mode(scriptname: str, files: list[str]):
    with open(scriptname) as script:
        lines = [el.strip() for el in script.readlines()]
        print(lines)
    sounds: list[Sound] = []
    for filename in files:
        sounds.append(Sound(filename))
    effects = [SoundEffects(snd) for snd in sounds]
    for line in lines:
        for i in range(len(effects)):
            do_command(line, effects[i])