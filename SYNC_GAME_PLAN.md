# Game Plan: Enable Cross-Device Sync (Issue #132)

## Overview
Implement cloud sync functionality to enable TeaTime sessions to be accessible across multiple devices (desktop/mobile). This will allow users to start a timer on one device and view history on another, with seamless synchronization.

## Step-by-Step Implementation Plan

### Step 1: Create Firebase Project and Enable Services
- [ ] Go to [Firebase Console](https://console.firebase.google.com/)
- [ ] Click "Start new project" or "Create project"
- [ ] Enter project name: "TeaTime-Sync"
- [ ] Select default account if prompted
- [ ] Accept Firebase terms and conditions
- [ ] Click "Create project"
- [ ] Wait for project creation to complete (few minutes)
- [ ] Click "Continue" to go to project overview

### Step 2: Enable Authentication
- [ ] In left sidebar, click "Authentication"
- [ ] Click "Get started" button
- [ ] Click "Sign-in method" tab
- [ ] Enable **Email/Password**:
  - [ ] Find "Email/Password" in the list
  - [ ] Toggle it to **"Enabled"**
  - [ ] Optionally enable "Email link" as an alternative
  - [ ] Scroll down and click **"Save"**
- [ ] Enable **Google** (recommended):
  - [ ] Scroll down to the Google provider
  - [ ] Toggle it to **"Enabled"**
  - [ ] Scroll down and click **"Save"**
- [ ] (Optional) Enable **GitHub**:
  - [ ] Scroll to the GitHub provider
  - [ ] Toggle it to **"Enabled"**
  - [ ] Click the **"OAuth Client ID"** link to register your app with GitHub
  - [ ] A new window will open - sign in to GitHub and fill in the form:
    - **Application name**: TeaTime Sync
    - **Homepage URL**: Your app's homepage (or leave blank if none)
    - **Authorization callback URL**: `https://<your-project-id>.firebaseapp.com/__/auth/handler` (replace with your Firebase project domain)
  - [ ] After registering, copy the **Client ID** and **Client Secret** back to Firebase
  - [ ] Scroll down and click **"Save"** in Firebase
- [ ] **Important**: After each provider, always scroll down and click **"Save"** to apply changes
- [ ] For production, configure OAuth consent screen in Google Cloud Console
- [ ] Firebase free tier includes auth for up to 10,000 active users/month

### Step 3: Create Firestore Database
- [ ] In left sidebar, click "Firestore Database"
- [ ] Click "Create database" button
- [ ] Choose "Start in production mode"
- [ ] Click "Next"
- [ ] Set up security rules (initially use default rules, will be updated later in code)
- [ ] Click "Enable"

### Step 4: Configure Firestore Security Rules
- [ ] In Firestore Database section, click "Rules" tab
- [ ] Replace default rules with initial rules (will be updated in code):
  ```
  rules_version = '2';
  service cloud.firestore {
    match /databases/{database}/documents {
      match /sessions/{sessionId} {
        allow read, write: if request.auth != null && resource.data.userId == request.auth.uid;
      }
    }
  }
  ```
- [ ] Click "Publish" (will be updated later when implementing security logic)

### Step 5: Get Firebase Config for Application
- [ ] In project settings (gear icon), go to "Your apps" section
- [ ] Click the web icon ("</>") to register web app
- [ ] Enter app nickname (e.g., "TeaTime-Web")
- [ ] Click "Register app"
- [ ] Copy the Firebase config object:
  ```javascript
  const firebaseConfig = {
    apiKey: "AIza...",
    authDomain: "teatime-sync.firebaseapp.com",
    projectId: "teatime-sync",
    storageBucket: "teatime-sync.appspot.com",
    messagingSenderId: "123456789",
    appId: "1:123456789:web:abcdef123456"
  };
  ```
- [ ] Save this config in your application (e.g., `src/firebase/config.ts`)

### Step 6: Enable Required APIs
- [ ] In project settings, go to "Cloud Firestore" tab
- [ ] Ensure the Firestore API is enabled (usually enabled by default)
- [ ] Go to Google Cloud Console for your project
- [ ] Enable "Firebase Authentication API" if not already enabled

### Step 7: Set Up Billing (if needed)
- [ ] Firebase free tier is generous, but if you exceed limits:
- [ ] In project settings, click "Use Google Cloud Platform"
- [ ] Enable billing if needed (free tier should be sufficient for development)

### Step 8: Install Firebase SDK
- [ ] In your project terminal:
  ```bash
  npm install firebase
  ```

### Step 9: Initialize Firebase in Code
- [ ] Create initialization file (e.g., `src/firebase/index.ts`):
  ```typescript
  import { initializeApp } from 'firebase/app';
  import { getAuth } from 'firebase/auth';
  import { getFirestore } from 'firebase/firestore';
  
  const firebaseConfig = { /* your config from step 5 */ };
  
  // Initialize Firebase
  const app = initializeApp(firebaseConfig);
  export const auth = getAuth(app);
  export const db = getFirestore(app);
  ```

### Step 10: Verify Setup
- [ ] Run your application
- [ ] Check Firebase Console for active users and database writes
- [ ] Verify authentication is working
- [ ] Check Firestore for session documents being created

## Implementation Phases (Detailed Tasks)

### Phase 1: Setup & Authentication
- [ ] 1. Create Firebase project and enable required services
- [ ] 2. Install Firebase SDK: `npm install firebase`
- [ ] 3. Create Firebase config file with API keys
- [ ] 4. Implement authentication UI (login, logout, signup)
- [ ] 5. Add authentication state persistence

### Phase 2: Data Sync Infrastructure
- [ ] 6. Initialize Firestore in the app
- [ ] 7. Create data mappers for Session ↔ Firestore document conversion
- [ ] 8. Implement initial data fetch on login
- [ ] 9. Set up real-time listeners for session changes
- [ ] 10. Implement session save with Firestore writes

### Phase 3: Conflict Handling & UX
- [ ] 11. Add `updatedAt` timestamps to session objects
- [ ] 12. Implement conflict detection using timestamps
- [ ] 13. Add sync status indicator in UI (top bar or settings)
- [ ] 14. Handle offline scenarios gracefully
- [ ] 15. Add data export functionality (JSON/CSV)

### Phase 4: Testing & Polish
- [ ] 16. Write Playwright tests for sync flows
- [ ] 17. Test conflict scenarios
- [ ] 18. Test offline behavior
- [ ] 19. Add loading states and error handling
- [ ] 20. Polish UI with appropriate feedback messages

## Timeline Estimate
- **Week 1**: Firebase setup, authentication, initial data fetch
- **Week 2**: Real-time sync, conflict handling, sync status UI
- **Week 3**: Offline support, data export, testing, polish

## Potential Challenges
- **Conflict resolution**: Simple timestamp approach may lose data; consider 3-way merge for complex conflicts
- **Offline support**: Need service worker or local storage for offline edits
- **Performance**: Large datasets may require pagination
- **Security**: Firestore rules must be carefully configured

## Success Metrics
- Users can log in on multiple devices and see consistent session data
- Sync completes within 2 seconds for <100 sessions
- Conflict rate < 1% in normal usage
- App remains functional offline with manual sync

## Alternatives Considered
- **Supabase**: Similar to Firebase but requires more SQL knowledge
- **User's Cloud Storage**: Too complex, requires OAuth and custom sync logic
- **Self-Hosted**: Higher maintenance, not suitable for free tier

---
*Last updated: 2026-04-13T20:00:54-04:00*