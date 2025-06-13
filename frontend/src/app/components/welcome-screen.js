'use client';

import { motion } from 'framer-motion';
import { Sparkles, Brain, MessageCircle, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';

const features = [
  {
    icon: Brain,
    title: "Campus",
    description: "Informações e serviços"
  },
  {
    icon: MessageCircle,
    title: "Chat",
    description: "Conversas naturais"
  },
  {
    icon: Zap,
    title: "Rapidez",
    description: "Respostas instantâneas"
  }
];

const quickQuestions = [
  "Como me inscrever no IFPE?",
  "Quais cursos estão disponíveis?",
  "Onde fica o campus?",
  "Como funciona a matrícula?"
];

export function WelcomeScreen() {
  const handleQuestionClick = (question) => {
    // Despacha evento customizado para o MessageInput
    window.dispatchEvent(
      new CustomEvent('sendMessage', { detail: question })
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="flex flex-col items-center justify-center min-h-[70vh] text-center space-y-12 px-4"
    >
      {/* Hero section */}
      <motion.div
        initial={{ scale: 0.9 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="relative z-10"
      >
        </motion.div>

      {/* Features grid */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.7 }}
        className="grid md:grid-cols-3 gap-6 w-full max-w-5xl"
      >
        {features.map((feature, index) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.8 + index * 0.1 }}
            whileHover={{ 
              y: -8,
              transition: { duration: 0.2 }
            }}
            className="glass glass-hover p-8 rounded-3xl text-left backdrop-blur-xl bg-gradient-to-br from-white/5 to-white/10 border border-orange-500/20 hover:border-orange-500/40"
          >
            <div className="w-16 h-16 bg-gradient-to-br from-orange-500/20 to-orange-600/30 rounded-2xl flex items-center justify-center mb-6 shadow-lg">
              <feature.icon className="w-8 h-8 text-orange-400" />
            </div>
            <h3 className="font-bold text-white mb-3 text-lg">{feature.title}</h3>
            <p className="text-gray-400 leading-relaxed">{feature.description}</p>
          </motion.div>
        ))}
      </motion.div>

      {/* Quick questions */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 1.0 }}
        className="w-full max-w-4xl"
      >
        <h3 className="text-2xl font-bold mb-8 text-white">
          Perguntas frequentes:
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {quickQuestions.map((question, index) => (
            <motion.div
              key={question}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: 1.1 + index * 0.1 }}
              whileHover={{ 
                scale: 1.02,
                transition: { duration: 0.2 }
              }}
              whileTap={{ scale: 0.98 }}
            >
              <Button
                variant="outline"
                className="w-full glass glass-hover p-6 h-auto text-left text-gray-300 hover:text-white border border-orange-500/30 hover:border-orange-500/60 bg-gradient-to-r from-orange-500/5 to-orange-600/10 hover:from-orange-500/10 hover:to-orange-600/20 backdrop-blur-xl transition-all duration-300"
                onClick={() => handleQuestionClick(question)}
              >
                <span className="text-orange-400 mr-3 text-lg">→</span>
                {question}
              </Button>
            </motion.div>
          ))}
        </div>
      </motion.div>

     
    </motion.div>
  );
}