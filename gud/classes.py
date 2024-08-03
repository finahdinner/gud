from argparse import Namespace
import os
import sys
from os.path import realpath
from datetime import datetime
from configparser import ConfigParser
from .helpers import OperatingSystem
from .config import (
    GlobalConfig,
    RepoConfig,
)
import platform


class CommandInvocation:
    def __init__(self, all_args: Namespace, cwd: str):
        self.command: str = all_args.command
        self.args: dict = __class__.get_additional_commands(all_args)
        self.cwd = cwd # current working directory
        self.timestamp = __class__.get_timestamp_aware()
        # get the OS of the host system
        try:
            pltform = platform.system()
            self.os = OperatingSystem(pltform)
        except ValueError:
            sys.exit(f"Your platform ({pltform}) is not supported.\nSupported platforms: {OperatingSystem.get_all_names()}")
        if self.command == "init":
            self.repo = Repository(cwd, create_new_repo=True)
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
    def __init__(self, cwd: str, create_new_repo = False):
        if create_new_repo:
            existing_repo_root_dir = __class__.find_repo_root_dir(cwd)
            if existing_repo_root_dir:
                existing_repo_path = os.path.join(existing_repo_root_dir, ".gud/")
                sys.exit(f"Repository already exists at {existing_repo_path}")
            else:
                self.root = cwd
                self.path = os.path.join(self.root, ".gud/")
                self.index = None # will be created later
        else:
            self.root = __class__.find_repo_root_dir(cwd)
            self.path = os.path.join(self.root, ".gud/")
            if not self.path:
                sys.exit("No gud repository found in this directory, or in any parent directory.")
            self.index = Index(repo_path=self.path)

        self.global_config = GlobalConfig()
        self.repo_config = RepoConfig(repo_path=self.path)

        # the "effective" config - combination of global and repo-specific settings
        if not create_new_repo:
            self.config = self.resolve_working_config()

    def create_repo(self) -> None:
        """
        Create the repo. This is called manually at the conclusion of the <init> command.
        """
        try:
            os.makedirs(self.path, exist_ok=False)
        except FileExistsError:
            sys.exit(f"Repository {self.path} already exists.")

        # create the index file
        self.index = Index(self.path)
  
    def resolve_working_config(self) -> ConfigParser:
        """
        Combine the global config and repo-specific config settings
        into a single config entity.
        """
        working_config = ConfigParser()
        global_config = self.global_config.get_config()
        repo_config = self.repo_config.get_config()
        configs_to_load = [global_config, repo_config]
        for cnf in configs_to_load:
            for section in cnf.sections():
                if not working_config.has_section(section):
                    working_config.add_section(section)
                for key, value in cnf.items(section):
                    working_config[section][key] = value
        return working_config

    def copy_global_to_repo_config(self, provided_options: dict|None = None) -> None:
        """
        Set the repo's config to same as the global config.
        Probably needs to bit of additional functionality eventually.
        """
        global_config = self.global_config.get_config()
        self.repo_config.set_config(global_config)

    @staticmethod
    def find_repo_root_dir(curr_path) -> str:
        """
        Recurse up the path tree to find the parent dir of
        the deepest .gud/ directory, if there is one
        """
        while True:
            parent_dir_path = realpath(os.path.dirname(curr_path))
            if curr_path == parent_dir_path:
                return ""
            if ".gud" in os.listdir(curr_path):
                break
            curr_path = parent_dir_path
        return curr_path   


class GudObject:
    # TODO - implement this
    """
    object types:
        - blob (eg a file)
        - tree (a snapshot of the index at a given time):
            - this contains a list of the file hashes and file paths of objects at a given time
        - commit:
            - tree
            - parent commit
            - author/timestamp etc    
    """
    def __init__(self, data):
        ...


class Blob(GudObject):
    ...


class Tree:
    """
    Imagine it as being a node in a larger tree
    This node contains 0 or more blobs
    and 0 or more trees (subdirectories)

    File contents:
        each row:
            mode, object_type, hash, name
        eg a blob:
            00644 blob a906cb2a4a904a152e80877d4088654daad0c859 README
        eg another tree:
            040000 tree 99f1a6d12cb4b6f19c8655fca46c3ecf317074e0 lib

    As trees point to subdirectory trees, when creating a tree object,
    you should start from the DEEPEST node and work your way up
    """


    def __init__(self, root_dir):
        """
        starting at the root_dir, traverse all files in the working directory




        """
        # TODO - implement
        
        


class Commit(GudObject):
    ...


class Index:
    """
    The index file is a virtual representation of what the repository views the current state
    of the repository to be. A tree object is a snapshot of the index at a given time.
    """
    def __init__(self, repo_path, index_already_exists=True):
        self.path = os.path.join(repo_path, "index")
        if not index_already_exists:
            # create blank index file
            with open(self.path, "w"):
                pass

        def add_to_index(self, object):
            """
            Add a single file to the index
            """
            ...

        def remove_from_index(self):
            """
            Remove a single file from the index
            """
            ...
