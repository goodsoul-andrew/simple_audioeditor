import argparse

from interactive_mode import interactive_mode
from script_mode import script_mode
from sound import Sound
from sound_effects import SoundEffects
from colored_text import red, green, light_green

parser = argparse.ArgumentParser(description="Консольный аудио редактор.")
parser.add_argument("filename", type=str, help="Путь до обрабатываемого файла / файла скрипта в скриптовом режиме")
parser.add_argument("-s", "--script", action="store_true", help="Включает скриптовый режим")
parser.add_argument(
        'extra_files',
        metavar='EXTRA_FILE',
        type=str,
        nargs='*',
        default=[],
        help="Файлы для обработки (принимаются только в скриптовом режиме)."
    )
args = parser.parse_args()
if not args.script:
    interactive_mode(args.filename)
else:
    if args.extra_files:
        script_mode(args.filename, args.extra_files)
    else:
        print(red("Нет файлов для обработки"))