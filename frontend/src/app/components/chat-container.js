'use client';

import { useState, useRef, useEffect } from 'react';
import { ChatMessage } from './chat-message';
import { MessageInput } from './message-input';
import Link from 'next/link';
import { fetchSuggestions } from '@/lib/chat-utils';
import { SuggestionButton } from './suggestion-button';

export function ChatContainer() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const messagesEndRef = useRef(null);

  // Role para o final quando as mensagens mudam
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Função para enviar mensagem
  const sendMessage = async (content) => {
    if (!content.trim()) return;

    console.log("Enviando mensagem:", content);

    // Adiciona mensagem do usuário
    const newUserMessage = { role: 'user', content };
    setMessages(prev => [...prev, newUserMessage]);
    
    // Limpa sugestões quando uma nova mensagem é enviada
    setSuggestions([]);
    
    // Prepara para resposta do assistente
    setIsLoading(true);

    try {
      // Envia a consulta para a API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: content,
          conversation_history: messages,
        }),
      });
    
      if (!response.ok) {
        throw new Error(`Erro na resposta da API: ${response.status}`);
      }
    
      const data = await response.json();
      console.log("Resposta da API:", data);
      
      // Verifica se temos uma resposta válida
      let responseText = "Desculpe, não consegui processar sua solicitação.";
      
      if (data.answer) {
        responseText = data.answer;
      } else if (data.error) {
        responseText = `Erro: ${data.error}`;
        console.error("Erro recebido da API:", data.error);
      }
      
      // Adiciona resposta do assistente
      const assistantMessage = { 
        role: 'assistant', 
        content: responseText
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
      // Obter sugestões baseadas na resposta (apenas se tiver resposta válida)
      if (data.answer) {
        console.log("Gerando sugestões com base na resposta");
        const newSuggestions = await fetchSuggestions(data.answer);
        console.log("Sugestões geradas:", newSuggestions);
        setSuggestions(newSuggestions);
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      
      // Adiciona mensagem de erro
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente mais tarde.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Função para usar uma sugestão
  const handleSuggestionClick = (suggestion) => {
    console.log("Usando sugestão:", suggestion);
    sendMessage(suggestion);
  };

  // Log para depuração
  useEffect(() => {
    console.log("Estado atual de mensagens:", messages);
    console.log("Estado atual de sugestões:", suggestions);
  }, [messages, suggestions]);

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto">
      {/* Link para a área administrativa */}
      <div className="flex justify-end p-2">
        <Link href="/admin/login" className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors">
          Administração
        </Link>
      </div>
      
      <div className="flex-1 overflow-auto p-4 scrollbar-hide">
        {/* Mensagem de boas vindas */}
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
            <div className="rounded-full bg-zinc-800 p-4">
              <span className="text-2xl">🥭</span>
            </div>
            <h1 className="text-xl font-semibold">Mango AI</h1>
            <p className="text-zinc-400 max-w-sm">
              Assistente virtual do Instituto Federal de Pernambuco. 
              Como posso ajudar você hoje?
            </p>
          </div>
        )}

        {/* Lista de mensagens */}
        {messages.map((message, index) => (
          <ChatMessage 
            key={index} 
            role={message.role} 
            content={message.content}
          />
        ))}

        {/* Indicador de carregamento */}
        {isLoading && (
          <div className="flex items-start my-4">
            <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center mr-4">
              <span className="text-sm">🥭</span>
            </div>
            <div className="flex space-x-2">
              <div className="h-2 w-2 rounded-full bg-zinc-400 animate-pulse"></div>
              <div className="h-2 w-2 rounded-full bg-zinc-400 animate-pulse" style={{ animationDelay: '0.2s' }}></div>
              <div className="h-2 w-2 rounded-full bg-zinc-400 animate-pulse" style={{ animationDelay: '0.4s' }}></div>
            </div>
          </div>
        )}

        {/* Referência para auto-scroll */}
        <div ref={messagesEndRef} />
      </div>

      {/* Sugestões de perguntas */}
      {!isLoading && suggestions.length > 0 && messages.length > 0 && (
        <div className="px-4 py-2 flex flex-wrap gap-2">
          {suggestions.map((suggestion, idx) => (
            <SuggestionButton 
              key={idx} 
              text={suggestion} 
              onClick={handleSuggestionClick}
            />
          ))}
        </div>
      )}

      {/* Input para enviar mensagem */}
      <div className="p-4 border-t border-zinc-800">
        <MessageInput onSendMessage={sendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}