# Note: This document outlines steps to be undertaken via [issue #134](https://github.com/genidma/teatime-accessibility/issues/134) directly via GitHub

## Repository Restructuring Plan - Sync Across Devices

**Author:** kilo (Trinity Large Thinking model by Arcee AI)  
**Requestor/Collaborator:** @genidma

---

**Checklist:**

### 1. Clean Up Stale Repositories

**Using GitHub CLI (recommended):**
```bash
# List all repositories to identify stale ones
gh repo list --repo genidma/teatime-accessibility --limit 20

# Delete obsolete electron repositories
gh repo delete electron-kcresonance --confirm
gh repo delete electron-photosensitive-dev --confirm
```

**Alternative: Using GitHub Website**
1. Go to GitHub.com and navigate to your repositories
2. For each stale repository (e.g., `electron-kcresonance`, `electron-photosensitive-dev`):
   - Open the repository page
   - Click **Settings** (gear icon)
   - Scroll down and click **"Delete this repository"**
   - Type the repository name to confirm deletion

**Important**: Ensure you no longer need these repositories before deleting. Export any necessary data first.

*Checklist:*
- [ ] Identify stale electron repositories
- [ ] Delete `electron-kcresonance` (if exists)
- [ ] Delete `electron-photosensitive-dev` (if exists)
- [ ] Verify deletion in GitHub UI

### 2. Create New Standalone Repository
- [ ] Create repository from `electron-main-dev` branch:
  ```bash
  gh repo create teatime-sync --description "TeaTime Sync - Cross-Device Cloud Sync" --public --source=.
  ```
- [ ] Push to new repository:
  ```bash
  git push teatime-sync electron-main-dev:main --force
  ```
- [ ] Set upstream tracking:
  ```bash
  git branch -u sync-origin/main
  ```

*Alternative name options:*
- [ ] `kcresonance` (distinct)
- [ ] `teatime-electron-sync` (specific)

### 3. Update README and Documentation
- [ ] Update README.md to reflect new project purpose
- [ ] Add contribution guidelines
- [ ] Update any references to old repository

### 4. Verify Repository
- [ ] Clone test: `git clone https://github.com/yourusername/teatime-sync.git`
- [ ] Verify history: `git log --oneline` (should show `electron-main-dev` history)

### 5. Clean Up Local Branches
- [ ] Delete stale branches locally:
  - [ ] `git branch -D electron-kcresonance`
  - [ ] `git branch -D electron-photosensitive-dev`
- [ ] Keep `electron-main-dev` for further development if needed

### 6. Decide on Repository Visibility
- [ ] Choose **Public** (accept contributions) or **Private** (experimental)

### 7. Archive or Rename Original Branch
- [ ] Keep `electron-main-dev` as archive branch
- [ ] Consider renaming to `sync-dev` if continuing work

---

## Key Considerations
- Ensure all sync functionality is properly tested before split
- Maintain commit history from `electron-main-dev`
- Update any hardcoded references to old repository paths
- Verify Firebase configuration works in new environment

---
*Last updated: 2026-04-13T21:35:54-04:00*
*Created by: kilo (Trinity Large Thinking model by Arcee AI)*
*Requestor: @genidma*