import FloatingHearts from "@/components/FloatingHearts";
import HeroSection from "@/components/HeroSection";
import ScrollIndicator from "@/components/ScrollIndicator";
import PhotoCarousel from "@/components/PhotoCarousel";
import LoveLetter from "@/components/LoveLetter";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main className="relative min-h-dvh bg-gradient-to-br from-navy-deep via-navy-mid to-navy-light">
      {/* Noise texture overlay */}
      <div className="pointer-events-none fixed inset-0 z-0 opacity-20">
        <svg width="100%" height="100%">
          <filter id="noise">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.65"
              numOctaves="3"
              stitchTiles="stitch"
            />
          </filter>
          <rect width="100%" height="100%" filter="url(#noise)" />
        </svg>
      </div>

      {/* Ambient light orbs */}
      <div
        className="pointer-events-none fixed top-[-10%] left-[-10%] z-0 h-[40vw] w-[40vw] rounded-full bg-rose-600/20 blur-[100px]"
        style={{ animation: "pulse-slow 8s ease-in-out infinite" }}
      />
      <div
        className="pointer-events-none fixed right-[-10%] bottom-[10%] z-0 h-[40vw] w-[40vw] rounded-full bg-purple-600/20 blur-[100px]"
        style={{ animation: "pulse-slow 8s 4s ease-in-out infinite" }}
      />

      <FloatingHearts />

      {/* Content layer — above fixed background effects */}
      <div className="relative z-10">
        <HeroSection />
        <ScrollIndicator />

        {/* Glass divider for photo carousel */}
        <div className="border-y border-white/5 bg-black/20 backdrop-blur-sm">
          <PhotoCarousel />
        </div>

        <LoveLetter />
        <Footer />
      </div>
    </main>
  );
}
