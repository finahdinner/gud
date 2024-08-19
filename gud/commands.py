"""
All of these are commands that will ultimately be used as `gud <command_name>`
"""
import questionary
from configparser import ConfigParser
from .helpers import (
    is_valid_username,
    is_valid_email,
    is_valid_branch_name,
    open_relevant_editor,
    get_default_file_from_package_installation,
    get_all_ignored_paths,
    format_path_for_gudignore,
    get_file_mode,
    see_if_command_exists,
    open_relevant_pager,
    print_red,
    print_green,
    print_dark_grey
)
from .classes import (
    Blob,
    Tree,
    Commit,
    Branch,
    PathValidatorQuestionary,
    TextValidatorQuestionaryNotEmpty,
    get_indexed_file_paths_that_may_not_exist
)
import os
import sys
import tempfile
from copy import deepcopy
from pathlib import Path


def hello():
    print("Hello! Gud is up and running on your computer!")
    print_green("Use the command `gud init` to create a repository here.")


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

        print("You will now be asked for your user credentials - feel free to provide whatever you like.\nThey are only used to label your commits.")
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

        print('You can tell Gud to "ignore" certain files and folders, so that they aren\'t tracked over time.')
        gudignore_prompt = "Are there any files or folders you want Gud to ignore?"
        answer = questionary.select(gudignore_prompt, ["No", "Yes"]).ask()
        if answer.lower() == "yes":
            paths_to_ignore = set()
            while True: # loop for selecting multiple files
                if paths_to_ignore:
                    print("Files/directories that will be ignored:")
                    for path in paths_to_ignore:
                        print(path)
                path = questionary.text(
                    f"Type in a file/directory path for Gud to ignore (enter blank when finished):"
                ).ask()
                if path is None:
                    return
                if path == "":
                    break
                paths_to_ignore.add(format_path_for_gudignore(path, check_if_dir=False))
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

    print_green(f"Initialised Gud repository in {invocation.repo.path}")


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


def ignoring(invocation, for_printing_to_user=True) -> set:
    """
    Show all files in this repository that Gud is set to ignore
    Find all .gudignore files, and print them out in stdout
    Make sure to label each file above its contents, and make it clear/well-formatted
    """
    repo_root = invocation.repo.root
    all_ignored_file_paths = get_all_ignored_paths(repo_root)        
    if for_printing_to_user:
        if not all_ignored_file_paths:
            print(f"No files/folders are being ignored in this repository ({invocation.repo.path})")
        else:
            print(f"Gud is ignoring the following files/folders in this repository ({invocation.repo.path}):\n")
            for file_path in sorted(all_ignored_file_paths):
                print(file_path)
    else:
        all_ignored_file_paths.add(format_path_for_gudignore(invocation.repo.path))
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
                print_red(f"Path {path} does not exist within the repository, so cannot be {connective} the staging area")
                continue
            paths_specified.add(abs_path) # store the rel path
            print(f"Files/directories to be {connective} the staging area:")
            for path in paths_specified:
                print(path)

    # convert all paths to rel_paths - this is how they will be stored in the index
    rel_paths_specified = [os.path.relpath(path, invocation.repo.root) for path in paths_specified]
    abs_paths_specified = [os.path.join(invocation.repo.root, path) for path in rel_paths_specified]

    # "expand" directories into their specific files
    for rel_path in rel_paths_specified:
        if os.path.isdir(rel_path):
            rel_paths_specified.remove(rel_path) # remove the directory path
            for file in os.listdir(rel_path):
                rel_file_path = os.path.join(rel_path, file)
                rel_paths_specified.append(rel_file_path)

    # prevent users from staging the .gud directory, or anything within it
    repo_path_obj = Path(invocation.repo.path)
    if any(Path(path).is_relative_to(repo_path_obj) for path in abs_paths_specified):
        sys.exit("You cannot add anything in the `.gud` directory into the staging area!")

    index = invocation.repo.parse_index()

    # for when you are adding a "deleted" file to the staging area
    file_paths_that_may_not_exist = get_indexed_file_paths_that_may_not_exist()

    if action == "add":
        # this should only contain files now, not directories
        ignored_abs_paths = ignoring(invocation, for_printing_to_user=False)
        for abs_path in abs_paths_specified:
            for ignored_path in ignored_abs_paths:
                if ignored_path.endswith("/"): # directory
                    if abs_path.startswith(ignored_path):
                        sys.exit(f"{abs_path} is being ignored by Gud.\nPlease remove it from your `.gudignore` file(s) if you wish to stage it.")
                else:
                    if ignored_path == abs_path:
                        sys.exit(f"{abs_path} is being ignored by Gud.\nPlease remove it from your `.gudignore` file(s) if you wish to stage it.")

        for rel_path in rel_paths_specified:
            # handle if a file which was deleted, was added to the staging area
            if not os.path.exists(rel_path):
                if rel_path in file_paths_that_may_not_exist:
                    del index[rel_path]
                    continue
                else:
                    sys.exit(f"{rel_path} does not exist")
            abs_path = os.path.join(invocation.repo.root, rel_path)
            blob = Blob(repo=invocation.repo)
            file_hash = blob.serialise(abs_path, write_to_file=True)
            file_mode = get_file_mode(abs_path)
            index[rel_path] = {
                "type": "blob",
                "mode": file_mode,
                "hash": file_hash
            }

    elif action == "remove":
        commit = Commit(invocation.repo)
        tree = Tree(invocation.repo)
        # prioritise detached head
        head_commit_hash = invocation.repo.detached_head or invocation.repo.head
        head_index = tree.get_index_of_commit(commit_obj=commit, commit_hash=head_commit_hash)
        # revert the file(s) to their previous version, if it exists, else remove entirely from the index
        for rel_path in rel_paths_specified:
            previous_version_of_file = head_index.get(rel_path, None)
            if previous_version_of_file is None: # file didn't exist at the last commit
                del index[rel_path]
            else:
                index[rel_path] = previous_version_of_file
    
    invocation.repo.write_to_index(index)
    num_files_staged = len(rel_paths_specified)
    print(f"{num_files_staged} file{'s' if num_files_staged > 1 else ''} {connective} the staging area.\nUse `gud status` for more details.\nUse `gud commit` when ready to commit.")


