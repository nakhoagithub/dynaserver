import re
import json


def valid_dict_str(value: str):
    try:
        if str(value).startswith("{") and str(value).endswith("}"):
            return eval(json.loads(json.dumps(value)))
    except:
        pass
    error = (f"{value} is not a dict.")
    raise ValueError(error)

def valid_dict(value: dict):
    try:
        if type(value) is dict:
            return value
    except:
        pass
    error = (f"{value} is not a dict.")
    raise ValueError(error)


def valid_list_str(value: str):
    if len(value.split(",")) > 0:
        return value.split(",")

    error = (f"{value} is not a list.")
    raise ValueError(error)


def valid_list(value):
    if type(value) is list:
        return value
    else:
        error = (f"{value} is not a list.")
        raise ValueError(error)


def valid_list_dict(value):
    if type(value) is list:
        if len(value) == 0:
            error = (f"{value} is empty")
            raise ValueError(error)

        check = []
        for i in value:
            if type(i) is not dict:
                check.append(False)
        if False not in check:
            return value
    error = (f"{value} is not a List[dict].")
    raise ValueError(error)


def valid_email(email):
    pattern = r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,}$"
    if re.match(pattern, email) is not None:
        return email

    error = (f"{email} is not a valid email.")
    raise ValueError(error)


def valid_password(password: str):
    if len(password) >= 1:
        return password

    raise ValueError("Not a valid password.")


def is_int(value: str | None):
    try:
        if value is None:
            return None
        return int(value)
    except:
        return None


def is_float(value: str | None):
    try:
        if value is None:
            return None
        return float(value)
    except:
        return None