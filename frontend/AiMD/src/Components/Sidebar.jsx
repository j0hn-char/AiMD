import { useState } from "react";

export default function Sidebar({
  chats,
  activeChatId,
  onSelect,
  onNew,
  onDelete,
  onLogout
}) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="relative flex">
      <div
        className={`h-screen bg-gray-900/80 border-r border-gray-700
        flex flex-col transition-all duration-300 ${isOpen ? "w-60" : "w-0 overflow-hidden border-none"}`}
      >
        <div
          className={`flex flex-col p-4 gap-3 h-full transition-opacity duration-200
          ${isOpen ? "opacity-100" : "opacity-0"}`}
        >
          <div className="flex items-center justify-center gap-2 py-4 pb-6 flex-shrink-0">
            <img src="/logo.svg" className="w-32 h-32" />
          </div>
          <button
            onClick={onNew}
            className="w-full px-4 py-2 bg-gradient-to-r from-sky-500 to-cyan-500
              hover:opacity-80 text-white font-semibold rounded-xl transition flex-shrink-0"
          >
            + New Chat
          </button>
          <div className="flex flex-col gap-1 overflow-y-auto flex-1 min-h-0">
            {chats.map((chat) => (
              <div
                key={chat.id}
                onClick={() => onSelect(chat.id)}
                className={`group flex items-center justify-between px-3 py-2 rounded-xl
                  cursor-pointer transition text-sm
                  ${activeChatId === chat.id
                    ? "bg-sky-600/40 text-white border border-sky-500/50"
                    : "text-gray-400 hover:bg-gray-700/50 hover:text-white"
                  }`}
              >
                <span className="truncate flex-1">💬 {chat.title}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(chat.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 text-gray-500
                    hover:text-red-400 transition ml-2 text-xs"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
          <button
            onClick={onLogout}
            className="w-full px-4 py-2 text-sm text-gray-400 hover:text-red-400
              border border-gray-700 hover:border-red-400/50 rounded-xl transition flex-shrink-0"
          >
            Logout
          </button>
        </div>
      </div>

      <button
        onClick={() => setIsOpen(!isOpen)}
        className="absolute -right-30 top-6 z-10 p-2 text-gray-400 h-8 bg-gray-800 border border-gray-600
          rounded-full hover:text-white hover:bg-gray-700 transition flex
          items-center justify-center text-xs shadow-lg"
      >
        {isOpen ? "Close chats tab" : "Open chats tab"}
      </button>
    </div>
  );
}