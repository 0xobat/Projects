"use client";

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

const LETTER_TEXT =
  "Every moment with you feels like the most beautiful dream I never want to wake up from. " +
  "You make ordinary days extraordinary just by being in them. " +
  "Your laugh is my favorite sound in the entire world. " +
  "I fall for you a little more every single day, and I didn't think that was possible. " +
  "Thank you for being you — my favorite person, my best friend, my everything.";

export default function LoveLetter() {
  const words = LETTER_TEXT.split(" ");
  const containerRef = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.2 }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <section className="relative flex min-h-dvh flex-col items-center justify-center gap-10 px-6 py-20">
      {/* Decorative top heart */}
      <div className="text-4xl text-rose-500/30">♥</div>

      <motion.h2
        className="bg-gradient-to-r from-rose-200 to-rose-400 bg-clip-text font-serif text-4xl font-bold text-transparent sm:text-5xl"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        viewport={{ once: true, amount: 0.5 }}
      >
        My Love For You
      </motion.h2>

      <div
        ref={containerRef}
        className="max-w-lg text-center font-serif text-xl leading-relaxed text-rose-100 sm:text-2xl sm:leading-relaxed"
      >
        {words.map((word, i) => (
          <span
            key={i}
            className="inline-block"
            style={{
              animation: visible
                ? `word-reveal 0.6s ${i * 0.08}s ease-out forwards`
                : "none",
              opacity: visible ? 0 : 0,
              marginRight: "0.3em",
            }}
          >
            {word}
          </span>
        ))}
      </div>

      {/* Decorative bottom heart */}
      <div className="text-4xl text-rose-500/30">♥</div>

      {/* Warm closing */}
      <p
        className="font-serif text-lg text-rose-300/70 italic"
        style={{
          animation: visible
            ? `word-reveal 0.8s ${words.length * 0.08 + 0.5}s ease-out forwards`
            : "none",
          opacity: 0,
        }}
      >
        Forever yours ♥
      </p>
    </section>
  );
}
