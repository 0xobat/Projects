"use client";

import { motion } from "framer-motion";
import { ArrowDown } from "lucide-react";

export default function ScrollIndicator() {
  return (
    <motion.div
      className="flex justify-center py-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 2, duration: 1 }}
    >
      <motion.div
        className="text-white/30"
        animate={{ y: [0, 10, 0] }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      >
        <ArrowDown className="h-6 w-6" />
      </motion.div>
    </motion.div>
  );
}
