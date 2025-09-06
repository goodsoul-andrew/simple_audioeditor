import argparse
from sound import Sound
from sound_effects import SoundEffects
from colored_text import red, green, light_green

parser = argparse.ArgumentParser(description="Консольный редактор аудио. Введите ")
parser.add_argument("filename", type=str, help="Путь до обрабатываемого файла", )
args = parser.parse_args()
print("Вводите команды. Команда 'help' выведет список доступных операций")
snd = Sound(args.filename)
effects = SoundEffects(snd)
while True:
    command_input = input().split()
    command = command_input[0]
    args = command_input[1:]
    # print(command, args)
    try:
        match command:
            case "cut":
                start, end = (float(sec) for sec in args[:2])
                effects = effects.cut_fragment(start, end)
                print(green(f"Вырезан фрагмент с {start} по {end}"))
            case "trim":
                start, end = (float(sec) for sec in args[:2])
                effects = effects.trim(start, end)
                print(green(f"Обрезано с {start} по {end}"))
            case "change_volume":
                factor = float(args[0])
                effects = effects.change_volume(factor)
                if factor > 1:
                    print(green(f"Громкость увеличена в {round(factor, 3)} раз"))
                if factor < 1:
                    print(green(f"Громкость уменьшена в {round(1 / factor, 3)} раз"))
            case "change_speed":
                factor = float(args[0])
                effects = effects.change_speed(factor)
                if factor > 1:
                    print(green(f"Ускорено в {round(factor, 3)} раз"))
                if factor < 1:
                    print(green(f"Замедлено в {round(1 / factor, 3)} раз"))
            case "concat":
                other_filename = args[0]
                other = Sound(other_filename)
                effects = effects.concat(other)
                print(green(f"Соединено с '{other_filename} в конце'"))
                del other
            case "select_fragment":
                start_sec = float(args[0])
                end_sec = float(args[1])
                effects = effects.select_fragment(start_sec, end_sec)
                print(green(f"Выделен фрагмент {start_sec}-{end_sec} сек"))
            case "undo_last":
                effects.undo_last()
                print(green(f"Отменено: {effects.last['operation']}"))
            case "replay_operation":
                count = int(args[0])
                effects.replay_operation(count)
                print(green(f"Выполнено заново первые {count} операций"))
            case "save":
                new_name = args[0]
                snd.save(new_name)
                print(green(f"Сохранено в '{new_name}'"))
            case "history":
                effects.show_effects_history()
            case "help":
                print(
                    "change_volume [factor] - изменяет громкость в factor раз; factor > 1 делает громче, если factor < 1 делает тише")
                print(
                    "change_speed [factor] - изменяет скорость в factor раз; factor > 1 делает быстрее, если factor < 1 делает медленнее")
                print("trim [start_sec] [end_sec] - обрезает всё до start_sec и после end_sec")
                print("cut [start_sec] [end_sec] - вырезает фрагмент с start_sec до end_sec")
                print("select_fragment [start_sec] [end_sec] - выделяет фрагмент с start_sec до end_sec")
                print("concat [path_to_audio] - соединяет обрабатываемое аудио с введённым")
                print("undo_last - удаляет последнюю выполненную операцию")
                print("replay_operation [count] - выполняет первые count операций из истории")
            case _:
                print(red("Неизвестная операция"))
    except Exception as exc:
        print(red(exc))
