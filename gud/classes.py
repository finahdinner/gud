import argparse
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
from .globals import COMPRESSION_LEVEL
import platform
import zlib
from hashlib import sha1
from questionary import Validator, ValidationError


class CommandInvocation:
    def __init__(self, all_args: argparse.Namespace, cwd: str):
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
    def get_additional_commands(args: argparse.Namespace) -> dict:
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
        else:
            self.root = __class__.find_repo_root_dir(cwd)
            if not self.root:
                sys.exit("No gud repository found in this directory, or in any parent directory.")
            self.path = os.path.join(self.root, ".gud/")

        self.global_config = GlobalConfig()
        self.repo_config = RepoConfig(repo_path=self.path)

        if not create_new_repo: # if the .gud dir already exists
            self.config = self.resolve_working_config()
            self.branch = self.get_current_branch() # get the name of the branch
            self.head: str|None = self.get_head() # get the commit of the HEAD

    def create_repo(self) -> None:
        """
        Create the repo. This is called manually at the conclusion of the <init> command.
        """
        try:
            os.makedirs(self.path, exist_ok=False)
        except FileExistsError:
            sys.exit(f"Repository {self.path} already exists.")
        # create objects dir
        objects_dir_path = os.path.join(self.path, "objects/")
        os.mkdir(objects_dir_path)
        # create heads dir, with main branch file
        heads_dir_path = os.path.join(self.path, "heads/")
        os.mkdir(heads_dir_path)
        main_head_path = os.path.join(heads_dir_path, "main")
        with open(main_head_path, "w", encoding="utf-8") as f:
            pass # (initially empty)
        # create BRANCH - this stores the current branch -- equivalent to git's HEAD
        head_path = os.path.join(self.path, "BRANCH")
        with open(head_path, "w", encoding="utf-8") as f:
            f.write("main") # store the name of the branch it is pointing to
        # create index
        index_path = os.path.join(self.path, "index")
        with open(index_path, "w", encoding="utf-8") as f:
            pass

    def get_current_branch(self) -> str:
        branch_ref_file_path = os.path.join(self.path, "BRANCH")
        with open(branch_ref_file_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def get_head(self, other_branch_name=None) -> str|None:
        """
        other_branch_name allows this function to look for the head of other branches
        """
        branch_name = other_branch_name if other_branch_name else self.branch
        branch_commit_file_path = os.path.join(self.path, "heads", branch_name)
        with open(branch_commit_file_path, "r", encoding="utf-8") as f:
            head_commit_hash = f.read().strip()
            if not head_commit_hash:
                return None
            return head_commit_hash

    def find_commit(self, hash):
        # TODO - consider if I even need this function. could I not just use Commit.deserialise()?
        dir_name, file_name = hash[:2], hash[2:]
        objects_dir_path = os.path.join(self.path, "objects/")
        commit_dir = os.path.join(objects_dir_path, dir_name)
        if not os.path.exists(commit_dir):
            raise Exception(f"Commit starting with hash {hash} does not exist")
        matching_objects = [os.path.join(commit_dir, file) for file in os.listdir(commit_dir) if file.startswith(hash)]
        if not matching_objects:
            raise Exception(f"Commit starting with hash {hash} does not exist")
        if len(matching_objects) > 1:
            raise Exception(f"Commit starting with hash {hash} is not unique. Please be more specific.")
        # check if it's a commit (raise an error if it's a blob or tree)

  
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

    def parse_index(self) -> dict:
        """ The index contains file paths relative to the root of the repo """
        index_path = os.path.join(self.path, "index")
        indexed_files = {}
        with open(index_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:
                file_mode, file_type, file_hash, file_path = line.split(" ")
                indexed_files[file_path] = {
                    "type": file_type,
                    "mode": file_mode,
                    "hash": file_hash
                }
        return indexed_files
    
    def write_to_index(self, new_index_dict) -> None:
        index_path = os.path.join(self.path, "index")
        with open(index_path, "w", encoding="utf-8") as f:
            for file_path in new_index_dict:
                file_mode = new_index_dict[file_path]["mode"]
                file_type = new_index_dict[file_path]["type"]
                file_hash = new_index_dict[file_path]["hash"]
                f.write(f"{file_mode} {file_type} {file_hash} {file_path}\n")
    
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
    def __init__(self, repo: Repository):
        self.objects_dir = os.path.join(repo.path, "objects")

    def deserialise(self, blob_hash, expected_type=None) -> bytes:
        """
        Serialised/stored data -> usable/readable data
        """
        full_file_path = self.get_full_file_path_from_hash(blob_hash)
        with open(full_file_path, "rb") as f:
            full_content = f.read()
        try:
            header, compressed_content = full_content.split(b"\0", 1) # only split on the first occurence
        except ValueError:
            raise ValueError("Null delimiter not found - incorrect blob format being read.")
        type, uncompressed_size_str = header.decode().split(" ")
        # if expecting the object to be a certain type, check it is this type
        if expected_type:
            assert type == expected_type
        uncompressed_content = zlib.decompress(compressed_content)
        assert int(uncompressed_size_str) == len(uncompressed_content)
        return uncompressed_content

    def get_full_file_path_from_hash(self, hash: str) -> str:
        dir_name = hash[:2]
        file_name = hash[2:]
        return os.path.join(self.objects_dir, dir_name, file_name)


class Blob(GudObject):    
    def serialise(self, og_file_path: str, write_to_file=False) -> str:
        """
        Usable/readable data -> serialised data for storage
        - read file contents
        - create the header
        - compress the file contents
        - combine the header + compressed file contents
        - hash this overall contents
        - store the blob, with the name/location based on the hash
        """
        # open and read bytes
        with open(og_file_path, "rb") as f:
            uncompressed_content = f.read()
        # create the header
        uncompressed_size = len(uncompressed_content)
        header = f"blob {uncompressed_size}\0".encode() # as bytes
        # compress the file
        compressed_content = zlib.compress(uncompressed_content, level=COMPRESSION_LEVEL)
        # full blob content
        full_content = header + compressed_content
        # hash
        blob_hash = sha1(full_content).hexdigest()
        # only if write_to_file is specified
        if write_to_file:
            full_file_path = self.get_full_file_path_from_hash(blob_hash)
            # create the dir if it doesn't already exist
            dir_path = os.path.dirname(full_file_path)
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
            # write to the objects file
            with open(full_file_path, "wb") as f:
                f.write(full_content)
        return blob_hash        

    def get_content(self, blob_hash) -> bytes:
        """
        Serialised/stored data -> usable/readable data
        """
        file_content = super().deserialise(blob_hash, expected_type="blob")
        return file_content


class Tree(GudObject):
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
    def serialise(self, index_dict):
        ...


    def get_content(self, tree_hash) -> bytes:
        """
        Serialised/stored data -> usable/readable data
        """
        file_content = super().deserialise(tree_hash, expected_type="tree")
        return file_content

class Commit(GudObject):
    def serialise(self) -> str:
        ...

    def get_content(self, commit_hash) -> bytes:
        """
        Serialised/stored data -> usable/readable data
        """
        file_content = super().deserialise(commit_hash, expected_type="commit")
        return file_content


class PathValidatorQuestionary(Validator):
    def validate(self, document):
        """
        The path must either be blank, in which case the user can 'complete' their selection
        or it must exist as a file path 
        """
        path = os.path.expanduser(document.text.strip()) # expanduser converts ~ to /home/<username>
        if (path == "/") or (path != "" and not os.path.exists(path)):
            raise ValidationError(
                message="Path is not valid"
            )
        

class PathValidatorArgparse(argparse.Action):
    def __call__(self, parser, namespace, paths, option_string=None):
        paths_not_valid = []
        for file_path in paths:
            if not os.path.exists(file_path):
                paths_not_valid.append(file_path)
        if paths_not_valid:
            error_msg = f"The following paths are not valid:\n{', '.join(paths_not_valid)}"
            sys.exit(error_msg)
        setattr(namespace, self.dest, paths)