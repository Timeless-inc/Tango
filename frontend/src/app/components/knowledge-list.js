import { Trash2, ExternalLink, FileText } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { useState } from 'react';

export function KnowledgeList({ documents, onDelete }) {
  const [expandedDoc, setExpandedDoc] = useState(null);
  
  if (!documents || documents.length === 0) {
    return (
      <div className="text-center py-6 text-zinc-400">
        Nenhum documento encontrado.
      </div>
    );
  }

  // Agrupa documentos por URL
  const groupedDocs = documents.reduce((acc, doc) => {
    const url = doc.url || 'Sem URL';
    if (!acc[url]) {
      acc[url] = [];
    }
    acc[url].push(doc);
    return acc;
  }, {});

  const toggleExpanded = (docId) => {
    setExpandedDoc(expandedDoc === docId ? null : docId);
  };

  return (
    <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
      {Object.entries(groupedDocs).map(([url, docs]) => (
        <div key={url} className="border border-zinc-700 rounded-lg overflow-hidden">
          {/* Cabeçalho do grupo */}
          <div className="bg-zinc-800 p-3 border-b border-zinc-700">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText size={16} className="text-zinc-400" />
                <div>
                  <p className="text-sm font-medium text-zinc-200">
                    {docs[0]?.title || 'Documento sem título'}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <p className="text-xs text-zinc-400">
                      {docs.length} chunk{docs.length > 1 ? 's' : ''}
                    </p>
                    {url !== 'Sem URL' && (
                      <a 
                        href={url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
                      >
                        <ExternalLink size={12} />
                        Ver fonte
                      </a>
                    )}
                  </div>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="text-zinc-400 hover:text-red-400"
                onClick={() => {
                  const docIds = docs.map(doc => doc.id);
                  if (window.confirm(`Remover todos os ${docs.length} chunks desta fonte?`)) {
                    docIds.forEach(id => onDelete(id));
                  }
                }}
              >
                <Trash2 size={16} />
              </Button>
            </div>
          </div>
          
          {/* Lista de chunks */}
          <div className="divide-y divide-zinc-700">
            {docs.map((doc, index) => (
              <div key={doc.id} className="p-3 bg-zinc-900/50">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-zinc-500 mb-1">
                      Chunk {index + 1} • {doc.content?.length || 0} caracteres
                    </p>
                    <p className={`text-sm text-zinc-300 ${
                      expandedDoc === doc.id ? '' : 'line-clamp-2'
                    }`}>
                      {expandedDoc === doc.id ? doc.full_content || doc.content : doc.content}
                    </p>
                    {doc.content && doc.content.length > 100 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-xs text-zinc-400 hover:text-zinc-200 p-0 h-auto mt-1"
                        onClick={() => toggleExpanded(doc.id)}
                      >
                        {expandedDoc === doc.id ? 'Mostrar menos' : 'Mostrar mais'}
                      </Button>
                    )}
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 text-zinc-400 hover:text-red-400 hover:bg-zinc-700/50"
                    onClick={() => {
                      if (window.confirm('Remover este chunk?')) {
                        onDelete(doc.id);
                      }
                    }}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}