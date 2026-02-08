"use client";

import { useRef, useState, useEffect } from "react";

interface VideoPlayerProps {
  src: string;
  visible: boolean;
}

export default function VideoPlayer({ src, visible }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [muted, setMuted] = useState(true);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    function tryPlay() {
      video!.play().catch(() => {});
    }

    function onCanPlay() {
      setReady(true);
      if (visible) tryPlay();
    }

    video.addEventListener("canplay", onCanPlay);

    // If already buffered enough, fire the handler immediately
    if (video.readyState >= 3) {
      onCanPlay();
    }

    return () => video.removeEventListener("canplay", onCanPlay);
  }, [visible]);

  useEffect(() => {
    if (visible && videoRef.current) {
      videoRef.current.play().catch(() => {});
    }
  }, [visible]);

  function toggleMute() {
    const video = videoRef.current;
    if (!video) return;
    const next = !muted;
    setMuted(next);
    video.muted = next;
    if (video.paused) {
      video.play().catch(() => {});
    }
  }

  return (
    <div
      className="absolute inset-0 flex items-center justify-center bg-black"
      style={{
        opacity: visible ? 1 : 0,
        transition: "opacity 1s ease-in-out",
      }}
    >
      <video
        ref={videoRef}
        src={src}
        muted={muted}
        autoPlay
        playsInline
        preload="auto"
        loop
        className="h-full w-full object-contain"
      />

      {visible && !ready && (
        <div className="absolute inset-0 flex items-center justify-center">
          <p className="text-lg text-white/70">Loading video...</p>
        </div>
      )}

      {visible && (
        <button
          onClick={toggleMute}
          className="absolute bottom-8 right-8 rounded-full bg-black/50 px-5 py-3 text-base text-white backdrop-blur-sm transition-opacity hover:bg-black/70"
        >
          {muted ? "Tap for sound 🔊" : "Mute 🔇"}
        </button>
      )}
    </div>
  );
}
