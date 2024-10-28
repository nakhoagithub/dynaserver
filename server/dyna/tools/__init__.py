import os
import secrets
import hashlib
import base64
import re
from copy import copy
from datetime import datetime, timezone
from flask import Request


def class_name_to_id(name: str):
    snake_case = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    return snake_case


def root_dir(indicator_file="requirements.txt"):
    current_path = os.path.abspath(os.path.dirname(__file__))
    while current_path != os.path.dirname(current_path):
        if indicator_file in os.listdir(current_path):
            return os.path.normcase(current_path)
        current_path = os.path.dirname(current_path)
    raise FileNotFoundError(f"Project root containing {indicator_file} not found.")


def generate_password(password: str):
    """
    Generate hashed password
    return hash
    """
    salt = secrets.token_bytes(16)
    str_salt = base64.b64encode(salt).decode("utf-8")
    salted_password = salt + password.encode("utf-8")
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    return f"{hashed_password}:{str_salt}"


def verify_password(password: str, password_hashed: str):
    """
    Vertify password
    """
    hash, salt = password_hashed.rsplit(":", 1)
    salt = base64.b64decode(salt)
    salted_password = salt + password.encode("utf-8")
    rehashed_password = hashlib.sha256(salted_password).hexdigest()
    return rehashed_password == hash


def get_remote_ip(request: Request):
    """
    Get ip of client
    """
    if request.headers.get("CF-Connecting-IP"):
        return request.headers.get("Cf-Connecting-Ip")
    elif request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    else:
        return request.remote_addr


def utc_now():
    local_time = datetime.now()
    utc_time = local_time.astimezone(timezone.utc)
    return utc_time

def timestamp():
    return utc_now().timestamp() * 1000


def timestamp_mongo():
    return {"$date": timestamp()}