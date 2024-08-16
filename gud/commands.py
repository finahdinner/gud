"""
All of these are commands that will ultimately be used as `gud <command_name>`
"""
import sys
import questionary
import shutil
from configparser import ConfigParser
from .helpers import (
    is_valid_username,
    is_valid_email,
    open_relevant_editor,
    get_default_file_from_package_installation,
    parse_gudignore_in_dir,
    get_all_ignored_files,
    format_path_for_gudignore
)
from .classes import (
    Blob,
    PathValidatorQuestionary
)
import os


def test(invocation):
    print("This is a test command!")
    import os
    file_path = os.path.join("/home/hanif/gud", "notes.txt")
    my_blob = Blob(invocation.repo)
    file_hash = my_blob.serialise(file_path, write_to_file=True)
    print(file_hash)
    file_contents = my_blob.deserialise(file_hash)
    print(file_contents)
    

def hello(invocation):
    name = invocation.args.get("name")
    if name:
        print(f"Hello {name}!")
    else:
        print("Hello there.")


def init(invocation):

    global_config = invocation.repo.global_config.get_config()

    if invocation.args["is_default"]:

        invocation.repo.create_repo()
        repo_config = invocation.repo.copy_global_to_repo_config()
        print("'default' flag provided: using global config options...")

    else:

        repo_config = ConfigParser()
        repo_config.add_section("user")
        repo_config.add_section("repo")

        username_prompt = f"Username? (leave blank to use {global_config['user']['name']}):"
        while True:
            username = questionary.text(username_prompt).ask()
            if not username: # default to global username
                username = invocation.repo.global_config.get_config()["user"]["name"]
                break
            if is_valid_username(username):
                break
            else:
                username_prompt = "Invalid username, please try another (must be between 1 and 16 characters):"
        repo_config["user"]["name"] = username

        email_prompt = f"Email address? (leave blank to use {global_config['user']['email']}):"
        while True:
            email_address = questionary.text(email_prompt).ask()
            if not email_address: # default to global email address
                email_address = invocation.repo.global_config.get_config()["user"]["email"]
                break
            if is_valid_email(email_address):
                break
            else:
                email_prompt = "Invalid email address, please try another:"
        repo_config["user"]["email"] = email_address

        gudignore_prompt = "Are there any files or folders you do not want Gud to track?"
        answer = questionary.select(gudignore_prompt, ["No", "Yes"]).ask()
        if answer.lower() == "yes":
            paths_to_ignore = set()
            while True: # loop for selecting multiple files
                if paths_to_ignore:
                    print("Files/directories that will be ignored:")
                    for path in paths_to_ignore:
                        print(path)
                path = questionary.path(
                    f"Search for a file/directory to for Gud to ignore (enter blank when finished):",
                    validate=PathValidatorQuestionary()
                ).ask()
                if path == "":
                    break
                paths_to_ignore.add(format_path_for_gudignore(path))
            # create and save the .gudignore file, including comments from the default gudignore file in the installation
            default_gudignore_file = get_default_file_from_package_installation("gudignore")
            if not default_gudignore_file:
                raise Exception("Default gudignore file not found - possibly corrupted installation.")
            repo_gudignore_path = os.path.join(invocation.repo.root, ".gudignore")
            with open(default_gudignore_file, "r", encoding="utf-8") as default_file:
                default_comments = [line for line in default_file.readlines() if line.strip()]
                with open(repo_gudignore_path, "w", encoding="utf-8") as repo_file:
                    repo_file.writelines(default_comments)
                    repo_file.write("\n")
                    repo_file.writelines([f"{path}\n" for path in paths_to_ignore])
            print("Note: If you wish to change which files Gud ignores, modify and save the .gudignore file at any time.")

        invocation.repo.create_repo()
        invocation.repo.repo_config.set_config(repo_config)

    print(f"Initialised Gud repository in {invocation.repo.path}")


