# gud

A recreation of the core functionality of [Git](https://git-scm.com/), designed for beginners.

### Gud has a [beginner tutorial](tutorial.md) that you may wish to check out.

### IMPORTANT NOTE: this is relatively untested software, so please do not use it for anything that is important!

<hr>

### Installation Instructions

#### For all platforms (Windows, MacOS, Linux)

1. Download and install Python **3.10 or above**, from https://www.python.org/downloads/
2. Open your `Terminal`
3. Confirm that `python` and `pip` are installed on your machine:
   - `python --version` (or `python3 --version`)
   - `pip --version` (or `pip3 --version`)
   - Ensure that neither of the above commands returns an error
4. Make sure you are not in a virtual environment in your terminal (you likely are not, but use the command `deactivate` just to make sure - don't worry if you get an error), then run the command:
   - `pip install "git+https://github.com/finahdinner/gud.git"`
5. Close your terminal and open it in your project directory
6. Run `gud hello` to confirm that Gud is installed!

#### Windows Users (Optional)

If you want a slightly nicer experience with the `gud log` command, you may wish to install
[less](https://community.chocolatey.org/packages/Less/) (which is included in Linux and MacOS by default)

1. Install the Chocolatey package manager: https://chocolatey.org/install#individual
2. Open PowerShell (**Run as Administrator**) and run:
   - `choco install less -y`
3. Reopen your powershell window and confirm installation with:
   - `less --version`

### Gud commands

Most of the following commands are named according to their [Git equivalents](https://git-scm.com/docs).

#### Core commands

- `gud init` - initialise a repository in the current working directory
- `gud stage` - add or remove files/directories from the staging area, ready to commit
- `gud commit` - commit the current staging area to the (permanent) commit history
- `gud status` - show all staged and untracked files
- `gud branch` - view or modify branches
- `gud log` - show the commit history for the current branch
- `gud checkout ` - restore the working directory to its state at a specific commit
- `gud restore` - restore a file to its version at the last commit

#### Additional commands

- `gud config` - view or modify Gud's configuration settings
- `gud ignoring` - show all files that Gud is not tracking in the the current repository
- `gud hello` - onfirm that Gud is installed properly

#### Help commands

If you ever wish to see which commands are available, or options available for a specific command, use the `-h` flag. _For example:_

- `gud -h` - shows all the gud commands
- `gud stage -h` - shows all the options available for the `stage` command