def commit(invocation):
    file_changes = status(invocation, print_output=False)
    num_files_staged: int = file_changes["num_staged"]
    if num_files_staged == 0:
        sys.exit("You cannot commit, as there are no changes in the staging area.")

    if invocation.repo.detached_head: # this should ideally not be hit
        sys.exit("Please create a branch with `gud branch create`, before committing files.")

    # create the tree object(s), using the current index
    tree = Tree(invocation.repo)
    tree_hash = tree.serialise()

    commit_message = questionary.text(
        "What changes does this commit represent?",
        validate=TextValidatorQuestionaryNotEmpty()
    ).ask()

    commit = Commit(
        repo=invocation.repo,
        tree_hash=tree_hash,
        commit_message=commit_message.strip(),
        timestamp=invocation.timestamp
    )
    commit_hash = commit.serialise()

    # update the reference to head
    heads_path = os.path.join(invocation.repo.path, "heads", invocation.repo.branch)
    with open(heads_path, "w", encoding="utf-8") as f:
        f.write(commit_hash)

    print_green(f"Successfully committed {num_files_staged} file{'s' if num_files_staged > 1 else ''} on branch {invocation.repo.branch}.\nUse `gud log` to view commit history.")
    

def status(invocation, print_output=True) -> dict:
    """
    6 categories for files:

    staged_modified
    staged_deleted
    staged_added

    unstaged_modified
    unstaged_deleted
    unstaged_added
    """
    tree = Tree(invocation.repo)
    staged_index = tree.index

    """ Determine STAGED file differences (where index =/ last commit) """
    commit = Commit(invocation.repo)
    tree = Tree(invocation.repo)
    head_commit_hash = invocation.repo.detached_head or invocation.repo.head
    head_index = tree.get_index_of_commit(commit_obj=commit, commit_hash=head_commit_hash)

    # compare head_index to staged_index
    files_in_head_index = set(head_index)
    files_in_staged_index = set(staged_index)
    _staged_existing_files = files_in_head_index & files_in_staged_index
    staged_modified_files = set()
    for file_path in _staged_existing_files:
        # simple implementation to see if anything about the file has changed
        info_str_head = "".join(head_index[file_path].values())
        info_str_staged = "".join(staged_index[file_path].values())
        if info_str_head != info_str_staged: # modified file
            staged_modified_files.add(file_path)

    staged_deleted_files = files_in_head_index - files_in_staged_index
    staged_added_files = files_in_staged_index - files_in_head_index

    """ Determine UNSTAGED file differences (where working directory =/ index) """
    # build a path_tree for the current index

    all_path_parts = [path.split(os.sep) for path in staged_index.keys()]
    path_tree = tree._build_path_tree(all_path_parts)

    # find all ignored files (this is messy but seems to work like git?)
    ignored_abs_paths = ignoring(invocation, for_printing_to_user=False)
    abs_staged_index_without_ignored_files = set(os.path.join(invocation.repo.root, path) for path in staged_index.keys())
    for path in abs_staged_index_without_ignored_files.copy():
        for ignored_path in ignored_abs_paths:
            if ignored_path.endswith("/"): # directory
                if path.startswith(ignored_path):
                    abs_staged_index_without_ignored_files.remove(path)
            else:
                if ignored_path == path:
                    abs_staged_index_without_ignored_files.remove(path)
    rel_staged_index_without_ignored = set(
        os.path.relpath(path, invocation.repo.root) for path in abs_staged_index_without_ignored_files
    )

    unstaged_added_files = set()
    unstaged_modified_files = set()

    # get all files in the working directory
    working_dir_paths_traversed = set()
    repo_root = invocation.repo.root
    for root, subdirs, files in os.walk(repo_root):
        root_formatted = format_path_for_gudignore(root)
        # stop traversing any directory that is listed in gudignore
        if root_formatted in ignored_abs_paths:
            subdirs[:] = [] # prevents traversal of ignored directories
            continue
        for file in files:
            full_path = os.path.join(root, file)
            full_path_formatted = format_path_for_gudignore(full_path)
            # if any of the ignored paths is a prefix to the current path, ignore the current path
            if any(full_path_formatted.startswith(ignored_path) for ignored_path in ignored_abs_paths):
                continue

            rel_path = os.path.relpath(full_path, invocation.repo.root)
            working_dir_paths_traversed.add(rel_path)
            path_parts = rel_path.split("/")

            subtree = deepcopy(path_tree)
            prefix_parts = []
            suffix_parts = path_parts[:]
            while suffix_parts:
                prefix_parts.append(suffix_parts[0])
                suffix_parts = suffix_parts[1:]
                next_lookup: str = prefix_parts[-1]
                subtree = subtree.get(next_lookup, None)
                file_path_so_far = os.path.join(*prefix_parts)
                abs_file_path_so_far = os.path.join(invocation.repo.root, file_path_so_far)
                if subtree is None: # untracked file/dir
                    # using untracked path like this ensures that it only lists the
                    # shallowest untracked directory, rather than listing the entire contents
                    # as untracked
                    if os.path.isdir(abs_file_path_so_far):
                        file_path_so_far += os.sep # trailing slash if dir - is clearer in the output
                    unstaged_added_files.add(file_path_so_far)
                    break
                elif isinstance(subtree, list): # tracked FILE
                    old_mode = subtree[0]
                    old_hash = subtree[1]
                    blob = Blob(invocation.repo)
                    new_mode = get_file_mode(abs_file_path_so_far)
                    new_hash = blob.serialise(abs_file_path_so_far, write_to_file=False)
                    if old_mode != new_mode or old_hash != new_hash:
                        unstaged_modified_files.add(file_path_so_far)
                    break
                # else, it's a tracked subtree and the loop continues
    
    # checks which staged/indexed files were not traversed
    unstaged_deleted_files = rel_staged_index_without_ignored - working_dir_paths_traversed

    """ Print out everything we determined from this whole function """
    staged = {
        "modified": sorted(staged_modified_files),
        "added": sorted(staged_added_files),
        "deleted": sorted(staged_deleted_files)
    }

    unstaged = {
        "modified": sorted(unstaged_modified_files),
        "added": sorted(unstaged_added_files),
        "deleted": sorted(unstaged_deleted_files)
    }

    num_staged = sum(len(lst) for lst in staged.values())
    num_unstaged_modified = len(unstaged["modified"])

    if print_output:
        
        if invocation.repo.detached_head:
            print(f"** Currently checked out at commit {invocation.repo.detached_head[:7]} **")
        else:
            print(f"On branch {invocation.repo.branch}\n")

        # if both staged and unstaged are empty
        if not (any(staged.values()) or any(unstaged.values())):
            print("nothing to commit, working tree clean")

        else:

            if any(staged.values()):
                print("Changes to be committed:\n  Use `gud stage remove <file>` to remove a file from the staging area")
                for file_path in staged["modified"]:
                    print_green(f"\tmodified: {file_path}")
                for file_path in staged["deleted"]:
                    print_green(f"\tdeleted: {file_path}")
                for file_path in staged["added"]:
                    print_green(f"\tnew file: {file_path}")
                print()

            if unstaged["modified"] or unstaged["deleted"]:
                print("Changes not staged for commit:\n  Use `gud stage add <file>` to update a file in the staging area")
                for file_path in unstaged["modified"]:
                    print_red(f"\tmodified: {file_path}")
                for file_path in unstaged["deleted"]:
                    print_red(f"\tdeleted: {file_path}")
                print()

            if unstaged["added"]:
                print("Untracked files:\n  Use `gud stage add <file>` to include a file in the staging area")
                for file_path in unstaged["added"]:
                    print_red(f"\tnew file: {file_path}")
                print()

    return {
        "num_staged": num_staged,
        "num_unstaged_modified": num_unstaged_modified,
        "staged": staged,
        "unstaged": unstaged
    }


