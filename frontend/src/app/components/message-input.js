'use client';

import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { SendIcon, Mic, Paperclip } from "lucide-react";

export function MessageInput({ onSendMessage, isLoading }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    onSendMessage(input);
    setInput('');
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="flex items-center gap-2 bg-zinc-800 rounded-lg p-1 border border-zinc-700">
        <Button 
          type="button" 
          size="icon" 
          variant="ghost" 
          className="text-zinc-400 hover:text-zinc-300 rounded-full h-8 w-8">
          <Paperclip className="h-4 w-4" />
        </Button>
        
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Send a message..."
          className="flex-1 bg-transparent border-none focus:outline-none text-zinc-100 placeholder:text-zinc-500 text-sm py-2 px-1"
          disabled={isLoading}
        />
        
        <Button 
          type="button" 
          size="icon" 
          variant="ghost" 
          className="text-zinc-400 hover:text-zinc-300 rounded-full h-8 w-8">
          <Mic className="h-4 w-4" />
        </Button>
        
        <Button
          type="submit"
          disabled={isLoading || !input.trim()}
          size="icon"
          className={`rounded-full h-8 w-8 ${
            isLoading || !input.trim() 
              ? 'bg-zinc-700 text-zinc-500' 
              : 'bg-zinc-600 hover:bg-zinc-500 text-white'
          }`}
        >
          <SendIcon className="h-4 w-4" />
        </Button>
      </div>
    </form>
  );
}