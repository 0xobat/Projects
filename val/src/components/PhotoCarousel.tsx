"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion } from "framer-motion";

const PHOTOS = [
  { src: "/photos/1.jpeg", caption: "Our first adventure" },
  { src: "/photos/2.jpeg", caption: "That unforgettable day" },
  { src: "/photos/3.jpeg", caption: "Just us" },
  { src: "/photos/4.jpeg", caption: "My favorite memory" },
  { src: "/photos/5.jpeg", caption: "Always smiling with you" },
  { src: "/photos/New-year.jpeg", caption: "Ringing in the New Year" },
  { src: "/photos/yes.jpeg", caption: "The moment you said yes" },
];

export default function PhotoCarousel() {
  const [current, setCurrent] = useState(0);
  const [paused, setPaused] = useState(false);
  const touchStart = useRef(0);

  const next = useCallback(() => {
    setCurrent((c) => (c + 1) % PHOTOS.length);
  }, []);

  const prev = useCallback(() => {
    setCurrent((c) => (c - 1 + PHOTOS.length) % PHOTOS.length);
  }, []);

  useEffect(() => {
    if (paused) return;
    const timer = setInterval(next, 4500);
    return () => clearInterval(timer);
  }, [paused, next]);

  return (
    <section className="relative flex min-h-dvh flex-col items-center justify-center gap-8 px-6 py-20">
      <motion.div
        className="text-center"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        viewport={{ once: true, amount: 0.5 }}
      >
        <h2 className="bg-gradient-to-r from-rose-200 to-rose-400 bg-clip-text font-serif text-4xl font-bold text-transparent sm:text-5xl">
          Our Memories
        </h2>
        <p className="mt-2 text-sm font-light text-gray-400">
          Moments I cherish forever
        </p>
      </motion.div>

      <motion.div
        className="relative w-full max-w-md overflow-hidden rounded-2xl border border-white/10 bg-white/5 shadow-2xl backdrop-blur-lg"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        viewport={{ once: true, amount: 0.3 }}
        onTouchStart={(e) => {
          touchStart.current = e.touches[0].clientX;
        }}
        onTouchEnd={(e) => {
          const diff = e.changedTouches[0].clientX - touchStart.current;
          if (diff > 50) {
            prev();
          } else if (diff < -50) {
            next();
          }
        }}
        onClick={() => setPaused((p) => !p)}
      >
        <div className="relative aspect-[4/5] w-full bg-navy-light">
          <img
            src={PHOTOS[current].src}
            alt={PHOTOS[current].caption}
            className="absolute inset-0 h-full w-full object-cover"
          />

          {/* Caption */}
          <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-6 pt-16">
            <p className="font-serif text-lg text-rose-100 italic">
              {PHOTOS[current].caption}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Dot indicators */}
      <div className="flex gap-2">
        {PHOTOS.map((_, i) => (
          <button
            key={i}
            onClick={() => setCurrent(i)}
            className={`h-2.5 rounded-full transition-all duration-300 ${
              i === current
                ? "w-8 bg-rose-500"
                : "w-2.5 bg-white/20 hover:bg-white/30"
            }`}
          />
        ))}
      </div>

      <p className="text-sm text-white/40">
        {paused ? "Tap to resume" : "Tap to pause"} · Swipe to navigate
      </p>
    </section>
  );
}
