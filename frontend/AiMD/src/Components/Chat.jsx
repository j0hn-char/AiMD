import { useState, useEffect, useRef } from "react";
import GradientText from "./GradientText";
import ChatWindow from "./ChatWindow";
import ChatInput from "./ChatInput";

export default function Chat({ chat, onUpdateMessages, token, apiFetch, onThinkingChange, onModeChange }) {
  const [inputValue, setInputValue] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const setThinking = (val) => { setIsThinking(val); onThinkingChange?.(val); };
  const [files, setFiles] = useState([]);
  const [mode, setMode] = useState("chat");
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const abortControllerRef = useRef(null);

  const scrollToEnd = () => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  useEffect(scrollToEnd, [chat.messages]);

  const saveMessage = async (sessionId, role, content, messageMode) => {
    try {
      await apiFetch("/api/session/message", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, mode: messageMode, message: { role, content } }),
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

  // files είναι πλέον File[] αντί για μεμονωμένο File
  const sendMessage = async (files = []) => {
    const message = inputValue.trim();
    if (!message && files.length === 0) return;

    // Για την εμφάνιση στο chat bubble δείχνουμε τα ονόματα των αρχείων
    const fileDisplay = files.length > 0
      ? { name: files.map(f => f.name).join(", ") }
      : null;

    const newMessages = [
      ...chat.messages,
      { content: message, isUser: true, file: fileDisplay, id: Date.now() + Math.random() }
    ];
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

      // Προσθέτουμε κάθε αρχείο με το ίδιο key "files" — το FastAPI το διαβάζει ως list
      for (const file of files) {
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
      await saveMessage(chat.id, "assistant", displayContent || fullContent, mode);
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
      // διαβάζουμε από το state, όχι από το fileInputRef (που είναι ήδη reset)
      sendMessage(files);
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center p-4 gap-6 h-screen">
      <div className="flex items-center justify-center gap-4 pt-2">
        <img src="/logo.svg" className="w-20 h-20" />
        <GradientText
          colors={["#0ea5e9", "#67e8f9", "#0d9488", "#67e8f9", "#0ea5e9"]}
          animationSpeed={6}
          showBorder={false}
          className="text-4xl sm:text-4xl lg:text-5xl font-bold" style={{ fontFamily: "'Outfit', sans-serif" }}
        >
          Welcome to AiMD
        </GradientText>
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
        />
      </div>
    </div>
  );
}