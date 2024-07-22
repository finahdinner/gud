import appdirs
import importlib.util
import os
from os.path import realpath
from configparser import ConfigParser


class Config:
    def __init__(self, repo_path):
        self.repo_config = RepoConfig(repo_path=repo_path)
        self.global_config = GlobalConfig()

    


class RepoConfig:
    """
    Configuration options for a specific repository.
    """
    def __init__(self, repo_path):
        self.path = os.path.join(repo_path, "config")
    
    def get_config(self) -> ConfigParser:
        """
        Retrieve the repo's configuration settings, as a ConfigParser object.
        """
        config = ConfigParser()
        with open(self.path, "r", encoding="utf-8") as f:
            config.read(f)
        return config

    def set_config(self, new_config_options: str|dict|ConfigParser) -> None:
        """
        Update the repo's config file with new_config_options, which is either
        a str (if reading from another config file) or a ConfigParser object.
        """
        with open(self.path, "w", encoding="utf-8") as f:
            if isinstance(new_config_options, ConfigParser):
                new_config_options.write(f)
            elif isinstance(new_config_options, str):
                f.write(new_config_options)               


class GlobalConfig:
    """
    Encapsulation of all the important methods and variables
    associated with the global gud config options.
    """
    __app_name = "gud"
    __app_author = "gud_industries"
    # these paths will vary depending on the OS
    __dir = appdirs.user_config_dir(__app_name, __app_author)
    path = os.path.join(__dir, "config")

    def __init__(self):
        # each time a GlobalConfig() object is created, ensure global config exists
        self.create_global_config_if_needed()

    @classmethod
    def create_global_config_if_needed(cls) -> None:
        """
        Create a global config file.
        If the file already exists, return and do nothing with it.
        If it does not exist, copy the default config values into it.
        """
        os.makedirs(cls.__dir, exist_ok=True)
        if os.path.exists(cls.path):
            return
        default_config_file = get_default_config_file_path()
        if not default_config_file:
            raise Exception("Default config file not found - possibly corrupted installation.")
        with open(default_config_file, "r", encoding="utf-8") as f:
            default_config = f.read()
        __class__.set_config(default_config)

    @classmethod
    def get_config(cls) -> ConfigParser:
        """
        Retrieve global configuration settings, as a ConfigParser object.
        """
        config = ConfigParser()
        with open(cls.path, "r", encoding="utf-8") as f:
            config.read(f)
        return config

    @classmethod
    def set_config(cls, new_config_options: str|ConfigParser) -> None:
        """
        Update the global config file with new_config_options, which is either
        a str (if reading from another config file) or a ConfigParser object.
        """
        with open(cls.path, "w", encoding="utf-8") as f:
            if isinstance(new_config_options, ConfigParser):
                new_config_options.write(f)
            elif isinstance(new_config_options, str):
                f.write(new_config_options)


def get_default_config_file_path() -> str|None:
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
    config_path = realpath(os.path.join(loc_dir, "defaults", "config"))
    return config_path
