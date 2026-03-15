import { useState, useEffect, useCallback } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./Components/Sidebar";
import Chat from "./Components/Chat";
import AuthPage from "./Components/AuthPage";
import Aurora from "./Components/Aurora";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [isLoadingChats, setIsLoadingChats] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [isAnalysis, setIsAnalysis] = useState(false);
  const [tokenVerified, setTokenVerified] = useState(false);

  const activeChat = chats.find((c) => c.id === activeChatId);

  const handleLogout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("userEmail");
    setToken(null);
    setChats([]);
    setActiveChatId(null);
  }, []);

  const apiFetch = useCallback(async (url, options = {}) => {
    const res = await fetch(url, options);
    if (res.status === 401 || res.status === 403) {
      handleLogout();
      throw new Error("Session expired");
    }
    return res;
  }, [handleLogout]);

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    if (!storedToken) setToken(null);
    setTokenVerified(true);
  }, []);

  useEffect(() => {
    if (!token) return;
    fetchChats();
  }, [token]);

  useEffect(() => {
    if (!activeChatId || !token) return;
    loadSessionMessages(activeChatId);
  }, [activeChatId]);

  const authHeaders = () => ({
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  });

  const fetchChats = async () => {
    setIsLoadingChats(true);
    try {
      const res = await apiFetch("/api/sessions", { headers: authHeaders() });
      const data = await res.json();
      if (data.sessions && data.sessions.length > 0) {
        const mapped = data.sessions.map((s) => ({
          id: s.session_id,
          title: s.title || "New Chat",
          messages: [],
        }));
        setChats(mapped);
        setActiveChatId(mapped[0].id);
      } else {
        await createNewChat();
      }
    } catch (err) {
      if (err.message === "Session expired") return;
      await createNewChat();
    } finally {
      setIsLoadingChats(false);
    }
  };

  const loadSessionMessages = async (sessionId) => {
    try {
      const res = await apiFetch(`/api/session?session_id=${sessionId}`, { headers: authHeaders() });
      const data = await res.json();

      const chatHistory = data?.conversations?.chat?.history || [];
      const analysisHistory = data?.conversations?.analysis?.history || [];
      const analysisPdf = data?.conversations?.analysis?.analysis_result?.pdf || null;

      const chatMessages = chatHistory.map((m, i) => ({
        id: `chat-${i}`, content: m.content, isUser: m.role === "user",
        file: null, mode: "chat", timestamp: m.timestamp || "",
        citations: m.citations || null,
        entities: m.entities || null,
      }));

      const analysisEntities = data?.conversations?.analysis?.analysis_result?.entities || null;

      const analysisMessages = analysisHistory.map((m, i) => ({
        id: `analysis-${i}`, content: m.content, isUser: m.role === "user",
        file: m.role === "assistant" && analysisPdf ? {
          type: "file", filename: "medical_report.pdf",
          mimetype: "application/pdf", data: analysisPdf
        } : null,
        citations: m.citations || null,
        entities: m.role === "assistant" ? (m.entities || analysisEntities) : null,
        mode: "analysis", timestamp: m.timestamp || ""
      }));

      const allMessages = [...chatMessages, ...analysisMessages].sort((a, b) =>
        new Date(a.timestamp) - new Date(b.timestamp)
      );

      setChats((prev) =>
        prev.map((c) => c.id === sessionId ? { ...c, messages: allMessages } : c)
      );
    } catch (err) {
      if (err.message === "Session expired") return;
      console.error("Failed to load messages", err);
    }
  };

  const createNewChat = async () => {
    try {
      const res = await apiFetch("/api/session", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ title: "New Chat" }),
      });
      const data = await res.json();
      const newChat = { id: data.session_id, title: "New Chat", messages: [] };
      setChats((prev) => [newChat, ...prev]);
      setActiveChatId(newChat.id);
      return newChat.id;
    } catch (err) {
      if (err.message === "Session expired") return;
      const newChat = { id: Date.now().toString(), title: "New Chat", messages: [] };
      setChats((prev) => [newChat, ...prev]);
      setActiveChatId(newChat.id);
      return newChat.id;
    }
  };

  const deleteChat = async (id) => {
    try {
      await apiFetch(`/api/session?session_id=${id}`, {
        method: "DELETE",
        headers: authHeaders(),
      });
    } catch (err) {
      if (err.message === "Session expired") return;
      console.error("Failed to delete session", err);
    }
    const remaining = chats.filter((c) => c.id !== id);
    if (remaining.length === 0) {
      setChats([]);
      setActiveChatId(null);
      await createNewChat();
    } else {
      setChats(remaining);
      if (activeChatId === id) setActiveChatId(remaining[0].id);
    }
  };

  const updateChat = (id, messages) => {
    setChats((prev) =>
      prev.map((c) => {
        if (c.id !== id) return c;
        const firstUserMsg = messages.find((m) => m.isUser);
        const title = firstUserMsg
          ? firstUserMsg.content.slice(0, 30) + (firstUserMsg.content.length > 30 ? "..." : "")
          : "New Chat";
        return { ...c, messages, title };
      })
    );
  };

  const handleLogin = (jwt) => {
    localStorage.setItem("token", jwt);
    setToken(jwt);
  };

  if (!tokenVerified) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-cyan-950 via-slate-950 to-indigo-950 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-white/30 border-t-white rounded-full"></div>
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/auth" element={
        token ? <Navigate to="/" /> : <AuthPage onLogin={handleLogin} />
      } />
      <Route path="/" element={
        !token ? <Navigate to="/auth" /> : (
          <div className="h-screen overflow-hidden flex"
            style={{ position: "relative", background: isAnalysis ? "#030d0d" : "#030810", transition: "background 1.5s ease" }}>
            <div style={{ position: "absolute", inset: 0, zIndex: 0 }}>
              <Aurora colorStops={isAnalysis ? ["#134e4a", "#064e3b", "#065f46"] : ["#0c4a6e", "#164e63", "#134e4a"]} blend={0.6} amplitude={0.8} speed={0.6} />
            </div>
            <div style={{ position: "relative", zIndex: 1, display: "flex", width: "100%" }}>
              <Sidebar
                chats={chats}
                activeChatId={activeChatId}
                onSelect={setActiveChatId}
                onNew={createNewChat}
                onDelete={deleteChat}
                userEmail={localStorage.getItem('userEmail')}
                onLogout={handleLogout}
              />
              {isLoadingChats ? (
                <div className="flex-1 flex items-center justify-center">
                  <div className="animate-spin w-8 h-8 border-2 border-white/30 border-t-white rounded-full"></div>
                </div>
              ) : activeChat ? (
                <Chat
                  key={activeChatId}
                  chat={activeChat}
                  onUpdateMessages={(messages) => updateChat(activeChatId, messages)}
                  token={token}
                  apiFetch={apiFetch}
                  onThinkingChange={setIsThinking}
                  onModeChange={setIsAnalysis}
                />
              ) : null}
            </div>
          </div>
        )
      } />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;