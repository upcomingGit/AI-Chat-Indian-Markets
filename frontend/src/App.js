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
    <div className="h-screen w-full flex flex-col bg-gray-900">
      <div className="w-full flex flex-col h-28 bg-gray-950 shadow-lg">
        <div className="text-white text-2xl font-semibold p-6 text-center tracking-wide">Saras – Your Personal AI Assistant for Indian Financial Markets</div>
      </div>
      <div className="flex-1 flex flex-col items-center overflow-y-auto space-y-6 p-10 bg-gray-950">
        {messages.map((msg, i) => (
          <div key={i} className={`flex w-full max-w-4xl ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            {msg.role === "assistant" && (
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-700 text-white flex items-center justify-center mr-3 text-xl">🤖</div>
            )}
            <div
              className={`prose prose-invert prose-blue prose-headings max-w-3xl w-full p-4 text-base leading-relaxed ${
                msg.role === "user"
                  ? "bg-blue-900 text-blue-100 self-end whitespace-pre-line break-words"
                  : "bg-transparent text-gray-100 self-start"
              }`}
              style={{
                boxShadow: "none",
                border: "none",
                borderRadius: 0,
                background: msg.role === "user" ? "#1e3a8a" : "transparent",
                color: msg.role === "user" ? "#dbeafe" : "#f3f4f6"
              }}
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
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gray-700 text-white flex items-center justify-center ml-3 text-xl">🧑</div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex w-full max-w-4xl justify-start">
            <div className="bg-transparent text-gray-100 p-4 self-start" style={{ boxShadow: "none", border: "none", borderRadius: 0 }}>Thinking...</div>
            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-700 text-white flex items-center justify-center ml-3 text-xl">🤖</div>
          </div>
        )}
      </div>
      <div className="flex w-full max-w-4xl mx-auto p-6 bg-gray-900" style={{ borderTop: 'none' }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          className="flex-1 p-3 rounded-l-lg border border-gray-700 bg-gray-900 text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-700 text-lg placeholder-gray-400"
          placeholder="Ask about a company's financials..."
        />
        <button
          onClick={sendMessage}
          className="bg-blue-700 text-white px-6 py-2 rounded-r-lg hover:bg-blue-800 transition-colors text-lg"
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default App;
