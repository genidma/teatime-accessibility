# Cross-Device Sync Implementation - Game Plan

## Issue #132: Enable Sync Across Devices

### Summary
Implement cloud sync functionality to enable TeaTime sessions to be accessible across multiple devices (desktop/mobile). This will allow users to start a timer on one device and view history on another, with seamless synchronization.

### Motivation
- Users increasingly use multiple devices (work computer, personal laptop, phone)
- Critical for a modern productivity app to offer cross-device consistency
- Increases user engagement and retention
- Enables use cases like starting a session on desktop and reviewing later on mobile

### Proposed Solution
Use **Firebase Free Tier** as the backend service due to its ease of implementation, generous free limits, and comprehensive feature set.

**Why Firebase:**
- Free tier includes 50K reads/month, 20K writes/month, 2GiB storage
- Built-in authentication (Email, Google, etc.)
- Real-time database with automatic conflict resolution
- File storage for backups
- Excellent JavaScript/React SDKs
- No server management required

### Technical Approach

#### Firebase Project Setup

**Step 1: Create Firebase Project**
- [x] note: using the gv...mul.. account: Go to [Firebase Console](https://console.firebase.google.com/)
- [x] Click "Start new project" or "Create project"
- [x] Enter project name: "electron-main-dev-sync"
- [x] Select default account if prompted
- [x] Accept Firebase terms and conditions
- [x] Click "Create project"
- [x] Wait for project creation to complete (few minutes)
- [x] Click "Continue" to go to project overview

**Step 2: Enable Authentication**

- [x] **Navigate to Authentication**
  - [x] In the Firebase Console left sidebar, click on **"Authentication"**
  - [x] If not visible, expand the sidebar using the three-line menu icon (☰) in the top-left corner
  - [x] Look for the Authentication icon (key 🔒 or person 👤)

- [x] **Start Setting Up**
  - [x] On the Authentication screen, click the **"Get started"** button (blue button in center)
  - [x] This enables the Authentication service for your project

- [x] **Configure Sign-in Methods**
  - [x] Click on the **"Sign-in method"** tab (near top, next to "Users")
- [ ] Enable **Email/Password**:
    - [x] Find "Email/Password" in the list
    - [x] Toggle it to **"Enabled"**
    - [x] Optionally enable "Email link" as an alternative
    - [x] Scroll down and click **"Save"**
  - [x] Enable **Google** (recommended):
    - [x] Scroll to the Google provider
    - [x] Toggle it to **"Enabled"**
    - [x] Scroll down and click **"Save"**
- [x] **Important Notes**
  - [x] After each provider, always scroll down and click **"Save"** to apply changes
  - [x] For production, configure OAuth consent screen in Google Cloud Console
  - [x] Firebase free tier includes auth for up to 10,000 active users/month
  - [x] If a provider is missing, click "Add method" at bottom for more options
  
 **Step 3: Create Firestore Database**
- [ ] In left sidebar, click "Firestore Database"
- [ ] Click "Create database" button
- [ ] Choose "Start in production mode"
- [ ] Click "Next"
- [ ] Set up security rules (initially use default rules, will be updated later in code)
- [ ] Click "Enable"

**Step 4: Configure Firestore Security Rules**
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

**Step 5: Get Firebase Config for Application**
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

**Step 6: Enable Required APIs**
- [ ] In project settings, go to "Cloud Firestore" tab
- [ ] Ensure the Firestore API is enabled (usually enabled by default)
- [ ] Go to Google Cloud Console for your project
- [ ] Enable "Firebase Authentication API" if not already enabled

**Step 7: Set Up Billing (if needed)**
- [ ] Firebase free tier is generous, but if you exceed limits:
- [ ] In project settings, click "Use Google Cloud Platform"
- [ ] Enable billing if needed (free tier should be sufficient for development)

**Step 8: Install Firebase SDK**
- [ ] In your project terminal:
  ```bash
  npm install firebase
  ```

**Step 9: Initialize Firebase in Code**
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

**Step 10: Verify Setup**
- [ ] Run your application
- [ ] Check Firebase Console for active users and database writes
- [ ] Verify authentication is working
- [ ] Check Firestore for session documents being created

#### 1. Data Model

```javascript
// sessions collection
{
  id: string,
  categoryId: string,
  title: string,
  date: string, // YYYY-MM-DD
  time: string, // HH:MM:SS
  duration: number,
  notes: string | null,
  createdAt: string, // ISO timestamp
  updatedAt: string, // ISO timestamp
  deviceId: string, // for conflict detection
  userId: string    // authenticated user identifier (required)
}
```

**Important**: Every document must include a `userId` field that references the authenticated user. This enables data separation and ensures users can only access their own sessions.

#### 2. Authentication

- Implement Firebase Authentication
- Options: Email/Password, Google Sign-In
- Store user preferences in Firestore under user-specific collections

#### 3. Security Rules

Firestore security rules are critical for data separation:

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

These rules ensure users can only access documents where `userId` matches their authenticated ID.

#### 4. Sync Logic

- **Initial sync**: Download all user sessions on first login
- **Real-time sync**: Listen to Firestore updates for live synchronization
- **Push changes**: Save sessions to Firestore on any modification
- **Conflict resolution**: Use `updatedAt` timestamps (last write wins)

#### 5. UI Components

- **Sync status indicator**: Show connection state (syncing, online, offline)
- **Login screen**: Simple authentication flow
- **Account settings**: Manage account, logout, data export

### Implementation Tasks

#### Phase 1: Setup & Authentication
- [ ] 1. Create Firebase project and enable required services
- [ ] 2. Install Firebase SDK: `npm install firebase`
- [ ] 3. Create Firebase config file with API keys
- [ ] 4. Implement authentication UI (login, logout, signup)
- [ ] 5. Add authentication state persistence

#### Phase 2: Data Sync Infrastructure
- [ ] 6. Initialize Firestore in the app
- [ ] 7. Create data mappers for Session ↔ Firestore document conversion
- [ ] 8. Implement initial data fetch on login
- [ ] 9. Set up real-time listeners for session changes
- [ ] 10. Implement session save with Firestore writes

#### Phase 3: Conflict Handling & UX
- [ ] 11. Add `updatedAt` timestamps to session objects
- [ ] 12. Implement conflict detection using timestamps
- [ ] 13. Add sync status indicator in UI (top bar or settings)
- [ ] 14. Handle offline scenarios gracefully
- [ ] 15. Add data export functionality (JSON/CSV)

#### Phase 4: Testing & Polish
- [ ] 16. Write Playwright tests for sync flows
- [ ] 17. Test conflict scenarios
- [ ] 18. Test offline behavior
- [ ] 19. Add loading states and error handling
- [ ] 20. Polish UI with appropriate feedback messages

### Timeline Estimate
- **Week 1**: Firebase setup, authentication, initial data fetch
- **Week 2**: Real-time sync, conflict handling, sync status UI
- **Week 3**: Offline support, data export, testing, polish

### Potential Challenges
- **Conflict resolution**: Simple timestamp approach may lose data; consider 3-way merge for complex conflicts
- **Offline support**: Need service worker or local storage for offline edits
- **Performance**: Large datasets may require pagination
- **Security**: Firestore rules must be carefully configured

### Success Metrics
- Users can log in on multiple devices and see consistent session data
- Sync completes within 2 seconds for <100 sessions
- Conflict rate < 1% in normal usage
- App remains functional offline with manual sync

### Alternatives Considered
- **Supabase**: Similar to Firebase but requires more SQL knowledge
- **User's Cloud Storage**: Too complex, requires OAuth and custom sync logic
- **Self-Hosted**: Higher maintenance, not suitable for free tier

---
*Last updated: 2026-04-13T17:53:54-04:00*
    * created by kilo ai code [link](kilo.ai/install)
    * via: arcee trinity large thinking model [link](https://www.arcee.ai/trinity#trinity-large-thinking)
    * collaborator @genidma 
