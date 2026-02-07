"use client";

import { useState } from "react";
import { motion } from "framer-motion";

function seededRandom(seed: number) {
  const x = Math.sin(seed + 1) * 10000;
  return x - Math.floor(x);
}

function generateHearts() {
  return Array.from({ length: 20 }, (_, i) => ({
    id: i,
    left: `${seededRandom(i * 5) * 100}%`,
    size: 14 + seededRandom(i * 5 + 1) * 22,
    delay: seededRandom(i * 5 + 2) * 12,
    duration: 12 + seededRandom(i * 5 + 3) * 12,
    swayAmount: 30 + seededRandom(i * 5 + 4) * 60,
  }));
}

export default function FloatingHearts() {
  const [hearts] = useState(generateHearts);

  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      {hearts.map((h) => (
        <motion.span
          key={h.id}
          className="absolute text-rose-500/20"
          style={{
            left: h.left,
            bottom: "-5%",
            fontSize: h.size,
          }}
          animate={{
            y: [0, -1000],
            x: [0, h.swayAmount, -h.swayAmount, h.swayAmount / 2, 0],
            opacity: [0, 0.6, 0.6, 0.6, 0],
          }}
          transition={{
            duration: h.duration,
            delay: h.delay,
            repeat: Infinity,
            ease: "linear",
          }}
        >
          ❤
        </motion.span>
      ))}
    </div>
  );
}
