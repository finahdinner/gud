"""
All of these are commands that will ultimately be used as `gud <command_name>`
"""
import questionary
from configparser import ConfigParser
from .helpers import (
    is_valid_username,
    is_valid_email,
    open_relevant_editor,
    get_default_file_from_package_installation,
    get_all_ignored_paths,
    format_path_for_gudignore,
    get_file_mode
)
from .classes import (
    Blob,
    Tree,
    Commit,
    PathValidatorQuestionary,
    TextValidatorQuestionaryNotEmpty
)
import os
from copy import deepcopy


def test(invocation):
    print("This is a test command!")
    tree = Tree(invocation.repo)
    tree.serialise()
    

def hello(invocation):
    name = invocation.args.get("name")
    if name:
        print(f"Hello {name}!")
    else:
        print("Hello there.")


def init(invocation):

    global_config = invocation.repo.global_config.get_config()

    if invocation.args["is_default"]:

        invocation.repo.create_repo()
        repo_config = invocation.repo.copy_global_to_repo_config()
        print("'default' flag provided: using global config options...")

    else:

        repo_config = ConfigParser()
        repo_config.add_section("user")
        repo_config.add_section("repo")

        username_prompt = f"Username? (leave blank to use {global_config['user']['name']}):"
        while True:
            username = questionary.text(username_prompt).ask()
            if not username: # default to global username
                username = invocation.repo.global_config.get_config()["user"]["name"]
                break
            if is_valid_username(username):
                break
            else:
                username_prompt = "Invalid username, please try another (must be between 1 and 16 characters):"
        repo_config["user"]["name"] = username

        email_prompt = f"Email address? (leave blank to use {global_config['user']['email']}):"
        while True:
            email_address = questionary.text(email_prompt).ask()
            if not email_address: # default to global email address
                email_address = invocation.repo.global_config.get_config()["user"]["email"]
                break
            if is_valid_email(email_address):
                break
            else:
                email_prompt = "Invalid email address, please try another:"
        repo_config["user"]["email"] = email_address

        gudignore_prompt = "Are there any files or folders you do not want Gud to track?"
        answer = questionary.select(gudignore_prompt, ["No", "Yes"]).ask()
        if answer.lower() == "yes":
            paths_to_ignore = set()
            while True: # loop for selecting multiple files
                if paths_to_ignore:
                    print("Files/directories that will be ignored:")
                    for path in paths_to_ignore:
                        print(path)
                path = questionary.path(
                    f"Search for a file/directory to for Gud to ignore (enter blank when finished):",
                    validate=PathValidatorQuestionary()
                ).ask()
                if path == "":
                    break
                paths_to_ignore.add(format_path_for_gudignore(path))
            # create and save the .gudignore file, including comments from the default gudignore file in the installation
            default_gudignore_file = get_default_file_from_package_installation("gudignore")
            if not default_gudignore_file:
                raise Exception("Default gudignore file not found - possibly corrupted installation.")
            repo_gudignore_path = os.path.join(invocation.repo.root, ".gudignore")
            with open(default_gudignore_file, "r", encoding="utf-8") as default_file:
                default_comments = [line for line in default_file.readlines() if line.strip()]
                with open(repo_gudignore_path, "w", encoding="utf-8") as repo_file:
                    repo_file.writelines(default_comments)
                    repo_file.write("\n")
                    repo_file.writelines([f"{path}\n" for path in paths_to_ignore])
            print("Note: If you wish to change which files Gud ignores, modify and save the .gudignore file at any time.")

        invocation.repo.create_repo()
        invocation.repo.repo_config.set_config(repo_config)

    print(f"Initialised Gud repository in {invocation.repo.path}")


def config(invocation):

    view_or_edit = invocation.args["view_or_edit"]
    repo_or_global = invocation.args["repo_or_global"]

    # if "repo" is passed, convert to more verbose version for later
    if repo_or_global == "repo":
        repo_or_global = "repository"

    if not view_or_edit:
        view_or_edit = questionary.select(
            "Would you like to view or edit a config file?",
            ["View", "Edit"]
        ).ask().lower()

    if not repo_or_global:
        repo_or_global = questionary.select(
            f"Would you like to {view_or_edit} this repository's configuration settings, or the global configuration settings?",
            ["Repository", "Global"]
        ).ask().lower()

    if repo_or_global == "global":
        config_path = invocation.repo.global_config.path
    else:
        config_path = invocation.repo.repo_config.path

    if view_or_edit == "edit":
        print(f"Opening {config_path}...\nClose editor to continue...")
        open_relevant_editor(invocation.os, config_path)
    else:
        print(f"{repo_or_global.capitalize()} config options ({config_path}):\n")
        with open(config_path, "r", encoding="utf-8") as f:
            print(f.read())


