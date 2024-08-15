import argparse
import sys
import os
from .classes import CommandInvocation
from .commands import (
    test,
    hello,
    init,
    config,
    ignoring,
    status,
    stage
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
init_subparser.add_argument("is_default", nargs="?", choices=["default"], help="Skip the interactive prompt and use default values")

config_subparser = subparsers.add_parser('config', help="View or edit configuration options")
config_subparser.add_argument("view_or_edit", nargs="?", choices=["view", "edit"], help="Choose to view or edit config files")
config_subparser.add_argument("global_or_repo", nargs="?", choices=["global", "repo"], help="Global or repository-specific config files")

# ignoring_subparser = subparsers.add_parser('ignore', help="View which files Gud is currently set to ignore")

# status_subparser = subparsers.add_parser('status', help="View all staged and unstaged files")

# stage_subparser = subparsers.add_parser('stage', help="Add or remove file(s) to or from the staging area")
# add_or_remove = stage_subparser.add_mutually_exclusive_group(required=False)
# add_or_remove.add_argument("--add", "-a", action="store_true", help="Add file(s) the staging area")
# add_or_remove.add_argument("--remove", "-r", action="store_true", help="Remove file(s) from the staging area")
# file_name = stage_subparser.add_argument("file_name", nargs="?", help="A specified file or directory to add/remove to/from the staging area")

# commit_subparser = subparsers.add_parser('config', help="Commit staged files to the repository's history")

# TODO - remove this once testing is over
test_command_subparser = subparsers.add_parser('test', help="Use this command for all your testing needs")


def main():
    
    all_args = parser.parse_args(sys.argv[1:])
    cwd = os.getcwd()
    invocation = CommandInvocation(all_args, cwd)
    print(invocation.command)
    print(invocation.args)

    match invocation.command:
        case "test":
            test(invocation)
        case "hello":
            hello(invocation)
        case "init":
            init(invocation)
        case "config":
            config(invocation)
        case "ignoring":
            ignoring(invocation)
        case "status":
            status(invocation)
        case "stage":
            stage(invocation)


if __name__ == "__main__":
    main()