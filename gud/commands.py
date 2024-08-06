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
    get_default_file_from_package_installation
)
from .classes import (
    Blob,
    Tree,
    Commit
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
    
    if invocation.args["global_config"]:

        invocation.repo.create_repo()
        repo_config = invocation.repo.copy_global_to_repo_config()
        print("--global-config flag provided: using global config options...")

    else:

        repo_config = ConfigParser()
        repo_config.add_section("user")
        repo_config.add_section("repo")

        username_prompt = f"Username? (leave blank to use default global username):"
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

        email_prompt = "Email address? (leave blank to use default global email address):"
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

        gudignore_prompt = "Do you want Gud to not track any files? (You can change this later)"
        answer = questionary.select(gudignore_prompt, ["No", "Yes"]).ask()
        if answer.lower() == "yes":
            default_gudignore_file = get_default_file_from_package_installation("gudignore")
            if not default_gudignore_file:
                raise Exception("Default gudignore file not found - possibly corrupted installation.")
            repo_gudignore_path = os.path.join(invocation.repo.root, ".gudignore")
            shutil.copyfile(default_gudignore_file, repo_gudignore_path)
            print(f"Opening {repo_gudignore_path}...\nClose editor to continue...")
            open_relevant_editor(invocation.os, repo_gudignore_path)

        invocation.repo.create_repo()
        invocation.repo.repo_config.set_config(repo_config)

    print(f"Initialised Gud repository in {invocation.repo.path}")


def config(invocation):

    # determine which modes the user wants
    if not invocation.args["view"] and not invocation.args["edit"]:
        # if the --global flag is passed, but neither --view nor --edit is specified, this is invalid usage
        if invocation.args["global"]:
            sys.exit("Since you provided a --global flag, you must also provide either a --view or --edit flag.")
        # otherwise, this means no flags were provided
        view_or_edit = questionary.select(
            "Would you like to view or edit a config file?",
            ["View", "Edit"]
        ).ask().lower()
        repo_or_global = questionary.select(
            f"Would you like to {view_or_edit} this repository's configuration settings, or the global configuration settings?",
            ["Repository", "Global"]
        ).ask().lower()
    else:
        if invocation.args["edit"]:
            view_or_edit = "edit"
        else:
            view_or_edit = "view"
        if invocation.args["global"]:
            repo_or_global = "global"
        else:
            repo_or_global = "repository"

    # execute the command based on the modes determined above
    if repo_or_global == "global":
        config_path = invocation.repo.global_config.path
    else: # else "repository"
        config_path = invocation.repo.repo_config.path

    if view_or_edit == "edit":
        print(f"Opening {config_path}...\nClose editor to continue...")
        open_relevant_editor(invocation.os, config_path)
    else:
        print(f"{repo_or_global.capitalize()} config options ({config_path}):\n")
        with open(config_path, "r", encoding="utf-8") as f:
            print(f.read())


def ignoring(invocation):
    """
    Show all files in this repository that Gud is set to ignore
    Find all .gudignore files, and print them out in stdout
    Make sure to label each file above its contents, and make it clear/well-formatted
    """
    # TODO - implement
    ...


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
    indexed_files = invocation.repo.index
    ignored_files = invocation.repo.ignored_files
    # reaching every file
    num_files = 0
    for root, subdirs, files in os.walk(repo_root):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, repo_root) # path relative to root of the repo

            if rel_path not in ignored_files:
                indexed_file = indexed_files(rel_path, None)
                if indexed_file:
                    ...
            else: # untracked files
                ...




            print(rel_path)
            num_files += 1
    print(f"{num_files=}")


def stage(invocation):

    action = invocation.args.get("add_or_remove", None)
    if not action:
        action = questionary.select(
            "Would you like to add files to, or remove files from, the staging area?",
            ["Add", "Remove"]
        ).ask().lower()

    if action == "add":
        files_to_add = []
        files_not_staged = [] # TODO - generate a list of files that are NOT in the staging area
        while True:
            file = questionary.select(
                "Select a file to add to the staging area",
                files_not_staged
            ).ask().lower()
            # TODO - add a way to allow the user to break the loop
            if not file.strip():
                break
            files_to_add.append(file)
        # TODO - with these files_to_add, add them all to the staging area here

    elif action == "remove":

        files_to_remove = []
        files_that_are_staged = [] # TODO - generate a list of files that are NOT in the staging area
        while True:
            file = questionary.select(
                "Select a file to add to the staging area",
                files_that_are_staged
            ).ask().lower()
            # TODO - add a way to allow the user to break the loop
            if not file.strip():
                break
            files_to_remove.append(file)
        # TODO - with these files_to_remove, remove them all to the staging area here
