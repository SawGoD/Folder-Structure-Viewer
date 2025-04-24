# Folder Structure Viewer

![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Montserrat&weight=500&size=25&duration=2800&pause=800&color=DC143C&vCenter=true&width=500&height=30&lines=S+U+T+I+V+I+S+M+Project.;.)

[![Telegram](https://img.shields.io/badge/SawGoD-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/SawGoD)

---

## О проекте

Этот проект представляет собой утилиту на Python для просмотра структуры папок и файлов в указанной директории. Утилита поддерживает гибкую систему исключений для папок, файлов и расширений, позволяя настраивать отображение только нужного содержимого.

## Возможности

- Интеллектуальный обход директорий с настраиваемыми исключениями:
  - Скрытые системные папки (`.git`, `.idea`, `.vscode`)
  - Отдельные файлы (`main.py`, `config.json` и т.д.)
  - Файлы по расширению (`*.py`, `*.dll`, `*.cache`)
- Поддержка предустановленных исключений через `exceptions.txt`
- Наглядное древовидное отображение структуры
- Интуитивно понятный интерфейс командной строки

## Установка

1. Требуется Python 3.6+
2. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/SawGoD/Folder-Structure-Viewer.git
   cd Folder-Structure-Viewer
   ```

## Использование

1. Запуск:

   ```bash
   python fsv.py
   ```

2. Укажите целевую директорию

3. Настройте исключения:
   - Папки: введите имена через запятую (например: `node_modules, cache, temp`)
   - Расширения: введите через запятую с `*.` (например: `*.pyc, *.log`)
   - Файлы: введите имена через запятую (например: `config.json, .env`)

4. Получите наглядную структуру каталога

## Пример работы

```bash
$ python fsv.py
Введите путь к директории: C:\Users\User\Documents\My Games
Для выхода из программы нажмите CTRL+C

Итоговые исключения:
  - игнорируемые папки:
    ['node_modules', 'cache', 'temp']
  - игнорируемые расширения:
    ['*.pyc', '*.log']
  - игнорируемые файлы:
    ['config.json', '.env']

Структура папки:

🗃️ My Games
├───📁 ClusterTruck
│   ├───📁 Models (🌫️)
│   └───📁 Sounds (🌫️)
├───📁 DiRT Rally 2.0
│   ├───📁 hardwaresettings (🔒)
│   └───📁 wheelsettings (🌫️)
└───📁 SnowRunner
    └───📁 base
        ├───📁 logs
        │   ├───📄 BackendLog.txt
        │   ├───📄 LegacyLog.txt
        │   ├───📄 ModMapError.txt
        │   └───📄 trace_truck.txt
        ├───📁 Mods
        │   └───📁 .modio
        │       ├───📁 cache (🌫️)
        │       ├───📁 mods (🌫️)
        │       └───📁 tmp (🌫️)
        ├───📁 storage
        │   ├───📁 20465234255619134 (🌫️)
        │   ├───📄 shared_user_settings.dat
        │   └───📄 video.dat
        └───📄 sandbox.json


Статистика:
📊 Всего папок: 16 (скрыто: 0/16, пусто: 7/16)
📊 Всего файлов: 9 (скрыто: 2/9)
📊 Всего элементов: 25 (скрыто: 2/25)
📊 Общий размер: 7.30 КБ
```

      🔒 - содержимое в исключениях

      🌫️ - содержимого нет