def log(invocation, internal_use=False, specified_branch=None) -> list|None:
    """
    internal_use -- represents whether this commnad was invoked within the code somewhere
    if this is the case, there need be no output to the terminal, just a return value
    """
    # get the HEAD commit
    if specified_branch:
        branch = Branch(invocation.repo)
        head_commit_hash = branch.get_branch_head(specified_branch)
    else:
        # get the detached head if it exists
        head_commit_hash = invocation.repo.detached_head or invocation.repo.head
        if not head_commit_hash:
            if not internal_use: # only show if the user invokes directly
                sys.exit(f"Your current branch {invocation.repo.branch} does not have any commits, so there are not logs to show.")
            return []

    commit = Commit(invocation.repo)
    commit_content = commit.get_content(head_commit_hash).decode()

    commit_has_parent = True
    commit_hash = head_commit_hash
    all_commit_contents = [] # left to right is most
    while commit_has_parent:
        curr_commit_content = {"hash": commit_hash}
        commit_content = commit.get_content(commit_hash).decode()
        for line in commit_content.split("\n"):
            if not line.strip(): # empty line
                continue
            parts = line.split("\t")
            if len(parts) == 1: # commit message
                curr_commit_content["message"] = parts[0]
            else:
                # either a tree, parent or committer
                key, value = parts
                curr_commit_content[key] = value
        # next commit hash
        commit_hash = curr_commit_content.get("parent", None)
        if commit_hash is None:
            commit_has_parent = False
        all_commit_contents.append(curr_commit_content)
    
    if internal_use: # if just wanting the values and don't need the output
        return all_commit_contents

    # determine which program to run
    less_exists = see_if_command_exists("less")
    pager = "less" if less_exists else "more"
    if pager == "less":
        instructions_str = "To scroll, use the arrow keys. **To exit, press q.**"
    else:
        instructions_str = "If scrollable, use spacebar to scrolldown and **press Q to exit.**"

    short = invocation.args["short"]
    with tempfile.NamedTemporaryFile(delete=False, mode="w", newline="") as temp_log_file:
        temp_log_file.write(f"\n-- Gud commits on branch {invocation.repo.get_effective_branch_name()} (newest to oldest) --\n")
        temp_log_file.write(f"-- {instructions_str} --\n\n\n")
        if short:
            for commit in all_commit_contents:
                temp_log_file.write(
                    f"{commit['hash'][:7]} -- {commit['message']}\n"
                )
        else:
            for commit in all_commit_contents:
                temp_log_file.write(
                    f"Commit: {commit['hash']}\n"
                    f"Committer: {commit['committer']}\n\n"
                    f"  {commit['message']}\n\n"
                )
        temp_log_file.write("\n\n")
        log_file_name = temp_log_file.name

    print(f"Gud logs are about to open...\n{instructions_str}")
    questionary.press_any_key_to_continue().ask()
    open_relevant_pager(invocation.os, pager, log_file_name)
    os.remove(log_file_name) # delete temp file