def config(invocation):

    view_or_edit = invocation.args["view_or_edit"]
    repo_or_global = invocation.args["repo_or_global"]

    # if "repo" is passed, convert to more verbose version for later
    if repo_or_global == "repo":
        repo_or_global = "repository"

    if not view_or_edit:
        view_or_edit = questionary.select(
            "Would you like to view or edit a config file?",
            ["View", "Edit"]
        ).ask().lower()

    if not repo_or_global:
        repo_or_global = questionary.select(
            f"Would you like to {view_or_edit} this repository's configuration settings, or the global configuration settings?",
            ["Repository", "Global"]
        ).ask().lower()

    if repo_or_global == "global":
        config_path = invocation.repo.global_config.path
    else:
        config_path = invocation.repo.repo_config.path

    if view_or_edit == "edit":
        print(f"Opening {config_path}...\nClose editor to continue...")
        open_relevant_editor(invocation.os, config_path)
    else:
        print(f"{repo_or_global.capitalize()} config options ({config_path}):\n")
        with open(config_path, "r", encoding="utf-8") as f:
            print(f.read())


def ignoring(invocation) -> None:
    """
    Show all files in this repository that Gud is set to ignore
    Find all .gudignore files, and print them out in stdout
    Make sure to label each file above its contents, and make it clear/well-formatted
    """
    repo_root = invocation.repo.root
    all_ignored_file_paths = get_all_ignored_files(repo_root)
    if not all_ignored_file_paths:
        print(f"No files/folders are being ignored in this repository ({invocation.repo.path})")
    else:
        print(f"Gud is ignoring the following files/folders in this repository ({invocation.repo.path}):\n")
        for file_path in sorted(all_ignored_file_paths):
            print(file_path)


def stage(invocation):

    action = invocation.args.get("add_or_remove", None)
    paths_specified = set(invocation.args.get("file_paths", []))

    if not action:
        action = questionary.select(
            "Would you like to add files to, or remove files from, the staging area?",
            ["Add", "Remove"]
        ).ask().lower()
    connective = "removed from" if action == "remove" else "added to"

    if not paths_specified:
        # TODO - implement a function to filter the paths, and pass it as the file_filter argument in questionary.path
        # the filter should probably not include files that are being tracked and haven't been modified since the last commit
        while True: # loop for selecting multiple files
            path = questionary.path(
                f"Search for a file/directory to be {connective} the staging area (enter blank when finished):",
                validate=PathValidatorQuestionary()
            ).ask()
            if path == "":
                break
            # check if the path exists within the repository
            abs_path = os.path.abspath(path)
            rel_path = os.path.relpath(path, invocation.repo.root) # relative to the repo root
            if os.path.commonprefix([abs_path, invocation.repo.root]) != invocation.repo.root:
                print(f"Path {path} does not exist within the repository, so cannot be {connective} the staging area")
                continue
            paths_specified.add(rel_path) # store the rel path
            print(f"Files/directories to be {connective} the staging area:")
            for path in paths_specified:
                print(path)

    if action == "add":
        abs_paths = []
        for rel_path in paths_specified:
            abs_path = os.path.join(invocation.repo.root, rel_path)
            abs_paths.append(abs_path)
            print(abs_path)

    elif action == "remove":
        # TODO - remove from the staging area
        raise NotImplementedError("'Remove' has not been implemented yet.")


def status(invocation):
    """
    - hash all files in the working dir (except "ignored" ones) and compare to the current index (.gud/index)
    (which represents the latest "tree"), and match each file to a file in the index
    - if a file is in the working dir but not the index, label as "untracked"
    - if a file is in the working dir AND index, but they do not match hashes/permissons, label as "changed"
    - if a file is in the working dir AND index, and is indentical, do not list/label it
    - additionally, 
    """
    # parse the index to get the latest virtual "tree"
    repo_root = invocation.repo.root
    indexed_files = invocation.repo.parse_index()

    # TODO - finish all these below
    changed_files = {}
    untracked_files = {}

    all_ignored_file_paths = get_all_ignored_files(repo_root)
    for root, subdirs, files in os.walk(repo_root):
        for file_path in files:
            full_path = os.path.join(root, file_path)
            # check if the file is ignored
            if full_path in all_ignored_file_paths:
                continue
            # check if the file is in the index
            rel_path = os.path.relpath(full_path, repo_root) # path relative to root of the repo
            indexed_file = indexed_files(rel_path, None)
            if not indexed_file:
                # TODO - implement
                ...
            else:
                # check file permissions and hash the file, and see if either of those have changed
                ...
