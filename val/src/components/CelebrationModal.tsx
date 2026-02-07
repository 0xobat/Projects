"use client";

import { useState, useEffect, useCallback } from "react";
import dynamic from "next/dynamic";
import VideoPlayer from "./VideoPlayer";

const HeartBurst = dynamic(() => import("./HeartBurst"), { ssr: false });

type Phase = "burst" | "video";

export default function CelebrationModal() {
  const [phase, setPhase] = useState<Phase>("burst");

  const goToVideo = useCallback(() => {
    setPhase((prev) => (prev === "burst" ? "video" : prev));
  }, []);

  // Safety timeout — transition even if HeartBurst onComplete doesn't fire
  useEffect(() => {
    const timer = setTimeout(goToVideo, 3500);
    return () => clearTimeout(timer);
  }, [goToVideo]);

  return (
    <div className="fixed inset-0 z-40 bg-black">
      {/* Video layer — always mounted, fades in when phase is "video" */}
      <div className="absolute inset-0 z-30">
        <VideoPlayer
          src="/photos/our-memories.mp4"
          visible={phase === "video"}
        />
      </div>

      {/* Heart burst layer — sits above video, fades out when done */}
      <div
        className="absolute inset-0 z-50"
        style={{
          opacity: phase === "burst" ? 1 : 0,
          transition: "opacity 1s ease-out",
          pointerEvents: phase === "burst" ? "auto" : "none",
        }}
      >
        <HeartBurst onComplete={goToVideo} />
      </div>
    </div>
  );
}
