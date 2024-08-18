import argparse
import os
import sys
from os.path import realpath
from datetime import datetime
from configparser import ConfigParser
from .helpers import (
    OperatingSystem,
    get_default_file_from_package_installation
)
from .globals import COMPRESSION_LEVEL
import platform
import zlib
from hashlib import sha1
from questionary import Validator, ValidationError
import appdirs


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
                file_mode, file_type, file_hash, file_path = line.split("\t")
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
                f.write(f"{file_mode}\t{file_type}\t{file_hash}\t{file_path}\n")
    
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
        self.repo = repo
        self.objects_dir = os.path.join(repo.path, "objects")

    def serialise_object(self, uncompressed_content: bytes, object_type: str, write_to_file=False) -> str:
        uncompressed_size = len(uncompressed_content)
        header = f"{object_type} {uncompressed_size}\0".encode()
        compressed_content = zlib.compress(uncompressed_content, level=COMPRESSION_LEVEL)
        full_content = header + compressed_content
        hash = sha1(full_content).hexdigest()
        if write_to_file:
            obj_file_path = self.get_full_file_path_from_hash(hash)
            dir_path = os.path.dirname(obj_file_path)
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
            with open(obj_file_path, "wb") as f:
                f.write(full_content)
        return hash

    def deserialise_object(self, obj_hash: str, expected_type=None) -> bytes:
        """
        Serialised/stored data -> usable/readable data
        """
        full_file_path = self.get_full_file_path_from_hash(obj_hash)
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
        blob_hash = super().serialise_object(uncompressed_content, "blob", write_to_file)
        return blob_hash        

    def get_content(self, blob_hash) -> bytes:
        """
        Serialised/stored data -> usable/readable data
        """
        file_content = super().deserialise_object(blob_hash, expected_type="blob")
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
    def __init__(self, repo):
        super().__init__(repo)
        self.index = self.repo.parse_index()
        self.tree_hash = None

    def serialise(self) -> str:
        """
        - read the current index and create and save a path_tree object from it
        - using the tree, and the hashes stored in it, generate and save tree objects
        """
        all_path_parts = [path.split(os.sep) for path in self.index.keys()]
        path_tree = self._build_path_tree(all_path_parts)
        self.tree_hash = self._create_tree_object(path_tree) # creates all the tree objects
        return self.tree_hash
        
    def get_content(self, tree_hash) -> bytes:
        """
        Serialised/stored data -> usable/readable data
        """
        file_content = super().deserialise_object(tree_hash, expected_type="tree")
        return file_content
    
    def _insert_path_into_tree(self, tree, prefix_parts, suffix_parts):
        """
        eg for the path /home/me/project/file.txt
        if we have navigated to tree["home"]["me"],
        - prefix_parts = ["home", "me"]
        - suffix_parts = ["project", "file.txt"]
        ie prefix_parts represents the file path *up to* this current directory
        suffix_parts represents the rest of the full file path
        -- prefix_parts is "remembered" so the full path can be reconstructed to
        read from the index (using index[file_path]) to get the file mode and hash,
        which will both be stored in the tree in a tuple (mode, hash)    
        """
        if len(suffix_parts) == 1: # this is a file
            file_name = suffix_parts[0]
            all_parts = [x for x in prefix_parts] + suffix_parts
            full_rel_file_path = os.path.join(*all_parts)
            blob_info_dict = self.index[full_rel_file_path] # this should exist
            blob_info = [blob_info_dict["mode"], blob_info_dict["hash"]]
            tree[file_name] = blob_info
            return
        # update the path parts
        prefix_parts.append(suffix_parts[0])
        suffix_parts = suffix_parts[1:]
        child_dir = prefix_parts[-1]
        if child_dir not in tree:
            tree[child_dir] = {} # dict represents a directory
        self._insert_path_into_tree(
            tree=tree[child_dir],
            prefix_parts=prefix_parts,
            suffix_parts=suffix_parts
        )

    def _build_path_tree(self, all_path_parts: list[list]) -> dict:
        """
        each dir is represented by a dictionary
        a dir can contain:
            - other dirs (which are dicts)
            - files (represented by [mode, hash])
        """
        tree = {}
        for path_parts in all_path_parts:
            self._insert_path_into_tree(
                tree=tree,
                prefix_parts=[],
                suffix_parts=path_parts
            )
        return tree
    
    def _create_tree_object(self, path_tree):
        """
        Creates all the tree objects in .gud/objects
        """
        tree_file_lines = []

        for name, subtree in path_tree.items():
            if isinstance(subtree, list): # it's a blob
                mode, hash = subtree
                type = "blob"
            else: # is a subtree (expected to be a dict)
                hash = self._create_tree_object(subtree)
                mode = "040000" # this is the mode git uses for directories
                type = "tree"
            # insert a single row representing the blob or tree
            tree_file_lines.append(f"{mode}\t{type}\t{hash}\t{name}\n")

        # using tree_file_lines, create and hash the actual file
        uncompressed_content = b"".join((line.encode() for line in tree_file_lines))
        tree_hash = super().serialise_object(uncompressed_content, "tree", write_to_file=True)
        return tree_hash
    
    def _read_tree_object(self, tree_hash, curr_path, indexed_files=None):
        """
        create an index (as a dictionary), representing all files descended from a specified
        tree_hash. it contains info about their mode, type, hash and path
        """
        if indexed_files is None:
            indexed_files = {}
        content = self.deserialise_object(tree_hash).decode()
        lines = content.split("\n")
        # collect blobs and trees
        blobs = []
        trees = []
        for line in lines:
            if not line.strip():
                continue
            mode, type, hash, path = line.split("\t")
            if type == "blob":
                blobs.append((mode, type, hash, path))
            elif type == "tree":
                trees.append((mode, type, hash, path))
        # index blobs first
        for mode, type, hash, path in blobs:
            full_path = os.path.join(curr_path, path)
            indexed_files[full_path] = {
                "type": type,
                "mode": mode,
                "hash": hash
            }
        # once all blobs have been processed from this tree, recurse into deeper trees
        for mode, type, hash, path in trees:
            tree_hash = hash
            subtree_path = os.path.join(curr_path, path)
            self._read_tree_object(tree_hash, curr_path=subtree_path, indexed_files=indexed_files)

        return indexed_files
    
    def get_index_of_commit(self, commit_obj, commit_hash) -> dict:
        """ Get an index representation of the HEAD commit """
        if not commit_hash: # no commits are recorded
            head_index = {}
        else:
            head_commit_contents = commit_obj.get_content(commit_hash).decode()
            for line in head_commit_contents.split("\n"):
                try:
                    type, value = line.split("\t")
                except ValueError:
                    continue
                else:
                    if type == "tree":
                        root_tree_hash = value
            if not root_tree_hash:
                raise Exception(f"Could not find tree_hash from commit {commit_hash}")
            # generate an "head_index" by recursively inspecting all the tree objects
            head_index = self._read_tree_object(root_tree_hash, curr_path="")
        return head_index
    
