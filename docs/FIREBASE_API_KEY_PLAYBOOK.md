# Firebase API Key Playbook

This repo no longer keeps the Firebase web config hardcoded in source.

## Where the config lives

- Local only: `.env.local`
- Tracked template: `.env.example`
- Read by app: `src/firebase/index.ts`
- Typed for Vite: `src/vite-env.d.ts`

## Important note

This is a Firebase web API key, not a service account private key.
Firebase documents that these web API keys are not secrets in the usual sense, but they should still be restricted, rotated carefully, and removed from tracked source when they trigger an alert.

## Normal setup

1. Open `.env.local`.
2. Paste the current Firebase web app values into the `VITE_FIREBASE_*` fields.
3. Keep real values out of `.env.example`.
4. Start the app and verify Firebase Auth / Firestore still work.

## Moving to another machine

1. Copy the repo as usual with git.
2. Use `.env.example` as the template to create a new `.env.local`.
3. Fill in the real `VITE_FIREBASE_*` values from the Firebase console.

Do not expect `.env.local` to come across with git. It stays local on purpose.

## If GitHub flags the key again

1. Confirm whether the key appears in current files or git history.
2. In Google Cloud Console for the Firebase project, rotate the key if the app still uses it.
3. Update `.env.local` with the replacement key and matching Firebase config values.
4. Test the app before revoking the old key.
5. Revoke or delete the previous key after the app is using the new one.
6. Review usage logs and quotas for suspicious activity.
7. Close the alert as revoked.

## Helpful checks

Current working tree:

```powershell
git status --short
```

Find Firebase config references:

```powershell
rg -n "VITE_FIREBASE_|firebaseConfig|initializeApp" src .env.example .env.local
```

Check whether a specific key value ever existed in git history:

```powershell
git log -S "PASTE_KEY_HERE" --oneline --all
```

## Notes for this repo

- `.env.local` is ignored by git and is the right place for the live Firebase config.
- `src/firebase/index.ts` throws a clear error if any required Firebase env var is missing.
- If Firebase packages are missing locally, install dependencies before running TypeScript checks.
