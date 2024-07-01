"""
All of these are commands that will ultimately be used as `gud <command_name>`
"""
import os
import sys

executed_from = os.getcwd()

def hello():
    print("Hello there.")

def init():
    try:
        os.makedirs(".gud", exist_ok=False)
    except FileExistsError:
        sys.exit(f"Repository {executed_from}/.gud already exists")
    print(f"Initialising Gud repository in {executed_from}/.gud")