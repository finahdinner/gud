import argparse
import sys
import os
from .classes import CommandInvocation, PathValidatorArgparse
from .commands import (
    test,
    hello,
    init,
    config,
    ignoring,
    stage,
    commit,
    status,
    log,
    branch,
    checkout
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
config_subparser.add_argument("repo_or_global", nargs="?", choices=["global", "repo"], help="Global or repository-specific config files")

ignoring_subparser = subparsers.add_parser('ignoring', help="View which files Gud is currently set to ignore")

stage_subparser = subparsers.add_parser('stage', help="Add or remove file(s) to or from the staging area")
add_or_remove = stage_subparser.add_argument('add_or_remove', nargs="?", choices=["add", "remove"], help="Add or remove from the staging area")
# file_names is a list of zero or more files
file_paths = stage_subparser.add_argument("file_paths", nargs="*", action=PathValidatorArgparse, help="A specified file or directory to add/remove to/from the staging area")

commit_subparser = subparsers.add_parser('commit', help="Commit staged files to the repository's history")

status_subparser = subparsers.add_parser('status', help="View all staged and unstaged files")

log_subparser = subparsers.add_parser('log', help="View the commit history")
log_subparser.add_argument("short", nargs="?", choices=["short"], help="Show less information about each commit")

branch_subparser = subparsers.add_parser('branch', help="View existing branches, rename a branch or create a new branch")
view_or_rename_or_create = branch_subparser.add_argument(
    'view_or_rename_or_create', nargs="?", choices=["view", "rename", "create"], help="Choose to view, rename or create a branch"
)

checkout_subparser = subparsers.add_parser('checkout', help="View a specific commit or branch")
branch_or_hash = checkout_subparser.add_mutually_exclusive_group(required=False)
branch_or_hash.add_argument("--branch", help="Choose a branch to checkout to")
branch_or_hash.add_argument("--hash", help="Choose a commit hash to checkout to")

# TODO - remove this once testing is over
test_command_subparser = subparsers.add_parser('test', help="Use this command for all your testing needs")


def main():
    
    all_args = parser.parse_args(sys.argv[1:])
    cwd = os.getcwd()
    invocation = CommandInvocation(all_args, cwd)

    match invocation.command:
        # TODO - remove test command eventually
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
        case "stage":
            stage(invocation)
        case "commit":
            commit(invocation)
        case "status":
            status(invocation)
        case "log":
            log(invocation)
        case "branch":
            branch(invocation)
        case "checkout":
            checkout(invocation)


if __name__ == "__main__":
    main()