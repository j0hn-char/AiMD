import { useState } from "react";

export default function Sidebar({ chats, activeChatId, onSelect, onNew, onDelete }) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="relative flex">
      {/* Sidebar */}
      <div className={`min-h-screen bg-gray-900/80 border-r border-gray-700
        flex flex-col transition-all duration-300 ${isOpen ? "w-80" : "w-0 overflow-hidden border-none"}`}>
        <div className={`flex flex-col p-4 gap-3 flex-1 transition-opacity duration-200
          ${isOpen ? "opacity-100" : "opacity-0"}`}>
          <h1 className="text-4xl font-light text-transparent bg-clip-text bg-gradient-to-r
            from-sky-400 via-cyan-300 to-teal-400 text-center py-4 pb-6 whitespace-nowrap">
            AiMD
          </h1>
          <button onClick={onNew}
            className="w-full px-4 py-2 bg-gradient-to-r from-sky-500 to-cyan-500
              hover:opacity-80 text-white font-semibold rounded-xl transition">
            + New Chat
          </button>
          <div className="flex flex-col gap-1 overflow-y-auto flex-1">
            {chats.map((chat) => (
              <div key={chat.id}
                onClick={() => onSelect(chat.id)}
                className={`group flex items-center justify-between px-3 py-2 rounded-xl
                  cursor-pointer transition text-sm
                  ${activeChatId === chat.id
                    ? "bg-sky-600/40 text-white border border-sky-500/50"
                    : "text-gray-400 hover:bg-gray-700/50 hover:text-white"}`}>
                <span className="truncate flex-1">💬 {chat.title}</span>
                <button
                  onClick={(e) => { e.stopPropagation(); onDelete(chat.id); }}
                  className="opacity-0 group-hover:opacity-100 text-gray-500
                    hover:text-red-400 transition ml-2 text-xs">
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Toggle button — always visible */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="absolute -right-30 top-6 z-10 p-2 text-gray-400 h-8 bg-gray-800 border border-gray-600
          rounded-full text-gray-400 hover:text-white hover:bg-gray-700 transition flex
          items-center justify-center text-xs shadow-lg">
        {isOpen ? "Close chats tab" : "Open chats tab"}
      </button>
    </div>
  );
}