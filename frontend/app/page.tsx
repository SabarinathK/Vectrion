"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

const API_BASE = "/api/proxy";
const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL ||
  "ws://localhost:8000/api/v1/ws/notifications";
const DASHBOARD_CACHE_KEY = "vectrion-dashboard-cache";

// Module-level fetch guard — survives StrictMode remounts
const fetchedTokens = new Set<string>();

async function api(
  path: string,
  method: string,
  token: string,
  body?: any,
  isForm = false
) {
  const headers: Record<string, string> = token
    ? { Authorization: `Bearer ${token}` }
    : {};
  if (!isForm) headers["Content-Type"] = "application/json";
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? (isForm ? body : JSON.stringify(body)) : undefined,
  });
  if (!res.ok) throw new Error(await res.text());
  if (res.status === 204) return null;
  const textBody = await res.text();
  return textBody ? JSON.parse(textBody) : null;
}

type SourceItem = {
  id: number;
  title: string;
  source_type: string;
  status: string;
  created_at?: string;
};

type NotificationItem = {
  id: number;
  title: string;
  message: string;
  created_at?: string;
};

type SocketEvent = {
  type?: string;
  source?: { id: number; status: string };
  notification?: NotificationItem;
};

type DashboardCache = {
  token: string;
  sources: SourceItem[];
  notifications: NotificationItem[];
};

function readCache(): DashboardCache | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(DASHBOARD_CACHE_KEY);
    return raw ? (JSON.parse(raw) as DashboardCache) : null;
  } catch {
    return null;
  }
}

function writeCache(
  token: string,
  sources: SourceItem[],
  notifications: NotificationItem[]
) {
  if (typeof window === "undefined") return;
  window.sessionStorage.setItem(
    DASHBOARD_CACHE_KEY,
    JSON.stringify({ token, sources, notifications })
  );
}

function clearCache() {
  if (typeof window === "undefined") return;
  window.sessionStorage.removeItem(DASHBOARD_CACHE_KEY);
}

