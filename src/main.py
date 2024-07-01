import argparse
import sys

parser = argparse.ArgumentParser(
    description="Functionality for parsing Gud commands.",
)
subparsers = parser.add_subparsers(title="commands", dest="command")
subparsers.required = True

# list of all Gud commands that the user can provide
hello_subparser = subparsers.add_parser('hello', help='Say hello') # remove this afterwards
init_subparser = subparsers.add_parser('init', help='Initialise repository')

# parse the args
args = parser.parse_args(sys.argv[1:])

print("{__file__} is running!")
match args.command:
    case "hello":
        print("Hello there.")
    case "init":
        print("Initialising repository...")