export function SuggestionButton({ text, onClick }) {
  return (
    <button
      onClick={() => onClick(text)}
      className="text-sm bg-zinc-800 hover:bg-zinc-700 text-zinc-300 py-1 px-3 rounded-full transition-colors"
    >
      {text}
    </button>
  );
}