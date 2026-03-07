import { useEffect, useRef, useState } from 'react';

type EmotionApiResponse = {
  emotion?: string;
  confidence?: number;
  label?: string;
  score?: number;
};

function App() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const intervalRef = useRef<number | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [emotion, setEmotion] = useState('—');
  const [confidence, setConfidence] = useState('—');

  useEffect(() => {
    let isMounted = true;

    const startWebcam = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });

        if (!isMounted) {
          stream.getTracks().forEach((track) => track.stop());
          return;
        }

        streamRef.current = stream;

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
        }

        intervalRef.current = window.setInterval(() => {
          void captureAndSendFrame();
        }, 1000);
      } catch {
        setEmotion('Camera unavailable');
        setConfidence('—');
      }
    };

    const captureAndSendFrame = async () => {
      const video = videoRef.current;
      const canvas = canvasRef.current;

      if (!video || !canvas || video.videoWidth === 0 || video.videoHeight === 0) {
        return;
      }

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const context = canvas.getContext('2d');
      if (!context) {
        return;
      }

      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      const dataUrl = canvas.toDataURL('image/jpeg');
      const base64Frame = dataUrl.split(',')[1] ?? '';

      if (!base64Frame) {
        return;
      }

      try {
        const response = await fetch('http://127.0.0.1:8000/emotion/face', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ image: base64Frame }),
        });

        if (!response.ok) {
          return;
        }

        const result = (await response.json()) as EmotionApiResponse;

        const emotionValue = result.emotion ?? result.label ?? 'Unknown';
        const confidenceValue = result.confidence ?? result.score;

        setEmotion(emotionValue);
        setConfidence(
          typeof confidenceValue === 'number'
            ? `${(confidenceValue * 100).toFixed(1)}%`
            : '—',
        );
      } catch {
        // Ignore transient network errors and keep previous values.
      }
    };

    void startWebcam();

    return () => {
      isMounted = false;

      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
      }

      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  return (
    <main>
      <video ref={videoRef} autoPlay playsInline muted />
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      <p>Emotion: {emotion}</p>
      <p>Confidence: {confidence}</p>
    </main>
  );
}

export default App;
