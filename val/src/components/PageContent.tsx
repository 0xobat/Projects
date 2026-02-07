"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import EnvelopeGate from "./EnvelopeGate";
import FloatingHearts from "./FloatingHearts";
import HeroSection from "./HeroSection";
import ScrollIndicator from "./ScrollIndicator";
import PhotoCarousel from "./PhotoCarousel";
import LoveLetter from "./LoveLetter";
import Footer from "./Footer";

export default function PageContent() {
  const [isOpened, setIsOpened] = useState(false);

  return (
    <>
      <FloatingHearts />

      {/* Envelope overlay */}
      <AnimatePresence>
        {!isOpened && (
          <motion.div
            key="envelope"
            exit={{ opacity: 0 }}
            transition={{ duration: 1 }}
          >
            <EnvelopeGate onOpen={() => setIsOpened(true)} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main content — fades in after envelope opens */}
      <motion.div
        className="relative z-10"
        initial={{ opacity: 0 }}
        animate={{ opacity: isOpened ? 1 : 0 }}
        transition={{ duration: 1, delay: isOpened ? 0.3 : 0 }}
        style={{ pointerEvents: isOpened ? "auto" : "none" }}
      >
        <HeroSection />
        <ScrollIndicator />

        {/* Glass divider for photo carousel */}
        <div className="border-y border-white/5 bg-black/20 backdrop-blur-sm">
          <PhotoCarousel />
        </div>

        <LoveLetter />
        <Footer />
      </motion.div>
    </>
  );
}
