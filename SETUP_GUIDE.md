# 🚀 TailorAI Quick Setup Guide

Get your AI fashion analysis app running in 10 minutes!

## 📋 Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- Git

## 🔥 Step 1: Firebase Setup (5 minutes)

1. **Go to [Firebase Console](https://console.firebase.google.com/)**
2. **Create a new project** called "TailorAI"
3. **Enable Authentication:**
   - Go to Authentication > Sign-in method
   - Enable "Email/Password"
   - Enable "Google" (recommended)
   - Enable "Apple" (optional)
   - Enable "Facebook" (optional)

4. **Get your config:**
   - Go to Project Settings (gear icon)
   - Scroll down to "Your apps"
   - Click "Add app" > Web
   - Copy the config object

## ⚙️ Step 2: Backend Setup (3 minutes)

```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

**Edit `.env` file:**
```env
# Add your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here

# Database (use SQLite for quick start)
DATABASE_URL=sqlite:///./tailorai.db

# Optional: AWS S3 (skip for now)
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
```

## 🎨 Step 3: Frontend Setup (2 minutes)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create environment file
cp env.example .env
```

**Edit `.env` file with your Firebase config:**
```env
REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
REACT_APP_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=123456789
REACT_APP_FIREBASE_APP_ID=1:123456789:web:abcdef123456
```

## 🚀 Step 4: Run the App

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

**Open your browser:** `http://localhost:3000`

## 🎯 What You'll See

1. **Beautiful login page** with TailorAI branding
2. **Sign up/login** with email/password or social logins
3. **Camera interface** with real-time fashion analysis
4. **Live feedback** on your outfit proportions, colors, and style

## 📱 Mobile Testing

- **Desktop:** Works perfectly in any browser
- **Mobile:** Open `http://localhost:3000` on your phone
- **Tablet:** Responsive design adapts automatically

## 🔧 Troubleshooting

**Firebase errors:**
- Make sure all environment variables are set correctly
- Check that Authentication providers are enabled

**Camera not working:**
- Ensure you're using HTTPS (required for camera access)
- Allow camera permissions in your browser

**Backend errors:**
- Check that OpenAI API key is valid
- Ensure all Python dependencies are installed

## 🎉 Next Steps

Once it's running, you can:
1. **Test the fashion analysis** with your camera
2. **Customize the UI** colors and branding
3. **Deploy to production** (Vercel/Netlify)
4. **Convert to mobile app** using Capacitor

## 📞 Need Help?

- Check the console for error messages
- Verify all environment variables are set
- Make sure both backend and frontend are running

**Your TailorAI app is now ready to use! 🎊**
