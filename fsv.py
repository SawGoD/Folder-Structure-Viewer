import os
import signal
import sys
from typing import Dict, List, Optional, Tuple, Union


def signal_handler(sig, frame):
    """Обработчик сигнала для корректного завершения программы"""
    print("\n\nПрограмма завершена пользователем")
    sys.exit(0)


def load_exclusions(file_path: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  "exceptions.txt")) -> Tuple[List[str], List[str], List[str]]:
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
        print(f"Файл {file_path} не найден. Исключений не загружено.")

    print("\n\nИсключения по умолчанию:")
    print("  - игнорируемые папки:\n    ", exclude_dirs)
    print("  - игнорируемые расширения:\n    ", exclude_extensions)
    print("  - игнорируемые файлы:\n    ", exclude_files)

    return exclude_dirs, exclude_extensions, exclude_files


def get_folder_structure(path: str,
                         depth: int = 0,
                         exclude_dirs: Optional[List[str]] = None,
                         exclude_extensions: Optional[List[str]] = None,
                         exclude_files: Optional[List[str]] = None) -> Dict[str, Union[None, Dict]]:
    """Получает структуру папок и файлов с учетом исключений"""

    structure: Dict[str, Union[None, Dict]] = {}
    exclude_dirs = exclude_dirs or []
    exclude_extensions = exclude_extensions or []
    exclude_files = exclude_files or []

    try:
        with os.scandir(path) as entries:
            for entry in entries:
                name = entry.name

                if entry.is_dir():
                    if name in exclude_dirs:
                        continue

                    sub_structure = get_folder_structure(entry.path, depth + 1, exclude_dirs, exclude_extensions, exclude_files)
                    structure[name] = sub_structure if sub_structure else {"<Пустая папка>": None}

                elif not (any(name.endswith(ext) for ext in exclude_extensions) or name in exclude_files):
                    structure[name] = None

    except PermissionError:
        structure['Permission Denied'] = None

    return structure


def format_structure(structure: Dict[str, Union[None, Dict]], indent: int = 0) -> str:
    """Форматирует структуру папок и файлов в читаемый вид"""

    formatted = ""
    items = list(structure.items())
    folders = [(k, v) for k, v in items if isinstance(v, dict)]
    files = [(k, v) for k, v in items if not isinstance(v, dict)]

    for i, (key, value) in enumerate(folders):
        is_last = i == len(folders) - 1 and not files
        prefix = "└───" if is_last else "├───"
        formatted += "│   "*indent + f"{prefix}📁 {key}\n"
        formatted += format_structure(value, indent + 1)

    for i, (key, _) in enumerate(files):
        prefix = "└───" if i == len(files) - 1 else "├───"
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


def main():
    """Основная логика программы"""
    # Регистрируем обработчик сигнала CTRL+C
    signal.signal(signal.SIGINT, signal_handler)

    print("Для выхода из программы нажмите CTRL+C")

    while True:
        path = input("\nВведите путь к папке: ")
        if validate_path(path):
            break

    folder_name = path.split(os.sep)[-1] if path != "." else "."

    # Загружаем исключения
    exclude_dirs, exclude_extensions, exclude_files = load_exclusions()

    # Добавляем пользовательские исключения
    user_dirs, user_extensions, user_files = get_user_exclusions()
    exclude_dirs.extend(user_dirs)
    exclude_extensions.extend(user_extensions)
    exclude_files.extend(user_files)

    # Выводим итоговые исключения
    print("\n\nИтоговые исключения:")
    print("  - игнорируемые папки:\n    ", exclude_dirs)
    print("  - игнорируемые расширения:\n    ", exclude_extensions)
    print("  - игнорируемые файлы:\n    ", exclude_files)

    # Получаем и выводим структуру
    folder_structure = get_folder_structure(path, exclude_dirs=exclude_dirs, exclude_extensions=exclude_extensions, exclude_files=exclude_files)

    if not folder_structure:
        print(f"\nПапка 🗃️ '{folder_name}' пуста или всё содержимое исключено!")
    else:
        print("\nСтруктура папки:\n")
        print(f"🗃️ {folder_name}")
        print(format_structure(folder_structure))


if __name__ == "__main__":
    main()
