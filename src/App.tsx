import React, { useState, useEffect, useRef } from 'react';
import { 
  Mic, 
  MicOff, 
  Video, 
  VideoOff, 
  Brain, 
  Sparkles, 
  Settings,
  RefreshCcw,
  FlipHorizontal
} from 'lucide-react';

const EMOTIONS: Record<string, { color: string, label: string }> = {
  neutral: { color: 'from-slate-400 to-slate-600', label: 'Neutral' },
  happy: { color: 'from-amber-300 to-orange-500', label: 'Joyful' },
  sad: { color: 'from-blue-400 to-indigo-600', label: 'Melancholic' },
  angry: { color: 'from-red-500 to-rose-700', label: 'Provoked' },
  surprised: { color: 'from-purple-400 to-fuchsia-600', label: 'Astonished' },
};

export default function App() {

  const [isCameraOn, setIsCameraOn] = useState(false);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('user');
  const [isMicOn, setIsMicOn] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState('neutral');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [insight, setInsight] = useState("System ready. Detecting faces...");
  const [stats, setStats] = useState({ confidence: 0, intensity: 0 });

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // -----------------------------
  // EMOTION API CALL
  // -----------------------------

  const analyzeEmotion = async (base64Image: string) => {

    try {

      const response = await fetch("http://127.0.0.1:8000/emotion/face", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          image_base64: base64Image
        })
      });

      if (!response.ok) {
        throw new Error("Backend error");
      }

      const result = await response.json();

      // Support multiple backend formats
      let emotion =
        (result.top_emotion ||
         result.dominant_emotion ||
         "neutral").toLowerCase();

      if (!EMOTIONS[emotion]) emotion = "neutral";

      const confidence =
        result.confidence
          ? Math.round(result.confidence * 100)
          : Math.round(result.emotion?.[emotion] || 0);

      const intensity = confidence;

      setCurrentEmotion(emotion);

      setStats({
        confidence,
        intensity
      });

      setInsight(
        `Detected ${emotion} emotion with ${confidence}% confidence.`
      );

    } catch (error) {

      console.error("Emotion engine error:", error);

      setInsight(
        "Emotion engine unreachable. Ensure FastAPI backend is running."
      );

    } finally {

      setIsAnalyzing(false);

    }
  };

  // -----------------------------
  // CAPTURE FRAME
  // -----------------------------

  const captureAndAnalyze = async () => {

    if (!videoRef.current || !canvasRef.current || !isCameraOn) return;

    setIsAnalyzing(true);

    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    if (!context) return;

    const video = videoRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const dataUrl = canvas.toDataURL("image/jpeg");

    const base64Image = dataUrl.split(",")[1];

    if (!base64Image) {
      setIsAnalyzing(false);
      return;
    }

    await analyzeEmotion(base64Image);
  };

  const toggleFacingMode = () => {
    setFacingMode(prev => prev === "user" ? "environment" : "user");
  };

  // -----------------------------
  // CAMERA CONTROL
  // -----------------------------

  useEffect(() => {

    const stopStream = () => {

      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }

    };

    const startCamera = async () => {

      stopStream();

      if (isCameraOn) {

        try {

          const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode },
            audio: false
          });

          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            streamRef.current = stream;
          }

        } catch (e) {

          console.error("Camera error", e);
          setInsight("Camera access denied.");

        }

      }

    };

    startCamera();

    return () => stopStream();

  }, [isCameraOn, facingMode]);

  // -----------------------------
  // UI
  // -----------------------------

  return (
    <div className="min-h-screen bg-[#050507] text-slate-100">

      {/* NAVBAR */}

      <nav className="flex items-center justify-between px-10 py-6">

        <div className="flex items-center gap-3">

          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">

            <Sparkles className="text-white w-5 h-5" />

          </div>

          <span className="text-xl font-black uppercase">
            Sentient<span className="text-indigo-400">Pro</span>
          </span>

        </div>

        <button className="p-3 rounded-full border border-white/10">
          <Settings className="w-5 h-5 text-slate-400" />
        </button>

      </nav>

      <main className="max-w-7xl mx-auto px-8 py-4 flex flex-col lg:flex-row gap-10 pb-24">

        {/* CAMERA */}

        <div className="w-full lg:w-[60%] space-y-8">

          <div className="relative">

            <div className="aspect-[16/10] bg-white/5 rounded-[40px] border border-white/10 overflow-hidden">

              {!isCameraOn ? (

                <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500">

                  <VideoOff className="w-12 h-12 opacity-40" />

                  <p className="text-sm font-bold uppercase opacity-40">
                    Initiate Visual Link
                  </p>

                </div>

              ) : (

                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className={`w-full h-full object-cover ${facingMode === "user" ? "scale-x-[-1]" : ""}`}
                />

              )}

            </div>

            {/* CONTROLS */}

            <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-3 bg-[#0f0f12]/90 p-3 rounded-3xl border border-white/10">

              <button
                onClick={() => setIsCameraOn(!isCameraOn)}
                className="p-4 rounded-2xl bg-white/5 hover:bg-white/10"
              >
                {isCameraOn ? <Video /> : <VideoOff />}
              </button>

              <button
                onClick={toggleFacingMode}
                disabled={!isCameraOn}
                className="p-4 rounded-2xl bg-white/5 hover:bg-white/10"
              >
                <FlipHorizontal />
              </button>

              <button
                onClick={() => setIsMicOn(!isMicOn)}
                className="p-4 rounded-2xl bg-white/5 hover:bg-white/10"
              >
                {isMicOn ? <Mic /> : <MicOff />}
              </button>

              <button
                onClick={captureAndAnalyze}
                disabled={!isCameraOn || isAnalyzing}
                className="px-10 py-5 bg-white text-black font-black uppercase rounded-2xl flex items-center gap-3"
              >
                {isAnalyzing
                  ? <RefreshCcw className="animate-spin" />
                  : <Brain />
                }

                {isAnalyzing ? "Scanning..." : "Analyze"}

              </button>

            </div>

          </div>

        </div>

        {/* RESULTS */}

        <div className="w-full lg:w-[40%] space-y-8">

          <div className="bg-white/5 border border-white/10 p-10 rounded-[50px]">

            <span className="text-[11px] font-black uppercase text-indigo-400/60 mb-10 block">
              System Output
            </span>

            <h2 className="text-7xl font-black capitalize mb-2">
              {currentEmotion}
            </h2>

            <div className="mt-6">

              <div className="flex justify-between text-xs text-slate-500 mb-2">
                <span>Confidence</span>
                <span>{stats.confidence}%</span>
              </div>

              <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">

                <div
                  className="h-full bg-indigo-500 transition-all"
                  style={{ width: `${stats.confidence}%` }}
                />

              </div>

            </div>

            <div className="mt-6">

              <div className="flex justify-between text-xs text-slate-500 mb-2">
                <span>Intensity</span>
                <span>{stats.intensity}%</span>
              </div>

              <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">

                <div
                  className="h-full bg-purple-500 transition-all"
                  style={{ width: `${stats.intensity}%` }}
                />

              </div>

            </div>

          </div>

          <div className="bg-indigo-600 rounded-[50px] p-10 text-white">

            <div className="flex items-center gap-2 mb-6">
              <Brain className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-widest">
                Neural Prediction
              </span>
            </div>

            <p className="text-xl italic opacity-90 min-h-[100px]">
              "{insight}"
            </p>

          </div>

        </div>

      </main>

      <canvas ref={canvasRef} className="hidden" />

    </div>
  );
}