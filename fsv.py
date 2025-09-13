import argparse
import os
import signal
import sys
from typing import Dict, List, Optional, Tuple, Union


def signal_handler(sig, frame):
    """Обработчик сигнала для корректного завершения программы"""
    print("\n\nПрограмма завершена пользователем")
    sys.exit(0)


def load_exclusions(file_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  "exceptions.txt"), quiet: bool = False) -> Tuple[List[str], List[str], List[str]]:
    """Загружает папки, расширения и файлы для исключения из файла."""
    exclude_dirs, exclude_extensions, exclude_files = [], [], []

    try:
        with open(file_path, 'r') as file:
            for line in file:
                entry = line.strip()
                if not entry:
                    continue

                if entry.startswith("*."):
                    exclude_extensions.append(entry[1:])
                elif entry.startswith(".") and "." not in entry[1:]:
                    exclude_dirs.append(entry)
                elif "." in entry:
                    exclude_files.append(entry)
                else:
                    exclude_dirs.append(entry)

    except FileNotFoundError:
        if not quiet:
            print(f"Файл {file_path} не найден. Исключений не загружено.")

    if not quiet:
        print("\n\nИсключения по умолчанию:")
        print("  - игнорируемые папки:\n    ", exclude_dirs)
        print("  - игнорируемые расширения:\n    ", exclude_extensions)
        print("  - игнорируемые файлы:\n    ", exclude_files)

    return exclude_dirs, exclude_extensions, exclude_files


def get_folder_structure(path: str,
                         depth: int = 0,
                         exclude_dirs: Optional[List[str]] = None,
                         exclude_extensions: Optional[List[str]] = None,
                         exclude_files: Optional[List[str]] = None) -> Tuple[Dict[str, Union[None, Dict]], int, int, int, int, int, int]:
    """Получает структуру папок и файлов с учетом исключений и возвращает статистику"""

    structure: Dict[str, Union[None, Dict]] = {}
    exclude_dirs = exclude_dirs or []
    exclude_extensions = exclude_extensions or []
    exclude_files = exclude_files or []

    total_dirs = 0
    total_files = 0
    hidden_dirs = 0
    hidden_files = 0
    empty_dirs = 0
    total_size = 0  # Размер в байтах

    try:
        with os.scandir(path) as entries:
            entries_list = list(entries)
            if not entries_list:
                empty_dirs += 1

            for entry in entries_list:
                name = entry.name

                if entry.is_dir():
                    total_dirs += 1
                    if name in exclude_dirs:
                        hidden_dirs += 1
                        continue

                    sub_structure, sub_dirs, sub_files, sub_hidden_dirs, sub_hidden_files, sub_empty_dirs, sub_size = get_folder_structure(
                        entry.path, depth + 1, exclude_dirs, exclude_extensions, exclude_files)
                    structure[name] = sub_structure
                    total_dirs += sub_dirs
                    total_files += sub_files
                    hidden_dirs += sub_hidden_dirs
                    hidden_files += sub_hidden_files
                    empty_dirs += sub_empty_dirs
                    total_size += sub_size
                else:
                    total_files += 1
                    try:
                        file_size = entry.stat().st_size
                        total_size += file_size
                    except (PermissionError, FileNotFoundError):
                        pass

                    if any(name.endswith(ext) for ext in exclude_extensions) or name in exclude_files:
                        hidden_files += 1
                    else:
                        structure[name] = None

    except PermissionError:
        structure['Permission Denied'] = None

    return structure, total_dirs, total_files, hidden_dirs, hidden_files, empty_dirs, total_size


