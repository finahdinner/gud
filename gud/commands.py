"""
All of these are commands that will ultimately be used as `gud <command_name>`
"""
import sys
import questionary
from configparser import ConfigParser

from .helpers import (
    is_valid_username,
    is_valid_email
)


def hello(invocation):
    name = invocation.args.get("name")
    if name:
        print(f"Hello {name}!")
    else:
        print("Hello there.")


def init(invocation):
    
    if invocation.args["global_config"]:

        repo_config = invocation.repo.copy_global_to_repo_config()
        print("--global-config flag provided: using global config options...")

    else:

        repo_config = ConfigParser()
        repo_config.add_section("user")
        repo_config.add_section("repo")

        experience_level = questionary.select(
            "What is your level of experience with Git, Gud or other similar"
            " version control softwares?",
            ["Beginner", "Intermediate", "Advanced"]
        ).ask()
        repo_config["repo"]["experience_level"] = experience_level.lower()

        username_prompt = "Username? (must be between 1 and 16 characters)"
        while True:
            username = questionary.text(username_prompt).ask()
            if is_valid_username(username):
                break
            else:
                username_prompt = "Invalid username, please try another (must be between 1 and 16 characters):"
        repo_config["user"]["name"] = username

        email_prompt = "Email address?"
        while True:
            email_address = questionary.text(email_prompt).ask()
            if is_valid_email(email_address):
                break
            else:
                email_prompt = "Invalid email address, please try another:"
        repo_config["user"]["email"] = email_address
    
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
            ["Repository", "global"]
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
        config_path = invocation.repo.global_repo.path
    else: # else "repository"
        config_path = invocation.repo.repo_config.path

    if view_or_edit == "edit":
        print("Editing...") # TODO - implement a way to edit
    else:
        print(f"{repo_or_global.capitalize()} config options ({config_path}):\n")
        with open(config_path, "r", encoding="utf-8") as f:
            print(f.read())
