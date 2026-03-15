import { useEffect } from "react";

export default function FilesDrawer({ messages, onClose, drawerRef }) {
  useEffect(() => {
    requestAnimationFrame(() => {
      if (drawerRef?.current) drawerRef.current.style.width = '280px';
    });
  }, []);

  const files = [];
  const seen = new Set();
  messages.forEach(m => {
    if (m.isUser && m.file?.name && !seen.has(m.file.name)) {
      seen.add(m.file.name);
      files.push({ name: m.file.name, source: "upload" });
    }
    if (!m.isUser && m.file?.filename && !seen.has(m.file.filename)) {
      seen.add(m.file.filename);
      files.push({ name: m.file.filename, source: "report" });
    }
  });

  return (
    <div
      ref={drawerRef}
      style={{
        width: 0,
        minWidth: 0,
        overflow: 'hidden',
        transition: 'width 0.3s ease',
        background: 'rgba(255,255,255,0.04)',
        backdropFilter: 'blur(20px)',
        borderLeft: '1px solid rgba(255,255,255,0.08)',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        flexShrink: 0,
      }}
    >
      <div style={{ width: 280, display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div className="flex items-center justify-between px-4 py-3"
          style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', flexShrink: 0 }}>
          <span style={{ fontSize: 13, fontWeight: 500, color: 'rgba(255,255,255,0.7)' }}>
            Session files
          </span>
          <button
            onClick={onClose}
            style={{ color: 'rgba(255,255,255,0.3)', fontSize: 16, lineHeight: 1 }}
            className="hover:text-white transition"
          >✕</button>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
          {files.length === 0 ? (
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.25)', textAlign: 'center', marginTop: 32 }}>
              No files uploaded yet
            </div>
          ) : files.map((file, i) => (
            <div key={i} className="flex items-center gap-3 px-3 py-2 rounded-xl"
              style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.08)' }}>
              <div style={{
                width: 32, height: 32, borderRadius: 8, flexShrink: 0,
                background: file.source === 'report' ? 'rgba(52,211,153,0.12)' : 'rgba(14,165,233,0.12)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                  <path d="M3 2h7l3 3v9H3V2z" stroke={file.source === 'report' ? '#34d399' : '#38bdf8'} strokeWidth="1.2"/>
                  <path d="M10 2v3h3" stroke={file.source === 'report' ? '#34d399' : '#38bdf8'} strokeWidth="1.2"/>
                  <path d="M5 7h6M5 9h4" stroke={file.source === 'report' ? '#34d399' : '#38bdf8'} strokeWidth="1.2" strokeLinecap="round"/>
                </svg>
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 12, fontWeight: 500, color: 'rgba(255,255,255,0.7)',
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {file.name}
                </div>
                <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', marginTop: 2 }}>
                  {file.source === 'report' ? 'Generated report' : 'Uploaded document'}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}