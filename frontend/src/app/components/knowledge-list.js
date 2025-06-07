import { Trash2, ExternalLink, FileText, Globe, File } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { useState } from 'react';
import { ConfirmationModal } from './confirmation-modal';

export function KnowledgeList({ documents, onDelete }) {
  const [expandedDoc, setExpandedDoc] = useState(null);
  const [modalState, setModalState] = useState({
    isOpen: false,
    type: 'single', // 'single' ou 'group'
    docId: null,
    groupData: null
  });
  
  if (!documents || documents.length === 0) {
    return (
      <div className="text-center py-6 text-zinc-400">
        Nenhum documento encontrado.
      </div>
    );
  }

  // Funções auxiliares
  const extractGroupTitle = (groupKey, sourceType) => {
    if (sourceType === 'pdf') {
      return groupKey.replace('📄 ', '').replace('.pdf', '');
    } else if (sourceType === 'website') {
      try {
        return new URL(groupKey).hostname;
      } catch {
        return groupKey;
      }
    }
    return 'Documentos manuais';
  };

  const getSourceIcon = (type) => {
    switch (type) {
      case 'website':
        return <Globe size={16} className="text-blue-400" />;
      case 'pdf':
        return <File size={16} className="text-red-400" />;
      default:
        return <FileText size={16} className="text-zinc-400" />;
    }
  };

  const toggleExpanded = (docId) => {
    setExpandedDoc(expandedDoc === docId ? null : docId);
  };

  // Funções de modal
  const openGroupDeleteModal = (group, groupKey) => {
    setModalState({
      isOpen: true,
      type: 'group',
      docId: null,
      groupData: {
        ...group,
        groupKey,
        docIds: group.docs.map(doc => doc.id)
      }
    });
  };

  const openSingleDeleteModal = (docId) => {
    setModalState({
      isOpen: true,
      type: 'single',
      docId,
      groupData: null
    });
  };

  const closeModal = () => {
    setModalState({
      isOpen: false,
      type: 'single',
      docId: null,
      groupData: null
    });
  };

  const handleConfirmDelete = async () => {
    try {
      if (modalState.type === 'group' && modalState.groupData) {
        // Deleta todos os chunks do grupo de uma vez
        const docIds = modalState.groupData.docIds;
        
        // Chama onDelete uma única vez com todos os IDs
        for (const id of docIds) {
          await onDelete(id);
        }
        
        console.log(`Grupo deletado: ${docIds.length} chunks removidos`);
        
      } else if (modalState.type === 'single' && modalState.docId !== null) {
        // Deleta um chunk específico
        await onDelete(modalState.docId);
        console.log(`Chunk deletado: ${modalState.docId}`);
      }
    } catch (error) {
      console.error('Erro ao deletar:', error);
    }
    
    // Fecha o modal apenas após completar a operação
    closeModal();
  };

  // Agrupa documentos por fonte
  const groupedDocs = documents.reduce((acc, doc) => {
    let groupKey = 'Documentos manuais';
    let sourceType = 'manual';
    
    if (doc.full_content || doc.content) {
      const content = doc.full_content || doc.content;
      
      if (content.includes('URL:')) {
        const urlMatch = content.match(/URL:\s*(.+)/);
        if (urlMatch) {
          groupKey = urlMatch[1].trim();
          sourceType = 'website';
        }
      } else if (content.includes('Arquivo:') || content.includes('Tipo: PDF')) {
        const fileMatch = content.match(/Arquivo:\s*(.+)/);
        if (fileMatch) {
          groupKey = `📄 ${fileMatch[1].trim()}`;
          sourceType = 'pdf';
        } else {
          groupKey = 'Documentos PDF';
          sourceType = 'pdf';
        }
      }
    }
    
    if (!acc[groupKey]) {
      acc[groupKey] = {
        docs: [],
        type: sourceType,
        title: extractGroupTitle(groupKey, sourceType)
      };
    }
    acc[groupKey].docs.push(doc);
    return acc;
  }, {});

  // Prepara dados do modal
  const getModalData = () => {
    if (modalState.type === 'group' && modalState.groupData) {
      const group = modalState.groupData;
      return {
        title: "Remover fonte completa",
        message: `Tem certeza que deseja remover todos os ${group.docs.length} chunks da fonte "${group.title}"? Esta ação não pode ser desfeita.`,
        confirmText: `Remover ${group.docs.length} chunks`,
        type: "danger"
      };
    } else {
      return {
        title: "Remover chunk",
        message: "Tem certeza que deseja remover este chunk? Esta ação não pode ser desfeita.",
        confirmText: "Remover chunk",
        type: "danger"
      };
    }
  };

  const modalData = getModalData();

  return (
    <>
      <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
        {Object.entries(groupedDocs).map(([groupKey, group]) => (
          <div key={groupKey} className="border border-zinc-700 rounded-lg overflow-hidden">
            {/* Cabeçalho do grupo */}
            <div className="bg-zinc-800 p-3 border-b border-zinc-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getSourceIcon(group.type)}
                  <div>
                    <p className="text-sm font-medium text-zinc-200">
                      {group.title}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <p className="text-xs text-zinc-400">
                        {group.docs.length} chunk{group.docs.length > 1 ? 's' : ''}
                      </p>
                      <span className="text-xs px-2 py-1 rounded-full bg-zinc-700 text-zinc-300">
                        {group.type === 'website' ? 'Website' : 
                         group.type === 'pdf' ? 'PDF' : 'Manual'}
                      </span>
                      {group.type === 'website' && (
                        <a 
                          href={groupKey} 
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
                  onClick={() => openGroupDeleteModal(group, groupKey)}
                >
                  <Trash2 size={16} />
                </Button>
              </div>
            </div>
            
            {/* Lista de chunks */}
            <div className="divide-y divide-zinc-700">
              {group.docs.map((doc, index) => (
                <div key={doc.id} className="p-3 bg-zinc-900/50">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-zinc-500 mb-1">
                        Chunk {index + 1} • {doc.content?.length || 0} caracteres
                        {group.type === 'pdf' && doc.full_content && (
                          <>
                            {(() => {
                              const pageMatch = doc.full_content.match(/Página:\s*(\d+)\s*de\s*(\d+)/);
                              return pageMatch ? ` • Página ${pageMatch[1]}` : '';
                            })()}
                          </>
                        )}
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
                      onClick={() => openSingleDeleteModal(doc.id)}
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

      {/* Modal de Confirmação */}
      <ConfirmationModal
        isOpen={modalState.isOpen}
        onClose={closeModal}
        onConfirm={handleConfirmDelete}
        title={modalData.title}
        message={modalData.message}
        confirmText={modalData.confirmText}
        cancelText="Cancelar"
        type={modalData.type}
      />
    </>
  );
}