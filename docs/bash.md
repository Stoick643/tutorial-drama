Whether you are using Git Bash or a full WSL instance, these ten commands are the "survival kit" for navigating and managing your system.

1. ls (List)
The most used command. It shows you what files and directories are in your current folder.

Pro tip: Use ls -la to see hidden files and detailed info (size, permissions).

2. cd (Change Directory)
How you move between folders.

cd .. moves you up one level.

cd ~ takes you straight back to your home directory.

3. pwd (Print Working Directory)
If you ever feel lost, this tells you exactly where you are in the file system (e.g., /c/Users/Name/Projects).

4. mkdir (Make Directory)
Creates a new folder.

Usage: mkdir my_new_project

5. touch
The quickest way to create a new, empty file.

Usage: touch index.html

6. rm (Remove)
Deletes files or directories. Be careful: Bash doesn't have a "Recycle Bin"; once it's gone, it's gone.

Usage: rm file.txt

For folders: rm -rf folder_name (deletes the folder and everything inside).

7. cp & mv (Copy & Move)
cp: Copies a file (cp source.txt destination.txt).

mv: Moves a file, but is also used to rename files.

8. grep (Global Regular Expression Print)
Search for specific text within files. It’s incredibly powerful for finding a needle in a haystack.

Usage: grep "error" log.txt

9. cat (Concatenate)
Quickly displays the entire contents of a file in your terminal without opening an editor.

Usage: cat README.md

10. chmod (Change Mode)
Changes the permissions of a file. On Bash, this is often used to make a script "executable."

Usage: chmod +x script.sh

Bonus: The "Save Me" Command
If you ever start a command and it hangs or you want to stop it immediately, press Ctrl + C. It kills the current process and gives you your prompt back.

Would you like me to show you how to chain these together using "pipes" (the | symbol) to perform more complex tasks?

You said
Oh, cool, I know them:)

So I am not a complete beginner

Please next 10, and include pipe

Since you’ve already mastered the basics, it’s time to move from "navigating" to "operating." These next 10 commands focus on data manipulation, system monitoring, and the "glue" that holds Bash together: The Pipe (|).

The Power of the Pipe (|)
The pipe takes the output of the command on the left and feeds it as the input to the command on the right. It allows you to build complex "pipelines" of data.

Example: ls | grep ".txt"
(List all files, but only show the ones that contain ".txt")

11. find
Locates files based on name, size, or modification date.

Usage: find . -name "*.js" (Finds all JavaScript files in the current folder and subfolders).

12. head & tail
Shows the beginning or the end of a file.

Usage: tail -n 20 access.log (Shows the last 20 lines of a log file).

Pro Tip: tail -f "follows" a file in real-time as it grows.

13. sort & uniq
Sorts lines of text alphabetically or numerically. uniq removes duplicate adjacent lines.

Pipeline: cat names.txt | sort | uniq (Gives you a sorted list of unique names).

14. awk
A powerhouse for processing data in columns (like a CSV).

Usage: ls -l | awk '{print $5, $9}' (Prints only the 5th column—size—and 9th column—filename—from a directory listing).

15. sed (Stream Editor)
Search and replace text within a stream.

Usage: echo "Hello World" | sed 's/World/Bash/' (Changes "World" to "Bash").

16. history
Shows a numbered list of every command you’ve typed recently.

Shortcut: Type !num (e.g., !42) to re-run command number 42 from your history.

17. xargs
Passes the output of one command as an argument to another.

Usage: find . -name "*.tmp" | xargs rm (Finds all .tmp files and deletes them all at once).

18. top (or htree)
The "Task Manager" of Bash. It shows running processes, CPU usage, and memory.

Note: In Git Bash, this may be limited; in WSL, it shows everything.

19. curl & wget
Download data from the internet directly to your terminal.

Usage: curl -O https://example.com/data.csv

20. alias
Creates a shortcut for long commands.

Usage: alias gs='git status' (Now you only have to type gs to see your Git status).

Putting it all together
Here is a classic "Power User" pipeline:
cat log.txt | grep "ERROR" | awk '{print $1}' | sort | uniq -c

cat: Reads the log.

grep: Filters for errors.

