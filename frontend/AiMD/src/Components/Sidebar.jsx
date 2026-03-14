import { useState } from "react";
import SpotlightCard from './SpotlightCard';
import AnimatedList from './AnimatedList';

export default function Sidebar({ chats, activeChatId, onSelect, onNew, onDelete, onLogout, userEmail }) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="relative flex">
      <div
        className={`h-screen flex flex-col transition-all duration-300 ${isOpen ? "w-60" : "w-0 overflow-hidden"}`}
        style={{
          background: 'rgba(255,255,255,0.04)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          borderRight: isOpen ? '1px solid rgba(255,255,255,0.08)' : 'none',
        }}
      >
        <div className={`flex flex-col p-4 gap-3 h-full transition-opacity duration-200 ${isOpen ? "opacity-100" : "opacity-0"}`}>

          <div className="flex items-center justify-center gap-2 py-4 pb-6 flex-shrink-0">
            <img src="/logo.svg" className="w-32 h-32" />
          </div>

          <button
            onClick={onNew}
            className="w-full px-4 py-2 font-semibold text-white rounded-xl transition flex-shrink-0"
            style={{
              background: 'linear-gradient(135deg, rgba(14,165,233,0.7), rgba(6,182,212,0.7))',
              border: '1px solid rgba(34,211,238,0.3)',
              backdropFilter: 'blur(8px)',
              boxShadow: '0 4px 16px rgba(6,182,212,0.2), inset 0 1px 0 rgba(255,255,255,0.15)',
            }}
            onMouseEnter={e => e.currentTarget.style.boxShadow = '0 4px 24px rgba(6,182,212,0.4), inset 0 1px 0 rgba(255,255,255,0.2)'}
            onMouseLeave={e => e.currentTarget.style.boxShadow = '0 4px 16px rgba(6,182,212,0.2), inset 0 1px 0 rgba(255,255,255,0.15)'}
          >
            + New Chat
          </button>

          {/* Animated chat list */}
          <div className="flex-1 min-h-0 overflow-hidden">
            <AnimatedList
              items={chats}
              onItemSelect={(chat) => onSelect(chat.id)}
              showGradients
              enableArrowNavigation
              displayScrollbar={false}
              initialSelectedIndex={chats.findIndex(c => c.id === activeChatId)}
              className="!w-full"
              itemClassName="!bg-transparent !p-0"
              renderItem={(chat, index, isSelected) => (
                <div
                  className={`group flex items-center justify-between px-3 py-2 rounded-xl text-sm transition-all ${
                    chat.id === activeChatId ? "text-white" : "text-white/50"
                  }`}
                  style={chat.id === activeChatId ? {
                    background: 'rgba(255,255,255,0.1)',
                    border: '1px solid rgba(255,255,255,0.15)',
                    backdropFilter: 'blur(8px)',
                  } : {
                    background: isSelected ? 'rgba(255,255,255,0.06)' : 'transparent',
                    border: '1px solid transparent',
                  }}
                >
                  <span className="truncate flex-1">💬 {chat.title}</span>
                  <button
                    onClick={(e) => { e.stopPropagation(); onDelete(chat.id); }}
                    className="opacity-0 group-hover:opacity-100 text-white/30 hover:text-red-400 transition ml-2 text-xs"
                  >
                    ✕
                  </button>
                </div>
              )}
            />
          </div>

          {userEmail && (
            <div
              className="flex-shrink-0 px-3 py-2 rounded-xl text-xs text-white/40 truncate text-center"
              style={{
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.07)',
              }}
            >
              👤 {userEmail}
            </div>
          )}

          <SpotlightCard
            className="flex-shrink-0"
            spotlightColor="rgba(248, 80, 80, 0.3)"
            style={{
              padding: 0,
              background: 'rgba(255,255,255,0.05)',
              backdropFilter: 'blur(12px)',
              WebkitBackdropFilter: 'blur(12px)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '0.75rem',
            }}
          >
            <button
              onClick={onLogout}
              className="w-full px-4 py-2 text-sm text-red-400/70 hover:text-red-400 transition rounded-xl"
            >
              Logout
            </button>
          </SpotlightCard>

        </div>
      </div>

      <button
        onClick={() => setIsOpen(!isOpen)}
        className="absolute -right-30 top-6 z-10 p-2 text-white/50 h-8 rounded-full hover:text-white transition flex items-center justify-center text-xs shadow-lg"
        style={{
          background: 'rgba(255,255,255,0.08)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(255,255,255,0.12)',
        }}
      >
        {isOpen ? "Close chats tab" : "Open chats tab"}
      </button>
    </div>
  );
}