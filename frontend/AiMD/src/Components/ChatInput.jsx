export default function ChatInput({ inputValue, onChange, onKeyDown, onSend, isThinking, fileInputRef, fileName, onFileChange }) {

  const handleFileChange = (e) => {
    onFileChange(e.target.files[0]?.name || null);
  };

  const handleSend = () => {
    const file = fileInputRef.current?.files[0] || null;
    onSend(file);
    fileInputRef.current.value = "";
    onFileChange(null);
  };

  return (
    <div className="flex flex-col gap-2">
      <input
        type="file"
        ref={fileInputRef}
        className="hidden"
        accept="image/*,.pdf,.txt,.doc,.docx"
        onChange={handleFileChange}
      />

      {fileName && (
        <div className="flex items-center gap-2 px-3 py-2 bg-gray-700/60 border border-gray-600
          rounded-xl text-sm text-gray-300">
          📎 <span className="truncate flex-1">{fileName}</span>
          <button onClick={() => { fileInputRef.current.value = ""; onFileChange(null); }}
            className="text-gray-500 hover:text-red-400 transition">✕</button>
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={() => fileInputRef.current.click()}
          disabled={isThinking}
          className="px-4 py-3 bg-gray-700/80 border border-gray-600 rounded-2xl
            text-gray-400 hover:text-white hover:border-sky-500 transition duration-300
            disabled:opacity-50 disabled:cursor-not-allowed">
          🔗
        </button>
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
        <button onClick={handleSend}
          disabled={isThinking || (!inputValue.trim() && !fileName)}
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
    </div>
  );
}