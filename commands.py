from colored_text import green, red, cyan
from sound import Sound
from sound_effects import SoundEffects


def print_with_name(name: str):
    def inner(text: str):
        print(f"{cyan(name)}: {text}")

    return inner


def parse_command(line: str):
    line = line.strip()
    if line[:4] == "save":
        start = 4
        for i in range(4, len(line)):
            if line[i] != " " and line[i] != "\t":
                start = i
                break
        return "save", [line[start:]]
    command_input = line.split()
    command = command_input[0]
    args = command_input[1:]
    return command, args


def cut(effects: SoundEffects, args: list[str]):
    log_print = print_with_name(effects.sound.filename)
    start, end = (float(sec) for sec in args[:2])
    effects.cut_fragment(start, end)
    log_print(green(f"Вырезан фрагмент с {start} по {end}"))


def trim(effects: SoundEffects, args: list[str]):
    log_print = print_with_name(effects.sound.filename)
    start, end = (float(sec) for sec in args[:2])
    effects.trim(start, end)
    log_print(green(f"Обрезано с {start} по {end}"))


def change_volume(effects: SoundEffects, args: list[str]):
    log_print = print_with_name(effects.sound.filename)
    factor = float(args[0])
    effects.change_volume(factor)
    if factor > 1:
        log_print(green(f"Громкость увеличена в {round(factor, 3)} раз"))
    if factor < 1:
        log_print(green(f"Громкость уменьшена в {round(1 / factor, 3)} раз"))


def change_speed(effects: SoundEffects, args: list[str]):
    log_print = print_with_name(effects.sound.filename)
    factor = float(args[0])
    effects.change_speed(factor)
    if factor > 1:
        log_print(green(f"Ускорено в {round(factor, 3)} раз"))
    if factor < 1:
        log_print(green(f"Замедлено в {round(1 / factor, 3)} раз"))


def change_pitch(effects: SoundEffects, args: list[str]):
    log_print = print_with_name(effects.sound.filename)
    factor = float(args[0])
    effects.change_pitch(factor)
    if factor > 0:
        log_print(green(f"Повышено в {round(factor, 3)} раз"))
    if factor < 0:
        log_print(green(f"Понижено в {round(1 / factor, 3)} раз"))


def concat(effects: SoundEffects, args: list[str]):
    log_print = print_with_name(effects.sound.filename)
    other_filename = args[0]
    other = Sound(other_filename)
    effects.concat(other)
    log_print(green(f"Соединено с '{other_filename}' в конце"))
    del other


def select_fragment(effects: SoundEffects, args: list[str]):
    log_print = print_with_name(effects.sound.filename)
    start_sec = float(args[0])
    end_sec = float(args[1])
    effects.select_fragment(start_sec, end_sec)
    log_print(green(f"Выделен фрагмент {start_sec}-{end_sec} сек"))


def undo_last(effects: SoundEffects, args: list[str]):
    log_print = print_with_name(effects.sound.filename)
    effects.undo_last()
    log_print(green(f"Отменено: {effects.last['operation']}"))


def replay_operation(effects: SoundEffects, args: list[str]):
    log_print = print_with_name(effects.sound.filename)
    count = int(args[0])
    effects.replay_operation(count)
    log_print(green(f"Выполнено заново первые {count} операций"))


def save(effects: SoundEffects, args: list[str]):
    log_print = print_with_name(effects.sound.filename)
    new_name = args[0]
    if not new_name:
        new_name = effects.sound.filename
    new_name = new_name.replace("{filename}", effects.sound.filename_stripped)
    effects.save(new_name)
    log_print(green(f"Сохранено в '{new_name}'"))


def history(effects: SoundEffects, args: list[str]):
    effects.show_effects_history()


def commands(effects: SoundEffects, args: list[str]):
    print(
        "- change_volume [factor] - изменяет громкость в factor раз; factor > 1 делает громче, если factor < 1 делает тише")
    print(
        "- change_speed [factor] - изменяет скорость в factor раз; factor > 1 делает быстрее, если factor < 1 делает медленнее")
    print(
        "- change_pitch [factor] - изменяет высоту звука в factor раз; factor > 0 - делает выше, factor < 0 - делает ниже")
    print("- trim [start_sec] [end_sec] - обрезает всё до start_sec и после end_sec")
    print("- cut [start_sec] [end_sec] - вырезает фрагмент с start_sec до end_sec")
    print("- select_fragment [start_sec] [end_sec] - выделяет фрагмент с start_sec до end_sec")
    print("- concat [path_to_audio] - соединяет обрабатываемое аудио с введённым")
    print("- undo_last - удаляет последнюю выполненную операцию")
    print("- replay_operation [count] - выполняет первые count операций из истории")
    print(
        "- save [new_name] - сохраняет результат в new_name, если new_name содержит строку '{filename}', то {filename} заменится на оригинальное имя")
    print("- history - показывает историю операций")
    print("- commands - показывает справку по командам операций")
    print("- для выхода нажмите 2 раза Enter")


COMMANDS = {
    "cut": cut,
    "trim": trim,
    "change_volume": change_volume,
    "change_speed": change_speed,
    "change_pitch": change_pitch,
    "concat": concat,
    "select_fragment": select_fragment,
    "undo_last": undo_last,
    "replay_operation": replay_operation,
    "save": save,
    "history": history,
    "commands": commands
}


def do_command(line: str, effects: SoundEffects):
    log_print = print_with_name(effects.sound.filename)
    try:
        command, args = parse_command(line)
        if command in COMMANDS:
            COMMANDS[command](effects, args)
        else:
            log_print(red("Неизвестная операция"))
    except Exception as exc:
        log_print(red(exc))
