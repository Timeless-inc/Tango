import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { AlertTriangle, X } from 'lucide-react';

export function ConfirmationModal({ 
  isOpen, 
  onClose, 
  onConfirm, 
  title, 
  message, 
  confirmText = "Confirmar", 
  cancelText = "Cancelar",
  type = "danger" // "danger" ou "warning"
}) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsVisible(true);
      // Previne scroll do body quando modal está aberto
      document.body.style.overflow = 'hidden';
    } else {
      // Restaura scroll do body
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(onClose, 150); // Aguarda animação
  };

  const handleConfirm = () => {
    onConfirm();
    handleClose();
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  // Não renderiza se não estiver aberto
  if (!isOpen) return null;

  return (
    <div 
      className={`fixed inset-0 z-50 flex items-center justify-center p-4 transition-all duration-150 ${
        isVisible ? 'bg-black/50 backdrop-blur-sm' : 'bg-transparent'
      }`}
      onClick={handleBackdropClick}
    >
      <div 
        className={`bg-zinc-900 border border-zinc-700 rounded-lg shadow-xl max-w-md w-full transition-all duration-150 ${
          isVisible ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
        }`}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-zinc-700">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-full ${
              type === 'danger' ? 'bg-red-900/50' : 'bg-yellow-900/50'
            }`}>
              <AlertTriangle 
                size={20} 
                className={type === 'danger' ? 'text-red-400' : 'text-yellow-400'} 
              />
            </div>
            <h3 className="text-lg font-semibold text-zinc-200">
              {title}
            </h3>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-zinc-400 hover:text-zinc-200"
            onClick={handleClose}
          >
            <X size={16} />
          </Button>
        </div>

        {/* Content */}
        <div className="p-4">
          <p className="text-zinc-300 leading-relaxed">
            {message}
          </p>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 p-4 border-t border-zinc-700">
          <Button
            variant="ghost"
            onClick={handleClose}
            className="text-zinc-400 hover:text-zinc-200"
          >
            {cancelText}
          </Button>
          <Button
            onClick={handleConfirm}
            className={
              type === 'danger' 
                ? 'bg-red-600 hover:bg-red-700 text-white' 
                : 'bg-yellow-600 hover:bg-yellow-700 text-white'
            }
          >
            {confirmText}
          </Button>
        </div>
      </div>
    </div>
  );
}