import argparse
from argparse import Namespace
import sys
import os
from .commands import (
    init,
    hello,
)

parser = argparse.ArgumentParser(
    description="Functionality for parsing Gud commands.",
)
subparsers = parser.add_subparsers(title="commands", dest="command")
subparsers.required = True

# list of all Gud commands that the user can provide
hello_subparser = subparsers.add_parser('hello', help='Say hello') # remove this afterwards
hello_subparser.add_argument("name", nargs="?", help="Name to greet")

init_subparser = subparsers.add_parser('init', help='Initialise repository')


class CommandInvocation:
    def __init__(self, all_args: Namespace, cwd: str):
        self.command: Namespace = all_args.command
        self.args: Namespace = __class__.get_additional_commands(all_args)
        self.cwd = cwd

    @staticmethod
    def get_additional_commands(args: Namespace) -> Namespace:
        args_dict = vars(args)
        args_dict.pop("command", None)
        return Namespace(**args_dict)


def main():
    # parse the args
    all_args = parser.parse_args(sys.argv[1:])
    cwd = os.getcwd()
    invocation = CommandInvocation(all_args, cwd)

    match invocation.command:
        case "hello":
            hello(invocation)
        case "init":
            init(invocation)


if __name__ == "__main__":
    main()