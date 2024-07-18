"""
All of these are commands that will ultimately be used as `gud <command_name>`
"""
import os
import sys
import questionary




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
    username = questionary.text(
        "Username?"
    ).ask()
    config_options["user"]["name"] = username
    email_address = questionary.text(
        "Email address?"
    ).ask()
    config_options["user"]["email"] = email_address
    # TODO - check email and username validity
    invocation.repo.create_repo()
    invocation.repo.set_config(config_options)
    print(f"Initialised Gud repository in {invocation.repo.path}")