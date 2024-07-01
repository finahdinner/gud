import argparse
import sys
from commands import (
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
init_subparser = subparsers.add_parser('init', help='Initialise repository')


def main():
    # parse the args
    args = parser.parse_args(sys.argv[1:])
    match args.command:
        case "hello":
            hello()
        case "init":
            init()


if __name__ == "__main__":
    main()