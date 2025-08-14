# TailorAI Frontend

A beautiful React web application for AI-powered fashion analysis with real-time camera feedback.

## 🚀 Features

- **Real-time Camera Analysis**: Live fashion feedback using your device's camera
- **Firebase Authentication**: Secure login with email/password, Google, Apple, and Facebook
- **Beautiful UI**: Modern, responsive design with smooth animations
- **Auto Analysis**: Continuous fashion feedback every 5 seconds
- **Manual Analysis**: On-demand analysis with custom settings
- **Mobile Responsive**: Works perfectly on desktop, tablet, and mobile devices

## 🛠️ Tech Stack

- **React 18** - Modern React with hooks
- **Firebase Auth** - Authentication with multiple providers
- **React Webcam** - Camera integration
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations
- **Axios** - HTTP client for API calls
- **React Router** - Client-side routing
- **React Hot Toast** - Beautiful notifications

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TailorAIApp/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your Firebase configuration:
   ```env
   REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
   REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   REACT_APP_FIREBASE_PROJECT_ID=your_project_id
   REACT_APP_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
   REACT_APP_FIREBASE_MESSAGING_SENDER_ID=123456789
   REACT_APP_FIREBASE_APP_ID=1:123456789:web:abcdef123456
   ```

4. **Start the development server**
   ```bash
   npm start
   ```

5. **Open your browser**
   Navigate to `http://localhost:3000`

## 🔧 Firebase Setup

1. **Create a Firebase project**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create a new project
   - Enable Authentication

2. **Configure Authentication providers**
   - Go to Authentication > Sign-in method
   - Enable Email/Password
   - Enable Google (recommended)
   - Enable Facebook (optional)
   - Enable Apple (optional)

3. **Get your configuration**
   - Go to Project Settings
   - Copy the Firebase config object
   - Update your `.env` file

## 📱 Usage

1. **Sign Up/Login**
   - Create an account with email/password
   - Or use Google, Apple, or Facebook login

2. **Camera Analysis**
   - Turn on your camera
   - Choose analysis mode (General or Style Match)
   - Get real-time fashion feedback

3. **Settings**
   - Adjust analysis intervals
   - Change camera quality
   - Customize preferences

## 🎨 UI Components

- **Login/Register**: Beautiful authentication forms
- **Camera Interface**: Real-time camera feed with controls
- **Feedback Panel**: Live fashion analysis results
- **Settings Modal**: Customizable preferences
- **Responsive Design**: Works on all screen sizes

## 🔒 Security

- Protected routes requiring authentication
- Secure Firebase authentication
- HTTPS in production
- No sensitive data stored locally

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Vercel (Recommended)
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Follow the prompts

### Deploy to Netlify
1. Build the project: `npm run build`
2. Drag the `build` folder to Netlify

## 📱 Mobile App Conversion

This React web app can be easily converted to a mobile app using:

- **Capacitor**: Convert to native mobile app
- **React Native Web**: Share code between web and mobile
- **PWA**: Progressive Web App for mobile-like experience

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support, email support@tailorai.com or create an issue in the repository.
