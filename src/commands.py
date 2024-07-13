"""
All of these are commands that will ultimately be used as `gud <command_name>`
"""
import os
import sys
import questionary

executed_from = os.getcwd()

def hello():
    print("Hello there.")

def init():
    # make .gud directory
    try:
        os.makedirs(".gud", exist_ok=False)
    except FileExistsError:
        sys.exit(f"Repository {executed_from}/.gud already exists")
    # create a config file in .gud
    with open(".gud/config", "w", encoding="utf-8") as f:
        # Define the questions and prompt the user
        autosave = questionary.confirm(
            "Would you like autosave?"
        ).ask()
        



    print(f"Initialising Gud repository in {executed_from}/.gud")