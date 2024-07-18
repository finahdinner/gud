from argparse import Namespace
import configparser
import os
import sys
from os.path import realpath
from datetime import datetime


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

    def set_default_config(self):
        config = configparser.ConfigParser()
        # default config settings
        config["user"] = {
            "name": "default_user",
            "email": "no_email"
        }
        config["repo"] = {
            "experience_level": "beginner"
        }
        with open(self.config_path, "w") as f:
            config.write(f)
        return config
    
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
        
    def get_config(self):
        config = configparser.ConfigParser()
        try:
            with open(self.config_path, "r") as f:
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