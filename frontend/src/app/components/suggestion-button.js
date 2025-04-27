import { Button } from "@/components/ui/button";

export function SuggestionButton({ text, onClick }) {
  return (
    <Button 
      variant="outline" 
      className="bg-zinc-800 text-zinc-100 hover:bg-zinc-700 border-zinc-700 h-auto py-3 px-3 text-left justify-start font-normal"
      onClick={() => onClick(text)}
    >
      <div className="flex flex-col">
        <span className="text-sm">{text}</span>
      </div>
    </Button>
  );
}