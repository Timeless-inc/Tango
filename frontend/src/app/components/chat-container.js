'use client';

import { useState, useRef, useEffect } from 'react';
import { ChatMessage } from './chat-message';
import { MessageInput } from './message-input';
import { WelcomeScreen } from './welcome-screen';
import { SuggestionButton } from './suggestion-button';
import { fetchSuggestions } from '@/lib/chat-utils';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Settings } from 'lucide-react';
import Link from 'next/link';

export function ChatContainer() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (content) => {
    if (!content.trim()) return;

    const newUserMessage = { role: 'user', content };
    setMessages(prev => [...prev, newUserMessage]);
    setSuggestions([]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: content,
          conversation_history: messages,
        }),
      });

      if (!response.ok) {
        throw new Error(`Erro na resposta da API: ${response.status}`);
      }

      const data = await response.json();
      
      let responseText = "Desculpe, não consegui processar sua solicitação.";
      
      if (data.answer) {
        responseText = data.answer;
      } else if (data.error) {
        responseText = `Erro: ${data.error}`;
      }
      
      const assistantMessage = { 
        role: 'assistant', 
        content: responseText
      };
      
      setMessages(prev => [...prev, assistantMessage]);

      if (data.answer) {
        const newSuggestions = await fetchSuggestions(data.answer);
        setSuggestions(newSuggestions);
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente mais tarde.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header simplificado */}
      <div className="bg-zinc-900/50 backdrop-blur-sm border-b border-zinc-800 p-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-white">MANGO</h1>
              <p className="text-xs text-zinc-400">Assistente inteligente</p>
            </div>
          </div>
          
          <Link 
            href="/admin/login" 
            className="p-2 rounded-lg hover:bg-zinc-800 transition-colors"
          >
            <Settings className="w-5 h-5 text-zinc-400" />
          </Link>
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-4xl mx-auto p-4 space-y-6">
          <AnimatePresence mode="wait">
            {messages.length === 0 ? (
              <WelcomeScreen key="welcome" />
            ) : (
              <motion.div 
                key="messages"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-6"
              >
                {messages.map((message, index) => (
                  <ChatMessage 
                    key={index} 
                    role={message.role} 
                    content={message.content}
                    index={index}
                  />
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Loading indicator */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-start space-x-3"
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div className="bg-zinc-800/80 backdrop-blur-sm p-4 rounded-2xl border border-zinc-700/50">
                <div className="flex space-x-1">
                  {[0, 1, 2].map((i) => (
                    <motion.div
                      key={i}
                      className="w-2 h-2 bg-orange-400 rounded-full"
                      animate={{ 
                        scale: [1, 1.2, 1],
                        opacity: [0.5, 1, 0.5]
                      }}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        delay: i * 0.2
                      }}
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Sugestões - SEM linha superior */}
      <AnimatePresence>
        {!isLoading && suggestions.length > 0 && messages.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="p-4 pt-2"
          >
            <div className="max-w-4xl mx-auto">
              <p className="text-xs text-zinc-400 mb-3">Sugestões:</p>
              <div className="flex flex-wrap gap-2">
                {suggestions.map((suggestion, idx) => (
                  <SuggestionButton 
                    key={idx} 
                    text={suggestion} 
                    onClick={handleSuggestionClick}
                  />
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input area */}
      <div className="p-4 pt-2">
        <div className="max-w-4xl mx-auto">
          <MessageInput onSendMessage={sendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}