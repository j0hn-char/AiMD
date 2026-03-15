import { useState, useEffect, useRef } from "react";
import FilesDrawer from "./FilesDrawer";
import GradientText from "./GradientText";
import ChatWindow from "./ChatWindow";
import ChatInput from "./ChatInput";

export default function Chat({ chat, onUpdateMessages, token, apiFetch, onThinkingChange, onModeChange }) {
  const [inputValue, setInputValue] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const setThinking = (val) => { setIsThinking(val); onThinkingChange?.(val); };
  const [files, setFiles] = useState([]);
  const [mode, setMode] = useState("chat");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const drawerRef = useRef(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const abortControllerRef = useRef(null);

  const openDrawer = () => { setDrawerVisible(true); setDrawerOpen(true); };
  const closeDrawer = () => {
    if (drawerRef.current) {
      drawerRef.current.style.width = '0px';
      setTimeout(() => setDrawerVisible(false), 300);
    } else {
      setDrawerVisible(false);
    }
    setDrawerOpen(false);
  };

  const scrollToEnd = () => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  useEffect(scrollToEnd, [chat.messages]);

  const saveMessage = async (sessionId, role, content, messageMode, citations = null, entities = null) => {
    try {
      const message = { role, content };
      if (citations) message.citations = citations;
      if (entities) message.entities = entities;
      await apiFetch("/api/session/message", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, mode: messageMode, message }),
      });
    } catch (err) {
      if (err.message === "Session expired") throw err;
      console.error("Failed to save message", err);
    }
  };

  const updateSessionTitle = async (sessionId, title) => {
    try {
      await apiFetch("/api/session", {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, title }),
      });
    } catch (err) {
      if (err.message === "Session expired") throw err;
      console.error("Failed to update session title", err);
    }
  };

  const sendMessage = async (fileList = []) => {
    const message = inputValue.trim();
    if (!message && fileList.length === 0) return;

    const fileDisplay = fileList.length > 0 ? { name: fileList.map(f => f.name).join(", ") } : null;
    const newMessages = [...chat.messages, { content: message, isUser: true, file: fileDisplay, id: Date.now() + Math.random() }];
    onUpdateMessages(newMessages);
    setInputValue("");
    if (fileInputRef.current) fileInputRef.current.value = "";
    setFiles([]);
    setThinking(true);

    try {
      await saveMessage(chat.id, "user", message, mode);

      if (chat.messages.length === 0) {
        const title = message.slice(0, 30) + (message.length > 30 ? "..." : "");
        await updateSessionTitle(chat.id, title);
      }

      const aiMessageId = Date.now() + Math.random();
      abortControllerRef.current = new AbortController();
      const formData = new FormData();
      formData.append("session_id", chat.id);
      formData.append("message", message);
      for (const file of fileList) {
        formData.append("files", file);
      }

      const endpoint = mode === "analysis" ? "/api/analysis" : "/api/chat";
      const res = await apiFetch(endpoint, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
        signal: abortControllerRef.current.signal,
      });

      let streamedMessages = [...newMessages, { content: "", isUser: false, file: null, id: aiMessageId }];
      onUpdateMessages(streamedMessages);
      setThinking(false);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";
      let attachedFile = null;
      let citations = null;
      let entities = null;
      let displayContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        fullContent += decoder.decode(value, { stream: true });

        if (fullContent.includes("__FILE__") && fullContent.includes("__ENDFILE__")) {
          const fileStart = fullContent.indexOf("__FILE__") + 8;
          const fileEnd = fullContent.indexOf("__ENDFILE__");
          attachedFile = JSON.parse(fullContent.slice(fileStart, fileEnd));
          fullContent = fullContent.slice(fileEnd + 11);
        }

        let tempContent = fullContent;
        if (tempContent.includes("__CITATIONS__") && tempContent.includes("__ENDCITATIONS__")) {
          const citStart = tempContent.indexOf("__CITATIONS__") + 13;
          const citEnd = tempContent.indexOf("__ENDCITATIONS__");
          try { citations = JSON.parse(tempContent.slice(citStart, citEnd)); } catch {}
          tempContent = tempContent.slice(0, tempContent.indexOf("__CITATIONS__")) + tempContent.slice(citEnd + 16);
        }
        if (tempContent.includes("__ENTITIES__") && tempContent.includes("__ENDENTITIES__")) {
          const entStart = tempContent.indexOf("__ENTITIES__") + 12;
          const entEnd = tempContent.indexOf("__ENDENTITIES__");
          try { entities = JSON.parse(tempContent.slice(entStart, entEnd)); } catch {}
          tempContent = tempContent.slice(0, tempContent.indexOf("__ENTITIES__"));
        }
        displayContent = tempContent;

        streamedMessages = [...newMessages, { content: displayContent, isUser: false, file: attachedFile, citations, entities, id: aiMessageId }];
        onUpdateMessages(streamedMessages);
      }
      await saveMessage(chat.id, "assistant", displayContent || fullContent, mode, citations, entities);
    } catch (err) {
      if (err.message === "Session expired") return;
      if (err.name === "AbortError") {
        onUpdateMessages(newMessages);
        setThinking(false);
        return;
      }
      onUpdateMessages([...newMessages, { content: "Something went wrong. Please try again.", isUser: false, file: null, id: Date.now() + Math.random() }]);
      setThinking(false);
    }
  };

  const cancelMessage = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage(files);
    }
  };

  return (
    <div className="flex-1 flex h-screen overflow-hidden">
      <div className="flex-1 flex flex-col items-center p-4 gap-6 overflow-hidden min-w-0">

        <div className="flex items-center justify-between w-full max-w-6xl pt-2">
          <div className="w-16 flex-shrink-0" />
          <div className="flex items-center gap-3 justify-center">
            <img src="/logo.svg" className="w-12 h-12" />
            <GradientText
              colors={["#0ea5e9", "#67e8f9", "#0d9488", "#67e8f9", "#0ea5e9"]}
              animationSpeed={6}
              showBorder={false}
              className="text-4xl sm:text-4xl lg:text-5xl font-bold"
              style={{ fontFamily: "'Outfit', sans-serif" }}
            >
              Welcome to AiMD
            </GradientText>
          </div>
          <button
            onClick={() => drawerOpen ? closeDrawer() : openDrawer()}
            className="flex items-center gap-2 px-3 py-2 rounded-xl hover:text-white/70 transition text-xs flex-shrink-0"
            style={{
              background: drawerOpen ? 'rgba(14,165,233,0.15)' : 'rgba(255,255,255,0.06)',
              border: '1px solid rgba(255,255,255,0.08)',
              color: 'rgba(255,255,255,0.5)',
              cursor: 'pointer',
            }}
          >
            <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
              <path d="M3 2h7l3 3v9H3V2z" stroke="currentColor" strokeWidth="1.3"/>
              <path d="M10 2v3h3" stroke="currentColor" strokeWidth="1.3"/>
            </svg>
            Files
          </button>
        </div>

        <div
          className="relative w-72 flex items-center px-1 py-1 rounded-2xl"
          style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)", backdropFilter: "blur(12px)" }}
        >
          <div
            className={`absolute top-1 bottom-1 w-[calc(50%-7px)] rounded-xl transition-all duration-300 ${
              mode === "chat"
                ? "left-1 bg-gradient-to-r from-sky-500/80 to-cyan-500/80"
                : "left-[calc(50%+3px)] bg-gradient-to-r from-emerald-500/80 to-teal-600/80"
            }`}
            style={{ backdropFilter: "blur(8px)", boxShadow: "0 2px 12px rgba(0,0,0,0.3)" }}
          />
          <button
            onClick={() => { setMode("chat"); onModeChange?.(false); }}
            className={`relative z-10 px-5 py-2 rounded-xl text-sm font-semibold transition-colors duration-200 w-1/2 ${mode === "chat" ? "text-white" : "text-white/50 hover:text-white/80"}`}
          >
            💬 Chat
          </button>
          <button
            onClick={() => { setMode("analysis"); onModeChange?.(true); }}
            className={`relative z-10 px-5 py-2 rounded-xl text-sm font-semibold transition-colors duration-200 w-1/2 ${mode === "analysis" ? "text-white" : "text-white/50 hover:text-white/80"}`}
          >
            🧠 Analysis
          </button>
        </div>

        <div
          className="w-full max-w-6xl flex flex-col flex-1 min-h-0 rounded-3xl p-6"
          style={{
            background: "rgba(255,255,255,0.04)",
            backdropFilter: "blur(24px)",
            WebkitBackdropFilter: "blur(24px)",
            border: "1px solid rgba(255,255,255,0.1)",
            boxShadow: "0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.08)",
          }}
        >
          <ChatWindow messages={chat.messages} isThinking={isThinking} messagesEndRef={messagesEndRef} token={token} sessionId={chat.id} />
          <ChatInput
            inputValue={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyPress}
            onSend={sendMessage}
            onCancel={cancelMessage}
            isThinking={isThinking}
            fileInputRef={fileInputRef}
            files={files}
            onFileChange={setFiles}
            mode={mode}
          />
        </div>

      </div>
      {drawerVisible && <FilesDrawer drawerRef={drawerRef} messages={chat.messages} onClose={closeDrawer} />}
    </div>
  );
}