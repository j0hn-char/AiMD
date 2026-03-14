import ReactMarkdown from "react-markdown";

export default function MessageBubble({ msg }) {
  const downloadFile = (fileData) => {
    const byteChars = atob(fileData.data);
    const byteArray = new Uint8Array([...byteChars].map(c => c.charCodeAt(0)));
    const blob = new Blob([byteArray], { type: fileData.mimetype });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileData.filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!msg.isUser) {
    return (
      <div className="px-2 py-3 text-gray-200 text-sm leading-relaxed">
        <ReactMarkdown
          components={{
            h1: ({ children }) => <h1 className="text-2xl font-bold text-white mb-2">{children}</h1>,
            h2: ({ children }) => <h2 className="text-xl font-bold text-white mb-2">{children}</h2>,
            h3: ({ children }) => <h3 className="text-lg font-semibold text-white mb-1">{children}</h3>,
            strong: ({ children }) => <strong className="font-bold text-white">{children}</strong>,
            em: ({ children }) => <em className="italic text-gray-300">{children}</em>,
            ul: ({ children }) => <ul className="list-disc list-inside my-2 space-y-1">{children}</ul>,
            ol: ({ children }) => <ol className="list-decimal list-inside my-2 space-y-1">{children}</ol>,
            li: ({ children }) => <li className="text-gray-200">{children}</li>,
            p: ({ children }) => <p className="mb-2">{children}</p>,
            code: ({ children }) => <code className="bg-gray-700 text-cyan-300 px-1 py-0.5 rounded text-xs">{children}</code>,
            pre: ({ children }) => <pre className="bg-gray-900 p-3 rounded-xl my-2 overflow-x-auto text-xs">{children}</pre>,
            blockquote: ({ children }) => <blockquote className="border-l-2 border-cyan-500 pl-3 italic text-gray-400 my-2">{children}</blockquote>,
          }}
        >
          {msg.content}
        </ReactMarkdown>

        {msg.file && (
          <button
            onClick={() => downloadFile(msg.file)}
            className="mt-3 flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-sky-600 to-cyan-500
              hover:opacity-80 text-white text-xs font-semibold rounded-xl transition"
          >
            ⬇️ Download {msg.file.filename}
          </button>
        )}
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