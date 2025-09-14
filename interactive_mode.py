from colored_text import green, red
from commands import do_command
from sound import Sound
from sound_effects import SoundEffects


def interactive_mode(filename: str):
    print("Вводите команды. Команда 'commands' выведет список доступных операций")
    try:
        snd = Sound(filename)
        effects = SoundEffects(snd)
    except ValueError as err:
        print(red(err))
        return
    except FileNotFoundError as err:
        print(red(f"Файл {filename} не найден"))
        return

    empty_count = 0
    while True:
        command = input()
        if command == "":
            empty_count += 1
            if empty_count >= 2:
                print("Выход из интерактивного режима")
                break
            else:
                continue
        else:
            empty_count = 0
            do_command(command, effects)
