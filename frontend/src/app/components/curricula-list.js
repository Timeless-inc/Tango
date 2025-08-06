'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Download, Trash2, FileText, Calendar, BookOpen } from 'lucide-react';
import { motion } from 'framer-motion';

export function CurriculaList({ onDelete }) {
  const [curricula, setCurricula] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [message, setMessage] = useState({ text: '', type: '' });

  useEffect(() => {
    fetchCurricula();
  }, []);

  const fetchCurricula = async () => {
    try {
      const response = await fetch('/api/upload-curriculum');
      const data = await response.json();
      setCurricula(data.curricula || []);
    } catch (error) {
      console.error('Erro ao carregar matrizes curriculares:', error);
      setMessage({ text: 'Erro ao carregar matrizes curriculares', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Tem certeza que deseja excluir esta matriz curricular?')) {
      return;
    }

    try {
      const response = await fetch('/api/upload-curriculum', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id }),
      });

      if (response.ok) {
        setMessage({ text: 'Matriz curricular excluída com sucesso!', type: 'success' });
        fetchCurricula();
        if (onDelete) onDelete();
        
        setTimeout(() => {
          setMessage({ text: '', type: '' });
        }, 3000);
      } else {
        const result = await response.json();
        setMessage({ text: result.error || 'Erro ao excluir matriz curricular', type: 'error' });
      }
    } catch (error) {
      console.error('Erro ao excluir:', error);
      setMessage({ text: 'Erro ao excluir matriz curricular', type: 'error' });
    }
  };

  const handleDownload = (curriculum) => {
    const link = document.createElement('a');
    link.href = curriculum.filePath;
    link.download = `${curriculum.courseName} - Matriz Curricular.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getCourseTypeColor = (type) => {
    const colors = {
      'Técnico Subsequente': 'bg-blue-500/20 text-blue-300 border-blue-500/30',
      'Técnico Integrado': 'bg-green-500/20 text-green-300 border-green-500/30',
      'Tecnologia Superior': 'bg-purple-500/20 text-purple-300 border-purple-500/30',
      'Bacharelado': 'bg-orange-500/20 text-orange-300 border-orange-500/30',
      'Licenciatura': 'bg-pink-500/20 text-pink-300 border-pink-500/30',
      'Qualificação Profissional': 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
      'FIC - Formação Inicial e Continuada': 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30'
    };
    return colors[type] || 'bg-zinc-500/20 text-zinc-300 border-zinc-500/30';
  };

  if (isLoading) {
    return (
      <Card className="bg-zinc-900/50 backdrop-blur-sm border-zinc-700/50">
        <CardContent className="p-6">
          <div className="flex items-center justify-center py-8">
            <div className="w-6 h-6 border-2 border-orange-500/30 border-t-orange-500 rounded-full animate-spin"></div>
            <span className="ml-2 text-zinc-400">Carregando matrizes curriculares...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-zinc-900/50 backdrop-blur-sm border-zinc-700/50">
      <CardHeader className="border-b border-zinc-700/50">
        <CardTitle className="flex items-center gap-2 text-white">
          <BookOpen className="w-5 h-5 text-orange-500" />
          Matrizes Curriculares ({curricula.length})
        </CardTitle>
      </CardHeader>
      <CardContent className="p-6">
        {/* Mensagem de Feedback */}
        {message.text && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-3 mb-4 rounded-lg text-sm ${
              message.type === 'success'
                ? 'bg-green-900/30 border border-green-700/50 text-green-300'
                : 'bg-red-900/30 border border-red-700/50 text-red-300'
            }`}
          >
            {message.text}
          </motion.div>
        )}

        {curricula.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="w-12 h-12 text-zinc-600 mx-auto mb-3" />
            <p className="text-zinc-400 mb-2">Nenhuma matriz curricular encontrada</p>
            <p className="text-zinc-500 text-sm">
              Use o formulário acima para adicionar matrizes curriculares dos cursos
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {curricula.map((curriculum, index) => (
              <motion.div
                key={curriculum.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 bg-zinc-800/50 rounded-lg border border-zinc-700/50 hover:border-orange-500/30 transition-all duration-200"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <FileText className="w-4 h-4 text-red-400 flex-shrink-0" />
                      <h3 className="text-white font-medium truncate">
                        {curriculum.courseName}
                      </h3>
                    </div>
                    
                    <div className="flex flex-wrap items-center gap-2 mb-3">
                      <Badge 
                        variant="outline" 
                        className={`text-xs ${getCourseTypeColor(curriculum.courseType)}`}
                      >
                        {curriculum.courseType}
                      </Badge>
                      <span className="text-zinc-500 text-xs">
                        {formatFileSize(curriculum.fileSize)}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-4 text-xs text-zinc-400">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatDate(curriculum.uploadDate)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDownload(curriculum)}
                      className="text-blue-400 hover:text-blue-300 hover:bg-blue-500/10"
                      title="Baixar matriz curricular"
                    >
                      <Download className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(curriculum.id)}
                      className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                      title="Excluir matriz curricular"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
