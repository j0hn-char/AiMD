import { useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Chat from "./components/Chat";
import AuthPage from "./components/AuthPage";

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "dev-token");

  const [chats, setChats] = useState([
    { id: 1, title: "New Chat", messages: [] }
  ]);
  const [activeChatId, setActiveChatId] = useState(1);

  const activeChat = chats.find((c) => c.id === activeChatId);

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
  };

  return (
    <Routes>
      {/* If not logged in, redirect to /auth */}
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
            <Chat
              key={activeChatId}
              chat={activeChat}
              onUpdateMessages={(messages) => updateChat(activeChatId, messages)}
              token={token}
            />
          </div>
        )
      } />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;