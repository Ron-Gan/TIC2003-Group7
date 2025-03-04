# TIC2003-Group7

## Initialisation
1. Install git from https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
2. Create new folder and open it using Visual Studio Code
3. Open terminal and type `git clone https://github.com/Ron-Gan/TIC2003-Group7.git`

## Creating Branch & Working on Branch (Always work on branch)
Create Branch:
1. Type `git checkout -b {branch_name}` in the terminal
   
Work on Branches:
1. Type `git checkout {branch_name}` to change branches 
   
To push:
1. Type `git add .` in the terminal
2. Type `git commit -m "{comments}"`
3. Type `git push --set-upstream origin {branch_name}`

## Ensuring version is up-to-date before pushing
1. Type `git checkout main` in terminal
2. Type `git pull`
3. Type `git checkout {branch_name}`
4. Type `git rebase main`
