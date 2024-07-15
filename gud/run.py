import argparse
from argparse import Namespace
import configparser
import sys
import os
from os.path import realpath
from .commands import (
    init,
    hello,
)

parser = argparse.ArgumentParser(
    description="Functionality for parsing Gud commands.",
)
subparsers = parser.add_subparsers(title="commands", dest="command")
subparsers.required = True

# list of all Gud commands that the user can provide
hello_subparser = subparsers.add_parser('hello', help='Say hello') # remove this afterwards
hello_subparser.add_argument("name", nargs="?", help="Name to greet")

init_subparser = subparsers.add_parser('init', help='Initialise repository')


class CommandInvocation:
    def __init__(self, all_args: Namespace, cwd: str):
        self.command: str = all_args.command
        self.args: dict = __class__.get_additional_commands(all_args)
        if self.command == "init":
            self.repo = Repository(cwd, make_new_repo=True)
        else:
            self.repo = Repository(cwd)

    @staticmethod
    def get_additional_commands(args: Namespace) -> dict:
        args_dict = vars(args)
        args_dict.pop("command", None)
        return args_dict
    

class Repository:
    def __init__(self, cwd: str, make_new_repo = False):
        if make_new_repo:
            self.path = cwd
        else:
            self.path = __class__.find_repo_path(cwd)
        self.config_path = os.path.join(self.path, "config")
        self.config = self.set_default_config()

    def set_default_config(self):
        config = configparser.ConfigParser()
        # default config settings
        config["user"] = {
            "name": "default_user"
        }
        config["core"] = {
            "autosave": "false"
        }
        with open(self.config_path, "w") as f:
            config.write(f)
        return config
    
    def set_config(self, config_options: dict):
        """
        example struction of config_options
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
        return config
        
    def load_config(self):
        config = configparser.ConfigParser()
        with open(self.config_path, "r") as f:
            config.read(f)
        return config

    @staticmethod
    def find_repo_path(curr_path):
        """ Recurse up the path tree to find the deepest .gud/ directory, if there is one """
        while True:
            parent_dir_path = realpath(os.path.dirname(curr_path))
            if curr_path == parent_dir_path:
                raise Exception("No gud repository found.")
            if ".gud" in os.listdir(curr_path):
                return curr_path
            curr_path = parent_dir_path


def main():
    # parse the args
    all_args = parser.parse_args(sys.argv[1:])
    cwd = os.getcwd()
    invocation = CommandInvocation(all_args, cwd)

    match invocation.command:
        case "hello":
            hello(invocation)
        case "init":
            init(invocation)


if __name__ == "__main__":
    main()