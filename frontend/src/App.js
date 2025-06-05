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
    <div className="h-screen flex flex-col items-center justify-center bg-gray-100">
      <div className="w-full max-w-4xl flex flex-col h-[90vh] bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="bg-blue-600 text-white text-2xl font-semibold p-6 text-center tracking-wide">AI Chat – Indian Financial Markets</div>
        <div className="flex-1 overflow-y-auto space-y-6 p-10 bg-gray-50">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              {msg.role === "assistant" && (
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center mr-3 text-xl">🤖</div>
              )}
              <div
                className={`prose prose-blue prose-headings prose-h3:max-w-2xl max-w-2xl p-4 rounded-lg shadow-md text-base leading-relaxed ${
                  msg.role === "user"
                    ? "bg-blue-100 self-end whitespace-pre-line break-words"
                    : "bg-white self-start border border-gray-200"
                }`}
                dangerouslySetInnerHTML={{
                  __html:
                    msg.role === "assistant"
                      ? DOMPurify.sanitize(marked.parse(msg.content, { gfm: true, breaks: true }))
                      : msg.content.replace(/\n/g, '<br/>'),
                }}
              />
              {msg.role === "user" && (
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gray-400 text-white flex items-center justify-center ml-3 text-xl">🧑</div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white p-4 rounded-lg shadow-md self-start border border-gray-200">Thinking...</div>
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center ml-3 text-xl">🤖</div>
            </div>
          )}
        </div>
        <div className="flex p-6 bg-white border-t border-gray-200">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            className="flex-1 p-3 rounded-l-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 text-lg"
            placeholder="Ask about a company's financials..."
          />
          <button
            onClick={sendMessage}
            className="bg-blue-500 text-white px-6 py-2 rounded-r-lg hover:bg-blue-600 transition-colors text-lg"
            disabled={loading}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;
