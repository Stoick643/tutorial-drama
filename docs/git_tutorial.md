# Git from the Terminal
*A practical guide for developers moving from desktop tools*

**INTRO TRACK**
- Lesson 1 · The `.git` folder & `.gitignore`
- Lesson 2 · The 4 Areas & Daily Cycle
- Lesson 3 · Branches as Pointers
- Lesson 4 · Inspecting History & Undoing Things
- Lesson 5 · The Big Picture: GitHub & CI/CD

---

## Introduction

You already know Git. You have been committing, pushing, pulling, and branching using a desktop tool — and that is perfectly valid. This tutorial does not start from zero.

What we will do here is look behind the curtain. Desktop tools are excellent at hiding complexity, but that means they also hide understanding. Once you see what your tool was doing on your behalf, everything clicks — and you gain full control.

> **Who this is for**
> - Developers who already use Git through a GUI (GitHub Desktop, SourceTree, VS Code, IntelliJ, etc.)
> - People who want to use the terminal but find Git commands confusing
> - Anyone who ever asked *"what does `git reset` actually do?"*

A note on didactics: a few key concepts will appear more than once throughout this tutorial. That is intentional. Seeing the same idea in a new context is how it becomes second nature.

---

## Lesson 1 — Under the Hood

### The `.git` folder: Git's database

When you run `git init` or `git clone`, Git creates a hidden folder called `.git` inside your project. This is Git's entire world. There is no cloud magic, no background service — just this folder.

```
my-project/
├── src/
│   └── App.java
├── .gitignore
└── .git/              ← Git's database (do not touch manually)
    ├── HEAD            ← which branch you're currently on
    ├── objects/        ← every version of every file ever committed
    ├── refs/           ← branches and tags (just files with commit hashes)
    └── config          ← this repo's settings
```

A few things worth knowing:

- Delete the `.git` folder and Git is gone — your files stay, but all history vanishes.
- The `objects/` folder is Git's content-addressed storage. Every commit, file, and tree is stored as a hash. This is why Git is so reliable.
- `HEAD` is just a text file. Open it and you will see something like: `ref: refs/heads/main`
- A branch is also just a file in `refs/heads/` containing a 40-character commit hash. That is all.

> 🔁 **First encounter with a key concept**
> A branch is a pointer — just a file with a commit hash inside it. No copy of your code, no folder. We will see this again in Lesson 3.

---

### The `.gitignore` file

Not everything in your working directory should be tracked. Build artifacts, IDE configuration, log files, and secrets should stay local. The `.gitignore` file tells Git which files to ignore completely.

```gitignore
# Example .gitignore

# Build output
target/
*.class

# IDE files
.idea/
*.iml
.vscode/

# Logs
*.log

# OS files
.DS_Store
Thumbs.db

# IMPORTANT: never commit secrets
.env
application-local.properties
```

Important rules:

