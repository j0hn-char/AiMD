import { useState, useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./Components/Sidebar";
import Chat from "./Components/Chat";
import AuthPage from "./Components/AuthPage";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [isLoadingChats, setIsLoadingChats] = useState(false);

  const activeChat = chats.find((c) => c.id === activeChatId);

  // Fetch chats whenever token changes (on login)
  useEffect(() => {
    if (!token) return;
    fetchChats();
  }, [token]);

  const fetchChats = async () => {
    setIsLoadingChats(true);
    try {
      const res = await fetch("/api/chats", {
        headers: { "Authorization": `Bearer ${token}` },
      });
      const data = await res.json();

      if (data.chats && data.chats.length > 0) {
        setChats(data.chats);
        setActiveChatId(data.chats[0].id);
      } else {
        const newChat = { id: Date.now(), title: "New Chat", messages: [] };
        setChats([newChat]);
        setActiveChatId(newChat.id);
      }
    } catch (err) {
      // Fallback for dev mode
      const newChat = { id: Date.now(), title: "New Chat", messages: [] };
      setChats([newChat]);
      setActiveChatId(newChat.id);
    } finally {
      setIsLoadingChats(false);
    }
  };

  const createNewChat = () => {
    const newChat = { id: Date.now(), title: "New Chat", messages: [] };
    setChats((prev) => [newChat, ...prev]);
    setActiveChatId(newChat.id);
  };

  const deleteChat = (id) => {
    const remaining = chats.filter((c) => c.id !== id);
    if (remaining.length === 0) {
      const newChat = { id: Date.now(), title: "New Chat", messages: [] };
      setChats([newChat]);
      setActiveChatId(newChat.id);
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

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setChats([]);
    setActiveChatId(null);
  };

  return (
    <Routes>
      <Route path="/auth" element={
        token ? <Navigate to="/" /> : <AuthPage onLogin={handleLogin} />
      } />
      <Route path="/" element={
        !token ? <Navigate to="/auth" /> : (
          <div className="min-h-screen bg-gradient-to-br from-cyan-950 via-slate-950 to-teal-950 flex">
            <Sidebar
              chats={chats}
              activeChatId={activeChatId}
              onSelect={setActiveChatId}
              onNew={createNewChat}
              onDelete={deleteChat}
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
              />
            ) : null}
          </div>
        )
      } />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;