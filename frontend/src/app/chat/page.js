'use client';

import { ChatContainer } from '../components/chat-container';

export default function ChatPage() {
  return (
    <div className="flex flex-col h-screen bg-black text-white">
      <main className="flex-1 overflow-hidden">
        <ChatContainer />
      </main>
    </div>
  );
}