import re
from enum import Enum
import os
import subprocess
import importlib.util
from os.path import realpath
from pathlib import Path


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


def open_relevant_editor(op_sys: OperatingSystem, file_path: str) -> None:
    match op_sys.name:
        case "WINDOWS":
            os.system(f"notepad {file_path}")
        case "MAC_OS":
            subprocess.call(["open", "-e", file_path])
        case "LINUX":
            subprocess.call(["nano", file_path])


def get_default_file_from_package_installation(file_name) -> None|str:
    """
    Retrieve the file path of the default config file,
    which is packaged up in the gud installation.
    """
    spec = importlib.util.find_spec("gud")
    if spec is None:
        return None
    loc = spec.origin
    if loc is None:
        return None
    loc_dir = os.path.dirname(loc)
    default_file_path = realpath(os.path.join(loc_dir, "defaults", file_name))
    return default_file_path


def parse_gudignore_in_dir(parent_dir) -> set:
    """ parent_dir is the directory where a specific gudignore exists """
    gudignore_path = os.path.join(parent_dir, ".gudignore")
    if not os.path.exists(gudignore_path):
        raise Exception(f"Gudignore file does not exist in {parent_dir}")
    ignored_file_paths = set()
    with open(gudignore_path, "r", encoding="utf-8") as f:
        file_paths = [line.strip() for line in f.readlines() if line.strip()]
        for file_path in file_paths:
            full_file_path = os.path.join(parent_dir, file_path)
            if not file_path.startswith("#"):
                ignored_file_paths.add(full_file_path)
    return ignored_file_paths


def get_all_ignored_files(initial_dir, as_rel_path=False) -> set:
    """
    as_rel_path determines if the paths returned are relative to the initial_dir or not
    """
    # TODO - determine if I will ever use as_rel_path
    all_ignored_file_paths = set() # contains full file paths
    for root, subdirs, files in os.walk(initial_dir):
        if ".gudignore" in files:
            ignored_file_paths = parse_gudignore_in_dir(root)
            if as_rel_path:
                rel_paths = set(os.path.relpath(file_path, initial_dir) for file_path in ignored_file_paths)
                all_ignored_file_paths.update(rel_paths)
            else:
                all_ignored_file_paths.update(ignored_file_paths)
    return all_ignored_file_paths


def format_path_for_gudignore(path_str):
    """
    1) posix-style file path
    2) ends in backslash if the path is a directory
    """
    path = Path(path_str)
    path_posix = path.as_posix()
    # ensure dirs end in a slash
    if path.is_dir():
        if not path_posix.endswith("/"):
            return path_posix + "/"
    return path_posix


def get_file_mode(file_path):
    """
    Returns a 6 digit octal number
    First 3 digits represent the file type (100 means normal file)
    The next 3 digits show the file mode for user, group, others (respectively)
    See https://docs.nersc.gov/filesystems/unix-file-permissions/ for an explanation
    """
    return oct(os.stat(file_path).st_mode).replace("0o", "")
