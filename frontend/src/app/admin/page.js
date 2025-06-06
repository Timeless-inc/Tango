'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardContent, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { LogOut } from 'lucide-react';
import { KnowledgeList } from '../components/knowledge-list';
import { WebsiteScraper } from '../components/website-scraper';
import { deleteCookie, getCookie } from 'cookies-next';

export default function AdminPage() {
  const [documents, setDocuments] = useState([]);
  const [newDocument, setNewDocument] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });
  const [isAuthChecking, setIsAuthChecking] = useState(true);
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
        fetchDocuments(); // Recarrega a lista
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
    if (!window.confirm('Tem certeza que deseja excluir este documento?')) return;
    
    try {
      const response = await fetch('/api/admin/documents', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: [id] }),
      });
      
      if (response.ok) {
        setMessage({ text: 'Documento excluído com sucesso!', type: 'success' });
        fetchDocuments(); // Recarrega a lista
      } else {
        setMessage({ text: 'Erro ao excluir documento.', type: 'error' });
      }
    } catch (error) {
      console.error('Erro:', error);
      setMessage({ text: 'Erro ao excluir documento.', type: 'error' });
    }
  };

  // Callback para quando o scraping é concluído
  const handleScrapingComplete = (data) => {
    fetchDocuments(); // Recarrega a lista de documentos
    setMessage({ 
      text: `Website processado! ${data.documents_added} documentos adicionados.`, 
      type: 'success' 
    });
  };

  // Fazer logout
  const handleLogout = () => {
    deleteCookie('admin_token');
    router.push('/admin/login');
  };

  // Se estamos verificando autenticação, mostrar tela de carregamento
  if (isAuthChecking) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-zinc-400">Verificando autenticação...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Administração do Mango</h1>
          <Button 
            variant="ghost" 
            className="flex items-center gap-2 text-zinc-400 hover:text-zinc-200"
            onClick={handleLogout}
          >
            <LogOut size={16} />
            <span>Sair</span>
          </Button>
        </div>
        
        {message.text && (
          <div className={`p-3 mb-4 rounded-md ${
            message.type === 'success' ? 'bg-green-900/50 text-green-300' : 'bg-red-900/50 text-red-300'
          }`}>
            {message.text}
          </div>
        )}
        
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Formulário para adicionar documento */}
          <Card className="bg-zinc-900 border-zinc-800">
            <CardHeader>
              <CardTitle>Adicionar Conhecimento</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAddDocument} className="space-y-4">
                <div>
                  <Textarea 
                    value={newDocument}
                    onChange={(e) => setNewDocument(e.target.value)}
                    placeholder="Digite o texto do documento..."
                    rows={6}
                    className="bg-zinc-800 border-zinc-700"
                  />
                </div>
                <Button 
                  type="submit" 
                  disabled={isLoading || !newDocument.trim()}
                  className="w-full"
                >
                  {isLoading ? 'Adicionando...' : 'Adicionar Documento'}
                </Button>
              </form>
            </CardContent>
          </Card>
          
          {/* Componente de Web Scraping */}
          <WebsiteScraper onScrapingComplete={handleScrapingComplete} />
          
          {/* Lista de documentos */}
          <Card className="bg-zinc-900 border-zinc-800">
            <CardHeader>
              <CardTitle>Base de Conhecimento</CardTitle>
            </CardHeader>
            <CardContent>
              <KnowledgeList 
                documents={documents} 
                onDelete={handleDeleteDocument}
              />
            </CardContent>
            <CardFooter className="text-xs text-zinc-500 justify-end">
              {documents.length} documentos encontrados
            </CardFooter>
          </Card>
        </div>
      </div>
    </div>
  );
}