- Create `.gitignore` before your first commit — retroactively ignoring already-tracked files is messy.
- Use `git rm --cached <file>` to stop tracking a file that was already committed.
- Ready-made templates for most languages and frameworks are available at [gitignore.io](https://gitignore.io).
- You can also have a global `.gitignore` for IDE and OS files that applies to all your projects.

```bash
# Setup: one-time global gitignore
git config --global core.excludesfile ~/.gitignore_global
```

---

### First-time setup

Before using Git from the terminal, tell it who you are. This information is recorded in every commit you make.

```bash
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"

# Optional but useful: set VS Code as your default editor
git config --global core.editor "code --wait"

# Verify your config
git config --list
```

---

## Lesson 2 — The 4 Areas & The Daily Cycle

### The mental model that explains everything

This is the most important concept in this tutorial. Git does not just "save" files — it moves snapshots of your files between four distinct areas. Every Git command is essentially moving something between these areas.

```
┌──────────────┐  git add   ┌──────────────┐  git commit  ┌──────────────┐  git push  ┌──────────────┐
│              │ ─────────► │              │ ───────────► │              │ ─────────► │              │
│  Working Dir │            │ Staging Area │              │  Local Repo  │            │  Remote Repo │
│  (your files)│ ◄───────── │  (the index) │              │   (.git/)    │ ◄───────── │   (GitHub)   │
└──────────────┘ git restore└──────────────┘              └──────────────┘ git fetch  └──────────────┘

                                      git pull = git fetch + git merge
```

Your desktop tool hid the Staging Area from you. That middle box is where you choose exactly which changes go into the next commit — even if you modified several files, you can commit them in logical groups.

> **What your desktop tool was doing**
> - Clicked "Stage All" → `git add .`
> - Typed a message and clicked "Commit" → `git commit -m "..."`
> - Clicked "Push" → `git push origin main`
> - Clicked "Pull" → `git pull` (= `git fetch` + `git merge`)

---

### `git status` — your compass

Always start here. `git status` shows you where each file currently lives across the four areas.

```
$ git status

On branch main

Changes not staged for commit:    ← Working Dir (modified, not yet staged)
  modified:   src/App.java

Changes to be committed:          ← Staging Area (ready to commit)
  modified:   pom.xml

Untracked files:                  ← Working Dir (new, Git doesn't know about it)
  notes.txt
```

---

### Moving files through the four areas

```bash
# Working Dir → Staging Area
git add App.java          # stage one specific file
git add src/              # stage an entire folder
git add .                 # stage everything that changed

# Staging Area → Local Repo
git commit -m "Fix login validation"

# Local Repo → Remote Repo
git push origin main

# Remote Repo → Local Repo (safe, does not touch your files yet)
git fetch origin

# Local Repo → Working Dir (applies fetched changes)
git merge origin/main

# Shortcut: fetch + merge in one step
git pull
```

> 🔁 **The 4 areas — second encounter**
> Notice how each command maps to an arrow in the diagram above. When you feel lost, come back to the diagram and ask: *which area am I in, and which area do I want to get to?*

---

## Lesson 3 — Branches as Pointers

### What a branch actually is

This is the concept most developers misunderstand. A branch is not a copy of your code. It is not a folder. It is a tiny file containing a single 40-character hash pointing to a commit.

That is why creating a branch in Git is instant and costs almost no disk space. Git is not copying anything.

```
         HEAD               ← points to the current branch
           │
           ▼
         main               ← points to commit C3
           │
           ▼
    C1 ◄── C2 ◄── C3       ← each commit points to its parent
```

> 🔁 **The `.git` folder — second encounter**
> Remember from Lesson 1: a branch is just a file in `.git/refs/heads/` with a commit hash inside. Open `.git/refs/heads/main` in a text editor and you will see exactly that.

---

### Creating and switching branches

```bash
git branch                    # list all branches (* marks the current one)
git branch feature-login      # create a new branch (pointer at current commit)
git switch feature-login      # move HEAD to that branch
git switch -c hotfix-typo     # create AND switch in one step (most common)
```

After one commit on `feature-login`:

```
         main
           │
           ▼
    C1 ◄── C2 ◄── C3
                    \
                     C4  ◄── feature-login  ◄── HEAD
```

---

### Merging

Merging brings one branch's commits into another. `HEAD` decides where the result lands — always switch to the target branch first.

```bash
git switch main               # go to the branch you want to merge INTO
git merge feature-login       # bring feature-login's commits in
```

Two types of merge:

```
FAST-FORWARD (no divergence — main just moves forward):
  Before:  main → C3,  feature-login → C4
  After:   main → C4   (pointer simply advances, no merge commit)

THREE-WAY MERGE (both branches moved independently):
  C3 ◄── C5  (main)
  │
  C2
  │
  C4         (feature-login)

  After merge: a new commit M is created with two parents
  main → M
```

> **Cleaning up**
> After merging, delete the feature branch — it has served its purpose:
> ```bash
> git branch -d feature-login   # safe: only deletes if already merged
> git branch -D feature-login   # force delete even if not merged
> ```

---

## Lesson 4 — Inspecting & Undoing

### Looking at history

These commands are where the terminal genuinely beats desktop tools. You have full, scriptable access to everything that ever happened in the repository.

```bash
git log                              # full history with author, date, message
git log --oneline                    # one line per commit
git log --oneline --graph --all      # visual tree of all branches
```

Example output:

```
* a3f9d12 (HEAD -> main) Fix login validation
* b72cc01 Add config file
| * e1f4c33 (feature-login) Add login form
|/
* 1da3e88 Initial commit
```

```bash
git diff                       # Working Dir vs Staging Area
git diff --staged              # Staging Area vs last commit
git show a3f9d12               # see exactly what changed in a specific commit
```

> **Useful alias** — add this once and use it everywhere:
> ```bash
> git config --global alias.lg "log --oneline --graph --all"
> git lg   # now this works as a shortcut
> ```

---

### Undoing things — mapped to the 4 areas

The most confusing part of Git for most people. The trick is to always ask: *which area do I want to undo changes in?*

> 🔁 **The 4 areas — third encounter**
> Each undo command targets a specific area. Knowing which area you want to roll back instantly tells you which command to use.

| Command | What it does |
|---|---|
| `git restore <file>` | Discard changes in Working Dir |
| `git restore --staged <file>` | Move file back from Staging Area to Working Dir |
| `git reset --soft HEAD~1` | Undo last commit, keep changes staged |
| `git reset --mixed HEAD~1` | Undo last commit, keep changes in Working Dir |
| `git reset --hard HEAD~1` | ⚠️ Undo last commit AND discard all changes |
| `git revert HEAD` | Create a new commit that undoes the last one (safe for shared branches) |

Use `git revert` when the commit has already been pushed to a remote. It creates a new undo-commit instead of rewriting history, which keeps your teammates happy. Use `git reset` only for local, unpushed commits.

> ⚠️ **The only dangerous command**
> `git reset --hard` is the only command in this tutorial that can make you lose work permanently. Everything else is recoverable.

---

## Lesson 5 — The Big Picture

### GitHub: just a remote with a web interface

Everything we have done so far is entirely local. GitHub is simply a Git remote — a hosted copy of your `.git` folder — with a web interface built around it.

When you push to GitHub, your commits travel from your Local Repo to a server anyone can access via a browser. Pull Requests, issues, and code review are GitHub features layered on top. The Git part underneath is identical to what you have been doing all along.

```bash
git remote -v                         # see what remotes are configured
git remote add origin <url>           # connect your local repo to a GitHub repo
git push -u origin main               # first push: -u sets the default tracking branch
git push                              # subsequent pushes
```

> **`origin` is just a name**
> When you clone a repo, Git automatically names the source remote `origin`. You could call it anything — `origin` is just the convention.

---

### CI/CD: the push that does more than push

Once your local repo is connected to a remote, you can wire up automation. CI/CD stands for Continuous Integration / Continuous Deployment. The idea is simple: a push to a specific branch triggers a pipeline automatically.

```
You type code
      │
      ▼
git commit          ← snapshot in your local repo (.git/objects/)
      │
      ▼
git push            ← sends commits to GitHub
      │
      │  GitHub detects the push, triggers the pipeline
      ▼
CI pipeline         ← runs tests, builds the project
      │
      │  If everything passes, deploys automatically
      ▼
fly.io / cloud      ← your new code is live
```

A common real-world setup looks exactly like this: a developer pushes to the `main` branch, GitHub Actions detects the push and runs a workflow file (`.github/workflows/deploy.yml`), and fly.io receives the new build and deploys it within seconds. **No manual steps after `git push`.**

> 🔁 **The `.git` folder — third encounter**
> The `objects/` folder in `.git` is what actually travels when you push. GitHub stores the exact same content-addressed objects. This is why Git is reliable across machines — the hash guarantees the content.

---

### Why clean Git habits matter here

Once a pipeline is wired to your repository, the quality of your Git workflow has direct consequences. A messy commit history makes it harder to understand what a broken deployment introduced. Good habits to build:

- Write meaningful commit messages — they appear in deployment logs.
- Keep the `main` branch stable — treat every push as a potential deployment.
- Use feature branches — let the pipeline run on your branch before it reaches `main`.
- Small, focused commits — easier to revert a single commit than untangle a large one.

---

## Quick Reference

### Daily Workflow

| Command | What it does |
|---|---|
| `git status` | Where am I? What has changed? |
| `git add .` | Stage all changes |
| `git add <file>` | Stage a specific file |
| `git commit -m "msg"` | Snapshot to local repo |
| `git push` | Send to remote |
| `git pull` | Fetch + merge from remote |

### Branches

| Command | What it does |
|---|---|
| `git branch` | List all branches |
| `git switch -c <name>` | Create and switch to new branch |
| `git switch <name>` | Switch to existing branch |
| `git merge <branch>` | Merge branch into current branch |
| `git branch -d <name>` | Delete merged branch |

### Inspecting

| Command | What it does |
|---|---|
| `git log --oneline --graph --all` | Visual history of all branches |
| `git diff` | Working Dir vs Staging Area |
| `git diff --staged` | Staging Area vs last commit |
| `git show <hash>` | See what a specific commit changed |

### Undoing

| Command | What it does |
|---|---|
| `git restore <file>` | Discard Working Dir changes |
| `git restore --staged <file>` | Unstage a file |
| `git reset --soft HEAD~1` | Uncommit, keep staged |
| `git reset --mixed HEAD~1` | Uncommit, keep in Working Dir |
| `git reset --hard HEAD~1` | ⚠️ Uncommit and discard all changes |
| `git revert HEAD` | Safe undo for pushed commits |

### Remote

| Command | What it does |
|---|---|
| `git remote -v` | List remotes |
| `git push -u origin main` | First push (sets tracking) |
| `git fetch origin` | Download changes without merging |
| `git clone <url>` | Copy a remote repo locally |

---

*— End of Intro Track —*
