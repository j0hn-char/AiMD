import { useState, useEffect, useRef } from "react";

function App() {

  const [ messages, setMessages ] = useState([]);
  const [ inputValue, setInputValue ] = useState("");
  const [ isThinking, setIsThinking ] = useState(false);
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
      {content: msg, isUser, id: Date.now() + Math.random()}
    ])
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-950 via-slate-950 to-teal-950
    flex flex-col items-center justify-center p-4 gap-8">
      <h1 className="text-6xl sm:text-7xl font-light bg-gradient-to-r 
      from-sky-400 via-cyan-300 to-teal-400 bg-clip-text text-transparent text-center">
        Welcome to AiMD
      </h1>
    </div>
  )
}

export default App