def branch(invocation):

    view_or_rename_or_create_or_delete = invocation.args.get("view_or_rename_or_create_or_delete", None)
    if not view_or_rename_or_create_or_delete:
        view_or_rename_or_create_or_delete = questionary.select(
            "Would you like to view branches, rename a branch, or create a new branch?",
            ["View", "Rename", "Create", "Delete"]
        ).ask().lower().strip()

    branch = Branch(invocation.repo)
    all_branches_info = branch.get_all_branches_info()

    # produce a list of sorted branch names, with the current branch at the start
    # used for view, rename and delete
    all_branch_names = list(all_branches_info)
    all_branch_names_sorted = sorted(all_branch_names)
    all_branch_names_sorted.remove(invocation.repo.branch)
    all_branch_names_sorted.insert(0, invocation.repo.branch)

    if view_or_rename_or_create_or_delete == "view":
        detached_head_commit = invocation.repo.detached_head
        print("-- All branches (* indicates current branch) --\n")
        if detached_head_commit:
            print_green(f"* DETACHED_HEAD {detached_head_commit[7:]}")
        for branch_name in all_branch_names_sorted:
            if not detached_head_commit and branch_name == invocation.repo.branch:
                print_green(f"*{branch_name}")
            else:
                print(branch_name)

    elif view_or_rename_or_create_or_delete == "rename":
        selected_branch = questionary.select(
            "Select a branch to rename:",
            all_branch_names_sorted
        ).ask()
        if not selected_branch:
            return
        while True:
            new_branch_name = questionary.text("Enter a name for your branch:").ask()
            if not new_branch_name:
                return
            new_branch_name = new_branch_name.strip()
            all_branches_except_selected = {branch for branch in all_branch_names_sorted if branch != selected_branch}
            is_valid_name = is_valid_branch_name(new_branch_name)
            is_unique_name = new_branch_name not in all_branches_except_selected
            if is_valid_branch_name(new_branch_name) and is_unique_name:
                break
            if not is_valid_name:
                print_red("The new branch name must contain only letters, numbers, dashes or underscores.")
            if not is_unique_name:
                print_red(f"{new_branch_name} already exists as a branch. Please choose another name.")
        branch.rename_branch(selected_branch, new_branch_name)
        print(f"Branch {selected_branch} renamed to {new_branch_name}{' (unchanged)' if new_branch_name == selected_branch else ''}")

    elif view_or_rename_or_create_or_delete == "create":
        while True:
            new_branch_name = questionary.text("Enter a name for your branch:").ask()
            if not new_branch_name:
                return
            new_branch_name = new_branch_name.strip()
            is_valid_name = is_valid_branch_name(new_branch_name)
            if is_valid_name and new_branch_name not in all_branches_info.keys():
                break
            if not is_valid_name:
                print_red("The branch name must contain only letters, numbers, dashes or underscores.")
            if new_branch_name in all_branches_info.keys():
                print_red(f"{new_branch_name} already exists as a branch. Please choose another name.")
        branch.create_branch(new_branch_name)
        # IMPORTANT - if they are in a detached head state, it should immediately switch them to the branch
        if invocation.repo.detached_head:
            detached_head_file_path = os.path.join(invocation.repo.path, "DETACHED_HEAD")
            with open(detached_head_file_path, "w", encoding="utf-8") as f:
                pass
            invocation.repo.set_branch(new_branch_name)          
        print(f"Branch {new_branch_name} created.")

    elif view_or_rename_or_create_or_delete == "delete":
        all_branches_except_current = [branch for branch in all_branch_names_sorted if branch != invocation.repo.branch]
        if not all_branches_except_current:
            print(f"You only have one branch ({invocation.repo.branch}), which you are currently on, so you cannot delete any branches.")
            return
        selected_branch = questionary.select(
            "Select a branch to delete:",
            all_branches_except_current
        ).ask()
        if selected_branch:
            to_delete = questionary.confirm(f"Are you sure you wish to delete branch {selected_branch}? You cannot undo this.").ask()
            if to_delete:
                branch.delete_branch(selected_branch)
                print(f"Branch {selected_branch} deleted.")
            else:
                print("Operation cancelled.")

