import MessageBubble from "./MessageBubble";
import ThinkingBubble from "./ThinkingBubble";

export default function ChatWindow({ messages = [], isThinking, messagesEndRef }) {
  return (
    <div className="flex-1 min-h-0 overflow-y-auto border-b border-gray-600
      mb-6 p-4 bg-gradient-to-b from-gray-900/50 to-gray-800/50 rounded-2xl">
      {messages.length === 0 && (
        <div className="text-center text-gray-400 mt-20">
          Start a conversation by typing a message below.
        </div>
      )}
      {messages.map((msg) => (
        <MessageBubble key={msg.id} msg={msg} />
      ))}
      {isThinking && <ThinkingBubble />}
      <div ref={messagesEndRef}></div>
    </div>
  );
}