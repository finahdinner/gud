### Gud Tutorial (10-15 minutes)

#### Before you begin, please make sure to follow the installation instructions [here](README.md).<br>Once Gud is up an running (use `gud hello` to test this), you may begin!

Quick notes before starting:

- All commands in this tutorial `look like this`.
- To use a command in the terminal, **type it in (exactly as shown)**, then **press enter.**
- If you are ever stuck in an interactive menu, press **ctrl-c (command-c on Mac)**.
- If you at any point get stuck or lost, feel free to start from the beginning.<br>To do this, do the following:
  - Use the command `cd ..` (this takes you back out of the tutorial folder)
  - Delete the _gud_tutorial_ folder
  - Then start the tutorial from the beginning

<hr>

### Gud Tutorial

#### Gud is a basic [version control system](https://en.wikipedia.org/wiki/Version_control) which, similar to [Git](https://git-scm.com/), offers an array of commands and functionality for keeping track of a part of your file system.

#### It is normally used to help people develop software, and is especially useful if you want to be able to revert changes, work on different features, or collaborate with others.

#### In this tutorial, we will be using a very simple example folder to demonstrate how _Gud_ works. Having some prior experience with using Git through the command line is _helpful_, although not necessary.

1. To begin, open up an empty folder in a text editor of your choice (for example, _VSCode_ or _Pycharm_).
2. Open up an integerated **terminal** window inside your text editor. It will normally be at the bottom of your screen.
3. Use the command `gud loadexample`
   - This will load a folder with example files in it
4. Use the command `cd loadexample`
   - This will navigate your terminal to the _loadexample_ folder
5. Take a moment to look at all the files in this folder. There are only a few, and they each only contain a single line of text. Nothing too exciting!
6. Use the command `gud init`
   - This will tell Gud to create a _repository_ in this folder. This is basically just a folder called _.gud_, which will contain all your configuration settings and file versions.<br>**You need not worry about this folder in the slightest**.
7. Gud will now ask you to provide your _name_ and _email_ (doesn't matter what you give), and then ask you if you wish to ignore any files. *You may skip this and select *no\*\* (although feel free to have a go!).
8. Now that your repository has been created (notice the _.gud_ folder now), you have access to Gud's full range of commands!
   <br>Begin by using `gud status`
   - This shows which files are, and are not, being tracked by Gud (by default, nothing is tracked at the beginning).
9. Now, let's tell Gud to start tracking one of our files!
   <br>Use the command `gud stage` - Gud will ask if you wish to _add_ or _remove_ a file from the stage - Select `view` - Type in `notes.txt`, and notice how it shows you auto-fill suggestions.
   <br>**Press tab** if you wish to let it autocomplete for you. - Press enter to confirm your selection. - Press enter again to confirm that you have no other files to add.
10. You should now be back at your terminal prompt.
    <br>Use `gud status` to check the status of your files now - Notice how it says that _notes.txt_
