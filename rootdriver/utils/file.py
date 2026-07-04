from pathlib import Path

def ensure_file_exist(path, default_content:str=''):
    file = Path(path)
    if not file.exists():
        with open(path, "w", encoding="utf-8") as f:
            f.write(default_content)