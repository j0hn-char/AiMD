export default function MessageBubble({ msg }) {
  return (
    <div className={`flex ${msg.isUser ? "justify-end" : "justify-start"}`}>
      <div className={`p-3 m-2 rounded-2xl max-w-[70%] break-words
        ${msg.isUser
          ? "bg-gradient-to-r from-sky-600 to-cyan-500 text-white text-right"
          : "bg-gradient-to-r from-slate-700 to-slate-800 text-white border border-slate-600"}`}>
        <div className="whitespace-pre-wrap">{msg.content}</div>
        {msg.file && (
          <div className="mt-2 pt-2 border-t border-white/20 text-xs opacity-70">
            📎 {msg.file.name}
          </div>
        )}
      </div>
    </div>
  );
}