def ignoring(invocation, include_gud_folder=False) -> set:
    """
    Show all files in this repository that Gud is set to ignore
    Find all .gudignore files, and print them out in stdout
    Make sure to label each file above its contents, and make it clear/well-formatted
    """
    repo_root = invocation.repo.root
    all_ignored_file_paths = get_all_ignored_paths(repo_root)
    if include_gud_folder:
        all_ignored_file_paths.add(format_path_for_gudignore(invocation.repo.path))
    if not all_ignored_file_paths:
        print(f"No files/folders are being ignored in this repository ({invocation.repo.path})")
    else:
        print(f"Gud is ignoring the following files/folders in this repository ({invocation.repo.path}):\n")
        for file_path in sorted(all_ignored_file_paths):
            print(file_path)
    return all_ignored_file_paths # return value for if another command calls this


def stage(invocation):

    action = invocation.args.get("add_or_remove", None)
    paths_specified = set(invocation.args.get("file_paths", []))

    if not action:
        action = questionary.select(
            "Would you like to add files to, or remove files from, the staging area?",
            ["Add", "Remove"]
        ).ask().lower()
    connective = "removed from" if action == "remove" else "added to"

    if not paths_specified:
        # TODO - implement a function to filter the paths, and pass it as the file_filter argument in questionary.path
        # the filter should probably not include files that are being tracked and haven't been modified since the last commit
        while True: # loop for selecting multiple files
            path = questionary.path(
                f"Search for a file/directory to be {connective} the staging area (enter blank when finished):",
                validate=PathValidatorQuestionary()
            ).ask()
            if path == "":
                break
            # check if the path exists within the repository
            abs_path = os.path.abspath(os.path.expanduser(path)) # expanduser expands the ~
            if os.path.commonprefix([abs_path, invocation.repo.root]) != invocation.repo.root:
                print(f"Path {path} does not exist within the repository, so cannot be {connective} the staging area")
                continue
            paths_specified.add(abs_path) # store the rel path
            # TODO - instead of the below, call gud status (once implemented) between each file selection
            print(f"Files/directories to be {connective} the staging area:")
            for path in paths_specified:
                print(path)

    # convert all paths to rel_paths - this is how they will be stored in the index
    rel_paths_specified = [os.path.relpath(path, invocation.repo.root) for path in paths_specified]

    if action == "add":
        index = invocation.repo.parse_index()
        for rel_path in rel_paths_specified:
            abs_path = os.path.join(invocation.repo.root, rel_path)
            if os.path.isfile(abs_path): # blob
                blob = Blob(repo=invocation.repo)
                file_hash = blob.serialise(abs_path, write_to_file=True)
                file_mode = get_file_mode(abs_path)
                index[rel_path] = {
                    "type": "blob",
                    "mode": file_mode,
                    "hash": file_hash
                }
            elif os.path.isdir(abs_path): # tree
                raise NotImplementedError("Adding directories has not been implemented yet")
        invocation.repo.write_to_index(index)

    elif action == "remove":
        # TODO - remove from the staging area
        # if a file is 'removed' from the staging area, this just means to replace its line in
        # the index with the file info from the last commit
        # if the file didn't exist in the last commit, the line in index will be removed
        # if it did exist in the last commit, the line will just be modified to reflect
        # the version of the file as it was at the last commit
        index = invocation.repo.parse_index()
        latest_commit = invocation.repo.head
        raise NotImplementedError("'Remove' has not been implemented yet.")


