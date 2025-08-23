from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from llm_router import router as chat_router
from typing import Any, Dict
import uuid
import time

# Reuse helpers from local mcp_client module for URL extraction and header parsing
from mcp_client import extract_url, parse_headers  # type: ignore

load_dotenv(dotenv_path="app/.env")

app = FastAPI()
#app.include_router(chat_router, prefix="/chat")



# Allow frontend access (dev mode)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://saras-ai-assistant-frontend.azurewebsites.net",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/chat")

# Optional: avoid 307 redirect from /chat to /chat/ by handling both.
@app.get("/chat")
async def chat_root_get():
    return {"message": "Chat endpoint is available. POST to /chat/ for queries."}

@app.get("/")
async def root():
    return {"status": "ok"}


# --- Minimal MCP endpoints ---
_MCP_SESSIONS: Dict[str, Dict[str, Any]] = {}


def _make_client() -> Any:
    from fastmcp import Client  # type: ignore
    from fastmcp.client.transports import SSETransport  # type: ignore

    sse_url = os.getenv("MCP_SSE_URL", "https://mcp.kite.trade/sse")
    headers_text = os.getenv("MCP_SSE_HEADERS", "")
    headers = parse_headers(headers_text)
    print("[DEBUG][_make_client] sse_url=", sse_url)
    print("[DEBUG][_make_client] raw headers_text=", headers_text)
    print("[DEBUG][_make_client] parsed headers=", headers)
    transport = SSETransport(url=sse_url, headers=headers or {})
    client = Client(transport)
    print("[DEBUG][_make_client] fastmcp Client created")
    return client


@app.get("/mcp/login")
async def mcp_login() -> Dict[str, Any]:
    """Create an MCP session, request login URL, and return {session_id, login_url}.

    Keep the fastmcp client open in-memory so subsequent calls can reuse the session.
    """
    try:
        print("[DEBUG][mcp_login] starting login flow")
        client = _make_client()
    except Exception as e:
        print(f"[ERROR][mcp_login] failed to create client: {e}")
        return {"error": f"fastmcp unavailable: {e}"}

    try:
        # Open the connection (equivalent to `async with Client(...)`)
        print("[DEBUG][mcp_login] entering client context and calling login tool")
        await client.__aenter__()
        result = await client.call_tool("login", {})
        print("[DEBUG][mcp_login] raw login tool result=", result)
        login_url = extract_url(result)
        print("[DEBUG][mcp_login] extracted login_url=", login_url)
        sid = str(uuid.uuid4())
        _MCP_SESSIONS[sid] = {"client": client, "created": time.time()}
        print(f"[DEBUG][mcp_login] session created sid={sid}")
        return {"session_id": sid, "login_url": login_url}
    except Exception as e:
        # Ensure we close any partially opened client
        print(f"[ERROR][mcp_login] login flow failed: {e}")
        try:
            await client.__aexit__(None, None, None)
        except Exception:
            pass
        return {"error": f"login_failed: {e}"}


@app.get("/mcp/holdings")
async def mcp_holdings(session_id: str) -> Dict[str, Any]:
    """Fetch holdings from Zerodha MCP server after user login.

    Returns a JSON structure suitable for rendering a table in the frontend.
    """
    print(f"[DEBUG][mcp_holdings] called with session_id={session_id}")
    sess = _MCP_SESSIONS.get(session_id)
    if not sess:
        print("[WARN][mcp_holdings] session not found")
        return {"error": "invalid_session"}
    client = sess.get("client")
    print("[DEBUG][mcp_holdings] found session, calling get_holdings tool")

    try:
        raw = await client.call_tool("get_holdings", {})
        print("[DEBUG][mcp_holdings] raw holdings result=", raw)

        # Normalize a few common shapes without being strict.
        content = raw
        try:
            if hasattr(raw, "content"):
                c = getattr(raw, "content")
                if isinstance(c, (list, tuple)) and c:
                    first = c[0]
                    content = getattr(first, "text", first)
            elif isinstance(raw, dict) and "content" in raw:
                c = raw.get("content")
                if isinstance(c, (list, tuple)) and c:
                    first = c[0]
                    content = first.get("text", first)
        except Exception as ex:
            print("[WARN][mcp_holdings] normalization failed, using raw. err=", ex)
            content = raw

        # Try to JSON-parse if it's a string
        if isinstance(content, str):
            try:
                content = __import__("json").loads(content)
                print("[DEBUG][mcp_holdings] parsed content as JSON")
            except Exception:
                print("[DEBUG][mcp_holdings] content is not JSON string, leaving as-is")
                pass

        print("[DEBUG][mcp_holdings] returning holdings content type=", type(content))
        return {"holdings": content}
    except Exception as e:
        print(f"[ERROR][mcp_holdings] failed to fetch holdings: {e}")
        return {"error": f"holdings_failed: {e}"}


@app.post("/mcp/session/close")
async def mcp_session_close(session_id: str) -> Dict[str, Any]:
    print(f"[DEBUG][mcp_session_close] closing session_id={session_id}")
    sess = _MCP_SESSIONS.pop(session_id, None)
    if not sess:
        print("[WARN][mcp_session_close] session not found")
        return {"status": "not_found"}
    client = sess.get("client")
    try:
        await client.__aexit__(None, None, None)
        print("[DEBUG][mcp_session_close] client closed")
    except Exception:
        print("[WARN][mcp_session_close] error while closing client")
    return {"status": "closed"}