export default function ThinkingBubble() {
  return (
    <div className="flex justify-start">
      <div className="p-3 m-2 rounded-2xl max-w-xs bg-gradient-to-r from-slate-700
        to-slate-800 text-white border border-slate-600">
        <div className="flex items-center gap-2">
          <div className="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full"></div>
          Thinking...
        </div>
      </div>
    </div>
  );
}