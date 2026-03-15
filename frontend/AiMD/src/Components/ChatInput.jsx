export default function ChatInput({ inputValue, onChange, onKeyDown, onSend, onCancel, isThinking, fileInputRef, fileName, onFileChange, mode }) {

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
        <div
          className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-white/60"
          style={{
            background: 'rgba(255,255,255,0.06)',
            border: '1px solid rgba(255,255,255,0.1)',
            backdropFilter: 'blur(8px)',
          }}
        >
          📎 <span className="truncate flex-1">{fileName}</span>
          <button
            onClick={() => { fileInputRef.current.value = ""; onFileChange(null); }}
            className="text-white/30 hover:text-red-400 transition"
          >✕</button>
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={() => fileInputRef.current.click()}
          disabled={isThinking || mode !== "analysis"}
          className="px-4 py-3 rounded-2xl text-white/50 hover:text-white transition duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            background: 'rgba(255,255,255,0.06)',
            border: '1px solid rgba(255,255,255,0.1)',
            backdropFilter: 'blur(8px)',
          }}
          onMouseEnter={e => !isThinking && (e.currentTarget.style.borderColor = 'rgba(34,211,238,0.4)')}
          onMouseLeave={e => e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'}
        >
          🔗
        </button>

        <input
          type="text"
          value={inputValue}
          onChange={onChange}
          onKeyDown={onKeyDown}
          placeholder="Type a message here..."
          disabled={isThinking}
          className="flex-1 px-4 py-3 rounded-2xl text-white placeholder-white/30 focus:outline-none transition duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            background: 'rgba(255,255,255,0.06)',
            border: '1px solid rgba(255,255,255,0.1)',
            backdropFilter: 'blur(8px)',
            boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.06)',
          }}
          onFocus={e => e.target.style.border = '1px solid rgba(34,211,238,0.45)'}
          onBlur={e => e.target.style.border = '1px solid rgba(255,255,255,0.1)'}
        />

        {isThinking ? (
          <button
            onClick={onCancel}
            className="px-6 py-3 font-semibold text-white rounded-2xl transition-all duration-300"
            style={{
              background: 'linear-gradient(135deg, rgba(239,68,68,0.7), rgba(220,38,38,0.7))',
              border: '1px solid rgba(248,113,113,0.3)',
              backdropFilter: 'blur(8px)',
              boxShadow: '0 4px 16px rgba(239,68,68,0.2), inset 0 1px 0 rgba(255,255,255,0.15)',
            }}
            onMouseEnter={e => e.currentTarget.style.boxShadow = '0 4px 24px rgba(239,68,68,0.4), inset 0 1px 0 rgba(255,255,255,0.2)'}
            onMouseLeave={e => e.currentTarget.style.boxShadow = '0 4px 16px rgba(239,68,68,0.2), inset 0 1px 0 rgba(255,255,255,0.15)'}
          >
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-white rounded-sm"></div>
              Stop
            </div>
          </button>
        ) : (
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() && !fileName}
            className="px-6 py-3 font-semibold text-white rounded-2xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              background: 'linear-gradient(135deg, rgba(14,165,233,0.7), rgba(6,182,212,0.7))',
              border: '1px solid rgba(34,211,238,0.3)',
              backdropFilter: 'blur(8px)',
              boxShadow: '0 4px 16px rgba(6,182,212,0.2), inset 0 1px 0 rgba(255,255,255,0.15)',
            }}
            onMouseEnter={e => e.currentTarget.style.boxShadow = '0 4px 24px rgba(6,182,212,0.4), inset 0 1px 0 rgba(255,255,255,0.2)'}
            onMouseLeave={e => e.currentTarget.style.boxShadow = '0 4px 16px rgba(6,182,212,0.2), inset 0 1px 0 rgba(255,255,255,0.15)'}
          >
            Send
          </button>
        )}
      </div>
    </div>
  );
}