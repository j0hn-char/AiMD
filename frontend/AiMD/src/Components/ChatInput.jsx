export default function ChatInput({ inputValue, onChange, onKeyDown, onSend, isThinking }) {
  return (
    <div className="flex flex-col sm:flex-row gap-3">
      <input
        type="text"
        value={inputValue}
        onChange={onChange}
        onKeyDown={onKeyDown}
        placeholder="Type a message here..."
        disabled={isThinking}
        className="flex-1 px-4 py-3 bg-gray-700/80 border border-gray-600 rounded-2xl
          text-white placeholder-gray-400 focus:outline-none focus:ring-2
          focus:ring-sky-500 focus:shadow-xl focus:shadow-sky-400/80 transition duration-400
          disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <button onClick={onSend}
        disabled={isThinking || !inputValue.trim()}
        className="px-6 py-3 bg-gradient-to-r from-sky-400 to-cyan-400 hover:opacity-80
          text-white font-semibold rounded-2xl transition disabled:opacity-50 disabled:cursor-not-allowed">
        {isThinking ? (
          <div className="flex items-center gap-2">
            <div className="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full"></div>
            Sending
          </div>
        ) : "Send"}
      </button>
    </div>
  );
}