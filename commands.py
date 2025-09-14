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

def do_command(line: str, effects: SoundEffects):
    log_print = print_with_name(effects.sound.filename)
    try:
        command, args = parse_command(line)
        match command:
            case "cut":
                start, end = (float(sec) for sec in args[:2])
                effects = effects.cut_fragment(start, end)
                log_print(green(f"Вырезан фрагмент с {start} по {end}"))
            case "trim":
                start, end = (float(sec) for sec in args[:2])
                effects = effects.trim(start, end)
                log_print(green(f"Обрезано с {start} по {end}"))
            case "change_volume":
                factor = float(args[0])
                effects = effects.change_volume(factor)
                if factor > 1:
                    log_print(green(f"Громкость увеличена в {round(factor, 3)} раз"))
                if factor < 1:
                    log_print(green(f"Громкость уменьшена в {round(1 / factor, 3)} раз"))
            case "change_speed":
                factor = float(args[0])
                effects = effects.change_speed(factor)
                if factor > 1:
                    log_print(green(f"Ускорено в {round(factor, 3)} раз"))
                if factor < 1:
                    log_print(green(f"Замедлено в {round(1 / factor, 3)} раз"))
            case "concat":
                other_filename = args[0]
                other = Sound(other_filename)
                effects = effects.concat(other)
                log_print(green(f"Соединено с '{other_filename}' в конце"))
                del other
            case "select_fragment":
                start_sec = float(args[0])
                end_sec = float(args[1])
                effects = effects.select_fragment(start_sec, end_sec)
                log_print(green(f"Выделен фрагмент {start_sec}-{end_sec} сек"))
            case "undo_last":
                effects.undo_last()
                log_print(green(f"Отменено: {effects.last['operation']}"))
            case "replay_operation":
                count = int(args[0])
                effects.replay_operation(count)
                log_print(green(f"Выполнено заново первые {count} операций"))
            case "save":
                new_name = args[0]
                if not new_name:
                    new_name = effects.sound.filename
                new_name = new_name.replace("{filename}", effects.sound.filename_stripped)
                effects = effects.save(new_name)
                log_print(green(f"Сохранено в '{new_name}'"))
            case "history":
                effects.show_effects_history()
            case "commands":
                print(
                    "- change_volume [factor] - изменяет громкость в factor раз; factor > 1 делает громче, если factor < 1 делает тише")
                print(
                    "- change_speed [factor] - изменяет скорость в factor раз; factor > 1 делает быстрее, если factor < 1 делает медленнее")
                print("- trim [start_sec] [end_sec] - обрезает всё до start_sec и после end_sec")
                print("- cut [start_sec] [end_sec] - вырезает фрагмент с start_sec до end_sec")
                print("- select_fragment [start_sec] [end_sec] - выделяет фрагмент с start_sec до end_sec")
                print("- concat [path_to_audio] - соединяет обрабатываемое аудио с введённым")
                print("- undo_last - удаляет последнюю выполненную операцию")
                print("- replay_operation [count] - выполняет первые count операций из истории")
                print("- save [new_name] - сохраняет результат в new_name, если new_name содержит строку '{filename}', то {filename} заменится на оригинальное имя")
                print("- history - показывает историю операций")
                print("- commands - показывает справку по командам операций")
            case _:
                log_print(red("Неизвестная операция"))
    except Exception as exc:
        log_print(red(exc))