def format_structure(structure: Dict[str, Union[None, Dict]], indent: int = 0, path: str = "") -> str:
    """Форматирует структуру папок и файлов в читаемый вид"""

    formatted = ""
    items = list(structure.items())
    folders = [(k, v) for k, v in items if isinstance(v, dict)]
    files = [(k, v) for k, v in items if not isinstance(v, dict)]

    for i, (key, value) in enumerate(folders):
        is_last = i == len(folders) - 1 and not files
        prefix = "└───" if is_last else "├───"

        current_path = os.path.join(path, key)

        if not value:
            # Проверяем содержимое папки напрямую
            try:
                has_content = False
                with os.scandir(current_path) as entries:
                    for _ in entries:
                        has_content = True
                        break

                if has_content:
                    formatted += "│   "*indent + f"{prefix}📁 {key} (🔒)\n"
                else:
                    formatted += "│   "*indent + f"{prefix}📁 {key} (🌫️)\n"
            except (PermissionError, FileNotFoundError):
                formatted += "│   "*indent + f"{prefix}📁 {key} (🌫️)\n"
        else:
            formatted += "│   "*indent + f"{prefix}📁 {key}\n"
            next_indent_prefix = "    " if is_last else "│   "
            sub_formatted = format_structure(value, indent + 1, current_path)

            # Заменяем префикс для последнего элемента, сохраняя вертикальные линии для других уровней
            if is_last:
                lines = sub_formatted.split('\n')
                for j, line in enumerate(lines):
                    if line:
                        if j == len(lines) - 1 and not line.strip():
                            continue
                        formatted += "│   "*indent + next_indent_prefix + line[indent*4 + 4:] + "\n"
            else:
                formatted += sub_formatted

    for i, (key, _) in enumerate(files):
        is_last = i == len(files) - 1
        prefix = "└───" if is_last else "├───"
        formatted += "│   "*indent + f"{prefix}📄 {key}\n"

    return formatted


def validate_path(path: str) -> bool:
    """Проверяет корректность введенного пути"""
    if not path:
        print("Путь не может быть пустым. Пожалуйста, повторите.")
        return False

    try:
        if not os.path.exists(path):
            print("Указанный путь не существует. Пожалуйста, проверьте правильность пути.")
            return False

        if not os.path.isdir(path):
            print("Указанный путь не является директорией. Пожалуйста, укажите путь к папке.")
            return False

        if any(char in path for char in ['<', '>', '|', '*', '?', '"']):
            print("Путь содержит недопустимые символы (<, >, |, *, ?, \"). Пожалуйста, исправьте путь.")
            return False

        return True

    except Exception as e:
        print(f"Ошибка при проверке пути: {str(e)}")
        return False


def get_user_exclusions() -> Tuple[List[str], List[str], List[str]]:
    """Получает пользовательские исключения"""
    user_dirs = input("\nВведите папки для исключения через запятую: ").split(",")
    exclude_dirs = [dir.strip() for dir in user_dirs if dir.strip()]

    user_extensions = input("Введите расширения файлов для исключения через запятую (например, *.py): ").split(",")
    exclude_extensions = [ext.strip()[1:] for ext in user_extensions if ext.strip().startswith("*.")]

    user_files = input("Введите имена файлов для исключения через запятую: ").split(",")
    exclude_files = [file.strip() for file in user_files if file.strip()]

    return exclude_dirs, exclude_extensions, exclude_files


def format_size(size_bytes: int) -> str:
    """Форматирует размер в байтах в читаемый вид"""
    if size_bytes < 1024:
        return f"{size_bytes} Б"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} КБ"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} МБ"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} ГБ"


def parse_arguments():
    """Парсит аргументы командной строки"""
    description = '''Folder Structure Viewer - визуализация структуры папок

Примеры использования:
  fsv.py                                          # Интерактивный режим
  fsv.py /path/to/folder                          # Анализ конкретной папки
  fsv.py . -c                                     # Анализ текущей папки только с конфигурацией
  fsv.py -c                                       # Анализ текущей папки только с конфигурацией
  fsv.py /path -d node_modules .git               # Исключить папки
  fsv.py /path -e .pyc .log                       # Исключить расширения файлов
  fsv.py /path -f config.ini settings.json       # Исключить конкретные файлы
  fsv.py /path --no-config -d temp                # Без конфигурации, исключить папку temp
  fsv.py -i                                       # Принудительный интерактивный режим'''

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('path', nargs='?', default=None, help='Путь к папке для анализа')
    parser.add_argument('--exclude-dirs', '-d', nargs='*', default=[],
                        help='Папки для исключения (например: --exclude-dirs node_modules .git)')
    parser.add_argument('--exclude-extensions', '-e', nargs='*', default=[],
                        help='Расширения файлов для исключения (например: --exclude-extensions .pyc .log)')
    parser.add_argument('--exclude-files', '-f', nargs='*', default=[],
                        help='Файлы для исключения (например: --exclude-files config.ini settings.json)')
    parser.add_argument('--no-config', action='store_true',
                        help='Не загружать исключения из файла exceptions.txt')
    parser.add_argument('--config-only', '-c', action='store_true',
                        help='Загружать только исключения из файла, без пользовательского ввода')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Запустить в интерактивном режиме')

    return parser.parse_args()


