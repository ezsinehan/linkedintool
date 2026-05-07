import { useState } from "react";
import styles from "./App.module.css";

const API_BASE = "http://localhost:8000";
const DEFAULT_URL = "https://www.linkedin.com/in/williamhgates/";

type Status =
  | { kind: "idle" }
  | { kind: "scraping" }
  | { kind: "done" }
  | { kind: "error"; message: string };

function App() {
  const [url, setUrl] = useState(DEFAULT_URL);
  const [showBrowser, setShowBrowser] = useState(false);
  const [output, setOutput] = useState("");
  const [status, setStatus] = useState<Status>({ kind: "idle" });
  const [copied, setCopied] = useState(false);

  async function handleScrape() {
    setStatus({ kind: "scraping" });
    setOutput("");
    setCopied(false);
    try {
      const res = await fetch(`${API_BASE}/scrape`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, headless: !showBrowser }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: res.statusText }));
        setStatus({ kind: "error", message: body.detail ?? `HTTP ${res.status}` });
        return;
      }
      const data: { text: string } = await res.json();
      setOutput(data.text);
      setStatus({ kind: "done" });
    } catch (e) {
      const message = e instanceof Error ? e.message : String(e);
      setStatus({ kind: "error", message: `cannot reach backend (${message})` });
    }
  }

  async function handleCopy() {
    if (!output) return;
    await navigator.clipboard.writeText(output);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  const statusLabel = (() => {
    switch (status.kind) {
      case "idle":
        return "ready";
      case "scraping":
        return "scraping…";
      case "done":
        return `done · ${output.length.toLocaleString()} chars`;
      case "error":
        return `error: ${status.message}`;
    }
  })();

  return (
    <main className={styles.app}>
      <header className={styles.header}>
        <h1>linkedintool</h1>
      </header>

      <section className={styles.controls}>
        <input
          className={styles.urlInput}
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://www.linkedin.com/in/..."
          disabled={status.kind === "scraping"}
        />
        <button
          className={styles.primary}
          onClick={handleScrape}
          disabled={status.kind === "scraping" || !url}
        >
          scrape
        </button>
      </section>

      <label className={styles.toggle}>
        <input
          type="checkbox"
          checked={showBrowser}
          onChange={(e) => setShowBrowser(e.target.checked)}
          disabled={status.kind === "scraping"}
        />
        <span>show browser window while scraping</span>
      </label>

      <p className={styles.status} data-kind={status.kind}>
        {statusLabel}
      </p>

      <section className={styles.outputSection}>
        <div className={styles.outputHeader}>
          <span>output</span>
          <button
            className={styles.secondary}
            onClick={handleCopy}
            disabled={!output}
          >
            {copied ? "copied" : "copy"}
          </button>
        </div>
        <pre className={styles.output}>{output || "(no output yet)"}</pre>
      </section>
    </main>
  );
}

export default App;
