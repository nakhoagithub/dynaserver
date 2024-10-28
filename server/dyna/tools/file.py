import os
import json


def list_file(folder_path: str, extension: str = None):
    json_files = []
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(extension):
                    json_files.append(os.path.normcase(os.path.join(root, file)))
    except Exception as e:
        pass
    return json_files


def read_json(file_path: str) -> dict | None:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None