def main():
    """Основная логика программы"""
    # Регистрируем обработчик сигнала CTRL+C
    signal.signal(signal.SIGINT, signal_handler)

    args = parse_arguments()

    # Интерактивный режим или отсутствие пути
    if args.interactive or (args.path is None and not args.config_only):
        print("Для выхода из программы нажмите CTRL+C")

        while True:
            path = input("\nВведите путь к папке: ")
            if validate_path(path):
                break

        # Загружаем исключения из файла
        if not args.no_config:
            exclude_dirs, exclude_extensions, exclude_files = load_exclusions()
        else:
            exclude_dirs, exclude_extensions, exclude_files = [], [], []

        # Добавляем пользовательские исключения интерактивно
        user_dirs, user_extensions, user_files = get_user_exclusions()
        exclude_dirs.extend(user_dirs)
        exclude_extensions.extend(user_extensions)
        exclude_files.extend(user_files)
    elif args.config_only:
        # Режим только с конфигурацией - загрузить конфиг и использовать текущую папку
        path = args.path or "."
        if not validate_path(path):
            sys.exit(1)

        # Загружаем исключения из файла в тихом режиме
        exclude_dirs, exclude_extensions, exclude_files = load_exclusions(quiet=True)

        # Добавляем исключения из аргументов командной строки
        exclude_dirs.extend(args.exclude_dirs)
        exclude_extensions.extend(args.exclude_extensions)
        exclude_files.extend(args.exclude_files)
    else:
        # Неинтерактивный режим
        path = args.path
        if not validate_path(path):
            sys.exit(1)

        # Загружаем исключения из файла, если не отключено
        if not args.no_config:
            exclude_dirs, exclude_extensions, exclude_files = load_exclusions()
        else:
            exclude_dirs, exclude_extensions, exclude_files = [], [], []
            print("Исключения из файла не загружены (--no-config)")

        # Добавляем исключения из аргументов командной строки
        exclude_dirs.extend(args.exclude_dirs)
        exclude_extensions.extend(args.exclude_extensions)
        exclude_files.extend(args.exclude_files)

    folder_name = path.split(os.sep)[-1] if path != "." else "."

    # Выводим итоговые исключения
    print("\n\nИтоговые исключения:")
    print("  - игнорируемые папки:\n    ", exclude_dirs)
    print("  - игнорируемые расширения:\n    ", exclude_extensions)
    print("  - игнорируемые файлы:\n    ", exclude_files)

    # Получаем и выводим структуру
    folder_structure, total_dirs, total_files, hidden_dirs, hidden_files, empty_dirs, total_size = get_folder_structure(
        path, exclude_dirs=exclude_dirs, exclude_extensions=exclude_extensions, exclude_files=exclude_files)

    if not folder_structure:
        print(f"\nПапка 🗃️ '{folder_name}' пуста или всё содержимое исключено!")
    else:
        print("\nСтруктура папки:\n")
        print(f"🗃️ {folder_name}")
        print(format_structure(folder_structure, path=path))

        # Выводим статистику
        print("\nСтатистика:")
        print(f"📊 Всего папок: {total_dirs} (скрыто: {hidden_dirs}/{total_dirs}, пусто: {empty_dirs}/{total_dirs})")
        print(f"📊 Всего файлов: {total_files} (скрыто: {hidden_files}/{total_files})")
        print(f"📊 Всего элементов: {total_dirs + total_files} (скрыто: {hidden_dirs + hidden_files}/{total_dirs + total_files})")
        print(f"📊 Общий размер: {format_size(total_size)}")


if __name__ == "__main__":
    main()
