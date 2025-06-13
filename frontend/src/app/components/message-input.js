'use client';

import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

export function MessageInput({ onSendMessage, disabled }) {
  const [inputValue, setInputValue] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
    }
  }, [inputValue]);

  // Escuta eventos personalizados da welcome screen
  useEffect(() => {
    const handleSendMessage = (event) => {
      setInputValue(event.detail);
      setTimeout(() => {
        handleSubmit(new Event('submit'));
      }, 100);
    };

    window.addEventListener('sendMessage', handleSendMessage);
    return () => window.removeEventListener('sendMessage', handleSendMessage);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !disabled) {
      onSendMessage(inputValue);
      setInputValue('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="relative">
      <motion.form 
        onSubmit={handleSubmit}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative"
      >
        <div className={`relative bg-zinc-900/80 backdrop-blur-sm rounded-xl transition-all duration-300 ${
          isFocused 
            ? 'ring-2 ring-orange-500/50 shadow-lg shadow-orange-500/20' 
            : 'ring-1 ring-zinc-700/50 hover:ring-zinc-600/50'
        }`}>
          
          <div className="relative flex items-end gap-3 p-3">
            {/* Text input container */}
            <div className="flex-1 relative">
              <Textarea
                ref={textareaRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                placeholder="Digite sua mensagem... (Shift + Enter para nova linha)"
                disabled={disabled}
                className="min-h-[44px] max-h-[150px] resize-none bg-transparent border-none focus:ring-0 focus:outline-none text-white placeholder:text-zinc-400 pr-4 py-2 text-sm leading-relaxed"
                rows={1}
              />
            </div>

            {/* Send button */}
            <Button
              type="submit"
              disabled={!inputValue.trim() || disabled}
              className={`shrink-0 w-10 h-10 rounded-lg transition-all duration-300 border-0 ${
                inputValue.trim() 
                  ? 'bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white shadow-lg shadow-orange-500/25' 
                  : 'bg-zinc-700/50 text-zinc-500 cursor-not-allowed'
              }`}
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </motion.form>
    </div>
  );
}