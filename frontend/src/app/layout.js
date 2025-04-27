import './globals.css';

export const metadata = {
  title: 'Mango AI',
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
  description: 'Em que posso te ajudar?',
  keywords: 'Mango AI, Chatbot, AI, Inteligência Artificial, Assistente Virtual',
  authors: [
    { name: 'Timeless', url: 'https://github.com/Timeless-inc' },
  ],
}

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR" className="dark">
      <body className="bg-black min-h-screen">
        {children}
      </body>
    </html>
  )
}