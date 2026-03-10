import { useState, useEffect, useRef } from "react";
import ChatWindow from "./ChatWindow";
import ChatInput from "./ChatInput";

export default function Chat({ chat, onUpdateMessages }) {
  const [inputValue, setInputValue] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [fileName, setFileName] = useState(null);
  const [mode, setMode] = useState("thinking");
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToEnd = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToEnd, [chat.messages]);

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

    // Replace with real API call
    setTimeout(() => {
      const replied = [
        ...newMessages,
        {
          content: mode == "thinking" ? "im thinking" : "here to chat",
          isUser: false,
          file: null,
          id: Date.now() + Math.random(),
        },
      ];
      onUpdateMessages(replied);
      setIsThinking(false);
    }, 2000);
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      const file = fileInputRef.current?.files[0] || null;
      sendMessage(file);
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-4 gap-8">
      <h1
        className="text-6xl sm:text-7xl font-light bg-gradient-to-r
        from-sky-400 via-cyan-300 to-teal-400 bg-clip-text text-transparent text-center"
      >
        Welcome to AiMD
      </h1>
      <div className="relative w-72 flex items-center bg-gray-800/60 border border-gray-600 rounded-2xl px-1 py-1">
        <div
          className={`absolute top-1 bottom-1 w-[calc(50%-7px)] rounded-xl transition-all duration-300
    ${
      mode === "chat"
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
          onClick={() => setMode("thinking")}
          className={`relative z-10 px-5 py-2 rounded-xl text-sm font-semibold transition-colors duration-200 w-1/2
      ${mode === "thinking" ? "text-white" : "text-gray-400 hover:text-white"}`}
        >
          🧠 Analysis
        </button>
      </div>
      <div
        className="w-full max-w-2xl bg-gradient-to-r from-gray-800/90 to-gray-700/90
        backdrop-blur-md border border-gray-600 rounded-3xl p-6 shadow-2xl"
      >
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
