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
    if not invocation.repo.path:
        raise Exception("Repository not created.")
    
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