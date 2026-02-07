"use client";

import { useState, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Stars, Heart } from "lucide-react";
import CelebrationModal from "./CelebrationModal";

export default function HeroSection() {
  const [celebrated, setCelebrated] = useState(false);
  const [noStyle, setNoStyle] = useState<React.CSSProperties>({});
  const [yesScale, setYesScale] = useState(1);
  const [dodgeCount, setDodgeCount] = useState(0);
  const noRef = useRef<HTMLButtonElement>(null);

  const dodgeMessages = [
    "No",
    "Nice try 😏",
    "Nope!",
    "Not happening",
    "I said NO to No",
    "Give up already 😂",
    "You can't catch me!",
  ];

  const dodgeNo = useCallback(() => {
    const padding = 80;
    const maxX = window.innerWidth - padding;
    const maxY = window.innerHeight - padding;
    const x = padding + Math.random() * (maxX - padding);
    const y = padding + Math.random() * (maxY - padding);

    setNoStyle({
      position: "fixed",
      left: x,
      top: y,
      zIndex: 9999,
      transition: "none",
    });

    setDodgeCount((c) => c + 1);
    setYesScale((s) => Math.min(s + 0.08, 1.8));
  }, []);

  if (celebrated) {
    return <CelebrationModal />;
  }

  return (
    <AnimatePresence>
      <motion.section
        className="relative flex min-h-dvh flex-col items-center justify-center px-6 text-center"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <div className="relative z-10 flex flex-col items-center gap-8">
          {/* Badge pill */}
          <motion.div
            className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-gray-300 backdrop-blur-sm"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            <Stars className="h-4 w-4 text-rose-400" />
            I have a question
          </motion.div>

          {/* Main heading with gradient text */}
          <motion.h1
            className="font-serif text-5xl leading-tight font-bold tracking-tight sm:text-7xl"
            style={{ animation: "text-glow 3s ease-in-out infinite" }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.8 }}
          >
            <span className="bg-gradient-to-b from-white to-rose-200 bg-clip-text text-transparent">
              Will you be my
            </span>
            <br />
            <span className="font-cursive text-rose-500 italic">
              Valentine?
            </span>
          </motion.h1>

          <motion.p
            className="max-w-md text-lg font-light text-gray-300 sm:text-xl"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8, duration: 0.6 }}
          >
            I&apos;ve been thinking about this for a while...
          </motion.p>

          {/* Buttons */}
          <motion.div
            className="flex items-center gap-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1, duration: 0.6 }}
          >
            <motion.button
              onClick={() => setCelebrated(true)}
              className="relative flex items-center gap-2 rounded-full bg-gradient-to-r from-rose-500 to-pink-600 px-10 py-4 font-serif text-xl font-semibold text-white shadow-lg transition-shadow duration-300 hover:shadow-rose-500/40 hover:shadow-xl"
              style={{ transform: `scale(${yesScale})` }}
              whileTap={{ scale: yesScale * 0.95 }}
            >
              Yes
              <Heart className="h-5 w-5" fill="currentColor" />
            </motion.button>

            <button
              ref={noRef}
              onMouseEnter={dodgeNo}
              onTouchStart={(e) => {
                e.preventDefault();
                dodgeNo();
              }}
              className="rounded-full border border-white/20 bg-white/10 px-8 py-4 font-serif text-lg text-white/70 backdrop-blur-md transition-colors hover:bg-white/15"
              style={noStyle}
            >
              {dodgeMessages[Math.min(dodgeCount, dodgeMessages.length - 1)]}
            </button>
          </motion.div>
        </div>
      </motion.section>
    </AnimatePresence>
  );
}
