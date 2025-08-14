import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, FacebookAuthProvider, OAuthProvider } from 'firebase/auth';

// Your Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyADQR8XSP34xxPoc75IRWzY3g3K-DFP2ig",
  authDomain: "tailorai-e07a2.firebaseapp.com",
  projectId: "tailorai-e07a2",
  storageBucket: "tailorai-e07a2.firebasestorage.app",
  messagingSenderId: "918717897683",
  appId: "1:918717897683:web:ed8d59b7259d7764ac6d26",
  measurementId: "G-TEZ3SBB3N3"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication
export const auth = getAuth(app);

// Configure providers
export const googleProvider = new GoogleAuthProvider();
export const facebookProvider = new FacebookAuthProvider();
export const appleProvider = new OAuthProvider('apple.com');

// Configure provider settings
googleProvider.setCustomParameters({
  prompt: 'select_account'
});

facebookProvider.setCustomParameters({
  display: 'popup'
});

appleProvider.setCustomParameters({
  locale: 'en_US'
});

export default app;
