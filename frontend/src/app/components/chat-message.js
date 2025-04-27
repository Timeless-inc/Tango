import React from 'react';
import { Card } from "@/components/ui/card";

export function ChatMessage({ message, isUser }) {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <Card className={`p-3 max-w-[85%] ${
        isUser 
          ? 'bg-zinc-700 text-white' 
          : 'bg-zinc-800 text-zinc-100'
      }`}>
        <div className="prose prose-sm dark:prose-invert">
          {message.content}
        </div>
        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 pt-2 border-t border-zinc-600 text-xs text-zinc-400">
            <p className="font-medium">Fontes:</p>
            <ul className="mt-1 space-y-1">
              {message.sources.map((source, idx) => (
                <li key={idx}>{source.document_name}</li>
              ))}
            </ul>
          </div>
        )}
      </Card>
    </div>
  );
}