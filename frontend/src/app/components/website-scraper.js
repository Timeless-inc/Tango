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
    <Card className="bg-zinc-900/50 backdrop-blur-sm border-zinc-700/50 hover:border-orange-500/30 transition-all duration-300 shadow-none">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-white">
          <Globe className="w-5 h-5 text-orange-500" />
          Extrair de Website
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
        
        <form onSubmit={handleScrape} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">
              URL do Website
            </label>
            <Input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://exemplo.com"
              className="bg-zinc-800/80 border-zinc-600 text-white placeholder:text-zinc-500 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all duration-200 shadow-none"
              required
            />
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="scrapeMultiple"
                checked={scrapeMultiple}
                onChange={(e) => setScrapeMultiple(e.target.checked)}
                className="w-4 h-4 text-orange-500 bg-zinc-800 border-zinc-600 rounded focus:ring-orange-500 focus:ring-2"
              />
              <label htmlFor="scrapeMultiple" className="text-sm text-zinc-300">
                Extrair múltiplas páginas
              </label>
            </div>
            
            {scrapeMultiple && (
              <div className="flex items-center gap-3 ml-7">
                <span className="text-sm text-zinc-400">Máximo:</span>
                <Input
                  type="number"
                  value={maxPages}
                  onChange={(e) => setMaxPages(parseInt(e.target.value) || 10)}
                  min="1"
                  max="50"
                  className="w-20 bg-zinc-800/80 border-zinc-600 text-white focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 transition-all duration-200 shadow-none"
                />
                <span className="text-sm text-zinc-400">páginas</span>
              </div>
            )}
          </div>
          
          <Button 
            type="submit" 
            disabled={isLoading || !url.trim()}
            className="w-full bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-medium transition-all duration-200 shadow-none"
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                Extraindo conteúdo...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4" />
                Extrair Conteúdo
              </div>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}