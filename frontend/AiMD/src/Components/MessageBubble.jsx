import ReactMarkdown from "react-markdown";
import { useState } from "react";


function EntityArtifacts({ entities }) {
  const [open, setOpen] = useState(true);

  const sections = [
    { key: "conditions", label: "Conditions", color: "#f87171", bg: "rgba(248,113,113,0.1)" },
    { key: "symptoms", label: "Symptoms", color: "#fb923c", bg: "rgba(251,146,60,0.1)" },
    { key: "medications", label: "Medications", color: "#a78bfa", bg: "rgba(167,139,250,0.1)" },
    { key: "lab_values", label: "Lab values", color: "#38bdf8", bg: "rgba(56,189,248,0.1)" },
    { key: "recommendations", label: "Recommendations", color: "#34d399", bg: "rgba(52,211,153,0.1)" },
  ].filter(s => entities[s.key]?.length > 0);

  if (sections.length === 0) return null;

  const severityColor = (s) => {
    if (!s) return "rgba(255,255,255,0.3)";
    if (s === "severe" || s === "critical" || s === "abnormal") return "#f87171";
    if (s === "moderate") return "#fb923c";
    return "#34d399";
  };

  return (
    <div className="mt-3" style={{ borderRadius: "10px", border: "1px solid rgba(255,255,255,0.08)", overflow: "hidden" }}>
      <div
        onClick={() => setOpen(o => !o)}
        className="flex items-center justify-between px-3 py-2 cursor-pointer"
        style={{ background: "rgba(255,255,255,0.04)" }}
      >
        <div className="flex items-center gap-2">
          <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
            <rect x="2" y="2" width="5" height="5" rx="1" stroke="rgba(255,255,255,0.4)" strokeWidth="1.3"/>
            <rect x="9" y="2" width="5" height="5" rx="1" stroke="rgba(255,255,255,0.4)" strokeWidth="1.3"/>
            <rect x="2" y="9" width="5" height="5" rx="1" stroke="rgba(255,255,255,0.4)" strokeWidth="1.3"/>
            <rect x="9" y="9" width="5" height="5" rx="1" stroke="rgba(255,255,255,0.4)" strokeWidth="1.3"/>
          </svg>
          <span style={{ fontSize: "12px", color: "rgba(255,255,255,0.4)", fontWeight: 500 }}>
            Knowledge artifacts
          </span>
        </div>
        <svg
          width="13" height="13" viewBox="0 0 16 16" fill="none"
          style={{ transform: open ? "rotate(180deg)" : "rotate(0deg)", transition: "transform 0.2s" }}
        >
          <path d="M4 6l4 4 4-4" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>

      {open && (
        <div style={{ borderTop: "1px solid rgba(255,255,255,0.06)", padding: "12px" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {sections.map(({ key, label, color, bg }) => (
              <div key={key}>
                <div style={{ fontSize: "11px", fontWeight: 500, color: color, marginBottom: 5, textTransform: "uppercase", letterSpacing: "0.05em" }}>
                  {label}
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                  {key === "recommendations" ? (
                    entities[key].map((r, i) => (
                      <div key={i} style={{
                        fontSize: "12px", color: "rgba(255,255,255,0.6)", padding: "5px 10px",
                        borderRadius: 6, background: bg, border: `1px solid ${color}30`,
                        lineHeight: 1.4, width: "100%"
                      }}>
                        {r}
                      </div>
                    ))
                  ) : key === "lab_values" ? (
                    entities[key].map((item, i) => (
                      <div key={i} style={{
                        display: "flex", alignItems: "center", gap: 6, padding: "4px 10px",
                        borderRadius: 6, background: bg, border: `1px solid ${color}30`,
                      }}>
                        <span style={{ fontSize: "12px", color: "rgba(255,255,255,0.7)", fontWeight: 500 }}>{item.name}</span>
                        {item.value && <span style={{ fontSize: "11px", color: "rgba(255,255,255,0.4)" }}>{item.value}</span>}
                        {item.status && (
                          <span style={{ fontSize: "10px", fontWeight: 500, color: severityColor(item.status) }}>
                            {item.status}
                          </span>
                        )}
                      </div>
                    ))
                  ) : (
                    entities[key].map((item, i) => (
                      <div key={i} style={{
                        display: "flex", alignItems: "center", gap: 5, padding: "4px 10px",
                        borderRadius: 6, background: bg, border: `1px solid ${color}30`,
                      }}>
                        <span style={{ fontSize: "12px", color: "rgba(255,255,255,0.7)", fontWeight: 500 }}>
                          {item.name || item}
                        </span>
                        {(item.severity || item.dosage) && (
                          <span style={{ fontSize: "10px", fontWeight: 500, color: severityColor(item.severity) }}>
                            {item.severity || item.dosage}
                          </span>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function Citations({ citations, onFeedback, feedbackSent }) {
  const [open, setOpen] = useState(false);

  const dedupedCitations = Object.values(
    citations.reduce((acc, c) => {
      if (!acc[c.filename] || c.score > acc[c.filename].score) {
        acc[c.filename] = c;
      }
      return acc;
    }, {})
  );

  return (
    <div className="mt-3" style={{ borderRadius: '10px', border: '1px solid rgba(255,255,255,0.08)', overflow: 'hidden' }}>
      <div
        onClick={() => setOpen(o => !o)}
        className="flex items-center justify-between px-3 py-2 cursor-pointer"
        style={{ background: 'rgba(255,255,255,0.04)' }}
      >
        <div className="flex items-center gap-2">
          <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
            <path d="M2 4h12M4 8h8M6 12h4" stroke="rgba(255,255,255,0.4)" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <span style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)', fontWeight: 500 }}>
            {dedupedCitations.length} source{dedupedCitations.length !== 1 ? 's' : ''} used
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.25)' }}>helpful?</span>
          <button
            onClick={e => { e.stopPropagation(); onFeedback('up'); }}
            disabled={!!feedbackSent}
            style={{
              background: feedbackSent === 'up' ? 'rgba(16,185,129,0.2)' : 'rgba(255,255,255,0.06)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '5px', padding: '1px 7px', fontSize: '12px',
              color: feedbackSent === 'up' ? '#6ee7b7' : 'rgba(255,255,255,0.4)',
              cursor: feedbackSent ? 'default' : 'pointer',
            }}
          >↑</button>
          <button
            onClick={e => { e.stopPropagation(); onFeedback('down'); }}
            disabled={!!feedbackSent}
            style={{
              background: feedbackSent === 'down' ? 'rgba(239,68,68,0.2)' : 'rgba(255,255,255,0.06)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '5px', padding: '1px 7px', fontSize: '12px',
              color: feedbackSent === 'down' ? '#fca5a5' : 'rgba(255,255,255,0.4)',
              cursor: feedbackSent ? 'default' : 'pointer',
            }}
          >↓</button>
          <svg
            width="13" height="13" viewBox="0 0 16 16" fill="none"
            style={{ transform: open ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}
          >
            <path d="M4 6l4 4 4-4" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      </div>

      {open && (
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
          {dedupedCitations.map((c, i) => {
            const isPubmed = c.source === 'pubmed';
            const pct = Math.round((c.score || 0) * 100);
            return (
              <div
                key={i}
                className="flex items-center gap-3 px-3 py-2"
                style={{
                  borderBottom: i < dedupedCitations.length - 1 ? '1px solid rgba(255,255,255,0.05)' : 'none',
                  background: 'rgba(255,255,255,0.02)',
                }}
              >
                <div style={{
                  width: 26, height: 26, borderRadius: 6, flexShrink: 0,
                  background: isPubmed ? 'rgba(16,185,129,0.12)' : 'rgba(14,165,233,0.12)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  {isPubmed ? (
                    <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
                      <circle cx="8" cy="8" r="6" stroke="#34d399" strokeWidth="1.2"/>
                      <path d="M5 8h6M8 5v6" stroke="#34d399" strokeWidth="1.2" strokeLinecap="round"/>
                    </svg>
                  ) : (
                    <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
                      <path d="M3 2h7l3 3v9H3V2z" stroke="#38bdf8" strokeWidth="1.2"/>
                      <path d="M10 2v3h3" stroke="#38bdf8" strokeWidth="1.2"/>
                      <path d="M5 7h6M5 9h4" stroke="#38bdf8" strokeWidth="1.2" strokeLinecap="round"/>
                    </svg>
                  )}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: '12px', fontWeight: 500, color: 'rgba(255,255,255,0.7)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {c.filename}
                  </div>
                  <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.3)', marginTop: 1 }}>
                    {isPubmed ? 'PubMed article' : 'Uploaded document'}
                  </div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 3, flexShrink: 0 }}>
                  <span style={{ fontSize: '11px', color: 'rgba(255,255,255,0.4)', fontWeight: 500 }}>{pct}%</span>
                  <div style={{ width: 56, height: 3, borderRadius: 2, background: 'rgba(255,255,255,0.08)', overflow: 'hidden' }}>
                    <div style={{
                      width: `${pct}%`, height: '100%', borderRadius: 2,
                      background: isPubmed ? '#34d399' : '#38bdf8',
                    }} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function MessageBubble({ msg, token, sessionId }) {
  const [feedbackSent, setFeedbackSent] = useState(null);

  const sendFeedback = async (vote) => {
    if (!msg.citations || feedbackSent) return;
    const chunkIds = msg.citations.map((_, i) => i.toString());
    try {
      await fetch("/api/feedback", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, chunk_ids: chunkIds, vote }),
      });
      setFeedbackSent(vote);
    } catch (e) { console.error("Feedback failed", e); }
  };

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
            className="mt-3 flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-sky-600 to-cyan-500 hover:opacity-80 text-white text-xs font-semibold rounded-xl transition"
          >
            ⬇️ Download {msg.file.filename}
          </button>
        )}

        {msg.entities && (
          <EntityArtifacts entities={msg.entities} />
        )}
        {msg.citations && msg.citations.length > 0 && (
          <Citations citations={msg.citations} onFeedback={sendFeedback} feedbackSent={feedbackSent} />
        )}
      </div>
    );
  }

  return (
    <div className="flex justify-end">
      <div className="p-3 m-2 rounded-2xl max-w-[70%] break-words bg-gradient-to-r from-sky-600 to-cyan-500 text-white text-right">
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