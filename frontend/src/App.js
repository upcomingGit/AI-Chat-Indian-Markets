import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import { marked } from "marked";
import DOMPurify from "dompurify";
import "./index.css";

const App = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  // MCP holdings pane state
  const [showHoldingsPane, setShowHoldingsPane] = useState(false);
  const [paneMounted, setPaneMounted] = useState(false);
  const [mcpSessionId, setMcpSessionId] = useState(null);
  const [holdings, setHoldings] = useState(null);
  const [holdingsLoading, setHoldingsLoading] = useState(false);
  const [mcpError, setMcpError] = useState("");

  // Mirror backend history limit for UI note
  const HISTORY_LIMIT = 20;

  // Simple session management: generate a fresh ID per chat session
  const generateSessionId = () =>
    `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
  const [sessionId, setSessionId] = useState(generateSessionId());

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    // Capture the session at send time to avoid race conditions on reset
    const activeSession = sessionId;

    try {
      const res = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/chat`, {
        query: input,
        session_id: activeSession,
      });
      // Ignore late responses from a previous session
      if (activeSession !== sessionId) return;
      setMessages([...newMessages, { role: "assistant", content: res.data.response }]);
    } catch (error) {
      if (activeSession !== sessionId) return;
      setMessages([...newMessages, { role: "assistant", content: "⚠️ Error fetching response." }]);
    }

    setLoading(false);
  };

  const resetChat = () => {
    // Try to clear server-side session first, then clear UI and start a new session
    const oldSession = sessionId;
    const apiBase = process.env.REACT_APP_API_BASE_URL;
    if (apiBase) {
      axios
        .post(`${apiBase}/chat/reset`, { session_id: oldSession })
        .then((res) => {
          // ignore response details; proceed to local reset
          setMessages([]);
          setInput("");
          setLoading(false);
          setSessionId(generateSessionId());
        })
        .catch((err) => {
          console.warn("Failed to clear server session, clearing locally", err);
          setMessages([]);
          setInput("");
          setLoading(false);
          setSessionId(generateSessionId());
        });
    } else {
      // No backend configured (dev); just clear locally
      setMessages([]);
      setInput("");
      setLoading(false);
      setSessionId(generateSessionId());
    }
  };

  // --- MCP (Zerodha) integration ---
  const openHoldingsPane = async () => {
  // mount first so we can animate open
  setPaneMounted(true);
  // small delay to allow mount -> visible transition
  setTimeout(() => setShowHoldingsPane(true), 20);
    setMcpError("");
    setHoldings(null);
  // compute pane position after layout
  setTimeout(() => updatePanePosition(), 50);
    try {
      const apiBase = process.env.REACT_APP_API_BASE_URL;
      const res = await axios.get(`${apiBase}/mcp/login`);
      if (res.data?.error) {
        setMcpError(res.data.error);
        return;
      }
      const { session_id, login_url } = res.data || {};
      if (session_id) setMcpSessionId(session_id);
      if (login_url) {
        // Open Zerodha login in a new tab
        window.open(login_url, "_blank", "noopener,noreferrer");
      }
    } catch (e) {
      setMcpError("Failed to initiate login.");
    }
  };

  // refs to align the pane with chat boundaries
  const headerRef = useRef(null);
  const bottomBarRef = useRef(null);
  const [panePos, setPanePos] = useState({ top: 16, height: null });

  const updatePanePosition = () => {
    try {
      const hdr = headerRef.current;
      const bottom = bottomBarRef.current;
      if (!hdr || !bottom) return;
      const hdrRect = hdr.getBoundingClientRect();
      const bottomRect = bottom.getBoundingClientRect();
      const top = Math.max(8, Math.round(hdrRect.bottom));
      const height = Math.max(200, Math.round(bottomRect.top - hdrRect.bottom));
      setPanePos({ top, height });
    } catch (e) {
      // ignore
    }
  };

  useEffect(() => {
    const onResize = () => {
      if (showHoldingsPane) updatePanePosition();
    };
    window.addEventListener("resize", onResize);
    window.addEventListener("orientationchange", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      window.removeEventListener("orientationchange", onResize);
    };
  }, [showHoldingsPane]);

  const loadHoldings = async () => {
    if (!mcpSessionId) return;
    setHoldingsLoading(true);
    setMcpError("");
    try {
      const apiBase = process.env.REACT_APP_API_BASE_URL;
      const res = await axios.get(`${apiBase}/mcp/holdings`, { params: { session_id: mcpSessionId } });
      if (res.data?.error) {
        setMcpError(res.data.error);
        setHoldingsLoading(false);
        return;
      }
      setHoldings(res.data?.holdings ?? null);
    } catch (e) {
      setMcpError("Failed to fetch holdings.");
    } finally {
      setHoldingsLoading(false);
    }
  };

  const closeHoldingsPane = () => {
    // animate close then unmount
    setShowHoldingsPane(false);
    setTimeout(() => setPaneMounted(false), 320);
    setHoldings(null);
    setMcpError("");
  };

  // Polling: auto-load holdings after login
  const pollingRef = useRef({ attempts: 0, timer: null });

  useEffect(() => {
    // start polling when we have a session and the pane is visible
    if (!mcpSessionId || !showHoldingsPane) return;

    pollingRef.current.attempts = 0;
    const maxAttempts = 10;
    const intervalMs = 3000;

    const tick = async () => {
      pollingRef.current.attempts += 1;
      try {
        await loadHoldings();
        // if holdings loaded, stop polling
        if (holdings && pollingRef.current.timer) {
          clearInterval(pollingRef.current.timer);
          pollingRef.current.timer = null;
        }
      } catch (e) {
        // ignore - loadHoldings handles errors
      }
      if (pollingRef.current.attempts >= maxAttempts && pollingRef.current.timer) {
        clearInterval(pollingRef.current.timer);
        pollingRef.current.timer = null;
      }
    };

    // first immediate attempt
    tick();
  pollingRef.current.timer = window.setInterval(tick, intervalMs);

    return () => {
      if (pollingRef.current.timer) {
        clearInterval(pollingRef.current.timer);
        pollingRef.current.timer = null;
      }
    };
  }, [mcpSessionId, showHoldingsPane]);

  const renderHoldingsTable = (data) => {
    if (!data) return null;
    // If it's an array of objects, render a table; otherwise show JSON
    if (Array.isArray(data) && data.length && data.every((x) => x && typeof x === "object" && !Array.isArray(x))) {
      const cols = Array.from(
        data.reduce((set, row) => {
          Object.keys(row).forEach((k) => set.add(k));
          return set;
        }, new Set())
      );
      return (
        <div className="card" style={{ overflow: "auto", borderRadius: 12 }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr>
                {cols.map((c) => (
                  <th key={c} style={{ textAlign: "left", padding: "10px", borderBottom: "1px solid var(--line)", position: "sticky", top: 0, background: "var(--bg-2)" }}>{c}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, i) => (
                <tr key={i}>
                  {cols.map((c) => (
                    <td key={c} style={{ padding: "8px 10px", borderBottom: "1px solid var(--line)", color: "var(--text-1)" }}>
                      {(() => {
                        const v = row?.[c];
                        if (v == null) return "";
                        if (typeof v === "object") return JSON.stringify(v);
                        return String(v);
                      })()}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }
    return (
      <pre className="card" style={{ padding: 12, borderRadius: 12, whiteSpace: "pre-wrap", wordBreak: "break-word", fontSize: 12 }}>{
        typeof data === "string" ? data : JSON.stringify(data, null, 2)
      }</pre>
    );
  };

  return (
    <div className="h-screen w-full flex flex-col" style={{ background: "transparent" }}>
      <div ref={headerRef} className="w-full flex flex-col header-bar" style={{ position: 'relative' }}>
        <div className="header-title text-2xl font-semibold p-6 text-center tracking-wide">Saras – Your Personal AI Assistant for Indian Financial Markets</div>
        <div style={{ position: 'absolute', top: 10, right: 12, display: 'flex', gap: 8 }}>
          <button
            onClick={openHoldingsPane}
            className="btn px-3 py-2 transition-colors text-sm"
            title="Interact with your Zerodha Portfolio"
            aria-label="Interact with your Zerodha Portfolio"
            style={{ border: '1px solid var(--line)', borderRadius: 8 }}
          >
            Interact with your Zerodha Portfolio
          </button>
        </div>
        <div className="text-center text-sm text-muted px-4 pb-4" style={{ color: 'var(--muted)' }}>
          Note: Only the last {HISTORY_LIMIT || 20} messages are remembered as context; older messages will not be used in the chat history
        </div>
      </div>

  <div className="flex-1 flex" style={{ minHeight: 0 }}>
        <div className="chat-column flex flex-col items-center" style={{ flex: showHoldingsPane ? '0 0 80%' : '1 1 100%', minHeight: 0 }}>
          <div className="flex-1 flex flex-col items-center overflow-y-auto space-y-6 p-10" style={{ backdropFilter: "saturate(120%)", minHeight: 0 }}>
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

      <div ref={bottomBarRef} className="flex w-full max-w-4xl mx-auto p-6 items-center" style={{ borderTop: '1px solid var(--line)' }}>
        <button
          onClick={resetChat}
          className="btn px-4 py-2 mr-3 transition-colors text-sm"
          disabled={loading}
          title="Reset chat"
          aria-label="Reset chat"
          style={{ border: '1px solid var(--line)', borderRadius: 8 }}
        >
          Reset
        </button>
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
          className="btn btn-primary ml-3 px-6 py-2 rounded-r-lg transition-colors text-lg"
          disabled={loading}
        >
          Send
        </button>
      </div>
        </div>

        {showHoldingsPane && (
          <aside className="card mcp-pane" style={{ width: '20%', minWidth: 300, borderLeft: '1px solid var(--line)', display: 'flex', flexDirection: 'column', background: 'var(--bg-2)' }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: 14, borderBottom: "1px solid var(--line)" }}>
              <div style={{ fontWeight: 700 }}>Zerodha Holdings</div>
              <button className="btn" onClick={closeHoldingsPane} title="Close" style={{ padding: "6px 10px" }}>✕</button>
            </div>
            <div style={{ padding: 12, display: "flex", flexDirection: "column", gap: 12, minHeight: 0, flex: 1, overflow: 'auto' }}>
              <div style={{ color: "var(--muted)", fontSize: 13 }}>
                1) Sign in to Zerodha in the opened tab. 2) Then click "Load Holdings".
              </div>
              {mcpError && (
                <div className="card" style={{ padding: 10, color: '#fca5a5', borderColor: '#7f1d1d' }}>Error: {mcpError}</div>
              )}
              <div style={{ display: "flex", gap: 8 }}>
                <button className="btn btn-primary" onClick={loadHoldings} disabled={!mcpSessionId || holdingsLoading}>
                  {holdingsLoading ? "Loading..." : "Load Holdings"}
                </button>
              </div>
              <div style={{ flex: 1, minHeight: 0, overflow: 'auto' }}>
                {holdingsLoading && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div className="loading-spinner" />
                    <div style={{ color: 'var(--muted)' }}>Fetching portfolio...</div>
                  </div>
                )}
                {!holdingsLoading && holdings && renderHoldingsTable(holdings)}
              </div>
            </div>
          </aside>
        )}
      </div>
    </div>
  );
};

export default App;