def commit(invocation):
    # TODO - initially run gud status to confirm that there ARE changes to be committed

    # create the tree object(s), using the current index
    tree = Tree(invocation.repo)
    tree_hash = tree.serialise()
    print(f"{tree_hash=}")

    #
    commit_message = questionary.text(
        "What changes does this commit represent?",
        validate=TextValidatorQuestionaryNotEmpty()
    ).ask()
    print(f"{commit_message=}")   

    commit = Commit(
        repo=invocation.repo,
        tree_hash=tree_hash,
        commit_message=commit_message.strip(),
        timestamp=invocation.timestamp
    )
    commit_hash = commit.serialise()
    print(f"{commit_hash=}")

    # update the reference to head
    heads_path = os.path.join(invocation.repo.path, "heads", invocation.repo.branch)
    with open(heads_path, "w", encoding="utf-8") as f:
        f.write(commit_hash)

    # FOR TESTING
    commit_contents = commit.get_content(commit_hash).decode()
    print(commit_contents)
    

def status(invocation):
    # build a path_tree
    tree = Tree(invocation.repo)
    path_tree = tree._build_path_tree()
    print(path_tree)

    # find all ignored files
    ignored_paths = ignoring(invocation, include_gud_folder=True)
    print(ignored_paths)

    untracked_files = set()
    tracked_unchanged_files = set()
    tracked_changed_files = set()

    # get all files in the working directory
    repo_root = invocation.repo.root
    print("Checking all working dir files...")
    for root, subdirs, files in os.walk(repo_root):
        root_formatted = format_path_for_gudignore(root)
        # stop traversing any directory that is listed in gudignore
        if root_formatted in ignored_paths:
            # print(f"IGNORING: {root_formatted}")
            subdirs[:] = [] # prevents traversal of 
            continue
        for file in files:
            full_path = os.path.join(root, file)
            full_path_formatted = format_path_for_gudignore(full_path)
            # if any of the ignored paths is a prefix to the current path, ignore the current path
            if any(full_path_formatted.startswith(ignored_path) for ignored_path in ignored_paths):
                print(f"IGORNING: {full_path_formatted}")
                continue
            # TODO - traverse the path_tree for any file that isn't ignored
            rel_path = os.path.relpath(full_path, invocation.repo.root)
            path_parts = rel_path.split("/")
            # print(path_parts)

            tracked = True
            subtree = deepcopy(path_tree)
            prefix_parts = []
            suffix_parts = path_parts[:]
            while suffix_parts:
                prefix_parts.append(suffix_parts[0])
                suffix_parts = suffix_parts[1:]
                next_lookup: str = prefix_parts[-1]
                subtree = subtree.get(next_lookup, None)
                if subtree is None: # untracked file/dir
                    # using untracked path like this ensures that it only lists the
                    # shallowest untracked directory, rather than listing the entire contents
                    # as untracked
                    untracked_path = os.path.join(*prefix_parts)
                    if os.path.isdir(untracked_path):
                        untracked_path += os.sep
                    untracked_files.add(untracked_path)
                    tracked = False
                    break
                elif isinstance(subtree, list): # tracked FILE
                    # TODO - compare the file's stored has to a new, computed hash for the file
                    # print(subdir)
                    break
                # else, it's a tracked subtree and the loop continues
            if tracked:
                print(f"{rel_path} is tracked!")

    print(untracked_files)

                
                # next_part = path_parts.pop(0)
                # subdir = path_tree.get(next_part, None)
                # if not subdir: # untracked file
                #     untracked_files.add(subdir)
                #     break
                # print(subdir)
            # at this point, you have reached a specific file that IS being tracked
            # tracked_files.add([])
            # print(path_parts)



    # # parse the index to get the latest virtual "tree"
    # repo_root = invocation.repo.root
    # indexed_files = invocation.repo.parse_index()

    # # TODO - finish all these below
    # changed_files = {}
    # untracked_files = {}

    # all_ignored_file_paths = get_all_ignored_paths(repo_root)
    # for root, subdirs, files in os.walk(repo_root):
    #     for file_path in files:
    #         full_path = os.path.join(root, file_path)
    #         # check if the file is ignored
    #         if full_path in all_ignored_file_paths:
    #             continue
    #         # check if the file is in the index
    #         rel_path = os.path.relpath(full_path, repo_root) # path relative to root of the repo
    #         indexed_file = indexed_files(rel_path, None)
    #         if not indexed_file:
    #             # TODO - implement
    #             ...
    #         else:
    #             # check file permissions and hash the file, and see if either of those have changed
    #             ...
