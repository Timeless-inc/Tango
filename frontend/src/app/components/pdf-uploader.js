import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { FileText, Loader2, Upload } from 'lucide-react';

export function PDFUploader({ onUploadComplete }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });
  const [chunkSize, setChunkSize] = useState(1000);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    
    if (file) {
      if (!file.type.includes('pdf') && !file.name.toLowerCase().endsWith('.pdf')) {
        setMessage({ text: 'Por favor, selecione apenas arquivos PDF.', type: 'error' });
        setSelectedFile(null);
        return;
      }
      
      if (file.size > 10 * 1024 * 1024) { // 10MB limite
        setMessage({ text: 'Arquivo muito grande. Máximo 10MB.', type: 'error' });
        setSelectedFile(null);
        return;
      }
      
      setSelectedFile(file);
      setMessage({ text: '', type: '' });
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setMessage({ text: 'Por favor, selecione um arquivo PDF.', type: 'error' });
      return;
    }

    setIsUploading(true);
    setMessage({ text: '', type: '' });

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('chunk_size', chunkSize.toString());

      const response = await fetch('/api/upload-pdf', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        
        setMessage({ 
          text: `✅ PDF processado! ${data.documents_added} chunks adicionados de ${data.total_pages} páginas.`, 
          type: 'success' 
        });
        
        setSelectedFile(null);
        
        // Reset file input
        const fileInput = document.getElementById('pdf-file-input');
        if (fileInput) fileInput.value = '';
        
        if (onUploadComplete) {
          onUploadComplete(data);
        }
      } else {
        const errorData = await response.json();
        setMessage({ 
          text: errorData.detail || 'Erro ao processar o PDF.', 
          type: 'error' 
        });
      }
    } catch (error) {
      console.error('Erro:', error);
      setMessage({ 
        text: 'Erro de conexão. Verifique se o backend está rodando.', 
        type: 'error' 
      });
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Card className="bg-zinc-900/50 backdrop-blur-sm border-zinc-700/50 hover:border-orange-500/30 transition-all duration-300 shadow-none">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-white">
          <FileText className="w-5 h-5 text-orange-500" />
          Upload de PDF
        </CardTitle>
      </CardHeader>
      <CardContent>
        {message.text && (
          <div className={`p-4 mb-4 rounded-lg border backdrop-blur-sm shadow-none ${
            message.type === 'success' 
              ? 'bg-green-900/30 border-green-700/50 text-green-300' 
              : 'bg-red-900/30 border-red-700/50 text-red-300'
          }`}>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                message.type === 'success' ? 'bg-green-400' : 'bg-red-400'
              }`}></div>
              {message.text}
            </div>
          </div>
        )}
        
        <form onSubmit={handleUpload} className="space-y-4">
          <div>
            <Input
              id="pdf-file-input"
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileSelect}
              className="bg-zinc-800/80 border-zinc-600 text-white placeholder:text-zinc-500 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all duration-200 shadow-none"
            />
            {selectedFile && (
              <div className="mt-2 p-3 bg-zinc-800/50 border border-zinc-700/50 rounded-lg shadow-none">
                <div className="flex items-center gap-2">
                  <FileText size={16} className="text-blue-400" />
                  <span className="text-zinc-200">{selectedFile.name}</span>
                  <span className="text-zinc-400">({formatFileSize(selectedFile.size)})</span>
                </div>
              </div>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">
              Tamanho do chunk (caracteres)
            </label>
            <Input
              type="number"
              value={chunkSize}
              onChange={(e) => setChunkSize(parseInt(e.target.value) || 1000)}
              min="500"
              max="5000"
              className="bg-zinc-800/80 border-zinc-600 text-white placeholder:text-zinc-500 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all duration-200 shadow-none"
            />
            <p className="text-xs text-zinc-500 mt-1">
              Chunks menores = mais precisão, chunks maiores = mais contexto
            </p>
          </div>
          
          <Button 
            type="submit" 
            disabled={isUploading || !selectedFile}
            className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-medium transition-all duration-200 shadow-none"
          >
            {isUploading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Processando PDF...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Upload className="w-4 h-4" />
                Fazer Upload e Processar
              </div>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}