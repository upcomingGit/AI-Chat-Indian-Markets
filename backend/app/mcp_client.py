"""
Stock/General Trading
get_holdings - Retrieves portfolio holdings
get_positions - Gets current positions
get_margins - Retrieves account margins
place_order - Places a trading order
get_quote - Gets quotes for specified symbols
get_historical_data - Retrieves historical price data

Mutual Funds
get_mf_orders - Retrieves mutual fund orders
place_mf_order - Places a mutual fund order
cancel_mf_order - Cancels a mutual fund order
get_mf_instruments - Gets available mutual fund instruments
get_mf_holdings - Retrieves mutual fund holdings
get_mf_sips - Gets active SIPs
place_mf_sip - Creates a new SIP
modify_mf_sip - Modifies an existing SIP
cancel_mf_sip - Cancels a SIP
"""


import argparse
import asyncio
import json
import re
import sys
import webbrowser
from typing import Optional, Dict

# fastmcp imports: attempt at module import time but tolerate missing package so file can be
# imported for linting or editing without having fastmcp installed.
try:
    from fastmcp import Client  # type: ignore
    from fastmcp.client.transports import SSETransport  # type: ignore
except Exception:
    Client = None
    SSETransport = None


# We are not running a local web server for the redirect_uri with this specific flow.
# The login flow is initiated by calling the 'login' tool and it returns a URL that the user must open
# in their browser to complete the login process. The user must then confirm they have logged in by
# pressing Enter in the terminal.
def extract_url(obj):
    """Attempt to extract the first HTTP(S) URL from a variety of tool response shapes.

    Handles: plain string, dicts containing 'text' or 'message', objects with 'text' attr, lists.
    Returns the URL string or None.
    """
    url_pattern = re.compile(r"https?://[\w\-./?=&%:]+")

    # Normalize to iterable
    candidates = []
    if obj is None:
        return None
    if isinstance(obj, (str, bytes)):
        candidates.append(obj)
    elif isinstance(obj, dict):
        # common fields
        for key in ("text", "message", "url", "data", "content", "structured_content"):
            if key in obj:
                candidates.append(obj[key])
    elif isinstance(obj, list) or isinstance(obj, tuple):
        for item in obj:
            candidates.append(item)
    else:
        # fallback: try attribute access
        text = getattr(obj, "text", None) or getattr(obj, "message", None)
        if text is not None:
            candidates.append(text)
        # also descend into common container attributes like 'content' or 'data'
        for attr in ("content", "data", "structured_content"):
            val = getattr(obj, attr, None)
            if val is not None:
                candidates.append(val)

    for c in candidates:
        try:
            if isinstance(c, (dict, list, tuple)):
                # recurse
                url = extract_url(c)
                if url:
                    return url
                continue
            s = c.decode() if isinstance(c, bytes) else str(c)
        except Exception:
            continue
        # try to find a URL or a 'URL: ' pattern
        m = re.search(r"URL:\s*(https?://[\w\-./?=&%:]+)", s)
        if m:
            return m.group(1)
        m2 = url_pattern.search(s)
        if m2:
            return m2.group(0)
    return None
def format_holdings(data) -> str:
    """Return a human-readable string for holdings data.

    - list[dict] -> aligned table
    - dict -> pretty JSON
    - list of primitives -> one-per-line
    - otherwise -> str()
    """
    # list of dicts -> table
    if isinstance(data, (list, tuple)) and data:
        if all(isinstance(item, dict) for item in data):
            # collect columns
            cols = []
            for item in data:
                for k in item.keys():
                    if k not in cols:
                        cols.append(k)

            # compute column widths
            rows = []
            col_widths = {c: len(str(c)) for c in cols}
            for item in data:
                row = []
                for c in cols:
                    v = item.get(c, "")
                    s = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                    row.append(s)
                    col_widths[c] = max(col_widths[c], len(s))
                rows.append(row)

            # build table string
            header = " | ".join(c.ljust(col_widths[c]) for c in cols)
            sep = "-+-".join("-" * col_widths[c] for c in cols)
            lines = [header, sep]
            for row in rows:
                lines.append(" | ".join(row[i].ljust(col_widths[cols[i]]) for i in range(len(cols))))
            return "\n".join(lines)

        # list of primitives
        if all(not isinstance(item, (dict, list, tuple)) for item in data):
            return "\n".join(str(x) for x in data)

    # dict -> pretty JSON
    if isinstance(data, dict):
        return json.dumps(data, indent=2)

    # fallback
    return str(data)


