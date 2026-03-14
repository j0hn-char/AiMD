export default function ThinkingBubble() {
  return (
    <div className="px-3 py-2 text-white/40 text-sm flex items-center gap-2 w-fit rounded-xl"
      style={{
        background: 'rgba(255,255,255,0.05)',
        border: '1px solid rgba(255,255,255,0.08)',
        backdropFilter: 'blur(8px)',
      }}
    >
      <div className="animate-spin w-4 h-4 border-2 border-white/20 border-t-white/60 rounded-full"></div>
      Thinking...
    </div>
  );
}