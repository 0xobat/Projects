"use client";

import { useState } from "react";
import { motion } from "framer-motion";

interface EnvelopeGateProps {
  onOpen: () => void;
}

export default function EnvelopeGate({ onOpen }: EnvelopeGateProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleOpen = () => {
    if (isOpen) return;
    setIsOpen(true);
    setTimeout(onOpen, 800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <motion.div
        className="relative cursor-pointer"
        onClick={handleOpen}
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 1, type: "spring" }}
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.98 }}
      >
        {/* Envelope body */}
        <div className="relative w-[300px] h-[200px] sm:w-[400px] sm:h-[260px] rounded-md overflow-hidden shadow-[0_20px_60px_rgba(244,63,94,0.15)]">
          {/* Envelope base */}
          <div className="absolute inset-0 bg-gradient-to-b from-rose-200 to-rose-300" />

          {/* Subtle inner shadow for depth */}
          <div className="absolute inset-0 shadow-[inset_0_2px_10px_rgba(0,0,0,0.1)]" />

          {/* "For Shindy" text */}
          <div className="relative z-10 flex h-full items-center justify-center">
            <span className="font-cursive text-3xl sm:text-4xl text-rose-900/80 tracking-wide">
              For Shindy
            </span>
          </div>

          {/* Bottom flap (decorative V shape) */}
          <div
            className="absolute bottom-0 left-0 w-full h-1/2 bg-rose-300/80"
            style={{ clipPath: "polygon(0 100%, 50% 0%, 100% 100%)" }}
          />

          {/* Top flap (animates open) */}
          <motion.div
            className="absolute top-0 left-0 w-full h-1/2 origin-top z-20"
            initial={{ rotateX: 0 }}
            animate={isOpen ? { rotateX: 180 } : { rotateX: 0 }}
            transition={{ duration: 0.6, ease: "easeInOut" }}
            style={{
              clipPath: "polygon(0 0, 50% 100%, 100% 0)",
              transformStyle: "preserve-3d",
              backfaceVisibility: "hidden",
            }}
          >
            <div className="h-full w-full bg-gradient-to-b from-rose-400 to-rose-300 shadow-lg" />
          </motion.div>

          {/* Wax seal */}
          <motion.div
            className="absolute top-[38%] left-1/2 -translate-x-1/2 -translate-y-1/2 z-30 w-12 h-12 sm:w-14 sm:h-14 rounded-full flex items-center justify-center shadow-lg"
            style={{
              background: "radial-gradient(circle at 40% 35%, #c62828, #8b0000)",
              border: "2px solid #6d0000",
            }}
            animate={
              isOpen
                ? { opacity: 0, scale: 1.5 }
                : { opacity: 1, scale: [1, 1.05, 1] }
            }
            transition={
              isOpen
                ? { duration: 0.3 }
                : { duration: 2, repeat: Infinity, ease: "easeInOut" }
            }
          >
            <span className="text-red-200 text-lg sm:text-xl">❤</span>
          </motion.div>
        </div>

        {/* "Tap to open" hint */}
        <motion.p
          className="mt-8 text-center font-light text-rose-300/80 text-sm tracking-[0.2em] uppercase"
          animate={{ opacity: isOpen ? 0 : [0.4, 1, 0.4] }}
          transition={
            isOpen
              ? { duration: 0.2 }
              : { duration: 2, repeat: Infinity }
          }
        >
          Tap to open
        </motion.p>
      </motion.div>
    </div>
  );
}
