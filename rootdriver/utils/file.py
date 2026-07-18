from pathlib import Path
import json

def ensure_file_exist(path, default_content:str='') -> None:
    file = Path(path)
    if not file.exists():
        with open(path, "w", encoding="utf-8") as f:
            f.write(default_content)

def check_json_format(path) -> bool:
    file = Path(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            json.load(f)
            return True
    except json.decoder.JSONDecodeError:
        return False


def ensure_json_file(path, default_content:str='', use_default_content_if_file_is_empty_str:bool=False) -> None:
    ensure_file_exist(path)
    if use_default_content_if_file_is_empty_str:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if content == "":
            with open(path, "w", encoding="utf-8") as f:
                f.write(default_content)
    if not check_json_format(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(default_content)

