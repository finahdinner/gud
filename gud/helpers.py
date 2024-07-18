import re
import importlib.util
import os
from os.path import realpath


def is_valid_username(username) -> bool:
    regex_pattern = r"^\w+$"
    results = re.search(regex_pattern, username)
    return results is not None and len(username) <= 16


def is_valid_email(email) -> bool:
    """
    Basic check to return if an email address is *basically* valid
    """
    regex_pattern = r"^\w+@[a-zA-Z]+\.[a-zA-Z]+$"
    results = re.search(regex_pattern, email)
    return results is not None


def get_default_config_file_path() -> str|None:
    spec = importlib.util.find_spec("gud")
    if spec is None:
        return None
    loc = spec.origin
    if loc is None:
        return None
    loc_dir = os.path.dirname(loc)
    config_path = realpath(os.path.join(loc_dir, "defaults", "config"))
    return config_path

def get_global_config_file_path() -> str|None:
    return ""