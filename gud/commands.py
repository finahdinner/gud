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
    # make .gud directory
    # TODO - only make the .gud folder (with its contents) once the user has gone through all the questions
    try:
        os.makedirs(".gud", exist_ok=False)
    except FileExistsError:
        sys.exit(f"Repository {cwd}/.gud already exists")
    # create a config file in .gud
    with open(".gud/config", "w", encoding="utf-8") as f:
        # Define the questions and prompt the user
        autosave = questionary.confirm(
            "Would you like autosave?"
        ).ask()
        
    print(f"Initialising Gud repository in {cwd}/.gud")