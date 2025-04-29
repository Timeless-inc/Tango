import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";

export function KnowledgeList({ documents, onDelete }) {
  if (!documents || documents.length === 0) {
    return (
      <div className="text-center py-6 text-zinc-400">
        Nenhum documento encontrado.
      </div>
    );
  }

  return (
    <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
      {documents.map((doc, index) => (
        <div key={index} className="bg-zinc-800 p-3 rounded-md group relative">
          <p className="text-sm text-zinc-300 pr-8">{doc.content || doc}</p>
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6 text-zinc-400 hover:text-red-400 hover:bg-zinc-700/50"
            onClick={() => onDelete(doc.id !== undefined ? doc.id : index)}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      ))}
    </div>
  );
}