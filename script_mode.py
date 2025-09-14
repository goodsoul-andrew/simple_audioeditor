from colored_text import green, red
from commands import do_command
from sound import Sound
from sound_effects import SoundEffects

def script_mode(scriptname: str, files: list[str]):
    try:
        with open(scriptname) as script:
            lines = [el.strip() for el in script.readlines()]
            print(lines)
        sounds: list[Sound] = []
        for filename in files:
            try:
                sounds.append(Sound(filename))
            except ValueError as err:
                print(red(err))
                return
            except FileNotFoundError as err:
                print(red(f"Файл {filename} не найден."))
        effects = [SoundEffects(snd) for snd in sounds]
    except FileNotFoundError as err:
        print(red(f"Файл {scriptname} не найден."))
        return
    for line in lines:
        for i in range(len(effects)):
            do_command(line, effects[i])