awk: Grabs the first column (likely the timestamp or IP).

sort: Groups identical entries together.

uniq -c: Counts how many times each specific entry occurred.

Would you like to try writing a custom script using these commands, or should we look at how to make these alias shortcuts permanent?


Great choice. Let's clear up those two points before we dive into scripting, as they are the "bread and butter" of automation.

1. curl vs. wget
Think of curl as a surgical tool and wget as a blunt instrument.

curl (Client URL): Its primary job is to transfer data. It is incredibly versatile and supports almost every protocol (HTTP, FTP, SCP, etc.). By default, it outputs the data to your terminal window (stdout).

Best for: Testing APIs, sending headers, or piping a download directly into another command.

wget (World Wide Web Get): Its primary job is downloading files. It is simpler to use for basic downloads and excels at "recursive" downloads (downloading an entire website or folder structure).

Best for: Grabbing a large installer or mirroring a directory.

Feature	curl	wget
Default Action	Prints to screen	Saves to a file
Recursion	No	Yes (can download a whole site)
Availability	Installed on almost everything	Often needs to be installed
Export to Sheets
2. Explaining find . -name "*.tmp" | xargs rm
This is a classic "Cleanup" pipeline. Here is how it works step-by-step:

find .: Start searching in the current directory (.) and all subdirectories.

-name "*.tmp": Only look for files that end in .tmp.

| (The Pipe): Take the list of filenames found by the find command and pass them to the next command.

xargs: This is the "bridge." It takes the list of filenames coming through the pipe and turns them into arguments for the next command.

rm: The remove command.

Why not just use rm *.tmp? If you have thousands of .tmp files scattered across different subfolders, rm *.tmp would only find the ones in your current folder. The find | xargs combo hunts them down everywhere and feeds them to rm one batch at a time.

Let’s Build a Script
Since you want to try a script, let's create a "Project Initializer". This script will create a folder, add an index.html and a style.css, and then automatically list the new structure.

Open your terminal.

Type nano setup.sh (this opens a simple text editor in the terminal).

Paste the following:

Bash
#!/bin/bash

# Ask the user for a project name
echo "Enter project name:"
read PROJ_NAME

# Create the directory and enter it
mkdir $PROJ_NAME
cd $PROJ_NAME

# Create files
touch index.html style.css
echo "<h1>Hello from $PROJ_NAME</h1>" > index.html

# List the result to show it worked
echo "Project $PROJ_NAME created successfully!"
ls -F
Press Ctrl + O, then Enter to save. Press Ctrl + X to exit.

Crucial Step: Make it executable: chmod +x setup.sh

Run it: ./setup.sh

#!/bin/bash

echo "Enter project name:"
read PROJ_NAME


#!/bin/bash

# Ask the user for a project name
echo "Enter project name:"
read PROJ_NAME

# Create the directory and enter it
mkdir $PROJ_NAME
cd $PROJ_NAME

# Create files
touch index.html style.css
echo "<h1>Hello from $PROJ_NAME</h1>" > index.html

# List the result to show it worked
echo "Project $PROJ_NAME created successfully!"
ls -F

# The check: -d returns true if the directory exists
if [ -d "$PROJ_NAME" ]; then
    echo "Error: A folder named '$PROJ_NAME' already exists!"
    exit 1  # Stop the script with an error code
else
    mkdir "$PROJ_NAME"
    cd "$PROJ_NAME"
    
    # Create files
    touch index.html style.css
    echo "<h1>Hello from $PROJ_NAME</h1>" > index.html
    
    echo "Project '$PROJ_NAME' created successfully."
    ls -F
fi


#!/bin/bash

echo "Enter project name:"
read PROJ_NAME

# The check: -d returns true if the directory exists
if [ -d "$PROJ_NAME" ]; then
    echo "Error: A folder named '$PROJ_NAME' already exists!"
    exit 1  # Stop the script with an error code
else
    mkdir "$PROJ_NAME"
    cd "$PROJ_NAME"
    
    # Create files
    touch index.html style.css
    echo "<h1>Hello from $PROJ_NAME</h1>" > index.html
    
    echo "Project '$PROJ_NAME' created successfully."
    ls -F
fi