import { useState, useEffect, useRef } from "react";
import ChatWindow from "./ChatWindow";
import ChatInput from "./ChatInput";

export default function Chat({ chat, onUpdateMessages }) {
    const [inputValue, setInputValue] = useState("");
    const [isThinking, setIsThinking] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToEnd = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToEnd, [chat.messages]);

    const addMessage = (msg, isUser, file = null) => {
        const newMessages = [
            ...chat.messages,
            { content: msg, isUser, file, id: Date.now() + Math.random() }
        ];
        onUpdateMessages(newMessages);
    };

    const sendMessage = async (file) => {
        const message = inputValue.trim();
        if (!message) return;

        const newMessages = [
            ...chat.messages,
            { content: message, isUser: true, file, id: Date.now() + Math.random() }
        ];
        onUpdateMessages(newMessages);
        setInputValue("");
        setIsThinking(true);

        // Replace with your real API call
        setTimeout(() => {
            const replied = [
                ...newMessages,
                { content: "hello world", isUser: false, file: null, id: Date.now() + Math.random() }
            ];
            onUpdateMessages(replied);
            setIsThinking(false);
        }, 2000);
    };

    const handleKeyPress = (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage(null);
        }
    };

    return (
        <div className="flex-1 flex flex-col items-center justify-center p-4 gap-8">
            <h1 className="text-6xl sm:text-7xl font-light bg-gradient-to-r
  from-sky-400 via-cyan-300 to-teal-400 bg-clip-text text-transparent text-center">
                Welcome to AiMD
            </h1>
            <div className="w-full max-w-2xl bg-gradient-to-r from-gray-800/90 to-gray-700/90
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
                />
            </div>
        </div>
    );
}