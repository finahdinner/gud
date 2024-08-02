import re
from hashlib import sha1
import zlib
from enum import Enum
import os
import subprocess


class EnumWrapper(Enum):
    @classmethod
    def get_all_names(cls):
        return [x.name for x in cls]
    
    @classmethod
    def get_all_values(cls):
        return [x.value for x in cls]

class OperatingSystem(EnumWrapper):
    WINDOWS = "Windows"
    MAC_OS = "Darwin"
    LINUX = "Linux"


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


def get_uncompressed_file_bytes(filepath, already_compressed=False) -> bytes:
    with open(filepath, "rb") as f:
        if already_compressed: # if reading from .gud/objects
            contents = zlib.decompress(f.read())
        else:
            contents = f.read()
        return contents
    

def get_compressed_file_bytes(filepath, already_compressed=False) -> bytes:
    with open(filepath, "rb") as f:
        if already_compressed: # if reading from .gud/objects
            contents = f.read()
        else:
            contents = zlib.compress(f.read())
        return contents


def hash_file_from_working_dir(filepath) -> str:
    file_uncompressed = get_uncompressed_file_bytes(filepath, already_compressed=False)
    file_hash = sha1(file_uncompressed).hexdigest()
    # TODO - make file in .gud/objects, relating to the file hash
    # then stored the COMPRESSED file at that path


def get_file_hash(filepath, decompress) -> str:
    file_contents = get_file_bytes(filepath, decompress)
    return sha1(file_contents).hexdigest()


def open_relevant_editor(op_sys: OperatingSystem, file_path: str) -> None:
    # TODO - figure out how to ensure file permissions are okay for opening the file
    match op_sys.name:
        case "WINDOWS":
            os.system(f"notepad {file_path}")
        case "MAC_OS":
            subprocess.call(["open", "-e", file_path])
        case "LINUX":
            subprocess.call(["nano", file_path])