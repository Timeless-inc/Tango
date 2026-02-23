'use client';

import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

export function ChatMessage({ role, content, index }) {
  if (!content) {
    return null;
  }

  const isUser = role === 'user';
  
  // Função para processar o conteúdo e melhorar a formatação
  const processContent = (content) => {
    return content
      .replace(/✅/g, '✅ ') // Adiciona espaço após checkmarks
      .replace(/•/g, '• ') // Adiciona espaço após bullets
      .replace(/📚|📋|🔧|🎓|📍|📞|💚|😊|🥭|👤/g, (match) => `${match} `) // Adiciona espaço após emojis comuns
      .trim();
  };
  
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
          <ReactMarkdown
            components={{
              p: ({ children }) => <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>,
              strong: ({ children }) => <strong className="font-bold text-white">{children}</strong>,
              em: ({ children }) => <em className="italic text-orange-200">{children}</em>,
              h1: ({ children }) => <h1 className="text-xl font-bold mb-4 text-orange-300">{children}</h1>,
              h2: ({ children }) => <h2 className="text-lg font-bold mb-3 text-orange-300">{children}</h2>,
              h3: ({ children }) => <h3 className="text-md font-bold mb-2 text-orange-300">{children}</h3>,
              ul: ({ children }) => <ul className="list-none pl-0 mb-3 space-y-2">{children}</ul>,
              ol: ({ children }) => <ol className="list-decimal pl-6 mb-3 space-y-1">{children}</ol>,
              li: ({ children }) => <li className="mb-1 leading-relaxed flex items-start gap-2">{children}</li>,
              code: ({ children }) => <code className="bg-zinc-700 px-2 py-1 rounded text-orange-200 text-sm">{children}</code>,
              pre: ({ children }) => <pre className="bg-zinc-700 p-3 rounded-lg overflow-x-auto mb-3">{children}</pre>,
              blockquote: ({ children }) => <blockquote className="border-l-4 border-orange-500 pl-4 italic text-zinc-300 mb-3">{children}</blockquote>,
              hr: () => <hr className="border-zinc-600 my-4" />,
              a: ({ href, children }) => <a href={href} className="text-orange-400 hover:text-orange-300 underline" target="_blank" rel="noopener noreferrer">{children}</a>,
            }}
          >
            {processContent(content)}
          </ReactMarkdown>
        </div>
      </div>
    </motion.div>
  );
}