def checkout(invocation):
    # ensure there are no staged files, otherwise shouldnt be able to checkout
    file_changes = status(invocation, print_output=False)
    num_files_staged: int = file_changes["num_staged"]
    num_files_unstaged_modified: int = file_changes["num_unstaged_modified"]
    if num_files_staged > 0:
        sys.exit("You have unsaved changes staged. Please either commit them or remove them (`gud stage remove`) from the staging area.")
    if num_files_unstaged_modified > 0:
        sys.exit("You have unstaged changes. Please either:\nStage and commit the files (`gud stage add` then `gud commit`)\nor\nRestore the files back to their previous state (`gud restore <file>`)")

    specific_branch = invocation.args.get("branch")
    specific_hash = invocation.args.get("hash")

    branch = Branch(invocation.repo)
    all_branches_info = branch.get_all_branches_info()

    if specific_branch is not None and specific_branch not in all_branches_info.keys():
        sys.exit(f"Branch {specific_branch} does not exist.")
    if specific_hash:
        try:
            _commit = Commit(invocation.repo)
            _ = _commit.get_full_file_path_from_hash(specific_hash)
        except FileNotFoundError:
            sys.exit(f"Hash {specific_hash} does not exist.")

    # do not include any branches without a HEAD (ie any branches with zero commits)
    all_branches_info_filtered = {branch: info for branch, info in all_branches_info.items() if info}
    if not all_branches_info_filtered:
        sys.exit("Cannot checkout any branch, because no commits exist on any branch. Please commit something first!")

    # produce a list of sorted branch names, with the current branch at the start
    all_branch_names = list(all_branches_info_filtered)
    all_branch_names_sorted = sorted(all_branch_names)
    all_branch_names_sorted.remove(invocation.repo.branch)
    all_branch_names_sorted.insert(0, invocation.repo.branch)

    # first, ensure they have a specific branch they want to checkout to
    if not specific_branch and not specific_hash:
        specific_branch = questionary.select(
            "Select a branch to checkout to:",
            all_branch_names_sorted
        ).ask()
        if not specific_branch:
            return

    # now, ensure they select a specific hash they want to checkout to 
    if not specific_hash:
        all_commit_contents = log(invocation, internal_use=True, specified_branch=specific_branch)
        if not all_commit_contents:
            sys.exit(f"The specified branch ({specific_branch}) has no commits to checkout to.")
        all_commit_contents_readable = [f"{commit['hash']} -- {commit['message']}" for commit in all_commit_contents]
        # labels the top commit as (HEAD)
        all_commit_contents_readable_with_head_labeled = ["(HEAD) " + all_commit_contents_readable[0]] + all_commit_contents_readable[1:]
        specific_hash = questionary.select(
            "Select a specific commit to checkout to:",
            all_commit_contents_readable_with_head_labeled
        ).ask()
        if not specific_hash:
            return
        # remove the `-- <commit_message>` bit and (HEAD), if it's there
        specific_hash = specific_hash.replace("(HEAD) ", "").split()[0].strip()

    """ modifying files and switching branches """

    detached_head_file_path = os.path.join(invocation.repo.path, "DETACHED_HEAD")

    tree = Tree(invocation.repo)
    commit = Commit(invocation.repo)
    staged_index = tree.index
    checked_out_index = tree.get_index_of_commit(commit_obj=commit, commit_hash=specific_hash)

    # abs paths so the modifications are easier
    staged_index_abs = {os.path.join(invocation.repo.root, path): value for path, value in staged_index.items()}
    checked_out_index_abs = {os.path.join(invocation.repo.root, path): value for path, value in checked_out_index.items()}

    # determine which files need creating/deleting/modifying, and create a backup (maybe) of them
    files_to_delete = set()
    files_to_modify: dict[str, dict] = {} # dict([type, mode, hash])
    files_to_not_change = set()

    for file_path, info_dict in staged_index_abs.items():
        checked_out_version = checked_out_index_abs.get(file_path, None) # either [type, mode, hash] or None
        if not checked_out_version:
            files_to_delete.add(file_path)
        else:
            info_str_staged = "".join(str(x) for x in info_dict.values())
            info_str_checked_out = "".join(str(x) for x in checked_out_version.values())
            if info_str_staged != info_str_checked_out:
                files_to_modify[file_path] = checked_out_version # store the checked out version of the file's hash etc
            else:
                files_to_not_change.add(file_path)

    # anything that exists in checked_out_index but not been seen yet
    file_paths_to_create = set(checked_out_index_abs.keys()) - files_to_delete - files_to_not_change - set(files_to_modify.keys())
    files_to_create = {file_path: checked_out_index_abs[file_path] for file_path in file_paths_to_create}

    # change the value of DETACHED_HEAD
    with open(detached_head_file_path, "w", encoding="utf-8") as f:
        f.write(specific_hash)

    # delete files
    for file in files_to_delete:
        os.remove(file)
        # this is a really bad implementation because it only up to one directory up
        # TODO - fix this implementation so it deletes all folders all the way up
        parent_dir = os.path.dirname(file)
        # try to remove the parent directory if deleting files made it it empty
        try:
            os.rmdir(parent_dir)
        except OSError as e:
            pass

    # create files
    for file, info_dict in files_to_create.items():
        # create directories if needed
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "wb") as f:
            blob = Blob(invocation.repo)
            blob_hash = info_dict["hash"]
            uncompressed_content = blob.deserialise_object(obj_hash=blob_hash, expected_type="blob")
            f.write(uncompressed_content)

    # modify existing files
    for file, info_dict in files_to_modify.items():
        with open(file, "wb") as f:
            blob = Blob(invocation.repo)
            blob_hash = info_dict["hash"]
            uncompressed_content = blob.deserialise_object(obj_hash=blob_hash, expected_type="blob")
            f.write(uncompressed_content)

    # update the current index so gud status etc doesn't go wild
    invocation.repo.write_to_index(checked_out_index)

    # if checking out the head of a branch, clear the detached HEAD file
    if specific_hash == invocation.repo.get_head(specific_branch):
        # set the branch and remove detached_head
        detached_head_file_path = os.path.join(invocation.repo.path, "DETACHED_HEAD")
        with open(detached_head_file_path, "w", encoding="utf-8") as f:
            pass
        invocation.repo.set_branch(specific_branch)
        # if previously detached on a branch and then switching back to its HEAD
        if specific_hash == invocation.repo.head:
            sys.exit(f"Returned to the HEAD of {invocation.repo.branch}.")
        else:
            sys.exit(f"Switched to branch {specific_branch}.")
    else:
        print(f"Checked out at {specific_hash[:7]}, in a `detached HEAD` state.")
        print_dark_grey("Please create a branch `gud branch create` if you wish to make changes.")


def restore(invocation):
    
    # get a set of all file paths that can be reset
    file_changes = status(invocation, print_output=False)
    unstaged_modified_files = set(
        os.path.join(invocation.repo.root, path)
        for path in file_changes["unstaged"]["modified"]
    )

    file_path_rel = os.path.relpath(invocation.args["file_path"][0], invocation.repo.root)
    file_path_abs = os.path.join(invocation.repo.root, file_path_rel)

    if not file_path_abs in unstaged_modified_files:
        sys.exit(f"Specified file path must be modified and unstaged. Use `gud status` to see which files can be restored.")

    # restore the file
    branch_commit_hash = invocation.repo.head
    tree = Tree(invocation.repo)
    commit = Commit(invocation.repo)
    blob = Blob(invocation.repo)
    head_index = tree.get_index_of_commit(commit, branch_commit_hash)
    blob_hash = head_index[file_path_rel]["hash"]
    uncompressed_content = blob.deserialise_object(obj_hash=blob_hash, expected_type="blob")
    with open(file_path_abs, "wb") as f:
        f.write(uncompressed_content)
    # don't need to update the index because the file was unstaged anyway
    print(f"Successfully restored file {file_path_rel} back to its previous state (on branch {invocation.repo.branch}).")