export default function Home() {
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("demo@example.com");
  const [fullName, setFullName] = useState("Demo User");
  const [password, setPassword] = useState("password123");
  const [title, setTitle] = useState("Sample Doc");
  const [text, setText] = useState("Paste source text here");
  const [url, setUrl] = useState("https://example.com");
  const [question, setQuestion] = useState("What is this source about?");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<SourceItem[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [error, setError] = useState("");
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmText, setConfirmText] = useState("");
  const [confirmAction, setConfirmAction] = useState<null | (() => Promise<void>)>(null);

  // Refs for stable access inside callbacks — never cause re-renders
  const sourcesRef = useRef<SourceItem[]>([]);
  const notificationsRef = useRef<NotificationItem[]>([]);
  const tokenRef = useRef("");

  // WebSocket refs — fully managed outside React render cycle
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const wsActiveRef = useRef(false); // true = we want WS running

  useEffect(() => { sourcesRef.current = sources; }, [sources]);
  useEffect(() => { notificationsRef.current = notifications; }, [notifications]);

  // ── WebSocket — completely ref-driven, never re-runs due to state ──────────
  // connectWS and disconnectWS are stable functions that don't depend on
  // any React state, so they never trigger re-renders or effect re-runs.
  function connectWS(tok: string) {
    // Don't open a second socket if one is already open/connecting
    if (
      socketRef.current &&
      (socketRef.current.readyState === WebSocket.OPEN ||
        socketRef.current.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    const ws = new WebSocket(`${WS_URL}?token=${encodeURIComponent(tok)}`);
    socketRef.current = ws;

    ws.onmessage = (event) => {
      let payload: SocketEvent;
      try {
        payload = JSON.parse(event.data) as SocketEvent;
      } catch {
        return;
      }

      if (payload.type === "notification_created" && payload.notification) {
        setNotifications((cur) => {
          const next = [payload.notification!, ...cur];
          writeCache(tokenRef.current, sourcesRef.current, next);
          return next;
        });
      }

      if (payload.type === "notifications_cleared") {
        setNotifications(() => {
          writeCache(tokenRef.current, sourcesRef.current, []);
          return [];
        });
      }

      if (payload.type === "source_updated" && payload.source) {
        setSources((cur) => {
          const next = cur.map((item) =>
            item.id === payload.source!.id
              ? { ...item, status: payload.source!.status }
              : item
          );
          writeCache(tokenRef.current, next, notificationsRef.current);
          return next;
        });
      }
    };

    ws.onerror = () => ws.close();

    ws.onclose = () => {
      socketRef.current = null;
      if (!wsActiveRef.current) return; // intentional disconnect, don't retry
      // Reconnect after 3s
      reconnectTimerRef.current = setTimeout(() => {
        if (wsActiveRef.current) connectWS(tokenRef.current);
      }, 3000);
    };
  }

  function disconnectWS() {
    wsActiveRef.current = false;
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
  }

  // ── Single effect: runs once on mount, cleans up on unmount ───────────────
  // Does NOT depend on token — token changes are handled imperatively
  // inside login/register/logout via connectWS/disconnectWS calls.
  useEffect(() => {
    return () => {
      disconnectWS();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Dashboard load ─────────────────────────────────────────────────────────
  useEffect(() => {
    if (!token) {
      setSources([]);
      setNotifications([]);
      clearCache();
      tokenRef.current = "";
      fetchedTokens.delete(token);
      return;
    }

    if (fetchedTokens.has(token)) return;

    const cached = readCache();
    if (cached && cached.token === token) {
      setSources(cached.sources);
      setNotifications(cached.notifications);
      tokenRef.current = token;
      fetchedTokens.add(token);
      return;
    }

    fetchedTokens.add(token);
    tokenRef.current = token;

    let ignore = false;

    (async () => {
      try {
        const [nextSources, nextNotifications] = await Promise.all([
          api("/sources", "GET", token) as Promise<SourceItem[]>,
          api("/notifications", "GET", token) as Promise<NotificationItem[]>,
        ]);
        if (ignore) return;
        setSources(nextSources);
        setNotifications(nextNotifications);
        writeCache(token, nextSources, nextNotifications);
        setError("");
      } catch (e: any) {
        if (ignore) return;
        fetchedTokens.delete(token);
        setError(`Load failed: ${e?.message || "Unknown error"}`);
      }
    })();

    return () => { ignore = true; };
  }, [token]);

  // ── Auth ───────────────────────────────────────────────────────────────────
  async function register(e: FormEvent) {
    e.preventDefault();
    try {
      const data = await api("/auth/register", "POST", "", {
        email,
        full_name: fullName,
        password,
      });
      disconnectWS();
      fetchedTokens.delete(data.access_token);
      setToken(data.access_token);
      tokenRef.current = data.access_token;
      wsActiveRef.current = true;
      connectWS(data.access_token);
      setError("");
    } catch (e: any) {
      setError(`Register failed: ${e?.message || "Unknown error"}`);
    }
  }

  async function login(e: FormEvent) {
    e.preventDefault();
    try {
      const data = await api("/auth/login", "POST", "", { email, password });
      disconnectWS();
      fetchedTokens.delete(data.access_token);
      setToken(data.access_token);
      tokenRef.current = data.access_token;
      wsActiveRef.current = true;
      connectWS(data.access_token);
      setError("");
    } catch (e: any) {
      setError(`Login failed: ${e?.message || "Unknown error"}`);
    }
  }

  // ── Ingest ─────────────────────────────────────────────────────────────────
  async function uploadText() {
    try {
      const source = (await api("/ingest/text", "POST", token, {
        title,
        text,
      })) as SourceItem;
      setSources((cur) => {
        const next = [source, ...cur];
        writeCache(token, next, notificationsRef.current);
        return next;
      });
      setError("");
    } catch (e: any) {
      setError(`Upload text failed: ${e?.message || "Unknown error"}`);
    }
  }

  async function uploadUrl() {
    try {
      const source = (await api("/ingest/url", "POST", token, {
        title,
        url,
      })) as SourceItem;
      setSources((cur) => {
        const next = [source, ...cur];
        writeCache(token, next, notificationsRef.current);
        return next;
      });
      setError("");
    } catch (e: any) {
      setError(`Upload URL failed: ${e?.message || "Unknown error"}`);
    }
  }

  async function uploadFile(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    try {
      const formData = new FormData(e.currentTarget);
      const source = (await api(
        "/ingest/file",
        "POST",
        token,
        formData,
        true
      )) as SourceItem;
      setSources((cur) => {
        const next = [source, ...cur];
        writeCache(token, next, notificationsRef.current);
        return next;
      });
      setError("");
    } catch (e: any) {
      setError(`Upload file failed: ${e?.message || "Unknown error"}`);
    }
  }

  // ── Q&A ────────────────────────────────────────────────────────────────────
  async function ask() {
    try {
      const out = await api("/qa/ask", "POST", token, { question });
      setAnswer(out.answer);
      setError("");
    } catch (e: any) {
      setError(`Ask failed: ${e?.message || "Unknown error"}`);
    }
  }

  // ── Notifications ──────────────────────────────────────────────────────────
  async function clearNotifications() {
    try {
      await api("/notifications/clear", "DELETE", token);
      setNotifications(() => {
        writeCache(token, sourcesRef.current, []);
        return [];
      });
      setError("");
    } catch (e: any) {
      setError(`Clear notifications failed: ${e?.message || "Unknown error"}`);
    }
  }

  // ── Sources ────────────────────────────────────────────────────────────────
  async function removeSource(sourceId: number) {
    try {
      await api(`/sources/${sourceId}`, "DELETE", token);
      setSources((cur) => {
        const next = cur.filter((s) => s.id !== sourceId);
        writeCache(token, next, notificationsRef.current);
        return next;
      });
      setError("");
    } catch (e: any) {
      setError(`Delete source failed: ${e?.message || "Unknown error"}`);
    }
  }

  // ── Confirm dialog ─────────────────────────────────────────────────────────
  function openConfirm(text: string, action: () => Promise<void>) {
    setConfirmText(text);
    setConfirmAction(() => action);
    setConfirmOpen(true);
  }

  async function onConfirmYes() {
    if (!confirmAction) return;
    setConfirmOpen(false);
    await confirmAction();
    setConfirmAction(null);
  }

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <main>
      <h1>Vectrion RAG</h1>
      <p className="muted">
        FastAPI + LangChain/LangGraph + Celery + Redis + Postgres
      </p>
      {error ? <p style={{ color: "#b91c1c", marginTop: 8 }}>{error}</p> : null}

      <div className="grid">
        <section className="card">
          <h3>Auth</h3>
          <form onSubmit={register}>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
            />
            <input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Full name"
            />
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              placeholder="Password"
            />
            <button type="submit">Register</button>
          </form>
          <form onSubmit={login}>
            <button type="submit">Login</button>
          </form>
          <p className="muted">Token: {token ? "logged in" : "not logged in"}</p>
        </section>

        <section className="card">
          <h3>Ingest Text / URL / PDF</h3>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Title"
          />
          <textarea value={text} onChange={(e) => setText(e.target.value)} />
          <button type="button" onClick={uploadText}>
            Upload Text
          </button>
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://..."
          />
          <button type="button" onClick={uploadUrl}>
            Scrape URL
          </button>
          <form onSubmit={uploadFile}>
            <input name="title" defaultValue={title} hidden />
            <input name="file" type="file" accept=".pdf" />
            <button type="submit">Upload PDF</button>
          </form>
        </section>

        <section className="card">
          <h3>Ask</h3>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <button type="button" onClick={ask}>
            Ask Question
          </button>
          <p>{answer}</p>
        </section>
      </div>

      <div className="grid" style={{ marginTop: 16 }}>
        <section className="card">
          <h3>Sources</h3>
          <ul className="list">
            {sources.map((s) => (
              <li key={s.id}>
                {s.title} | {s.source_type} | {s.status}
                <button
                  type="button"
                  style={{ marginLeft: 8, width: "auto", padding: "6px 10px" }}
                  onClick={() =>
                    openConfirm(
                      "Delete this source from PostgreSQL and vector database?",
                      () => removeSource(s.id)
                    )
                  }
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        </section>

        <section className="card">
          <h3>Notifications</h3>
          <button
            type="button"
            style={{ width: "auto", padding: "6px 10px" }}
            onClick={() =>
              openConfirm("Clear all notifications?", clearNotifications)
            }
          >
            Clear
          </button>
          <ul className="list">
            {notifications.map((n) => (
              <li key={n.id}>
                {n.title}: {n.message}
              </li>
            ))}
          </ul>
        </section>
      </div>

      {confirmOpen ? (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.35)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
          }}
        >
          <div className="card" style={{ maxWidth: 420, width: "90%" }}>
            <h3>Confirm Action</h3>
            <p>{confirmText}</p>
            <div style={{ display: "flex", gap: 10, marginTop: 12 }}>
              <button type="button" onClick={onConfirmYes}>
                Yes, Continue
              </button>
              <button
                type="button"
                onClick={() => {
                  setConfirmOpen(false);
                  setConfirmAction(null);
                }}
                style={{ background: "#6b7280" }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </main>
  );
}