import os


def add_init_py(root_path):
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Пропускаем скрытые папки (например, .git, .venv и т.д.)
        if any(part.startswith('.') for part in dirpath.split(os.sep)):
            continue

        init_file = os.path.join(dirpath, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write('# Automatically added to make this directory a Python package\n')
            print(f'✅ Added: {init_file}')


# Запускаем на директории проекта
add_init_py('lms_platform')
