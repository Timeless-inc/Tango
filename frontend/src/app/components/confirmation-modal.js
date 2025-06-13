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
  type = "danger"
}) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
      onClick={handleBackdropClick}
      style={{ boxShadow: 'none' }}
    >
      <div 
        className="bg-zinc-900 border border-zinc-700 rounded-lg w-full max-w-md min-w-[350px]"
        onClick={(e) => e.stopPropagation()}
        style={{ boxShadow: 'none' }}
      >
       {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-zinc-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-500/20 rounded-lg">
              <AlertTriangle size={18} className="text-red-400" />
            </div>
            <h3 className="text-lg font-semibold text-white">
              {title}
            </h3>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0 text-zinc-400 hover:text-white"
            onClick={onClose}
            style={{ boxShadow: 'none' }}
          >
            <X size={16} />
          </Button>
        </div>

        {/* Content */}
        <div className="p-4">
          <p className="text-zinc-300 text-sm leading-relaxed whitespace-pre-line break-words">
            {message}
          </p>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-2 p-4 border-t border-zinc-700">
          <Button
            variant="ghost"
            onClick={onClose}
            className="text-zinc-400 hover:text-white hover:bg-zinc-800"
            style={{ boxShadow: 'none' }}
          >
            {cancelText}
          </Button>
          <Button
            onClick={onConfirm}
            className="bg-red-600 hover:bg-red-700 text-white"
            style={{ boxShadow: 'none' }}
          >
            {confirmText}
          </Button>
        </div>
      </div>
    </div>
  );
}