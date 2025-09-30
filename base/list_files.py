import os

EXCLUDE_DIRS = {'.venv', '__pycache__', '.git'}
EXCLUDE_EXTS = {'.pyc', '.pyo', '.log', '.sqlite3'}

for root, dirs, files in os.walk('.'):
    # Убираем ненужные папки
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

    for f in files:
        if not any(f.endswith(ext) for ext in EXCLUDE_EXTS):
            print(os.path.relpath(os.path.join(root, f), '.'))
