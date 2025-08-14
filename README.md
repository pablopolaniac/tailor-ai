# TailorAI - AI-Powered Fashion Analysis App

A smart web application that analyzes your fashion choices using AI, providing personalized style feedback and outfit recommendations.

## ✨ Features

- **📸 Smart Camera Analysis**: Real-time fashion analysis using your device's camera
- **📱 Mobile-First Design**: Optimized for mobile devices with responsive UI
- **🎯 Full-Body Shot Support**: 5-second countdown timer with positioning guides
- **📤 Photo Upload Fallback**: Upload photos when camera isn't available
- **🎨 Style Matching**: Compare your outfit with reference style images
- **🌤️ Seasonal Recommendations**: Get season-appropriate fashion advice
- **🔍 Detailed Feedback**: Receive specific, actionable style improvement tips

## 🚀 Getting Started

### Prerequisites

- Node.js (v14 or higher)
- Python 3.8+
- Modern web browser with camera support

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/tailor-ai.git
   cd tailor-ai
   ```

2. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Install Backend Dependencies**
   ```bash
   cd ../backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables**
   ```bash
   cd ../frontend
   # Create .env file with your configuration
   HOST=0.0.0.0
   PORT=3001
   ```

### Running the Application

1. **Start the Backend Server**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. **Start the Frontend Development Server**
   ```bash
   cd frontend
   npm start
   ```

3. **Access the Application**
   - Desktop: `http://localhost:3001`
   - Mobile: Use your local network IP (e.g., `http://10.0.3.102:3001`)

## 📱 Mobile Usage

- **Camera Access**: Works best on HTTPS or local network
- **Photo Upload**: Fallback option for browsers without camera support
- **Positioning Guide**: Visual guides help you take perfect full-body shots
- **Countdown Timer**: 5-second timer gives you time to position yourself

## 🏗️ Architecture

- **Frontend**: React.js with Tailwind CSS
- **Backend**: Python FastAPI
- **AI Analysis**: Integration with fashion analysis API
- **Real-time**: WebSocket support for live feedback

## 🔧 Configuration

### Environment Variables

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 3001)
- `API_URL`: Backend API endpoint

### Camera Settings

- **Resolution**: 1280x720 (ideal), 640x360 (minimum)
- **Focus Mode**: Continuous autofocus
- **Facing Mode**: User (front) or Environment (back)

## 📸 Camera Troubleshooting

### iOS Safari Issues
- **Problem**: Camera not working
- **Solution**: Use photo upload feature or access via local network

### Permission Issues
- **Problem**: Camera access denied
- **Solution**: Allow camera permissions in browser settings

### Network Issues
- **Problem**: Can't access from phone
- **Solution**: Ensure both frontend and backend are running on the same network

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- React.js community for the amazing framework
- FastAPI for the high-performance backend
- Tailwind CSS for the beautiful styling
- All contributors who helped make this project possible

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the troubleshooting section above
- Ensure all dependencies are properly installed

---

**Made with ❤️ for fashion enthusiasts everywhere**
