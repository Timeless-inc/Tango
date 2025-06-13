'use client';

import { motion } from 'framer-motion';

export function ChatMessage({ role, content, index }) {
  if (!content) {
    return null;
  }

  const isUser = role === 'user';
  
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
        isUser ? 'bg-gradient-to-br from-amber-500 to-amber-600' : 'bg-gradient-to-br from-orange-500 to-orange-600'
      }`}>
        <span className="text-sm">
          {isUser ? '👤' : '🥭'}
        </span>
      </div>
      
      {/* Message bubble */}
      <div className={`max-w-[70%] rounded-2xl p-4 ${
        isUser 
          ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-white' 
          : 'bg-zinc-800/80 backdrop-blur-sm text-zinc-100 border border-zinc-700/50'
      }`}>
        <div className="prose prose-invert prose-sm max-w-none">
          {content.split('\n').map((line, i) => (
            <p key={i} className={`${i === 0 ? 'mt-0' : ''} ${i === content.split('\n').length - 1 ? 'mb-0' : ''}`}>
              {line}
            </p>
          ))}
        </div>
      </div>
    </motion.div>
  );
}