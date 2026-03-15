export default function ChatInput({ inputValue, onChange, onKeyDown, onSend, onCancel, isThinking, fileInputRef, files, onFileChange }) {

  const handleFileChange = (e) => {
    // Διαβάζουμε τα File objects ΑΜΕΣΩΣ — πριν οποιοδήποτε reset
    const newFiles = Array.from(e.target.files || []);
    if (newFiles.length === 0) return;

    // Συνδυάζουμε με τα ήδη επιλεγμένα, χωρίς functional updater (πιο ασφαλές)
    const existing = Array.isArray(files) ? files : [];
    const merged = [...existing];
    for (const f of newFiles) {
      const duplicate = existing.some(x => x.name === f.name && x.size === f.size);
      if (!duplicate) merged.push(f);
    }
    onFileChange(merged);

    // Reset ΜΕΤΑ — ώστε το ίδιο αρχείο να μπορεί να επιλεγεί ξανά
    setTimeout(() => { if (fileInputRef.current) fileInputRef.current.value = ""; }, 0);
  };

  const removeFile = (indexToRemove) => {
    const updated = (Array.isArray(files) ? files : []).filter((_, i) => i !== indexToRemove);
    onFileChange(updated);
  };

  const handleSend = () => {
    onSend(Array.isArray(files) ? files : []);
    if (fileInputRef.current) fileInputRef.current.value = "";
    onFileChange([]);
  };

  const fileList = Array.isArray(files) ? files : [];
  const hasFiles = fileList.length > 0;

  return (
    <div className="flex flex-col gap-2">
      <input
        type="file"
        ref={fileInputRef}
        className="hidden"
        accept="image/*,.pdf,.txt,.doc,.docx"
        multiple
        onChange={handleFileChange}
      />

      {hasFiles && (
        <div className="flex flex-wrap gap-2">
          {fileList.map((file, i) => (
            <div
              key={i}
              className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm text-white/60"
              style={{
                background: 'rgba(255,255,255,0.06)',
                border: '1px solid rgba(255,255,255,0.1)',
                backdropFilter: 'blur(8px)',
              }}
            >
              📎 <span className="truncate max-w-40">{file.name}</span>
              <button
                onClick={() => removeFile(i)}
                className="text-white/30 hover:text-red-400 transition"
              >✕</button>
            </div>
          ))}
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={() => fileInputRef.current.click()}
          disabled={isThinking}
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
            disabled={!inputValue.trim() && !hasFiles}
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