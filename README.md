# simple_audioeditor
Консольный аудио редактор.
Использование: python3 audioeditor.py [путь до файла]
Далее программа переходит в интерактивный режим.  
Вводите команды. Команда 'help' выведет список доступных операций  
- change_volume [factor] - изменяет громкость в factor раз; factor > 1 делает громче, если factor < 1 делает тише
- change_speed [factor] - изменяет скорость в factor раз; factor > 1 делает быстрее, если factor < 1 делает медленнее
- trim [start_sec] [end_sec] - обрезает всё до start_sec и после end_sec
- cut [start_sec] [end_sec] - вырезает фрагмент с start_sec до end_sec
- select_fragment [start_sec] [end_sec] - выделяет фрагмент с start_sec до end_sec
- concat [path_to_audio] - соединяет обрабатываемое аудио с введённым
- undo_last - удаляет последнюю выполненную операцию
- replay_operation [count] - выполняет первые count операций из истории
