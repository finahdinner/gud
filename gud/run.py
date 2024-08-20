import argparse
import sys
import os
from .classes import CommandInvocation
from .commands import (
    hello,
    load_example,
    init,
    config,
    ignoring,
    stage,
    commit,
    status,
    log,
    branch,
    checkout,
    restore
)


parser = argparse.ArgumentParser(
    description="Functionality for parsing Gud commands.",
)
subparsers = parser.add_subparsers(title="commands", dest="command")
subparsers.required = True

hello_subparser = subparsers.add_parser("hello", help="Hello!")

# used to load the example folder, so people can use it alongside the written tutorial
load_example_subparser = subparsers.add_parser("loadexample", help="Load an example folder into your directory. For use alongside the written Gud tutorial.")

init_subparser = subparsers.add_parser('init', help='Initialise repository')
init_subparser.add_argument("is_default", nargs="?", choices=["default"], help="Skip the interactive prompt and use default values")

config_subparser = subparsers.add_parser('config', help="View or edit configuration options")
config_subparser.add_argument("view_or_edit", nargs="?", choices=["view", "edit"], help="Choose to view or edit config files")
config_subparser.add_argument("repo_or_global", nargs="?", choices=["global", "repo"], help="Global or repository-specific config files")

ignoring_subparser = subparsers.add_parser('ignoring', help="View which files Gud is currently set to ignore")

stage_subparser = subparsers.add_parser('stage', help="Add or remove file(s) to or from the staging area")
add_or_remove = stage_subparser.add_argument('add_or_remove', nargs="?", choices=["add", "remove"], help="Add or remove from the staging area")
# file_names is a list of zero or more files
file_paths = stage_subparser.add_argument("file_paths", nargs="*", help="A specified file or directory to add/remove to/from the staging area")

commit_subparser = subparsers.add_parser('commit', help="Commit staged files to the repository's history")

status_subparser = subparsers.add_parser('status', help="View all staged and unstaged files")

log_subparser = subparsers.add_parser('log', help="View the commit history")
log_subparser.add_argument("short", nargs="?", choices=["short"], help="Show less information about each commit")

branch_subparser = subparsers.add_parser('branch', help="View existing branches, rename a branch, create a new branch or delete a branch")
view_or_rename_or_create_or_delete = branch_subparser.add_argument(
    'view_or_rename_or_create_or_delete', nargs="?", choices=["view", "rename", "create", "delete"], help="Choose to view, rename, create or delete a branch"
)

checkout_subparser = subparsers.add_parser('checkout', help="View a specific commit or branch")
branch_or_hash = checkout_subparser.add_mutually_exclusive_group(required=False)
branch_or_hash.add_argument("--branch", help="Choose a branch to checkout to")
branch_or_hash.add_argument("--hash", help="Choose a commit hash to checkout to")

restore_subparser = subparsers.add_parser("restore", help="Restore a file back to its state at the HEAD commit")
file_path = restore_subparser.add_argument("file_path", nargs=1, help="A specified file to restore")


def main():
    
    all_args = parser.parse_args(sys.argv[1:])
    cwd = os.getcwd()

    if all_args.command == "hello":
        hello()
        return
    elif all_args.command == "loadexample":
        load_example(cwd)
        return

    invocation = CommandInvocation(all_args, cwd)

    match invocation.command:
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
        case "restore":
            restore(invocation)

    # some commands break if the user isn't in the root directory - so this is a warning to them
    if invocation.command != "init":
        if cwd != invocation.repo.root:
            cwd_parts, root_parts = cwd.split(os.sep), invocation.repo.root.split(os.sep)
            dirs_difference = len(cwd_parts) - len(root_parts)
            cd_helper_str = ".." + "/.." * (dirs_difference - 1)
            print(f"You are not currently in the root of your repository.\nUse the command\ncd {cd_helper_str}\nto return to the root, before continuing.")


if __name__ == "__main__":
    main()