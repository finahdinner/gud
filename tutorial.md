### Gud Tutorial (10-20 minutes)

#### Before you begin, please make sure to follow the installation instructions [here](README.md).<br>Once Gud is up an running (use `gud hello` to test this), you may begin!

Quick notes before starting:

- All commands in this tutorial `look like this`.
- To use a command in the terminal, **type it in (exactly as shown)**, then **press enter.**
- If you are ever stuck in an interactive menu, press **ctrl-c (command-c on Mac)**.
- If at any point you get stuck or lost, feel free to start from the beginning.
- To do this, do the following:
  - Use the command `cd ..` (this takes you back out of the tutorial folder)
  - Delete the _gud_tutorial_ folder
  - Then start the tutorial from the beginning

<hr>

### Gud Tutorial

#### Gud is a basic [version control system](https://en.wikipedia.org/wiki/Version_control) which, similar to [Git](https://git-scm.com/), offers an array of commands and functionality for keeping track of a part of your file system.

#### It is normally used to help people develop software, and is especially useful if you want to be able to revert changes, work on different features, or collaborate with others.

#### In this tutorial, we will be using a very simple example folder to demonstrate how _Gud_ works. Having some prior experience with using Git through the command line is _helpful_, although not necessary.

#### Part 1/3

1. To begin, open up an empty folder in a text editor of your choice (for example, _VSCode_ or _Pycharm_).
2. Open up an integerated **terminal** window inside your text editor. It will normally be at the bottom of your screen.
3. In the terminal, use the command `gud loadexample`
   - This will load a folder with example files in it.
   - Your terminal prompt should show something like `\gud_tutorial>` or `/gud_tutorial$` to indicate that you are in the correct folder.
4. Use the command `cd gud_tutorial`
   - This will navigate your terminal to the _loadexample_ folder.
5. Take a moment to look at all the files in this folder. There are only a few, and they each only contain a single line of text. Nothing too exciting!

#### Part 2/3

1. Use the command `gud init`
   - This will tell Gud to create a _repository_ in this folder. This is basically just a folder called _.gud_, which will contain all your configuration settings and file versions.<br>**You need not worry about the _.git_ folder at all**.
2. Gud will now ask you to **provide your _name_ and _email_** (type in whatever you like), and then ask you if you wish to ignore any files.
   - **Select `No` on the last question** (it's not relevant to this tutorial).
3. Now that your repository has been created (notice the _.gud_ folder now), you have access to Gud's full range of commands!
   <br>Begin by using `gud status`
   - This shows which files are, and are not, being tracked by Gud (by default, nothing is tracked at the beginning).
4. Now, let's tell Gud to start tracking one of our files!
   <br>Use the command `gud stage`
   - Gud will ask if you wish to _add_ or _remove_ a file from the stage.
   - Select `Add` then, when prompted, type in the file name `notes.txt`.
   - Notice how it shows you _suggestions_ as you type - **press tab** if you wish to let it autocomplete for you.
   - Press enter to confirm your selection.
   - **Press enter again** to confirm that you have no other files to add.
5. You should now be back at your terminal prompt.
   <br>Use `gud status` to check the status of your files now.
   - Your output should look similar to below:
     ![image](https://github.com/user-attachments/assets/b8016ba5-e704-4ff5-967a-f55425bf46a7)
   - This is effectively saying that, next time you make a _commit_ (which is in the next step), _notes.txt_ will be included in that _commit_.
6. Use the command `gud commit`
   - It will now prompt you to include a _message_ for this commit. You would normally describe what changes you have made since the last commit.
   - Write something like "added notes.txt", and then **press any key to continue.**
7. "Committing" files like this, is effectively creating a _snapshot_ in time. At some point in the future you could go back to the files, and restore them to the state that they were in at the time of this commit. Pretty nifty - more on this later!
8. Use the command `gud log`
   - Press enter, and you should see something like this:
     ![image](https://github.com/user-attachments/assets/67a0a17a-3b27-4620-92ec-0faac2bd7199)
   - This shows you _all_ of your previous commits, and is helpful for seeing what changes have been made in the past.
   - **NOTE: If you find yourself stuck in a window (most likely if you are on Mac or Linux), press q to exit.**
9. Let's create another commit.
   <br>Use the command `gud stage add project`
   - This is a shorthand version of what we did earlier. This time, we're telling Gud that we want to include the entire _project_ folder in our next commit.
10. Use the command `gud commit` and provide a commit message. Something like "added project folder" should be fine.
11. Use the command `gud log`
    - You will notice that the log has been updated with your most recent commit.
    - Don't forget to **press q** to exit if you need to!
12. Open up _notes.txt_ and make some change to the file (literally anything!).
13. Use `gud status` and you'll see that Gud has detected this modification:
    ![image](https://github.com/user-attachments/assets/514d7161-d6c0-45fc-9222-495968227f4c)
14. Use `gud stage add notes.txt` then `gud commit`, and leave a message like "changed notes.txt".

#### So why are we doing all of this? What is the point of this software?

Good question. Up until this point, we haven't really done anything too exciting.

#### But here is when it gets a little interesting!

#### Part 3/3

1. Delete the project folder. Yes, delete it!
2. Use the command `gud status`
   - You will notice that Gud has detected that you deleted the folder.
   - Your output should look similar to below:
     ![image](https://github.com/user-attachments/assets/a6de36cd-9dae-444a-ab9d-039e1bb62d91)
3. The next commands will depend on whether you are on Windows or Mac/Linux (due to how file paths work):
   - On **Windows** - use `gud stage add project\main.py` then `gud stage add project\vars.py`
   - On **Mac or Linux** - use `gud stage add project/main.py` then `gud stage add project/vars.py`
4. Use the command `gud commit`
   - Leave a message such as "deleted project folder", or similar. This commit is telling Gud to take note of these deletions.

#### Remember what we said about version control software letting you restore files to a previous state?

#### Let's do that!

5. Use `gud log`
   - Your output should show 4 commits, as below:
     ![image](https://github.com/user-attachments/assets/a22e5a22-5c07-4a45-885c-30d24d693c7c)
   - Each of these 4 commits represents a _snapshot_ in time, and Gud (like Git) lets you hop back and forth between different individual snapshots.
6. Use `gud checkout`
   - This command allows you to switch between different _snapshots_.
   - After using the command, you will be prompted to select a branch to "checkout" to.
   - **Select master** (it should be the only option).
7. It now shows you all your commits, like _gud log_, but in a compressed form. And it lets you select one.
   - Use the arrow keys to **select the _added project folder_ commit (second from the bottom)**.
8. **Now look in your _gud_tutorial_ folder**.
   - If you followed all these steps correctly, **your _project_ folder will have returned!** And everything inside it too.
   - Both _main.py_ and _vars.py_ should also contain the same text that they did before you deleted them.
9. Use `gud checkout` again, this time selecting the top-most ("HEAD") commit.
   - **Your project folder should automatically be deleted again.**
   - This is because, at this specific commit, the project folder doesn't exist. And Gud handles all of these files changes, creations and deletions whenever you _checkout_ to a specific commit.

This is the magic of version control! It is super useful being able to track your changes over time _and_ switch between these different versions. And it goes a lot deeper than this too.

#### And that concludes this Gud tutorial! We touched upon a few of the core commands that Gud has to offer, although there are some others that we didn't get to discuss, such as `gud branch`, `gud restore` and `gud config`.

Git, which Gud is based on, goes much, much, MUCH deeper than all of this. The number of features that it boasts is astounding. Read more about Git [here](https://git-scm.com/docs).

#### If you made it this far, well done! And thank you!
