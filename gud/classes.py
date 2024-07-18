from argparse import Namespace
import configparser
import os
import sys
from os.path import realpath
from datetime import datetime
from .helpers import get_default_config_file_path, get_global_config_file_path


class CommandInvocation:
    def __init__(self, all_args: Namespace, cwd: str):
        self.command: str = all_args.command
        self.args: dict = __class__.get_additional_commands(all_args)
        self.cwd = cwd # current working directory
        self.timestamp = __class__.get_timestamp_aware()
        if self.command == "init":
            self.repo = Repository(cwd, repo_exists=False)
        else:
            self.repo = Repository(cwd)

    @staticmethod
    def get_additional_commands(args: Namespace) -> dict:
        args_dict = vars(args)
        args_dict.pop("command", None)
        return args_dict
    
    @staticmethod
    def get_timestamp_aware() -> datetime:
        local_time = datetime.now()
        local_tz = local_time.astimezone().tzinfo
        local_time_aware = local_time.replace(tzinfo=local_tz)
        return local_time_aware
    

class Repository:
    def __init__(self, cwd: str, repo_exists = True):
        if not repo_exists:
            # this dir doesn't exist but will be made if the 'init' command is completed
            self.path = f"{cwd}/.gud"
        else:
            self.path = __class__.find_repo_path(cwd)
        self.config_path = os.path.join(self.path, "config")
        self.config = self.get_config()
        self.global_config = self.get_global_config_options()

    def set_default_config_options(self):
        default_config_path = get_default_config_file_path()
        if not default_config_path:
            raise Exception("Could not find default config file in installation package.")
        default_config_options = dict(self.get_config())
        self.set_config(default_config_options)

    def get_global_config_options(self):
        config_path = get_global_config_file_path()
        if not config_path:
            raise Exception("Could not find global config file.")
        config_options = dict(self.get_config())
        return config_options
    
    def create_repo(self):
        try:
            os.makedirs(self.path, exist_ok=False)
        except FileExistsError:
            sys.exit(f"Repository {self.path} already exists.") 
    
    def set_config(self, config_options: dict):
        """
        example structure of config_options
        config_options = {
            <section1>: {
                <option>: <value>
            },
            <section2>: {
                <option>: <value>
            },
        }
        """
        config = configparser.ConfigParser()
        for section in config_options:
            config[section] = config_options[section]
        with open(self.config_path, "w") as f:
            config.write(f)
        
    def get_config(self, specified_path=None):
        config = configparser.ConfigParser()
        config_file_path = specified_path if specified_path else self.config_path
        try:
            with open(config_file_path, "r") as f:
                config.read(f)
        except FileNotFoundError:
            pass # will then return an empty config object
        return config

    @staticmethod
    def find_repo_path(curr_path):
        """ Recurse up the path tree to find the deepest .gud/ directory, if there is one """
        while True:
            parent_dir_path = realpath(os.path.dirname(curr_path))
            if curr_path == parent_dir_path:
                sys.exit("No gud repository found in this directory, or in any parent directory.")
            if ".gud" in os.listdir(curr_path):
                break
            curr_path = parent_dir_path
        return f"{curr_path}/.gud"