import React, { useState, useRef, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Camera, 
  CameraOff, 
  Settings, 
  Sparkles, 
  User,
  LogOut,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import axios from 'axios';

// Utilities
const isiOS = () => /iPad|iPhone|iPod/.test(navigator.userAgent);
const isSecureContextNeeded = () => {
  // Allow localhost and local IP addresses for development
  const isLocalhost = location.hostname.includes("localhost") || 
                     location.hostname.includes("127.0.0.1") ||
                     location.hostname.match(/^10\.|^192\.168\.|^172\.(1[6-9]|2[0-9]|3[0-1])\./);
  return !isLocalhost && location.protocol !== "https:";
};

// Ensure video has metadata before we read videoWidth/Height (prevents 0x0 canvas on iOS)
async function waitForVideoReady(video) {
  if (!video) return;
  if (video.readyState >= 2 && video.videoWidth && video.videoHeight) return;
  await new Promise((resolve) => {
    const onLoaded = () => {
      video.removeEventListener("loadedmetadata", onLoaded);
      resolve();
    };
    video.addEventListener("loadedmetadata", onLoaded, { once: true });
  });
}

// Build constraints with a safe fallback for iOS
function buildConstraints(facing = "environment") {
  // iOS behaves better with 'exact' only if the camera exists; else fall back to 'ideal'
  const facingConstraint = [{ facingMode: { exact: facing } }, { facingMode: { ideal: facing } }];

  return {
    audio: false,
    video: {
      // try exact first, then ideal
      ...(facingConstraint[0]),
      width: { ideal: 1280, min: 640 },
      height: { ideal: 720, min: 360 },
      // improve AF on some Androids
      focusMode: "continuous",
    },
  };
}

const CameraAnalysis = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const { currentUser, logout } = useAuth();
  
  // State for camera and analysis
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [isInitializing, setIsInitializing] = useState(false);
  const [cameraError, setCameraError] = useState(null);
  const [analysisMode, setAnalysisMode] = useState('outfit');
  const [season, setSeason] = useState('summer');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [feedback, setFeedback] = useState([]);
  const [overlayData, setOverlayData] = useState({});
  const [confidenceScore, setConfidenceScore] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [styleImages, setStyleImages] = useState([]);
  const [showStyleUpload, setShowStyleUpload] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [cameraPermission, setCameraPermission] = useState(null);
  const [stream, setStream] = useState(null);
  const [facingMode, setFacingMode] = useState("environment"); // "user" | "environment"
  const [availableCameras, setAvailableCameras] = useState([]);
  const [countdown, setCountdown] = useState(0);
  const [isCountingDown, setIsCountingDown] = useState(false);

  // Detect mobile device
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
  const isSafari = /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent);
  const isChrome = /Chrome/.test(navigator.userAgent);

  // Debug information
  useEffect(() => {
    console.log('Device Info:', {
      userAgent: navigator.userAgent,
      isMobile: isMobile,
      isIOS: isIOS,
      isSafari: isSafari,
      isChrome: isChrome,
      mediaDevices: !!navigator.mediaDevices,
      getUserMedia: !!navigator.mediaDevices?.getUserMedia,
    });
  }, [isMobile, isIOS, isSafari, isChrome]);

  // Device discovery effect
  useEffect(() => {
    async function listCams() {
      try {
        if (!navigator.mediaDevices?.enumerateDevices) return;
        const devices = await navigator.mediaDevices.enumerateDevices();
        const cams = devices.filter((d) => d.kind === "videoinput");
        setAvailableCameras(cams);
      } catch (e) {
        console.log("enumerateDevices failed:", e);
      }
    }
    listCams();
    navigator.mediaDevices?.addEventListener?.("devicechange", listCams);
    return () => navigator.mediaDevices?.removeEventListener?.("devicechange", listCams);
  }, []);

  // Check camera permissions
  const checkCameraPermission = async () => {
    try {
      if (navigator.permissions && navigator.permissions.query) {
        const permission = await navigator.permissions.query({ name: 'camera' });
        setCameraPermission(permission.state);
        return permission.state;
      }
      return 'granted';
    } catch (error) {
      console.log('Permission check failed:', error);
      return 'granted';
    }
  };

  // Simple camera test
  const testCamera = async () => {
    try {
      console.log('Testing camera with native getUserMedia...');
      
      const testStream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'user' },
        audio: false 
      });
      
      console.log('Camera test successful:', testStream);
      testStream.getTracks().forEach(track => track.stop());
      return true;
    } catch (error) {
      console.error('Camera test failed:', error);
      toast.error(`Camera test failed: ${error.message}`);
      return false;
    }
  };

  // Start camera with native HTML5 video - mobile-safe version
  const startCamera = async () => {
    try {
      // Check if getUserMedia is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Camera not supported in this browser. Please use the photo upload option.");
      }

      // Close any previous stream first
      if (stream) {
        stream.getTracks().forEach((t) => t.stop());
      }

      const constraints = buildConstraints(facingMode);
      console.log("Requesting camera with constraints:", constraints);

      let videoStream;
      try {
        videoStream = await navigator.mediaDevices.getUserMedia(constraints);
      } catch (errExact) {
        // If 'exact' facingMode fails, retry with 'ideal' or without facingMode
        console.warn("Exact facingMode failed, retrying with ideal/any camera:", errExact);
        videoStream = await navigator.mediaDevices.getUserMedia({
          audio: false,
          video: { facingMode: { ideal: facingMode } },
        });
      }

      if (!videoRef.current) return;

      videoRef.current.srcObject = videoStream;

      // Wait until metadata is ready so videoWidth/Height are valid (for capture)
      await waitForVideoReady(videoRef.current);

      await videoRef.current.play().catch(() => {
        // On iOS, play() might require a user gesture; your UI buttons already provide that
      });

      setStream(videoStream);
      setIsCameraOn(true);
      setCameraError(null);
      toast.success("Camera started!");
    } catch (error) {
      console.error("Failed to start camera:", error);
      let msg = error?.message || "Failed to start camera. Please try again.";
      if (error.name === "NotAllowedError") {
        msg = "Camera access denied. Please allow camera permissions in your browser settings.";
      } else if (error.name === "NotFoundError") {
        msg = "No camera found on this device.";
      } else if (error.name === "OverconstrainedError") {
        msg = "Camera does not support the requested settings.";
      } else if (error.message.includes("not implemented")) {
        msg = "Camera not supported in this browser. Please use the photo upload option below.";
      }
      setCameraError(msg);
      toast.error(msg);
    }
  };

  // Switch camera handler
  const switchCamera = async () => {
    try {
      const next = facingMode === "user" ? "environment" : "user";
      setFacingMode(next);
      // restart with new facingMode
      await startCamera();
    } catch (e) {
      console.error("Switch camera failed:", e);
      toast.error("Could not switch camera");
    }
  };

  // Stop camera
  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraOn(false);
    setCameraError(null);
    setFeedback([]);
    setOverlayData({});
    setConfidenceScore(0);
    setIsPaused(false);
  };

  // Simplified camera toggle
  const handleCameraToggle = async () => {
    if (isCameraOn) {
      stopCamera();
    } else {
      setIsInitializing(true);
      setCameraError(null);
      
      try {
        await startCamera();
      } catch (error) {
        console.error('Camera initialization error:', error);
        setCameraError('Failed to start camera. Please try again.');
      } finally {
        setIsInitializing(false);
      }
    }
  };

  // Capture image from video stream - mobile-safe version
  const captureImage = () => {
    if (!videoRef.current || !canvasRef.current || isAnalyzing) return null;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    // Guard: if metadata didn't load yet
    const vw = video.videoWidth;
    const vh = video.videoHeight;
    if (!vw || !vh) {
      console.warn("Video metadata not ready yet, skipping capture this tick.");
      return null;
    }

    canvas.width = vw;
    canvas.height = vh;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", 0.8);
  };

  // Start countdown for photo capture
  const startCountdown = () => {
    if (!isCameraOn || isAnalyzing || isCountingDown) return;
    
    setIsCountingDown(true);
    setCountdown(5); // 5 second countdown
    
    const timer = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          setIsCountingDown(false);
          // Auto-capture when countdown reaches 0
          setTimeout(() => {
            capture();
          }, 500); // Small delay to show "0"
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  // Capture and analyze frame
  const capture = async () => {
    if (!isCameraOn || isAnalyzing) return;

    try {
      setIsAnalyzing(true);
      const imageSrc = captureImage();
      
      if (!imageSrc) {
        toast.error('Failed to capture image');
        return;
      }

      // Convert to base64
      const base64Data = imageSrc.split(',')[1];
      
      // Prepare request payload
      const payload = {
        mode: analysisMode === 'outfit' ? 'general' : 'style',
        frame_b64: base64Data,
        season: season,
        style_profile: styleImages.length > 0 ? {
          images: styleImages.map(img => img.data)
        } : null
      };

      console.log('Sending analysis request:', {
        mode: payload.mode,
        season: payload.season,
        hasStyleImages: !!payload.style_profile
      });

      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.feedback && result.feedback.length > 0) {
        setFeedback(result.feedback);
        setOverlayData(result.overlay_data || {});
        setConfidenceScore(result.confidence_score || 0);
        toast.success('Analysis complete!');
      } else {
        toast.error('No feedback received');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error('Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Analyze fashion
  const analyzeFashion = useCallback(async () => {
    if (!isCameraOn) {
      toast.error('Please turn on the camera first');
      return;
    }

    await capture();
  }, [isCameraOn, capture]);

  // Handle logout
  const handleLogout = async () => {
    try {
      await logout();
      toast.success('Logged out successfully');
    } catch (error) {
      toast.error('Failed to log out');
    }
  };

  // Handle style image upload
  const handleStyleImageUpload = (event) => {
    const files = Array.from(event.target.files);
    if (files.length > 5) {
      toast.error('Maximum 5 images allowed');
      return;
    }
    
    const newImages = files.map(file => ({
      id: Date.now() + Math.random(),
      file: file,
      preview: URL.createObjectURL(file)
    }));
    
    setStyleImages(prev => [...prev, ...newImages]);
    toast.success(`${files.length} image(s) uploaded`);
  };

  // Handle photo upload for analysis (fallback when camera doesn't work)
  const handlePhotoUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setIsAnalyzing(true);
      
      // Convert file to base64
      const reader = new FileReader();
      reader.onload = async (e) => {
        const base64Data = e.target.result.split(',')[1];
        
        // Prepare request payload
        const payload = {
          mode: analysisMode === 'outfit' ? 'general' : 'style',
          frame_b64: base64Data,
          season: season,
          style_profile: styleImages.length > 0 ? {
            images: styleImages.map(img => img.data)
          } : null
        };

        console.log('Sending uploaded photo for analysis:', {
          mode: payload.mode,
          season: payload.season,
          hasStyleImages: !!payload.style_profile
        });

        const response = await fetch('/api/analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.feedback && result.feedback.length > 0) {
          setFeedback(result.feedback);
          setOverlayData(result.overlay_data || {});
          setConfidenceScore(result.confidence_score || 0);
          toast.success('Analysis complete!');
        } else {
          toast.error('No feedback received');
        }
      };
      
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('Photo analysis error:', error);
      toast.error('Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Remove style image
  const removeStyleImage = (id) => {
    setStyleImages(prev => prev.filter(img => img.id !== id));
  };

  // Auto-analyze every 10 seconds when camera is on and not paused
  useEffect(() => {
    let interval;
    if (isCameraOn && !isAnalyzing && !isPaused) {
      interval = setInterval(() => {
        analyzeFashion();
      }, 10000);
    }
    return () => clearInterval(interval);
  }, [isCameraOn, isAnalyzing, isPaused, analyzeFashion]);

  // Check camera permission on component mount
  useEffect(() => {
    checkCameraPermission();
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [stream]);

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <div className="bg-black border-b border-gray-800">
        <div className="px-4 py-3">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <Camera className="w-6 h-6 text-purple-400 mr-2" />
              <h1 className="text-lg font-bold text-white">TailorAI</h1>
            </div>
            
            <div className="flex items-center space-x-2">
              {currentUser && (
                <div className="hidden sm:flex items-center space-x-2">
                  <User className="w-4 h-4 text-gray-400" />
                  <span className="text-xs text-gray-400 truncate max-w-20">
                    {currentUser.email || currentUser.displayName}
                  </span>
                </div>
              )}
              
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
              >
                <Settings className="w-5 h-5" />
              </button>
              
              <button
                onClick={handleLogout}
                className="p-2 text-gray-400 hover:text-red-400 rounded-lg hover:bg-gray-800 transition-colors"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Layout - Hidden on desktop */}
      <div className="block xl:hidden">
        <div className="flex flex-col h-[calc(100vh-80px)]">
          {/* Camera Section - Full Screen on Mobile */}
          <div className="flex-1 relative bg-black">
            {/* Camera View */}
            <div className="relative w-full h-full">
              {isCameraOn ? (
                <video
                  ref={(el) => {
                    videoRef.current = el;
                    if (!el) return;
                    // iOS-specific inline playback flags
                    el.setAttribute("playsinline", "true");
                    el.setAttribute("webkit-playsinline", "true");
                    el.muted = true; // required for autoplay on mobile
                    el.autoplay = true;
                  }}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full bg-gray-900 flex items-center justify-center">
                  <div className="text-center text-gray-400 px-4">
                    {isInitializing ? (
                      <>
                        <Loader2 className="w-16 h-16 mx-auto mb-4 animate-spin" />
                        <p className="text-lg">Starting camera...</p>
                        <p className="text-sm">Please wait</p>
                      </>
                    ) : cameraError ? (
                      <>
                        <AlertCircle className="w-16 h-16 mx-auto mb-4 text-red-400" />
                        <p className="text-lg text-red-400 mb-2">Camera Error</p>
                        <p className="text-sm text-gray-300 mb-4">{cameraError}</p>
                        <div className="space-y-3">
                          <button
                            onClick={handleCameraToggle}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                          >
                            Try Camera Again
                          </button>
                          
                          <div className="text-center">
                            <p className="text-sm text-gray-400 mb-2">Or upload a photo instead:</p>
                            <label className="inline-block px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors cursor-pointer">
                              📷 Upload Photo
                              <input
                                type="file"
                                accept="image/*"
                                onChange={handlePhotoUpload}
                                className="hidden"
                              />
                            </label>
                          </div>
                        </div>
                      </>
                    ) : (
                      <>
                        <Camera className="w-16 h-16 mx-auto mb-4" />
                        <p className="text-lg">Camera is off</p>
                        <p className="text-sm">Tap "Start" to begin</p>
                        {cameraPermission === 'denied' && (
                          <p className="text-xs text-red-400 mt-2">
                            Camera permission denied. Please enable in browser settings.
                          </p>
                        )}
                        {isMobile && (
                          <div className="mt-4 space-y-2">
                            <button
                              onClick={async () => {
                                const result = await testCamera();
                                toast.success(result ? 'Camera test passed!' : 'Camera test failed');
                              }}
                              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
                            >
                              Test Camera
                            </button>
                            
                            <div className="text-center">
                              <label className="inline-block px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700 transition-colors cursor-pointer">
                                📷 Upload Photo Instead
                                <input
                                  type="file"
                                  accept="image/*"
                                  onChange={handlePhotoUpload}
                                  className="hidden"
                                />
                              </label>
                            </div>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
              )}

              {/* Hidden canvas for capturing images */}
              <canvas ref={canvasRef} style={{ display: 'none' }} />

              {/* Mobile Controls Overlay */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                <div className="flex items-center justify-center space-x-4 mb-4">
                  <button
                    onClick={handleCameraToggle}
                    disabled={isInitializing}
                    className={`flex items-center justify-center w-12 h-12 rounded-full font-medium transition-colors ${
                      isCameraOn 
                        ? 'bg-red-500 text-white' 
                        : 'bg-green-500 text-white'
                    } ${isInitializing ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    {isInitializing ? (
                      <Loader2 className="w-6 h-6 animate-spin" />
                    ) : isCameraOn ? (
                      <CameraOff className="w-6 h-6" />
                    ) : (
                      <Camera className="w-6 h-6" />
                    )}
                  </button>

                  <button
                    onClick={startCountdown}
                    disabled={!isCameraOn || isAnalyzing || isCountingDown}
                    className="flex items-center justify-center w-16 h-16 bg-purple-600 text-white rounded-full font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {isAnalyzing ? (
                      <Loader2 className="w-6 h-6 animate-spin" />
                    ) : isCountingDown ? (
                      <span className="text-lg font-bold">{countdown}</span>
                    ) : (
                      <Sparkles className="w-6 h-6" />
                    )}
                  </button>

                  <button
                    onClick={() => setIsPaused(!isPaused)}
                    disabled={!isCameraOn}
                    className={`flex items-center justify-center w-12 h-12 rounded-full font-medium transition-colors ${
                      isPaused 
                        ? 'bg-green-500 text-white' 
                        : 'bg-orange-500 text-white'
                    }`}
                  >
                    {isPaused ? (
                      <span className="text-lg">▶</span>
                    ) : (
                      <span className="text-lg">⏸</span>
                    )}
                  </button>

                  {/* Switch camera button */}
                  <button
                    onClick={switchCamera}
                    disabled={!isCameraOn || isInitializing}
                    className="flex items-center justify-center w-12 h-12 rounded-full bg-gray-700 text-white"
                    title="Switch camera"
                  >
                    🔄
                  </button>
                </div>

                {/* Mode Selector */}
                <div className="flex items-center justify-center space-x-2">
                  {/* Analysis Mode Selector */}
                  <div className="flex items-center space-x-3 mb-4">
                    <select
                      value={analysisMode}
                      onChange={(e) => setAnalysisMode(e.target.value)}
                      className="px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="outfit">Outfit Check</option>
                      <option value="style">Style Match</option>
                    </select>
                    
                    <select
                      value={season}
                      onChange={(e) => setSeason(e.target.value)}
                      className="px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="spring">Spring</option>
                      <option value="summer">Summer</option>
                      <option value="autumn">Autumn</option>
                      <option value="winter">Winter</option>
                    </select>
                  </div>

                  {analysisMode === 'style' && (
                    <button
                      onClick={() => setShowStyleUpload(true)}
                      className="px-3 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
                    >
                      📁 Style ({styleImages.length}/5)
                    </button>
                  )}
                </div>
              </div>

              {/* Status Overlays */}
              {confidenceScore > 0 && (
                <div className="absolute top-4 right-4 bg-black/75 text-white px-3 py-1 rounded-lg">
                  <span className="text-sm">Confidence: {Math.round(confidenceScore * 100)}%</span>
                </div>
              )}

              {isPaused && isCameraOn && (
                <div className="absolute top-4 left-4 bg-orange-500 text-white px-3 py-1 rounded-lg shadow-lg">
                  <span className="text-sm font-medium">⏸️ Paused</span>
                </div>
              )}

              {/* Countdown Overlay */}
              {isCountingDown && (
                <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-8xl font-bold text-white mb-4 animate-pulse">
                      {countdown}
                    </div>
                    <div className="text-white text-lg font-medium">
                      {countdown > 3 ? "Get ready!" : 
                       countdown > 1 ? "Position yourself" : 
                       "Smile!"}
                    </div>
                    <div className="text-white/80 text-sm mt-2">
                      {countdown > 3 ? "Step back for full body shot" : 
                       countdown > 1 ? "Make sure you're fully visible" : 
                       "Photo will be taken automatically"}
                    </div>
                  </div>
                </div>
              )}

              {/* Positioning Guide Overlay */}
              {isCountingDown && countdown > 3 && (
                <div className="absolute inset-0 pointer-events-none">
                  {/* Full body positioning guide */}
                  <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2">
                    <div className="w-32 h-64 border-2 border-white/50 border-dashed rounded-lg flex items-center justify-center">
                      <div className="text-white/70 text-xs text-center">
                        Stand here<br/>for full body
                      </div>
                    </div>
                  </div>
                  
                  {/* Distance indicator */}
                  <div className="absolute bottom-20 left-1/2 transform -translate-x-1/2">
                    <div className="bg-black/70 text-white px-3 py-1 rounded-full text-sm">
                      📏 Step back ~6 feet
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Mobile Feedback Panel - Slides up from bottom */}
          {feedback.length > 0 && (
            <div className="fixed bottom-0 left-0 right-0 bg-black/95 backdrop-blur-sm border-t border-gray-800 max-h-[40vh] overflow-y-auto">
              <div className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-lg font-semibold text-white">Fashion Feedback</h2>
                  <div className="w-8 h-1 bg-gray-600 rounded-full"></div>
                </div>
                
                <div className="space-y-3">
                  {feedback.map((item, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                      className={`p-3 rounded-lg border-l-4 ${
                        item.priority === 'high' 
                          ? 'border-red-500 bg-red-900/20' 
                          : item.priority === 'medium'
                          ? 'border-yellow-500 bg-yellow-900/20'
                          : 'border-green-500 bg-green-900/20'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="text-sm font-medium text-white mb-1">
                            {item.type.charAt(0).toUpperCase() + item.type.slice(1)}
                          </p>
                          <p className="text-sm text-gray-300">{item.message}</p>
                        </div>
                        <span className="text-xs text-gray-400 ml-2">
                          {Math.round(item.confidence * 100)}%
                        </span>
                      </div>
                      {item.actionable && (
                        <div className="mt-2">
                          <span className="inline-block bg-blue-600 text-white text-xs px-2 py-1 rounded">
                            Actionable
                          </span>
                        </div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Desktop Layout - Hidden on mobile */}
      <div className="hidden xl:block bg-white">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="grid grid-cols-3 gap-8">
            {/* Camera Section */}
            <div className="col-span-2">
              <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
                {/* Desktop Camera Controls */}
                <div className="bg-gray-50 px-6 py-4 border-b">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <button
                        onClick={handleCameraToggle}
                        disabled={isInitializing}
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                          isCameraOn 
                            ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                            : 'bg-green-100 text-green-700 hover:bg-green-200'
                        } ${isInitializing ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        {isInitializing ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span>Starting...</span>
                          </>
                        ) : isCameraOn ? (
                          <>
                            <CameraOff className="w-4 h-4" />
                            <span>Turn Off</span>
                          </>
                        ) : (
                          <>
                            <Camera className="w-4 h-4" />
                            <span>Turn On</span>
                          </>
                        )}
                      </button>

                      <button
                        onClick={startCountdown}
                        disabled={!isCameraOn || isAnalyzing || isCountingDown}
                        className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        {isAnalyzing ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span>Analyzing...</span>
                          </>
                        ) : isCountingDown ? (
                          <>
                            <span className="text-lg font-bold">{countdown}</span>
                            <span>Countdown...</span>
                          </>
                        ) : (
                          <>
                            <Sparkles className="w-4 h-4" />
                            <span>Take Photo (5s)</span>
                          </>
                        )}
                      </button>

                      <button
                        onClick={() => setIsPaused(!isPaused)}
                        disabled={!isCameraOn}
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                          isPaused 
                            ? 'bg-green-500 text-white hover:bg-green-600 shadow-lg' 
                            : 'bg-orange-500 text-white hover:bg-orange-600 shadow-lg'
                        }`}
                      >
                        {isPaused ? (
                          <>
                            <span>▶️ Resume Auto-Analysis</span>
                          </>
                        ) : (
                          <>
                            <span>⏸️ Pause Auto-Analysis</span>
                          </>
                        )}
                      </button>

                      {/* Switch camera button for desktop */}
                      <button
                        onClick={switchCamera}
                        disabled={!isCameraOn || isInitializing}
                        className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700"
                        title="Switch camera"
                      >
                        🔄 Switch Camera
                      </button>
                    </div>

                    {/* Analysis Controls */}
                    <div className="flex flex-col space-y-4">
                      <div className="flex items-center space-x-4">
                        <label className="text-sm font-medium text-gray-700">Mode:</label>
                        <select
                          value={analysisMode}
                          onChange={(e) => setAnalysisMode(e.target.value)}
                          className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="outfit">Outfit Check</option>
                          <option value="style">Style Match</option>
                        </select>
                      </div>
                      
                      <div className="flex items-center space-x-4">
                        <label className="text-sm font-medium text-gray-700">Season:</label>
                        <select
                          value={season}
                          onChange={(e) => setSeason(e.target.value)}
                          className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="spring">Spring</option>
                          <option value="summer">Summer</option>
                          <option value="autumn">Autumn</option>
                          <option value="winter">Winter</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Desktop Camera View */}
                <div className="relative bg-black">
                  {isCameraOn ? (
                    <video
                      ref={(el) => {
                        videoRef.current = el;
                        if (!el) return;
                        // iOS-specific inline playback flags
                        el.setAttribute("playsinline", "true");
                        el.setAttribute("webkit-playsinline", "true");
                        el.muted = true; // required for autoplay on mobile
                        el.autoplay = true;
                      }}
                      autoPlay
                      playsInline
                      muted
                      className="w-full h-[500px] md:h-[600px] object-cover"
                    />
                  ) : (
                    <div className="w-full h-[500px] md:h-[600px] bg-gray-900 flex items-center justify-center">
                      <div className="text-center text-gray-400">
                        {isInitializing ? (
                          <>
                            <Loader2 className="w-16 h-16 mx-auto mb-4 animate-spin" />
                            <p className="text-lg">Starting camera...</p>
                          </>
                        ) : cameraError ? (
                          <>
                            <AlertCircle className="w-16 h-16 mx-auto mb-4 text-red-400" />
                            <p className="text-lg text-red-400 mb-2">Camera Error</p>
                            <p className="text-sm text-gray-300">{cameraError}</p>
                          </>
                        ) : (
                          <>
                            <Camera className="w-16 h-16 mx-auto mb-4" />
                            <p className="text-lg">Camera is off</p>
                            <p className="text-sm">Click "Turn On" to start</p>
                          </>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Desktop Status Overlays */}
                  {confidenceScore > 0 && (
                    <div className="absolute top-4 right-4 bg-black bg-opacity-75 text-white px-3 py-1 rounded-lg">
                      <span className="text-sm">Confidence: {Math.round(confidenceScore * 100)}%</span>
                    </div>
                  )}

                  {isPaused && isCameraOn && (
                    <div className="absolute top-4 left-4 bg-orange-500 text-white px-3 py-1 rounded-lg shadow-lg">
                      <span className="text-sm font-medium">⏸️ Auto-Analysis Paused</span>
                    </div>
                  )}

                  {/* Desktop Countdown Overlay */}
                  {isCountingDown && (
                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-9xl font-bold text-white mb-6 animate-pulse">
                          {countdown}
                        </div>
                        <div className="text-white text-2xl font-medium">
                          {countdown > 3 ? "Get ready!" : 
                           countdown > 1 ? "Position yourself" : 
                           "Smile!"}
                        </div>
                        <div className="text-white/80 text-lg mt-3">
                          {countdown > 3 ? "Step back for full body shot" : 
                           countdown > 1 ? "Make sure you're fully visible" : 
                           "Photo will be taken automatically"}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Desktop Feedback Section */}
            <div className="col-span-1">
              <div className="bg-white rounded-2xl shadow-xl p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Fashion Feedback</h2>
                
                <AnimatePresence>
                  {feedback.length > 0 ? (
                    <div className="space-y-3">
                      {feedback.map((item, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -20 }}
                          transition={{ duration: 0.3 }}
                          className={`p-4 rounded-lg border-l-4 ${
                            item.priority === 'high' 
                              ? 'border-red-500 bg-red-50' 
                              : item.priority === 'medium'
                              ? 'border-yellow-500 bg-yellow-50'
                              : 'border-green-500 bg-green-50'
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <p className="text-sm font-medium text-gray-900 mb-1">
                                {item.type.charAt(0).toUpperCase() + item.type.slice(1)}
                              </p>
                              <p className="text-sm text-gray-700">{item.message}</p>
                            </div>
                            <span className="text-xs text-gray-500 ml-2">
                              {Math.round(item.confidence * 100)}%
                            </span>
                          </div>
                          {item.actionable && (
                            <div className="mt-2">
                              <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                                Actionable
                              </span>
                            </div>
                          )}
                        </motion.div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center text-gray-500 py-8">
                      <Sparkles className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                      <p>No feedback yet</p>
                      <p className="text-sm">Turn on camera and analyze to get started</p>
                    </div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Style Upload Panel */}
      <AnimatePresence>
        {showStyleUpload && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={() => setShowStyleUpload(false)}
          >
            <motion.div
              className="bg-white rounded-2xl p-6 w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Style Reference Images</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Upload 1-5 reference images (max 5MB each)
                  </label>
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleStyleImageUpload}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>

                {styleImages.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Uploaded Images:</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {styleImages.map((image) => (
                        <div key={image.id} className="relative">
                          <img
                            src={image.preview}
                            alt="Style reference"
                            className="w-full h-24 object-cover rounded-lg"
                          />
                          <button
                            onClick={() => removeStyleImage(image.id)}
                            className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={() => setShowStyleUpload(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Done
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Settings Panel */}
      <AnimatePresence>
        {showSettings && (
         <motion.div
           initial={{ opacity: 0, y: 20 }}
           animate={{ opacity: 1, y: 0 }}
           exit={{ opacity: 0, y: 20 }}
           className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
           onClick={() => setShowSettings(false)}
         >
           <motion.div
             className="bg-white rounded-2xl p-6 w-full max-w-md mx-4"
             onClick={(e) => e.stopPropagation()}
           >
             <h3 className="text-lg font-semibold text-gray-900 mb-4">Settings</h3>
             
             <div className="space-y-4">
               <div>
                 <label className="block text-sm font-medium text-gray-700 mb-2">
                   Analysis Mode
                 </label>
                 <select
                   value={analysisMode}
                   onChange={(e) => setAnalysisMode(e.target.value)}
                   className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                 >
                   <option value="outfit">Outfit Check</option>
                   <option value="style">Style Match</option>
                 </select>
               </div>

               <div>
                 <label className="block text-sm font-medium text-gray-700 mb-2">
                   Auto Analysis Interval
                 </label>
                 <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                   <option value="5">5 seconds</option>
                   <option value="10">10 seconds</option>
                   <option value="15">15 seconds</option>
                   <option value="manual">Manual only</option>
                 </select>
               </div>

               <div>
                 <label className="block text-sm font-medium text-gray-700 mb-2">
                   Camera Quality
                 </label>
                 <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                   <option value="720p">720p</option>
                   <option value="1080p">1080p</option>
                   <option value="4k">4K</option>
                 </select>
               </div>
             </div>

             <div className="mt-6 flex justify-end space-x-3">
               <button
                 onClick={() => setShowSettings(false)}
                 className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
               >
                 Cancel
               </button>
               <button
                 onClick={() => setShowSettings(false)}
                 className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
               >
                 Save
               </button>
             </div>
           </motion.div>
         </motion.div>
       )}
     </AnimatePresence>
   </div>
 );
};

export default CameraAnalysis;
