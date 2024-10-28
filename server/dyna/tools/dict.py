from typing import List, Callable
from copy import copy
from datetime import datetime, timezone


def remove_where(d: dict, condition: Callable[[str | int], bool]):
    return {k: v for k, v in d.items() if not condition(k, v)}


def index_where(lst, condition):
    for index, item in enumerate(lst):
        if condition(item):
            return index
    return -1


def rename(d: dict, old_key: str, new_key: str):
    """
    Đổi tên các `old_key` trong `d` thành `new_key`
    """
    new_d = copy(d)
    if old_key in d:
        new_d[new_key] = new_d.pop(old_key)
    return new_d


def delete_keys(d: dict, keys: List[str]):
    for key in keys:
        if key in d:
            del d[key]
    return d

def convert_date(values: dict):
    for key, value in values.items():
        if isinstance(value, dict):
            convert_date(value)
            if "$date" in value:
                date_value = value["$date"]
                if isinstance(date_value, str):
                    try:
                        values[key] = datetime.fromisoformat(date_value)
                    except ValueError:
                        try:
                            values[key] = datetime.fromisoformat(date_value.replace("ISODate(", "").replace(")", "").replace('"', ''))
                        except ValueError:
                            pass
                elif isinstance(date_value, (int, float)):
                    try:
                        date_value_format = 0.0
                        if len(str(int(date_value))) > 10:
                            date_value_format = date_value / 1000
                        else:
                            date_value_format = date_value
                        values[key] = datetime.fromtimestamp(date_value_format, timezone.utc)
                    except:
                        raise ValueError("\"date\" invalid")
    return values

def convert_key(values: dict, old_key: str, new_key: str):
    if isinstance(values, dict):
        new_dict = {}
        for key, value in values.items():
            new_key if key == old_key else key
            new_dict[new_key] = convert_key(value, old_key, new_key)
        return new_dict
    elif isinstance(values, list):
        return [convert_key(item, old_key, new_key) for item in values]
    else:
        return values
                

def merge_dict(d1: dict, d2: dict):
    result = d1.copy()
    for key, value in d2.items():
        if value:
            result[key] = value
    return result