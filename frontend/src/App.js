import React, { useState } from "react";
import axios from "axios";
import { marked } from "marked";
import DOMPurify from "dompurify";
import "./index.css";

const App = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/chat`, {
        query: input,
      });
      setMessages([...newMessages, { role: "assistant", content: res.data.response }]);
    } catch (error) {
      setMessages([...newMessages, { role: "assistant", content: "⚠️ Error fetching response." }]);
    }

    setLoading(false);
  };

  return (
    <div className="h-screen w-full flex flex-col" style={{ background: "transparent" }}>
      <div className="w-full flex flex-col header-bar">
        <div className="header-title text-2xl font-semibold p-6 text-center tracking-wide">Saras – Your Personal AI Assistant for Indian Financial Markets</div>
      </div>

      <div className="flex-1 flex flex-col items-center overflow-y-auto space-y-6 p-10" style={{ backdropFilter: "saturate(120%)" }}>
        {messages.map((msg, i) => (
          <div key={i} className={`flex w-full max-w-4xl ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {msg.role === "assistant" && (
              <div className="flex-shrink-0 w-10 h-10 rounded-full" style={{ background: "linear-gradient(135deg, var(--purple-600), var(--purple-400))", color: "#fff" }}>
                <div className="w-10 h-10 flex items-center justify-center text-xl">🤖</div>
              </div>
            )}
            <div
              className={`prose prose-invert prose-headings max-w-3xl w-full p-4 text-base leading-relaxed bubble ${
                msg.role === "user" ? "bubble-user self-end whitespace-pre-line break-words" : "bubble-assistant self-start"
              }`}
              style={{ boxShadow: "0 8px 24px rgba(0,0,0,0.25)", borderRadius: 14 }}
              dangerouslySetInnerHTML={{
                __html:
                  msg.role === "assistant"
                    ? msg.content
                      ? DOMPurify.sanitize(marked.parse(msg.content, { gfm: true, breaks: true }))
                      : (() => { console.warn("[Debug] Assistant message content is missing or undefined", msg); return "<span style='color: #f87171'>[No response from backend]</span>"; })()
                    : msg.content
                      ? msg.content.replace(/\n/g, '<br/>')
                      : (() => { console.warn("[Debug] User message content is missing or undefined", msg); return "<span style='color: #f87171'>[No user message]</span>"; })(),
              }}
            />
            {msg.role === "user" && (
              <div className="flex-shrink-0 w-10 h-10 rounded-full" style={{ background: "#222", color: "#fff", border: "1px solid var(--line)" }}>
                <div className="w-10 h-10 flex items-center justify-center text-xl">🧑</div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex w-full max-w-4xl items-center gap-3 justify-start">
            <div className="loading-spinner" aria-label="Loading" />
            <div className="text-sm" style={{ color: "var(--muted)" }}>Thinking...</div>
          </div>
        )}
      </div>

      <div className="flex w-full max-w-4xl mx-auto p-6" style={{ borderTop: '1px solid var(--line)' }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          className="flex-1 p-3 rounded-l-lg input focus:outline-none focus:ring-2 text-lg"
          style={{ outlineColor: "var(--purple-500)", boxShadow: "0 0 0 2px rgba(124,58,237,0.25)" }}
          placeholder="Ask about a company's financials..."
        />
        <button
          onClick={sendMessage}
          className="btn btn-primary px-6 py-2 rounded-r-lg transition-colors text-lg"
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default App;
