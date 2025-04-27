'use client';

import { useRef, useEffect, useState } from 'react';
import { ChatMessage } from './chat-message';
import { MessageInput } from './message-input';
import { SuggestionButton } from './suggestion-button';

const suggestions = [
  "Você pode me ajudar com a monitoria?",
  "Qual o número da CRADT?",
  "O que é o Mango?",
  "Como funciona o IFPE?",
];

export function ChatContainer() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;

    const userMessage = { role: 'user', content: message };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: message,
          conversation_history: messages,
        }),
      });

      if (!response.ok) throw new Error('Failed to fetch response');
      
      const data = await response.json();
      
      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        sources: data.sources || []
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Desculpe, ocorreu um erro ao processar sua mensagem.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto">
      <div className="flex-1 overflow-auto p-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col justify-center items-center space-y-6">
            <div className="text-center space-y-2">
              <h1 className="text-2xl font-medium text-white">Olá, eu sou o Mango!</h1>
              <p className="text-zinc-400">Em que posso te ajudar?</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 w-full max-w-2xl">
              {suggestions.map((suggestion) => (
                <SuggestionButton 
                  key={suggestion} 
                  text={suggestion} 
                  onClick={handleSendMessage} 
                />
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <ChatMessage 
                key={index} 
                message={message} 
                isUser={message.role === 'user'} 
              />
            ))}
          </>
        )}
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-zinc-800 text-white p-3 rounded-lg">
              <div className="flex space-x-2">
                <div className="h-2 w-2 rounded-full bg-zinc-400 animate-pulse"></div>
                <div className="h-2 w-2 rounded-full bg-zinc-400 animate-pulse delay-200"></div>
                <div className="h-2 w-2 rounded-full bg-zinc-400 animate-pulse delay-500"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="border-t border-zinc-800 p-4">
        <MessageInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}