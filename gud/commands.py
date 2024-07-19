"""
All of these are commands that will ultimately be used as `gud <command_name>`
"""
import os
import sys
import questionary

from .helpers import (
    is_valid_username,
    is_valid_email
)
from .config import get_default_config_file_path


def hello(invocation):
    name = invocation.args.get("name")
    if name:
        print(f"Hello {name}!")
    else:
        print("Hello there.")


def init(invocation):
    
    if invocation.args["skip"]:

        config_options = invocation.repo.get_default_config_options()
        print("--skip flag provided: selecting default config options...")

    else:
        config_options = {
            "user": {},
            "repo": {}
        }

        experience_level = questionary.select(
            "What is your level of experience with Git, Gud or other similar"
            " version control softwares?",
            ["Beginner", "Intermediate", "Advanced"]
        ).ask()
        config_options["repo"]["experience_level"] = experience_level.lower()

        username_prompt = "Username? (must be between 1 and 16 characters)"
        while True:
            username = questionary.text(username_prompt).ask()
            if is_valid_username(username):
                break
            else:
                username_prompt = "Invalid username, please try another (must be between 1 and 16 characters):"
        config_options["user"]["name"] = username

        email_prompt = "Email address?"
        while True:
            email_address = questionary.text(email_prompt).ask()
            if is_valid_email(email_address):
                break
            else:
                email_prompt = "Invalid email address, please try another:"
        config_options["user"]["email"] = email_address
    
    invocation.repo.create_repo()
    invocation.repo.set_config(config_options)
    print(f"Initialised Gud repository in {invocation.repo.path}")


def config(invocation):

    # determine which modes the user wants
    if not invocation.args["view"] and not invocation.args["edit"]:
        # if the --default flag is passed, but neither --view nor --edit is specified, this is invalid usage
        if invocation.args["default"]:
            sys.exit("Since you provided a --default flag, you must also provide either a --view or --edit flag.")
        # otherwise, this means no flags were provided
        view_or_edit = questionary.select(
            "Would you like to view or edit a config file?",
            ["View", "Edit"]
        ).ask().lower()
        repo_or_default = questionary.select(
            f"Would you like to {view_or_edit} this repository's configuration settings, or the global default configuration settings?",
            ["Repository", "Default"]
        ).ask().lower()
    else:
        if invocation.args["edit"]:
            view_or_edit = "edit"
        else:
            view_or_edit = "view"
        if invocation.args["default"]:
            repo_or_default = "default"
        else:
            repo_or_default = "repository"

    # execute the command based on the modes determined above
    if repo_or_default == "default":
        config_path = invocation.repo.config_path # TODO - change this to wherever the defaults will get stored
        heading_string = "Default config options:"
    else: # else "repository"
        config_path = invocation.repo.config_path
        heading_string = f"Repository config options ({config_path}):"

    if view_or_edit == "edit":
        config_path = get_default_config_file_path()
        print("Default config path: ", config_path)
    else:
        print(heading_string, "\n")
        with open(config_path, "r", encoding="utf-8") as f:
            print(f.read())
