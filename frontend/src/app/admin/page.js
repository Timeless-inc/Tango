'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardContent, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { LogOut, Plus, Database, Activity, Shield, BarChart3 } from 'lucide-react';
import { KnowledgeList } from '../components/knowledge-list';
import { WebsiteScraper } from '../components/website-scraper';
import { PDFUploader } from '../components/pdf-uploader';
import { deleteCookie, getCookie } from 'cookies-next';
import { motion } from 'framer-motion';

export default function AdminPage() {
  const [documents, setDocuments] = useState([]);
  const [newDocument, setNewDocument] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });
  const [isAuthChecking, setIsAuthChecking] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    manual: 0,
    pdf: 0,
    website: 0
  });
  const router = useRouter();

  // Verificar autenticação quando a página carrega
  useEffect(() => {
    const checkAuthentication = () => {
      const adminToken = getCookie('admin_token');
      
      if (!adminToken || adminToken !== 'authenticated') {
        console.log('Não autenticado, redirecionando para login...');
        router.replace('/admin/login');
      } else {
        setIsAuthChecking(false);
      }
    };
    
    checkAuthentication();
  }, [router]);

  // Calcular estatísticas
  useEffect(() => {
    const calculateStats = () => {
      const manual = documents.filter(doc => 
        !doc.content?.includes('URL:') && !doc.content?.includes('Arquivo:')
      ).length;
      
      const pdf = documents.filter(doc => 
        doc.content?.includes('Arquivo:') || doc.content?.includes('Tipo: PDF')
      ).length;
      
      const website = documents.filter(doc => 
        doc.content?.includes('URL:')
      ).length;

      setStats({
        total: documents.length,
        manual,
        pdf,
        website
      });
    };

    calculateStats();
  }, [documents]);

  // Buscar documentos existentes
  const fetchDocuments = async () => {
    try {
      const response = await fetch('/api/admin/documents');
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
      }
    } catch (error) {
      console.error('Erro ao buscar documentos:', error);
    }
  };

  useEffect(() => {
    if (!isAuthChecking) {
      fetchDocuments();
    }
  }, [isAuthChecking]);

  // Adicionar novo documento
  const handleAddDocument = async (e) => {
    e.preventDefault();
    
    if (!newDocument.trim()) return;
    
    setIsLoading(true);
    setMessage({ text: '', type: '' });
    
    try {
      const response = await fetch('/api/admin/documents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ documents: [newDocument] }),
      });
      
      if (response.ok) {
        setNewDocument('');
        setMessage({ text: 'Documento adicionado com sucesso!', type: 'success' });
        fetchDocuments();
      } else {
        setMessage({ text: 'Erro ao adicionar documento.', type: 'error' });
      }
    } catch (error) {
      console.error('Erro:', error);
      setMessage({ text: 'Erro ao adicionar documento.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // Excluir documento
  const handleDeleteDocument = async (id) => {
    try {
      const response = await fetch('/api/admin/documents', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: [id] }),
      });
      
      if (response.ok) {
        setMessage({ text: 'Documento excluído com sucesso!', type: 'success' });
        fetchDocuments();
      } else {
        setMessage({ text: 'Erro ao excluir documento.', type: 'error' });
      }
    } catch (error) {
      console.error('Erro:', error);
      setMessage({ text: 'Erro ao excluir documento.', type: 'error' });
    }
  };

  // Callbacks
  const handleScrapingComplete = (data) => {
    fetchDocuments();
    setMessage({ 
      text: `Website processado! ${data.documents_added} documentos adicionados.`, 
      type: 'success' 
    });
  };

  const handlePDFUploadComplete = (data) => {
    fetchDocuments();
    setMessage({ 
      text: `PDF processado! ${data.documents_added} documentos adicionados de ${data.total_pages} páginas.`, 
      type: 'success' 
    });
  };

  const handleLogout = () => {
    deleteCookie('admin_token');
    router.push('/admin/login');
  };

  // Loading state
  if (isAuthChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-orange-500 mx-auto"></div>
            <Shield className="absolute inset-4 text-orange-500" />
          </div>
          <p className="mt-6 text-zinc-400 text-lg">Verificando autenticação...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Header moderno */}
      <div className="border-b border-zinc-800/50 backdrop-blur-sm bg-zinc-900/20 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-4"
            >
              <div className="p-2 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Painel Administrativo</h1>
                <p className="text-zinc-400 text-sm">Mango AI - Sistema de Gerenciamento</p>
              </div>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-4"
            >
              <Badge variant="outline" className="border-green-600 text-green-400">
                <Activity className="w-3 h-3 mr-1" />
                Online
              </Badge>
              <Button 
                variant="ghost" 
                className="flex items-center gap-2 text-zinc-400 hover:text-white hover:bg-zinc-800/50 transition-all duration-200"
                onClick={handleLogout}
              >
                <LogOut size={16} />
                <span>Sair</span>
              </Button>
            </motion.div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Cards de estatísticas */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
        >
          <Card className="bg-zinc-900/50 backdrop-blur-sm border-zinc-700/50 hover:border-orange-500/30 transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-zinc-400 text-sm font-medium">Total de Documentos</p>
                  <p className="text-2xl font-bold text-white">{stats.total}</p>
                </div>
                <div className="p-3 bg-blue-500/20 rounded-full">
                  <Database className="w-6 h-6 text-blue-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-zinc-900/50 backdrop-blur-sm border-zinc-700/50 hover:border-green-500/30 transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-zinc-400 text-sm font-medium">Documentos Manuais</p>
                  <p className="text-2xl font-bold text-white">{stats.manual}</p>
                </div>
                <div className="p-3 bg-green-500/20 rounded-full">
                  <Plus className="w-6 h-6 text-green-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-zinc-900/50 backdrop-blur-sm border-zinc-700/50 hover:border-red-500/30 transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-zinc-400 text-sm font-medium">Arquivos PDF</p>
                  <p className="text-2xl font-bold text-white">{stats.pdf}</p>
                </div>
                <div className="p-3 bg-red-500/20 rounded-full">
                  <BarChart3 className="w-6 h-6 text-red-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-zinc-900/50 backdrop-blur-sm border-zinc-700/50 hover:border-purple-500/30 transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-zinc-400 text-sm font-medium">Sites Extraídos</p>
                  <p className="text-2xl font-bold text-white">{stats.website}</p>
                </div>
                <div className="p-3 bg-purple-500/20 rounded-full">
                  <Activity className="w-6 h-6 text-purple-400" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Mensagem de feedback */}
        {message.text && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-4 mb-6 rounded-lg border backdrop-blur-sm ${
              message.type === 'success' 
                ? 'bg-green-900/30 border-green-700/50 text-green-300' 
                : 'bg-red-900/30 border-red-700/50 text-red-300'
            }`}
          >
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                message.type === 'success' ? 'bg-green-400' : 'bg-red-400'
              }`}></div>
              {message.text}
            </div>
          </motion.div>
        )}
        
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Formulário para adicionar documento */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card className="bg-zinc-900/50 backdrop-blur-sm border-zinc-700/50 hover:border-orange-500/30 transition-all duration-300">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-white">
                  <Plus className="w-5 h-5 text-orange-500" />
                  Adicionar Conhecimento
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleAddDocument} className="space-y-4">
                  <div>
                    <Textarea 
                      value={newDocument}
                      onChange={(e) => setNewDocument(e.target.value)}
                      placeholder="Digite o texto do documento..."
                      rows={6}
                      className="bg-zinc-800/80 border-zinc-600 text-white placeholder:text-zinc-500 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all duration-200 resize-none"
                    />
                  </div>
                  <Button 
                    type="submit" 
                    disabled={isLoading || !newDocument.trim()}
                    className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-medium shadow-lg hover:shadow-orange-500/25 transition-all duration-200"
                  >
                    {isLoading ? (
                      <div className="flex items-center gap-2">
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                        Adicionando...
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <Plus className="w-4 h-4" />
                        Adicionar Documento
                      </div>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </motion.div>
          
          {/* Componente de Upload de PDF */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <PDFUploader onUploadComplete={handlePDFUploadComplete} />
          </motion.div>
          
          {/* Componente de Web Scraping */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <WebsiteScraper onScrapingComplete={handleScrapingComplete} />
          </motion.div>
          
          {/* Lista de documentos - ocupa toda a largura */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="lg:col-span-3"
          >
            <Card className="bg-zinc-900/50 backdrop-blur-sm border-zinc-700/50">
              <CardHeader className="border-b border-zinc-700/50">
                <CardTitle className="flex items-center gap-2 text-white">
                  <Database className="w-5 h-5 text-blue-500" />
                  Base de Conhecimento
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <KnowledgeList 
                  documents={documents} 
                  onDelete={handleDeleteDocument}
                />
              </CardContent>
              <CardFooter className="border-t border-zinc-700/50 bg-zinc-800/30">
                <div className="flex items-center justify-between w-full">
                  <div className="flex items-center gap-4 text-xs text-zinc-400">
                    <span className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                      {stats.total} total
                    </span>
                    <span className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                      {stats.manual} manuais
                    </span>
                    <span className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                      {stats.pdf} PDFs
                    </span>
                    <span className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                      {stats.website} websites
                    </span>
                  </div>
                  <Badge variant="secondary" className="bg-zinc-700/50 text-zinc-300">
                    Atualizado agora
                  </Badge>
                </div>
              </CardFooter>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
}