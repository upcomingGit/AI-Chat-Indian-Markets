import React, { useState } from "react";
import axios from "axios";
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
    <div className="h-screen flex flex-col p-4 bg-gray-100">
      <div className="bg-red-500 text-white p-4">Tailwind is working!</div>
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`max-w-md p-3 rounded-lg ${
              msg.role === "user" ? "bg-blue-200 self-end" : "bg-white self-start"
            }`}
          >
            {msg.content}
          </div>
        ))}
        {loading && <div className="bg-white p-3 rounded-lg self-start">Thinking...</div>}
      </div>

      <div className="flex">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          className="flex-1 p-2 rounded-l-lg border"
          placeholder="Ask about a company's financials..."
        />
        <button onClick={sendMessage} className="bg-blue-500 text-white px-4 py-2 rounded-r-lg">
          Send
        </button>
      </div>
    </div>
  );
};

export default App;
