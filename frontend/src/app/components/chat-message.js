import React from 'react';

export function ChatMessage({ role, content }) {
  // Verificação de segurança para valores undefined ou nulos
  if (!content) {
    return null; // Não renderiza nada se não houver conteúdo
  }

  const isUser = role === 'user';
  
  return (
    <div className={`scrollbar-hide flex items-start my-4 ${isUser ? 'justify-end' : ''}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center mr-4">
          <span className="text-sm">🥭</span>
        </div>
      )}
      <div className={`max-w-3/4 rounded-lg p-3 ${isUser 
        ? 'bg-blue-600 text-white' 
        : 'bg-zinc-800 text-zinc-200'}`}>
        {content}
      </div>
      {isUser && (
        <div className="w-8 opacity-0 ml-4">
          <span className="text-sm">👤</span>
        </div>
      )}
    </div>
  );
}