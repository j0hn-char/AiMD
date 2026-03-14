import MessageBubble from "./MessageBubble";
import ThinkingBubble from "./ThinkingBubble";

export default function ChatWindow({ messages = [], isThinking, messagesEndRef }) {
  return (
    <div
      className="flex-1 min-h-0 overflow-y-auto mb-6 p-4 rounded-2xl"
      style={{
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.07)',
        backdropFilter: 'blur(8px)',
      }}
    >
      {messages.length === 0 && (
        <div className="text-center text-white/30 mt-20 text-sm">
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