class MCPClient:
    """Small wrapper around fastmcp Client to organize the login + tool-call flow.

    Uses print statements for verbosity/debug output (no logging module).
    """

    def __init__(self, sse_url: str, headers: Optional[Dict[str, str]] = None, auto_open: bool = True):
        self.sse_url = sse_url
        self.headers = headers or {}
        self.auto_open = auto_open

    def _print(self, level: str, *parts):
        # Simple print-based logger replacement. Level in {INFO, DEBUG, WARN, ERROR}.
        print(f"[{level}]", *parts)


    async def run(self, tool_retry: int = 3):
        if Client is None or SSETransport is None:
            raise RuntimeError(
                "fastmcp package is not available. Install it (pip install fastmcp) or ensure it is on PYTHONPATH."
            )

        transport = SSETransport(url=self.sse_url, headers=self.headers or {})

        async with Client(transport) as client:
            self._print("INFO", "Connected to fastmcp client.")

            # 1. Call the 'login' tool
            self._print("INFO", "Calling fastmcp 'login' tool...")
            login_result = await client.call_tool("login", {})
            self._print("DEBUG", "Login result from fastmcp:", login_result)

            # 2. Extract login URL
            login_url = extract_url(login_result)

            if login_url:
                print("\n=======================================================")
                print("  Please open this URL in your browser to login to Kite:")
                print(f"  {login_url}")
                print("=======================================================\n")

                if self.auto_open:
                    print("[INFO] Opening login URL in browser...")
                    try:
                        webbrowser.open(login_url)
                    except Exception as e:
                        self._print("WARN", "Failed to open browser automatically:", e)

                # 3. Wait for user confirmation (crucial step for CLI)
                input("Press Enter after you have successfully logged in to Kite in your browser...")
                self._print("INFO", "User confirmed login. Attempting to proceed with fastmcp calls.")

                self._print("DEBUG", "Session details after login:", getattr(client, "session", None))

                # small buffer for server-side session propagation
                await asyncio.sleep(2)

                # 4. Call subsequent tools with retries
                self._print("INFO", "Calling fastmcp 'get_holdings' tool...")
                attempts = 0
                while attempts < tool_retry:
                    try:
                        raw_holdings = await client.call_tool("get_holdings", {})
                        # Normalize common call-tool shapes: content list with TextContent, plain JSON string, or already parsed list
                        holdings = raw_holdings
                        try:
                            # If it's an object with 'content' attribute or key, pull the first text
                            if hasattr(raw_holdings, "content"):
                                cont = getattr(raw_holdings, "content")
                                if isinstance(cont, (list, tuple)) and cont:
                                    first = cont[0]
                                    text = getattr(first, "text", None) or first
                                    holdings = text
                            elif isinstance(raw_holdings, dict) and "content" in raw_holdings:
                                cont = raw_holdings.get("content")
                                if isinstance(cont, (list, tuple)) and cont:
                                    first = cont[0]
                                    holdings = first.get("text", first)

                            # If holdings is a JSON string, parse it
                            if isinstance(holdings, str):
                                try:
                                    parsed = json.loads(holdings)
                                    holdings = parsed
                                except Exception:
                                    # not JSON, leave as-is
                                    pass
                        except Exception:
                            # fallback: use raw result
                            holdings = raw_holdings

                        print("Your holdings:")
                        print(format_holdings(holdings))
                        break
                    except Exception as e:
                        attempts += 1
                        self._print("WARN", f"Attempt {attempts}/{tool_retry} failed fetching holdings:", e)
                        if attempts >= tool_retry:
                            self._print("ERROR", "All attempts to fetch holdings failed.")
                            raise
                        await asyncio.sleep(1.5 ** attempts)
            else:
                self._print("ERROR", "Could not find login URL in fastmcp response.")
                self._print("DEBUG", "Full login result:", login_result)


def parse_headers(text: str):
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        # try semi-colon separated key=value pairs
        headers = {}
        for part in text.split(";"):
            if "=" in part:
                k, v = part.split("=", 1)
                headers[k.strip()] = v.strip()
        return headers
    return headers


def main():
    parser = argparse.ArgumentParser(description="FastMCP client for Zerodha MCP (kite) using SSE transport")
    parser.add_argument("--url", default="https://mcp.kite.trade/sse", help="SSE transport URL")
    parser.add_argument("--headers", default=None, help='Optional headers as JSON or semi-colon key=val; example: "Authorization=Bearer ...;Cookie=sessionid=..."')
    # Default auto-open to True; provide --no-auto-open to opt out
    auto_group = parser.add_mutually_exclusive_group()
    auto_group.add_argument("--auto-open", dest="auto_open", action="store_true", help="Open the login URL automatically in the default browser (default)")
    auto_group.add_argument("--no-auto-open", dest="auto_open", action="store_false", help="Do not auto-open the login URL")
    parser.set_defaults(auto_open=True)
    args = parser.parse_args()

    headers = parse_headers(args.headers)

    client = MCPClient(sse_url=args.url, headers=headers, auto_open=args.auto_open)
    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        print("[INFO] Interrupted by user, exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()