import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { Globe, Loader2 } from 'lucide-react';

export function WebsiteScraper({ onScrapingComplete }) {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });
  const [scrapeMultiple, setScrapeMultiple] = useState(false);
  const [maxPages, setMaxPages] = useState(10);

  const handleScrape = async (e) => {
    e.preventDefault();
    
    if (!url.trim()) {
      setMessage({ text: 'Por favor, insira uma URL válida.', type: 'error' });
      return;
    }

    setIsLoading(true);
    setMessage({ text: '', type: '' });

    try {
      const response = await fetch('/api/scrape-website', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: url.trim(),
          scrape_multiple: scrapeMultiple,
          max_pages: maxPages,
          max_length: 5000
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        let messageText = `✅ Scraping concluído! ${data.documents_added} documentos adicionados.`;
        
        if (data.failed_urls.length > 0) {
          messageText += ` ${data.failed_urls.length} URLs falharam.`;
        }
        
        setMessage({ text: messageText, type: 'success' });
        setUrl('');
        
        if (onScrapingComplete) {
          onScrapingComplete(data);
        }
      } else {
        const errorData = await response.json();
        setMessage({ 
          text: errorData.detail || 'Erro ao processar o site.', 
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
      setIsLoading(false);
    }
  };

  return (
    <Card className="bg-zinc-900 border-zinc-800">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Globe size={20} />
          Extrair de Website
        </CardTitle>
      </CardHeader>
      <CardContent>
        {message.text && (
          <div className={`p-3 mb-4 rounded-md text-sm ${
            message.type === 'success' 
              ? 'bg-green-900/50 text-green-300' 
              : 'bg-red-900/50 text-red-300'
          }`}>
            {message.text}
          </div>
        )}
        
        <form onSubmit={handleScrape} className="space-y-4">
          <div>
            <Input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://exemplo.com"
              className="bg-zinc-800 border-zinc-700"
              required
            />
          </div>
          
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={scrapeMultiple}
                onChange={(e) => setScrapeMultiple(e.target.checked)}
                className="rounded"
              />
              Extrair múltiplas páginas
            </label>
            
            {scrapeMultiple && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-zinc-400">Máx:</span>
                <Input
                  type="number"
                  value={maxPages}
                  onChange={(e) => setMaxPages(parseInt(e.target.value) || 10)}
                  min="1"
                  max="50"
                  className="w-20 bg-zinc-800 border-zinc-700"
                />
                <span className="text-sm text-zinc-400">páginas</span>
              </div>
            )}
          </div>
          
          <Button 
            type="submit" 
            disabled={isLoading || !url.trim()}
            className="w-full"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Extraindo conteúdo...
              </>
            ) : (
              'Extrair Conteúdo'
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}