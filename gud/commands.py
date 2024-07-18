"""
All of these are commands that will ultimately be used as `gud <command_name>`
"""
import os
import sys
import questionary

from .helpers import is_valid_username, is_valid_email


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
            " version control software?",
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

    if not (invocation.args["view"] or invocation.args["edit"]):

        # if the --default flag is passed, but neither --view nor --edit is specified, this is invalid usage
        if invocation.args["default"]:
            sys.exit("Since you provided a --default flag, you must also provide either a --view or --edit flag.")

        # otherwise, this means no flags were provided
        # therefore, take them through a questionary prompt
        print("You provided no flags!")

    else:

        print("You provided flags!")
    
    print(invocation.args)