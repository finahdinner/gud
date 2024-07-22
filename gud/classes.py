from argparse import Namespace
import os
import sys
from os.path import realpath
from datetime import datetime
from .config import (
    RepoConfig,
    GlobalConfig
)


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
        self.repo_config = RepoConfig(repo_path=self.path)
        self.global_config = GlobalConfig()

    def create_repo(self) -> None:
        """
        Create the repo. This is called manually at the conclusion of the <init> command.
        """
        try:
            os.makedirs(self.path, exist_ok=False)
        except FileExistsError:
            sys.exit(f"Repository {self.path} already exists.")

    def copy_global_to_repo_config(self, provided_options: dict|None = None) -> None:
        """
        Set the repo's config to same as the global config.
        Probably needs to bit of additional functionality eventually.
        """
        global_config = self.global_config.get_global_config()
        self.repo_config.set_config(global_config)

    @staticmethod
    def find_repo_path(curr_path) -> str:
        """ Recurse up the path tree to find the deepest .gud/ directory, if there is one """
        while True:
            parent_dir_path = realpath(os.path.dirname(curr_path))
            if curr_path == parent_dir_path:
                sys.exit("No gud repository found in this directory, or in any parent directory.")
            if ".gud" in os.listdir(curr_path):
                break
            curr_path = parent_dir_path
        return f"{curr_path}/.gud"