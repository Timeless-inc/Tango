'use client';

import { useState } from 'react';
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Upload, File, X, BookOpen } from 'lucide-react';
import { motion } from 'framer-motion';

export function CurriculumUploader({ onUploadComplete }) {
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [courseName, setCourseName] = useState('');
  const [courseType, setCourseType] = useState('');
  const [message, setMessage] = useState({ text: '', type: '' });

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setMessage({ text: '', type: '' });
    } else {
      setMessage({ text: 'Por favor, selecione apenas arquivos PDF.', type: 'error' });
      e.target.value = '';
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setMessage({ text: '', type: '' });
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!selectedFile || !courseName.trim() || !courseType.trim()) {
      setMessage({ text: 'Por favor, preencha todos os campos e selecione um arquivo.', type: 'error' });
      return;
    }

    setIsUploading(true);
    setMessage({ text: '', type: '' });

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('courseName', courseName.trim());
      formData.append('courseType', courseType.trim());

      const response = await fetch('/api/upload-curriculum', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setMessage({ text: 'Matriz curricular enviada com sucesso!', type: 'success' });
        setSelectedFile(null);
        setCourseName('');
        setCourseType('');
        
        if (onUploadComplete) {
          onUploadComplete(result);
        }
        
        // Limpar formulário após 3 segundos
        setTimeout(() => {
          setMessage({ text: '', type: '' });
        }, 3000);
      } else {
        setMessage({ text: result.error || 'Erro ao enviar matriz curricular.', type: 'error' });
      }
    } catch (error) {
      console.error('Erro no upload:', error);
      setMessage({ text: 'Erro ao enviar matriz curricular.', type: 'error' });
    } finally {
      setIsUploading(false);
    }
  };

  const courseTypes = [
    'Técnico Subsequente',
    'Técnico Integrado',
    'Tecnologia Superior',
    'Bacharelado',
    'Licenciatura',
    'Qualificação Profissional',
    'FIC - Formação Inicial e Continuada'
  ];

  return (
    <Card className="bg-zinc-900/50 backdrop-blur-sm border-zinc-700/50 hover:border-orange-500/30 transition-all duration-300">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-white">
          <BookOpen className="w-5 h-5 text-orange-500" />
          Upload de Matriz Curricular
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleUpload} className="space-y-4">
          {/* Nome do Curso */}
          <div className="space-y-2">
            <Label htmlFor="courseName" className="text-zinc-300 text-sm font-medium">
              Nome do Curso
            </Label>
            <Input
              id="courseName"
              type="text"
              value={courseName}
              onChange={(e) => setCourseName(e.target.value)}
              placeholder="Ex: Tecnologia em Sistemas para Internet"
              className="bg-zinc-800/80 border-zinc-600 text-white placeholder:text-zinc-500 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all duration-200"
            />
          </div>

          {/* Tipo do Curso */}
          <div className="space-y-2">
            <Label htmlFor="courseType" className="text-zinc-300 text-sm font-medium">
              Tipo do Curso
            </Label>
            <select
              id="courseType"
              value={courseType}
              onChange={(e) => setCourseType(e.target.value)}
              className="w-full px-3 py-2 bg-zinc-800/80 border border-zinc-600 text-white rounded-md focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all duration-200"
            >
              <option value="">Selecione o tipo de curso</option>
              {courseTypes.map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          {/* Upload de Arquivo */}
          <div className="space-y-2">
            <Label className="text-zinc-300 text-sm font-medium">
              Arquivo PDF da Matriz Curricular
            </Label>
            
            {!selectedFile ? (
              <div className="relative">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                />
                <div className="border-2 border-dashed border-zinc-600 hover:border-orange-500/50 rounded-lg p-6 text-center transition-all duration-200 bg-zinc-800/30 hover:bg-zinc-800/50">
                  <Upload className="w-8 h-8 text-zinc-400 mx-auto mb-2" />
                  <p className="text-zinc-300 text-sm">
                    Clique para selecionar ou arraste o arquivo PDF
                  </p>
                  <p className="text-zinc-500 text-xs mt-1">
                    Apenas arquivos PDF são aceitos
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-between p-3 bg-zinc-800/80 border border-zinc-600 rounded-lg">
                <div className="flex items-center gap-3">
                  <File className="w-5 h-5 text-red-400" />
                  <div>
                    <p className="text-white text-sm font-medium">{selectedFile.name}</p>
                    <p className="text-zinc-400 text-xs">
                      {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={removeFile}
                  className="text-zinc-400 hover:text-red-400 hover:bg-red-500/10"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            )}
          </div>

          {/* Mensagem de Feedback */}
          {message.text && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`p-3 rounded-lg text-sm ${
                message.type === 'success'
                  ? 'bg-green-900/30 border border-green-700/50 text-green-300'
                  : 'bg-red-900/30 border border-red-700/50 text-red-300'
              }`}
            >
              {message.text}
            </motion.div>
          )}

          {/* Botão de Upload */}
          <Button
            type="submit"
            disabled={isUploading || !selectedFile || !courseName.trim() || !courseType.trim()}
            className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-medium shadow-lg hover:shadow-orange-500/25 transition-all duration-200"
          >
            {isUploading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Enviando Matriz...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Upload className="w-4 h-4" />
                Enviar Matriz Curricular
              </div>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
