"use client";

import { useEffect, useState } from "react";
import { formatCitationLabel } from "../lib/citations";

export default function Page() {
  const [message, setMessage] = useState("Where do mystery novels stay?");
  const [turns, setTurns] = useState([]);
  const [shelf, setShelf] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/backend/documents")
      .then((response) => response.json())
      .then((body) => setShelf(body.documents || []))
      .catch(() => setShelf([]));
  }, []);

  async function onSubmit(event) {
    event.preventDefault();
    const question = message.trim();
    if (!question || busy) return;
    setBusy(true);
    setError("");
    setMessage("");
    setTurns((prev) => [
      ...prev,
      { role: "user", text: question },
      { role: "assistant", text: "", citations: [] },
    ]);

    try {
      const response = await fetch("/backend/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question }),
      });
      if (!response.ok || !response.body) {
        throw new Error("The shelf assistant did not answer.");
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const blocks = buffer.split("\n\n");
        buffer = blocks.pop() || "";
        for (const block of blocks) {
          const line = block
            .split("\n")
            .find((item) => item.startsWith("data:"));
          if (!line) continue;
          const data = line.slice(5).trim();
          if (data === "[DONE]") continue;
          const payload = JSON.parse(data);
          setTurns((prev) => {
            const next = [...prev];
            const last = { ...next[next.length - 1] };
            if (payload.token) last.text += payload.token;
            if (payload.citations) last.citations = payload.citations;
            next[next.length - 1] = last;
            return next;
          });
        }
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <h1>BookNook shelf assistant</h1>
      <p className="lede">
        A demo reading-room chat. Answers come from the sample notes, with the
        passage that supported them.
      </p>
      <div className="shelf">
        {shelf.map((doc) => (
          <span key={doc.id}>{doc.title}</span>
        ))}
      </div>
      <div className="log">
        {turns.map((turn, index) => (
          <article key={index} className={`bubble ${turn.role}`}>
            <p>{turn.text}</p>
            {turn.citations?.length ? (
              <div className="citations">
                {turn.citations.map((item) => (
                  <span className="cite" key={item.marker} title={item.quote}>
                    {formatCitationLabel(item)}
                  </span>
                ))}
              </div>
            ) : null}
          </article>
        ))}
      </div>
      <form onSubmit={onSubmit}>
        <input
          aria-label="Question"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Ask about hours, fees, or the lectern copy"
        />
        <button type="submit" disabled={busy}>
          {busy ? "Reading…" : "Ask"}
        </button>
      </form>
      {error ? <p>{error}</p> : null}
    </main>
  );
}
