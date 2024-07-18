import argparse
import sys
import os
from .classes import CommandInvocation
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
init_subparser.add_argument("--skip", "-s", action="store_true", help="Skip the interactive prompt and use default values")


def main():
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