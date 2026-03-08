import { useState, useEffect, useRef } from "react";
import ChatWindow from "./Components/ChatWindow";
import ChatInput from "./Components/ChatInput";

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToEnd = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToEnd, [messages]);

  const addMessages = (msg, isUser) => {
    setMessages((prev) => [
      ...prev,
      { content: msg, isUser, id: Date.now() + Math.random() }
    ]);
  };

  const sendMessage = async () => {
    const message = inputValue.trim();
    if (!message) return;
    addMessages(message, true);
    setInputValue("");
    setIsThinking(true);
    setTimeout(() => {
      addMessages("hello world", false);
      setIsThinking(false);
    }, 2000);
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-950 via-slate-950 to-teal-950
      flex flex-col items-center justify-center p-4 gap-8">
      <h1 className="text-6xl sm:text-7xl font-light bg-gradient-to-r
        from-sky-400 via-cyan-300 to-teal-400 bg-clip-text text-transparent text-center">
        Welcome to AiMD
      </h1>
      <div className="w-full max-w-2xl bg-gradient-to-r from-gray-800/90 to-gray-700/90
        backdrop-blur-md border border-gray-600 rounded-3xl p-6 shadow-2xl">
        <ChatWindow messages={messages} isThinking={isThinking} messagesEndRef={messagesEndRef} />
        <ChatInput
          inputValue={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyPress}
          onSend={sendMessage}
          isThinking={isThinking}
        />
      </div>
    </div>
  );
}

export default App;