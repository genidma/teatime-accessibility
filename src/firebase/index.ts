import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCeQeBzYRICCexeiZvPhoQX5UBDLBc6ZWY",
  authDomain: "electron-main-dev-sync.firebaseapp.com",
  projectId: "electron-main-dev-sync",
  storageBucket: "electron-main-dev-sync.firebasestorage.app",
  messagingSenderId: "973402365427",
  appId: "1:973402365427:web:158cc70d2f66e80f69c686",
  measurementId: "G-87Y08LM8WC"
};

// Initialize Firebase Application
export const app = initializeApp(firebaseConfig);
export const analytics = getAnalytics(app);
export const auth = getAuth(app);
export const db = getFirestore(app);
