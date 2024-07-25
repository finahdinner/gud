import re
from hashlib import sha1
import zlib


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


def get_file_bytes(filepath, decompress=False):
    with open(filepath, "rb") as f:
        if decompress:
            contents = zlib.decompress(f.read())
        else:
            contents = f.read()
        return contents


def get_file_hash(filepath, decompress):
    file_contents = get_file_bytes(filepath, decompress)
    return sha1(file_contents).hexdigest()