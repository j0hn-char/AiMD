import { useState, useEffect, useRef } from "react";
import ChatWindow from "./ChatWindow";
import ChatInput from "./ChatInput";

export default function Chat({ chat, onUpdateMessages, token }) {
  const [inputValue, setInputValue] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [fileName, setFileName] = useState(null);
  const [mode, setMode] = useState("chat");
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToEnd = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToEnd, [chat.messages]);

  const saveMessage = async (sessionId, role, content, messageMode) => {
    try {
      await fetch("/api/session/message", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          mode: messageMode,
          message: { role, content },
        }),
      });
    } catch (err) {
      console.error("Failed to save message", err);
    }
  };

  const updateSessionTitle = async (sessionId, title) => {
    try {
      await fetch("/api/session", {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ session_id: sessionId, title }),
      });
    } catch (err) {
      console.error("Failed to update session title", err);
    }
  };

  const sendMessage = async (file) => {
    const message = inputValue.trim();
    if (!message && !file) return;

    const newMessages = [
      ...chat.messages,
      { content: message, isUser: true, file, id: Date.now() + Math.random() },
    ];
    onUpdateMessages(newMessages);
    setInputValue("");
    if (fileInputRef.current) fileInputRef.current.value = "";
    setFileName(null);
    setIsThinking(true);

    await saveMessage(chat.id, "user", message, mode);

    // Save title on first message
    if (chat.messages.length === 0) {
      const title = message.slice(0, 30) + (message.length > 30 ? "..." : "");
      await updateSessionTitle(chat.id, title);
    }

    const aiMessageId = Date.now() + Math.random();

    try {
      const formData = new FormData();
      formData.append("message", message);
      if (file) formData.append("file", file);

      const endpoint = mode === "analysis" ? "/api/analysis" : "/api/chat";

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      let streamedMessages = [
        ...newMessages,
        { content: "", isUser: false, file: null, id: aiMessageId },
      ];
      onUpdateMessages(streamedMessages);
      setIsThinking(false);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = "";
      let attachedFile = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        fullContent += decoder.decode(value, { stream: true });

        if (fullContent.includes("__FILE__") && fullContent.includes("__ENDFILE__")) {
          const fileStart = fullContent.indexOf("__FILE__") + 8;
          const fileEnd = fullContent.indexOf("__ENDFILE__");
          const fileMeta = JSON.parse(fullContent.slice(fileStart, fileEnd));
          attachedFile = fileMeta;
          fullContent = fullContent.slice(fileEnd + 11);
        }

        streamedMessages = [
          ...newMessages,
          { content: fullContent, isUser: false, file: attachedFile, id: aiMessageId },
        ];
        onUpdateMessages(streamedMessages);
      }

      await saveMessage(chat.id, "assistant", fullContent, mode);

    } catch (err) {
      onUpdateMessages([
        ...newMessages,
        { content: "Something went wrong. Please try again.", isUser: false, file: null, id: Date.now() + Math.random() },
      ]);
      setIsThinking(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      const file = fileInputRef.current?.files[0] || null;
      sendMessage(file);
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center p-4 gap-8 h-screen">
      <div className="flex items-center justify-center gap-4">
        <img src="/logo.svg" className="w-24 h-24" />
        <h1 className="text-4xl sm:text-5xl lg:text-7xl font-light bg-gradient-to-r
          from-sky-400 via-cyan-300 to-teal-400 bg-clip-text text-transparent text-center">
          Welcome to AiMD
        </h1>
      </div>
      <div className="relative w-72 flex items-center bg-gray-800/60 border border-gray-600 rounded-2xl px-1 py-1">
        <div
          className={`absolute top-1 bottom-1 w-[calc(50%-7px)] rounded-xl transition-all duration-300
            ${mode === "chat"
              ? "left-1 bg-gradient-to-r from-sky-500 to-cyan-500"
              : "left-[calc(50%+3px)] bg-gradient-to-r from-violet-500 to-purple-600"
            }`}
        />
        <button
          onClick={() => setMode("chat")}
          className={`relative z-10 px-5 py-2 rounded-xl text-sm font-semibold transition-colors duration-200 w-1/2
            ${mode === "chat" ? "text-white" : "text-gray-400 hover:text-white"}`}
        >
          💬 Chat
        </button>
        <button
          onClick={() => setMode("analysis")}
          className={`relative z-10 px-5 py-2 rounded-xl text-sm font-semibold transition-colors duration-200 w-1/2
            ${mode === "analysis" ? "text-white" : "text-gray-400 hover:text-white"}`}
        >
          🧠 Analysis
        </button>
      </div>
      <div className="w-full max-w-6xl flex flex-col flex-1 min-h-0 bg-gradient-to-r from-gray-800/90 to-gray-700/90
        backdrop-blur-md border border-gray-600 rounded-3xl p-6 shadow-2xl">
        <ChatWindow
          messages={chat.messages}
          isThinking={isThinking}
          messagesEndRef={messagesEndRef}
        />
        <ChatInput
          inputValue={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyPress}
          onSend={sendMessage}
          isThinking={isThinking}
          fileInputRef={fileInputRef}
          fileName={fileName}
          onFileChange={setFileName}
        />
      </div>
    </div>
  );
}