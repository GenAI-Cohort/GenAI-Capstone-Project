# Git Merge Commands Guide

> **Purpose**: This guide walks you through merging a feature branch into your `develop` branch using Git command line tools. Following these steps ensures a clean merge process and helps avoid common pitfalls.

---

## Overview

When working with Git, merging branches is a fundamental operation that combines changes from one branch into another. This guide focuses on merging a feature branch into your `develop` branch, which is a common workflow in team-based development.

**What you'll learn:**

- How to safely merge branches
- How to handle merge conflicts
- Advanced merge options and when to use them

---

## Prerequisites

Before starting, ensure you have:

- ✅ Git installed and configured
- ✅ Access to the repository
- ✅ The feature branch ready to merge
- ✅ All your work committed (no uncommitted changes)

---

## Step-by-Step Merge Guide

Follow these steps in order to successfully merge your feature branch into `develop`.

### Step 1: Switch to the Develop Branch

**Why this matters**: You need to be on the target branch (`develop`) to merge changes into it. Think of it as being in the "receiving" branch.

```bash
git checkout develop
```

**Expected output**: You should see a message like `Switched to branch 'develop'` or `Already on 'develop'`.

---

### Step 2: Fetch and Pull Latest Changes

**Why this matters**: Before merging, ensure your local `develop` branch is synchronized with the remote repository. This prevents conflicts with work done by other team members and ensures you're working with the most up-to-date codebase.

```bash
git fetch origin
git pull origin develop
```

**What these commands do:**

- `git fetch origin`: Downloads the latest changes from the remote repository without merging them
- `git pull origin develop`: Fetches and merges the latest changes from the remote `develop` branch into your local `develop` branch

**💡 Tip**: Running `git fetch` first lets you review changes before pulling, giving you more control over the update process.

---

### Step 3: Merge the Feature Branch

**Why this matters**: This is where the actual merge happens. Git will combine all commits from your feature branch into `develop`.

```bash
git merge feature_branch_name
```

**Replace `feature_branch_name`** with the actual name of your branch (e.g., `feature/user-authentication`, `bugfix/login-error`, etc.).

**What happens next:**

- ✅ **If successful**: Git will create a merge commit and you'll see a message like `Merge made by the 'recursive' strategy`
- ⚠️ **If conflicts occur**: Git will pause and ask you to resolve conflicts (see Step 4)

---

### Step 4: Resolve Merge Conflicts (If Any)

**Why conflicts happen**: Merge conflicts occur when the same lines of code were modified differently in both branches. Git can't automatically decide which version to keep, so it needs your input.

**How to identify conflicts:**

```bash
git status
```

This command shows which files have conflicts. Look for files marked as "both modified".

**Resolving conflicts:**

1. **Open the conflicted files** in your editor. Git marks conflict areas with special markers:

   ```text
   <<<<<<< HEAD
   Code from develop branch
   =======
   Code from feature branch
   >>>>>>> feature_branch_name
   ```

2. **Edit the file** to resolve the conflict:
   - Keep the code you want (or combine both versions)
   - Remove the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)

3. **Stage the resolved file**:

   ```bash
   git add <filename>
   ```

4. **Complete the merge** by committing:

   ```bash
   git commit -m "Merged feature_branch_name into develop"
   ```

**💡 Tip**: Use a merge tool like `git mergetool` for a visual interface to resolve conflicts more easily.

---

### Step 5: Push to Remote Repository

**Why this matters**: After merging locally, push your changes to share them with your team and update the remote `develop` branch.

```bash
git push origin develop
```

**Expected output**: You should see a message indicating that your changes have been pushed successfully.

**⚠️ Important**: If the push is rejected, someone else may have pushed changes to `develop` since you last pulled. Run `git pull origin develop` again, resolve any conflicts, and then push.

---

## Advanced Merge Options

These optional flags give you more control over how merges are performed.

### `--no-ff` (No Fast-Forward)

**When to use**: When you want to preserve the branch history and always create a merge commit, even when a fast-forward merge is possible.

**Benefits**: Creates a clear record of all merges in your project history, making it easier to track when features were integrated.

```bash
git merge --no-ff feature_branch_name
```

**Example scenario**: Useful in team environments where you want to see explicit merge points in the commit history.

---

### `--squash`

**When to use**: When you want to combine all commits from the feature branch into a single commit on the target branch.

**Benefits**: Creates a cleaner, more linear history by condensing multiple commits into one.

```bash
git merge --squash feature_branch_name
```

**⚠️ Note**: After using `--squash`, you must manually commit the changes:

```bash
git commit -m "Squashed feature_branch_name into develop"
```

**Example scenario**: Useful when your feature branch has many small commits (like "fix typo", "update comment") that you want to consolidate.

---

### `--abort`

**When to use**: When you encounter problems during a merge and want to cancel it, returning to the state before the merge started.

```bash
git merge --abort
```

**What it does**: Completely undoes the merge attempt and restores your branch to its pre-merge state.

**⚠️ Warning**: Only use this if you haven't committed the merge yet. Once committed, you'll need to use `git reset` instead.

---

## Quick Reference

| Command | Purpose |
| ------- | ------- |
| `git checkout develop` | Switch to the develop branch |
| `git fetch origin` | Download latest changes without merging |
| `git pull origin develop` | Fetch and merge latest changes |
| `git merge feature_branch` | Merge feature branch into current branch |
| `git status` | Check for conflicts and file status |
| `git add <file>` | Stage resolved files |
| `git push origin develop` | Push merged changes to remote |

---

## Troubleshooting

**Problem**: `git pull` fails with "Your local changes would be overwritten"

- **Solution**: Commit or stash your local changes first

**Problem**: Merge conflicts seem overwhelming

- **Solution**: Use `git mergetool` for a visual conflict resolution interface

**Problem**: Accidentally merged the wrong branch

- **Solution**: Use `git reset --hard HEAD~1` to undo the merge (⚠️ be careful, this discards the merge)

---

## Best Practices

1. ✅ Always pull latest changes before merging
2. ✅ Test your feature branch before merging
3. ✅ Use descriptive commit messages
4. ✅ Communicate with your team about large merges
5. ✅ Review changes with `git log` or `git diff` before merging
6. ✅ Keep feature branches focused on a single feature or fix

---

## Additional Resources

- [Git Documentation](https://git-scm.com/doc)
- [Atlassian Git Merge Guide](https://www.atlassian.com/git/tutorials/using-branches/git-merge)
- [GitHub: Merging a Pull Request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/about-pull-request-merges)
