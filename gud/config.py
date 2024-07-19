import appdirs
import importlib.util
import os
from os.path import realpath
from .helpers import get_default_config_file_path


class GlobalConfig():

    app_name = "gud"
    app_author = "gud_industries"

    dir = appdirs.user_config_dir(app_name, app_author)
    full_path = os.path.join(dir, "config")

    @classmethod
    def create_config_if_needed(cls, ) -> None:
        """
        
        """
        os.makedirs(cls.dir, exist_ok=True)
        if os.path.exists(cls.full_path):
            return
        with open(cls.full_path, "w", encoding="utf-8") as f:
            ...

    @staticmethod
    def get_default_config_file_path() -> str|None:
        """
        
        """
        spec = importlib.util.find_spec("gud")
        if spec is None:
            return None
        loc = spec.origin
        if loc is None:
            return None
        loc_dir = os.path.dirname(loc)
        config_path = realpath(os.path.join(loc_dir, "defaults", "config"))
        return config_path



def setup_global_config():
    
    app_name = "gud"
    app_author = "GudIndustries"

    global_config_dir = appdirs.user_config_dir(app_name, app_author)
    os.makedirs(global_config_dir, exist_ok=True)
    global_config_file = os.path.join(global_config_dir, "config")

    if os.path.exists(global_config_file):
        return
    
    default_config_path = get_default_config_file_path()
    if not default_config_path:
        raise Exception("Default config file not found - possibly corrupted installation.")
    
    with open(default_config_path, "r", encoding="utf-8") as f:
        default_config = f.read()
    
    with open(global_config_file, "w", encoding="utf-8") as g:
        g.write(default_config)



def get_global_config_info() -> dict:

    app_name = "gud"
    app_author = "guddev"

    global_config_dir = appdirs.user_config_dir(app_name, app_author)
    global_config_file = os.path.join(global_config_dir, "config")

    return {
        ""
    }

    return global_config_file, global_config_dir

    print(global_config_file)
    print(type(global_config_file))

    os.makedirs(global_config_dir, exist_ok=True)

