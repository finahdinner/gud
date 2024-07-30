import argparse
import sys
import os
from .classes import CommandInvocation
from .commands import (
    init,
    hello,
    config,
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
init_subparser.add_argument("--global-config", "-gc", action="store_true", help="Skip the interactive prompt and use default values")


config_subparser = subparsers.add_parser('config', help="View or edit configuration options")
view_or_edit = config_subparser.add_mutually_exclusive_group(required=False)
view_or_edit.add_argument("--view", "-v", action="store_true", help="View configuration options")
view_or_edit.add_argument("--edit", "-e", action="store_true", help="Edit configuration options")
repo_or_default = config_subparser.add_mutually_exclusive_group(required=False)
repo_or_default.add_argument("--default", "-d", action="store_true", help="Access the default configuration options")

status_subparser = subparsers.add_parser('config', help="View all staged and unstaged files")

stage_subparser = subparsers.add_parser('stage', help="Add or remove file(s) to or from the staging area")
add_or_remove = stage_subparser.add_mutually_exclusive_group(required=False)
add_or_remove.add_argument("--add", "-a", action="store_true", help="Add file(s) the staging area")
add_or_remove.add_argument("--remove", "-r", action="store_true", help="Remove file(s) from the staging area")

commit_subparser = subparsers.add_parser('config', help="Commit staged files to the repository's history")



def main():
    
    all_args = parser.parse_args(sys.argv[1:])
    cwd = os.getcwd()
    invocation = CommandInvocation(all_args, cwd)

    match invocation.command:
        case "hello":
            hello(invocation)
        case "init":
            init(invocation)
        case "config":
            config(invocation)


if __name__ == "__main__":
    main()