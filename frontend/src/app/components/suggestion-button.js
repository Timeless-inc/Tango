'use client';

import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';

export function SuggestionButton({ text, onClick }) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2 }}
    >
      <Button
        variant="outline"
        size="sm"
        onClick={() => onClick(text)}
        className="text-xs border-zinc-700/50 text-zinc-300 hover:text-white hover:border-orange-500/50 hover:bg-orange-500/10 bg-zinc-800/50 backdrop-blur-sm transition-all duration-200"
      >
        {text}
      </Button>
    </motion.div>
  );
}