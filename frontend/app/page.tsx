"use client";

import { FormEvent, useEffect, useState } from "react";

const API_BASE = "/api/proxy";

async function api(path: string, method: string, token: string, body?: any, isForm = false) {
  const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {};
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
  const [sources, setSources] = useState<any[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [error, setError] = useState("");
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [confirmText, setConfirmText] = useState("");
  const [confirmAction, setConfirmAction] = useState<null | (() => Promise<void>)>(null);

  async function refresh() {
    if (!token) return;
    try {
      setSources(await api("/sources", "GET", token));
      setNotifications(await api("/notifications", "GET", token));
      setError("");
    } catch (e: any) {
      setError(`Refresh failed: ${e?.message || "Unknown error"}`);
    }
  }

  useEffect(() => {
    if (!token) return;
    refresh();
    const t = setInterval(refresh, 4000);
    return () => clearInterval(t);
  }, [token]);

  async function register(e: FormEvent) {
    e.preventDefault();
    const data = await api("/auth/register", "POST", "", { email, full_name: fullName, password });
    setToken(data.access_token);
  }

  async function login(e: FormEvent) {
    e.preventDefault();
    const data = await api("/auth/login", "POST", "", { email, password });
    setToken(data.access_token);
  }

  async function uploadText() {
    await api("/ingest/text", "POST", token, { title, text });
    await refresh();
  }

  async function uploadUrl() {
    await api("/ingest/url", "POST", token, { title, url });
    await refresh();
  }

  async function uploadFile(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    await api("/ingest/file", "POST", token, formData, true);
    await refresh();
  }

  async function ask() {
    const out = await api("/qa/ask", "POST", token, { question });
    setAnswer(out.answer);
  }

  async function clearNotifications() {
    try {
      await api("/notifications/clear", "DELETE", token);
      await refresh();
      setError("");
    } catch (e: any) {
      setError(`Clear notifications failed: ${e?.message || "Unknown error"}`);
    }
  }

  async function removeSource(sourceId: number) {
    try {
      await api(`/sources/${sourceId}`, "DELETE", token);
      await refresh();
      setError("");
    } catch (e: any) {
      setError(`Delete source failed: ${e?.message || "Unknown error"}`);
    }
  }

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

  return (
    <main>
      <h1>Vectrion RAG</h1>
      <p className="muted">FastAPI + LangChain/LangGraph + Celery + Redis + Postgres</p>
      {error ? <p style={{ color: "#b91c1c", marginTop: 8 }}>{error}</p> : null}

      <div className="grid">
        <section className="card">
          <h3>Auth</h3>
          <form onSubmit={register}>
            <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
            <input value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Full name" />
            <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Password" />
            <button type="submit">Register</button>
          </form>
          <form onSubmit={login}>
            <button type="submit">Login</button>
          </form>
          <p className="muted">Token: {token ? "logged in" : "not logged in"}</p>
        </section>

        <section className="card">
          <h3>Ingest Text/URL/PDF</h3>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" />
          <textarea value={text} onChange={(e) => setText(e.target.value)} />
          <button type="button" onClick={uploadText}>Upload Text</button>
          <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://..." />
          <button type="button" onClick={uploadUrl}>Scrape URL</button>
          <form onSubmit={uploadFile}>
            <input name="title" defaultValue={title} hidden />
            <input name="file" type="file" accept=".pdf" />
            <button type="submit">Upload PDF</button>
          </form>
        </section>

        <section className="card">
          <h3>Ask</h3>
          <textarea value={question} onChange={(e) => setQuestion(e.target.value)} />
          <button type="button" onClick={ask}>Ask Question</button>
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
                  onClick={() => openConfirm("Delete this source from PostgreSQL and vector database?", () => removeSource(s.id))}
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
            onClick={() => openConfirm("Clear all notifications?", clearNotifications)}
          >
            Clear
          </button>
          <ul className="list">
            {notifications.map((n) => (
              <li key={n.id}>{n.title}: {n.message}</li>
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
