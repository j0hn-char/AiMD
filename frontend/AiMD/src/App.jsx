import { useState, useEffect, useRef } from "react";

function App() {

  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToEnd = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth"
    });
  }

  useEffect(scrollToEnd, [messages]);

  const addMessages = (msg, isUser) => {
    setMessages((prev) => [
      ...prev,
      { content: msg, isUser, id: Date.now() + Math.random() }
    ])
  }

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
  }

  const handleKeyPress = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-950 via-slate-950 to-teal-950
    flex flex-col items-center justify-center p-4 gap-8">
      <h1 className="text-6xl sm:text-7xl font-light bg-gradient-to-r 
      from-sky-400 via-cyan-300 to-teal-400 bg-clip-text text-transparent text-center">
        Welcome to AiMD
      </h1>

      <div className="w-full max-w-2xl bg-gradient-to-r from-gray-800/90 to-gray-700/90 
      backdrop-blur-md border border-gray-600 rounded-3xl p-6 shadow-2xl">
        <div className="h-80 overflow-y-auto border-b border-gray-600
        mb-6 p-4 bg-gradient-to-b from-gray-900/50 to-gray-800/50 rounded-2xl">
          {
            messages.length === 0 && (
              <div className="text-center text-gray-400 mt-20">
                Start a conversation by typing a message below.
              </div>
            )
          }

          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.isUser ? "justify-end" : "justify-start"}`}>
              <div className={`p-3 m-2 rounded-2xl max-w-[70%] break-words
      ${msg.isUser
                  ? "bg-gradient-to-r from-sky-600 to-cyan-500 text-white text-right"
                  : "bg-gradient-to-r from-slate-700 to-slate-800 text-white border border-slate-600"}`}>
                <div className="whitespace-pre-wrap">
                  {msg.content}
                </div>
              </div>
            </div>
          ))}

          {isThinking && (
            <div className="flex justify-start">
              <div className="p-3 m-2 rounded-2xl max-w-xs bg-gradient-to-r from-slate-700
      to-slate-800 text-white border border-slate-600">
                <div className="flex items-center gap-2">
                  <div className="animate-spin w-4 h-4 border-2 border-white/30
          border-t-white rounded-full"></div>
                  Thinking...
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef}></div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            value={inputValue}
            onChange={(event) => setInputValue(event.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type a message here..."
            disabled={isThinking}
            className="flex-1 px-4 py-3 bg-gray-700/80 border border-gray-600 rounded-2xl
          text-white placeholder-gray-400 focus:outline-none focus:ring-2
          focus:ring-sky-500 focus:shadow-xl focus:shadow-sky-400/80 transition duration-400
          disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button onClick={sendMessage}
            disabled={isThinking || !inputValue.trim()}
            className="px-6 py-3 bg-gradient-to-r from-sky-400 to-cyan-400 hover:opacity-80
        text-white font-semibold rounded-2xl transition disabled:opacity-50 
        disabled:cursor-not-allowed"
          >
            {isThinking ? (
              <div className="flex items-center gap-2">
                <div className="animate-spin w-4 h-4 border-2
              border-white/30 border-t-white rounded-full"></div>
                Sending
              </div>
            ) : (
              "Send"
            )
            }
          </button>
        </div>
      </div>
    </div>
  )
}

export default App
