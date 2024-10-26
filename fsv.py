import os

def load_exclusions(file_path="exceptions.txt"):
    """Загружает папки, расширения и файлы для исключения из файла."""
    exclude_dirs = []
    exclude_extensions = []
    exclude_files = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                entry = line.strip()
                if entry:
                    # Если исключение начинается с '*.', то это расширение файла
                    if entry.startswith("*."):
                        exclude_extensions.append(entry[1:])  # Добавляем расширение без '*'
                    # Если имя начинается с точки и не содержит "*.", это скрытая папка
                    elif entry.startswith(".") and "." not in entry[1:]:
                        exclude_dirs.append(entry)  # Добавляем как имя папки
                    # Если указано конкретное имя файла
                    elif "." in entry:
                        exclude_files.append(entry)  # Добавляем как имя файла
                    else:
                        exclude_dirs.append(entry)  # Иначе добавляем как имя папки
    except FileNotFoundError:
        print(f"Файл {file_path} не найден. Исключений не загружено.")
    
    print("\n\nИсключения по умолчанию:")
    print("  - игнорируемые папки:\n    ", exclude_dirs)
    print("  - игнорируемые расширения:\n    ", exclude_extensions)
    print("  - игнорируемые файлы:\n    ", exclude_files)
    return exclude_dirs, exclude_extensions, exclude_files

def get_folder_structure(path, depth=0, exclude_dirs=None, exclude_extensions=None, exclude_files=None):
    if exclude_dirs is None:
        exclude_dirs = []
    if exclude_extensions is None:
        exclude_extensions = []
    if exclude_files is None:
        exclude_files = []
    structure = {}
    
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_dir():
                    # Пропускаем папки, если они в списке исключений
                    if entry.name in exclude_dirs:
                        continue
                    structure[entry.name] = get_folder_structure(entry.path, depth + 1, exclude_dirs, exclude_extensions, exclude_files)
                else:
                    # Пропускаем файлы, если их расширение или имя в списке исключений
                    if any(entry.name.endswith(ext) for ext in exclude_extensions) or entry.name in exclude_files:
                        continue
                    structure[entry.name] = None
    except PermissionError:
        structure['Permission Denied'] = None
    return structure

def format_structure(structure, indent=0):
    formatted = ""
    for key, value in structure.items():
        formatted += "    " * indent + "├── " + key + "\n"
        if isinstance(value, dict):
            formatted += format_structure(value, indent + 1)
    return formatted

# Пример использования
path = input("\nВведите путь к папке: ")

if path == "":
    path = "."

# Загружаем исключаемые папки, расширения и файлы из файла
exclude_dirs, exclude_extensions, exclude_files = load_exclusions()

# Ввод пользовательских исключений для папок
user_exclude_dirs = input("\nВведите папки для исключения через запятую: ").split(",")
exclude_dirs += [dir.strip() for dir in user_exclude_dirs if dir.strip()]

# Ввод пользовательских исключений для расширений файлов
user_exclude_extensions = input("Введите расширения файлов для исключения через запятую (например, *.py): ").split(",")
exclude_extensions += [ext.strip()[1:] for ext in user_exclude_extensions if ext.strip().startswith("*.")]

# Ввод пользовательских исключений для конкретных файлов
user_exclude_files = input("Введите имена файлов для исключения через запятую: ").split(",")
exclude_files += [file.strip() for file in user_exclude_files if file.strip()]

# Выводим итоговые исключения
print("\n\nИтоговые исключения:")
print("  - игнорируемые папки:\n    ", exclude_dirs)
print("  - игнорируемые расширения:\n    ", exclude_extensions)
print("  - игнорируемые файлы:\n    ", exclude_files)

folder_structure = get_folder_structure(path, exclude_dirs=exclude_dirs, exclude_extensions=exclude_extensions, exclude_files=exclude_files)
print("\nСтруктура папки:\n")
print(path)
print(format_structure(folder_structure))
