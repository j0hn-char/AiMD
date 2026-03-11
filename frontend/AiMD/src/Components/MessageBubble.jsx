export default function MessageBubble({ msg }) {
  if (!msg.isUser) {
    return (
      <div className="px-2 py-3 text-gray-200 text-sm leading-relaxed whitespace-pre-wrap">
        {msg.content}
      </div>
    );
  }

  return (
    <div className="flex justify-end">
      <div className="p-3 m-2 rounded-2xl max-w-[70%] break-words
        bg-gradient-to-r from-sky-600 to-cyan-500 text-white text-right">
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