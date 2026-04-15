import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getFirestore, enableIndexedDbPersistence } from "firebase/firestore";

function getRequiredEnvVar(name: keyof ImportMetaEnv): string {
  const value = import.meta.env[name];

  if (!value) {
    throw new Error(`[firebase] Missing required environment variable: ${name}`);
  }

  return value;
}

const firebaseConfig = {
  apiKey: getRequiredEnvVar("VITE_FIREBASE_API_KEY"),
  authDomain: getRequiredEnvVar("VITE_FIREBASE_AUTH_DOMAIN"),
  projectId: getRequiredEnvVar("VITE_FIREBASE_PROJECT_ID"),
  storageBucket: getRequiredEnvVar("VITE_FIREBASE_STORAGE_BUCKET"),
  messagingSenderId: getRequiredEnvVar("VITE_FIREBASE_MESSAGING_SENDER_ID"),
  appId: getRequiredEnvVar("VITE_FIREBASE_APP_ID"),
  measurementId: getRequiredEnvVar("VITE_FIREBASE_MEASUREMENT_ID"),
};

// Initialize Firebase Application
export const app = initializeApp(firebaseConfig);
export const analytics = getAnalytics(app);
export const auth = getAuth(app);
export const db = getFirestore(app);

// Enable Offline Persistence
if (typeof window !== 'undefined') {
  enableIndexedDbPersistence(db).catch((err) => {
    if (err.code === 'failed-precondition') {
      // Multiple tabs open, persistence can only be enabled in one tab at a time.
      console.warn('[firebase] Persistence failed: Multiple tabs open');
    } else if (err.code === 'unimplemented') {
      // The current browser does not support all of the features required to enable persistence
      console.warn('[firebase] Persistence failed: Browser not supported');
    }
  });
}