class Commit(GudObject):
    def __init__(self, repo, tree_hash=None, commit_message=None, timestamp=None):
        super().__init__(repo)
        self.tree_hash = tree_hash
        self.commit_message = commit_message
        self.timestamp = timestamp

    def serialise(self) -> str:
        """
        tree <hash>
        parent <hash> (unless it's the first commit, in which case this line is empty)
        committer <email>
        message <message>
        """
        commit_file_lines = []
        commit_file_lines.append(f"tree\t{self.tree_hash}\n")
        curr_head = self.repo.head
        if curr_head:
            commit_file_lines.append(f"parent\t{curr_head}\n")
        committer_name = self.repo.config["user"]["name"]
        committer_email = self.repo.config["user"]["email"]
        commit_file_lines.append(f"committer\t{committer_name} <{committer_email}> ({self.timestamp})\n")
        commit_file_lines.append("\n")
        commit_file_lines.append(self.commit_message)

        uncompressed_content = b"".join((line.encode() for line in commit_file_lines))
        commit_hash = super().serialise_object(uncompressed_content, "commit", write_to_file=True)
        return commit_hash

    def get_content(self, commit_hash) -> bytes:
        """
        Serialised/stored data -> usable/readable data
        """
        file_content = super().deserialise_object(commit_hash, expected_type="commit")
        return file_content   
        

class Branch:
    def __init__(self, repo: Repository):
        self.repo = repo
        self.heads_dir = os.path.join(self.repo.path, "heads")

    def create_branch(self, branch_name):
        new_branch_path = self._get_branch_path(branch_name)
        if os.path.exists(new_branch_path):
            raise FileExistsError("Branch already exists")
        with open(new_branch_path, "w", encoding="utf-8") as f:
            # copy the current head's commit into the new branch
            head_commit_hash = self.repo.head if self.repo.head else "" 
            f.write(head_commit_hash)

    def delete_branch(self, branch_name: str):
        branch_path = self._get_branch_path(branch_name)
        if branch_name == self.repo.branch:
            raise Exception("You cannot delete a branch that you are currently on")
        os.remove(branch_path)

    def rename_branch(self, old_name: str, new_name: str):
        existing_branch_path = self._get_branch_path(old_name)
        new_branch_path = self._get_branch_path(new_name)
        os.rename(existing_branch_path, new_branch_path)
        # change the contents of the BRANCH file if currently on it
        if self.repo.branch == old_name:
            _BRANCH_path = os.path.join(self.repo.path, "BRANCH")
            with open(_BRANCH_path, "w", encoding="utf-8") as f:
                f.write(new_name)

    def get_branch_head(self, branch_name) -> str:
        branch_path = self._get_branch_path(branch_name)
        with open(branch_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def get_all_branches_info(self) -> dict:
        all_branches_info = {}
        all_names = os.listdir(self.heads_dir)
        for branch_name in all_names:
            all_branches_info[branch_name] = self.get_branch_head(branch_name)
        return all_branches_info

    def _get_branch_path(self, branch_name) -> str:
        return os.path.join(self.heads_dir, branch_name)

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
            config.read_file(f)
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
        default_config_file = get_default_file_from_package_installation("config")
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
            config.read_file(f)
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
        

class TextValidatorQuestionaryNotEmpty(Validator):
    def validate(self, document):
        text = document.text.strip()
        if not text:
            raise ValidationError(
                message="You cannot leave this blank"
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
