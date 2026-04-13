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

#### Database Options Comparison for Cross-Device Sync

##### PostgreSQL (Data Connect)
**Supabase** (Recommended SQL alternative)
- Open-source Firebase alternative
- Full PostgreSQL capabilities
- Real-time subscriptions
- Generous free tier (2GiB data, 10K daily rows)
- RESTful API and GraphQL support
- Self-hostable option

**Self-Hosted Node.js + PostgreSQL**
- Maximum flexibility and control
- Full SQL capabilities
- Can use any PostgreSQL-compatible database
- No vendor lock-in
- Requires server hosting and maintenance
- Higher development effort

##### NoSQL (Document Databases)
**Firebase Firestore**
- Real-time sync out of the box
- Built-in authentication and security rules
- Generous free tier (50K reads/month, 20K writes/month, 2GiB storage)
- Excellent JavaScript SDKs
- No server management required
- Automatic conflict resolution

**Firebase Realtime Database**
- Original Firebase NoSQL database
- Real-time sync with simpler data model
- Free tier includes 10GiB storage
- Slightly less structured than Firestore
- Good for simple key-value storage

##### Object Storage (File/Object Storage)
**Firebase Storage**
- Simple file upload and download
- Integrated with Firebase Authentication
- 10GiB free storage
- Easy to use with Firebase SDK
- Good for storing user-generated content

**Google Cloud Storage**
- More powerful object storage
- Multiple storage classes (Standard, Nearline, Coldline)
- Fine-grained access control
- Integrates with Firebase Authentication via Cloud Functions
- More complex setup

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
*Last updated: 2026-04-13T20:00:54-04:00*
* created by kilo ai code [link](kilo.ai/install)
* via: arcee trinity large thinking model [link](https://www.arcee.ai/trinity#trinity-large-thinking-is-free-in)
* collaborator @genidma
