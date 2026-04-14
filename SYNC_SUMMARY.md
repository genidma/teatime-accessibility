# Note: This document outlines steps to be undertaken via [issue #134](https://github.com/genidma/teatime-accessibility/issues/134) directly via GitHub

## Repository Restructuring Plan - kc-rhythm

**Author:** kilo (Trinity Large Thinking model by Arcee AI)  
**Requestor/Collaborator:** @genidma

---

**Checklist:**

### 1. Clean Up Stale Branches in Main Repository
Before creating the new repository, clean up stale branches in the main repository:

**Using Git CLI:**
```bash
# List branches to identify stale ones
git branch -r | grep electron

# Delete stale branches locally (if they exist)
git push origin --delete electron-kcresonance 2>/dev/null || true
git push origin --delete electron-photosensitive-dev 2>/dev/null || true
```

**Using GitHub Website:**
1. Go to GitHub.com and navigate to the main repository
2. Click on **"Branches"** in the left sidebar
3. Find stale branches (`electron-kcresonance`, `electron-photosensitive-dev`)
4. Click the **trash can icon** next to each branch to delete
5. Confirm deletion

**Important**: Ensure you no longer need these branches before deleting. Export any necessary data first.

### 2. Create New Standalone Repository from `electron-main-dev`
- [ ] Create repository from `electron-main-dev` branch:
  ```bash
  gh repo create kc-rhythm --description "Cross-Device Cloud Sync - kc-rhythm" --public --source=.
  ```
- [ ] Push to new repository:
  ```bash
  git push kc-rhythm electron-main-dev:main --force
  ```
- [ ] Set upstream tracking:
  ```bash
  git branch -u sync-origin/main
  ```

*Alternative name options:*
- [ ] `kc-rhythm` (distinct)
- [ ] `teatime-electron-sync` (specific)

### 3. Update README and Documentation
- [ ] Update README.md to reflect new project purpose
- [ ] Add contribution guidelines
- [ ] Update any references to old repository

### 4. Verify Repository
- [ ] Clone test: `git clone https://github.com/yourusername/kc-rhythm.git`
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