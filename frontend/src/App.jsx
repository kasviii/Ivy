import { useState, useEffect, useRef } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";


const API = "http://localhost:8001";
export default function App() {
  const [topic, setTopic] = useState("");
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [papers, setPapers] = useState([]);
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const pollRef = useRef(null);

  const startResearch = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    setResult(null);
    setPapers([]);
    setProgress([]);
    setStatus("queued");

    try {
      const res = await axios.post(`${API}/research`, { topic });
      setJobId(res.data.job_id);
    } catch (err) {
      alert("Failed to start research. Is the API running?");
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!jobId) return;
    pollRef.current = setInterval(async () => {
      try {
        const res = await axios.get(`${API}/research/${jobId}`);
        const job = res.data;
        setStatus(job.status);
        setProgress(job.progress || []);
        if (job.status === "complete") {
          setResult(job.result);
          setPapers(job.papers || []);
          setLoading(false);
          setHistory(h => [{ jobId, topic, result: job.result, papers: job.papers }, ...h.slice(0, 4)]);
          clearInterval(pollRef.current);
        } else if (job.status === "failed") {
          setLoading(false);
          clearInterval(pollRef.current);
        }
      } catch (err) {
        console.error(err);
      }
    }, 2000);
    return () => clearInterval(pollRef.current);
  }, [jobId]);

  const exportMarkdown = () => {
    const blob = new Blob([`# Literature Review: ${topic}\n\n${result}`], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ivy-review-${topic.slice(0, 30).replace(/\s+/g, "-")}.md`;
    a.click();
  };

  const statusColor = {
    queued: "#F59E0B",
    running: "#3B82F6",
    complete: "#10B981",
    failed: "#EF4444",
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0F0F13", color: "#E8E8E8", fontFamily: "'DM Sans', sans-serif" }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet" />

      {/* Header */}
      <header style={{ borderBottom: "1px solid #1E1E2E", padding: "1.25rem 5vw", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <div style={{ width: 32, height: 32, borderRadius: "50%", background: "linear-gradient(135deg, #6366F1, #8B5CF6)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16 }}>🌿</div>
          <span style={{ fontFamily: "'DM Serif Display', serif", fontSize: "1.3rem", color: "#fff" }}>Ivy</span>
          <span style={{ fontSize: "0.72rem", background: "#1E1E2E", color: "#6366F1", padding: "0.2rem 0.6rem", borderRadius: 4, letterSpacing: "0.08em" }}>RESEARCH AGENT</span>
        </div>
        <span style={{ fontSize: "0.8rem", color: "#555" }}>Powered by LangGraph + Groq + sheer luck</span>
      </header>
      

      <main style={{ maxWidth: 860, margin: "0 auto", padding: "3rem 2rem" }}>

        {/* Hero */}
        <div style={{ textAlign: "center", marginBottom: "3rem" }}>
          <h1 style={{ fontFamily: "'DM Serif Display', serif", fontSize: "clamp(2.5rem, 6vw, 4.5rem)", color: "#fff", lineHeight: 1.1, marginBottom: "0.5rem" }}>
            <em style={{ color: "#6366F1", fontStyle: "italic" }}>Ivy</em>
          </h1>
          <p style={{ color: "#888", fontSize: "0.95rem", marginBottom: "1.5rem", letterSpacing: "0.02em" }}>
            your personal autonomous research agent
          </p>
        </div>

        {/* Input */}
        <div style={{ background: "#16161F", border: "1px solid #1E1E2E", borderRadius: 12, padding: "1.5rem", marginBottom: "2rem" }}>
          <div style={{ display: "flex", gap: "0.75rem" }}>
            <input
              value={topic}
              onChange={e => setTopic(e.target.value)}
              onKeyDown={e => e.key === "Enter" && !loading && startResearch()}
              placeholder="e.g. transformer models in medical imaging..."
              style={{
                flex: 1, background: "#0F0F13", border: "1px solid #2A2A3E", borderRadius: 8,
                padding: "0.85rem 1rem", color: "#E8E8E8", fontSize: "0.95rem", outline: "none"
              }}
            />
            <button
              onClick={startResearch}
              disabled={loading || !topic.trim()}
              style={{
                padding: "0.85rem 1.75rem", background: loading ? "#2A2A3E" : "#6366F1",
                color: "#fff", border: "none", borderRadius: 8, cursor: loading ? "not-allowed" : "pointer",
                fontWeight: 500, fontSize: "0.9rem", transition: "background 0.2s", whiteSpace: "nowrap"
              }}
            >
              {loading ? "Researching..." : "Generate Review →"}
            </button>
          </div>

          {/* Status */}
          {status && (
            <div style={{ marginTop: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: statusColor[status] || "#555",
                animation: status === "running" ? "pulse 1.5s infinite" : "none" }} />
              <span style={{ fontSize: "0.82rem", color: statusColor[status] || "#555", textTransform: "capitalize" }}>{status}</span>
              {progress.length > 0 && (
                <span style={{ fontSize: "0.82rem", color: "#555", marginLeft: "0.5rem" }}>
                  — {progress[progress.length - 1]}
                </span>
              )}
            </div>
          )}
        </div>

        {/* Papers found */}
        {papers.length > 0 && (
          <div style={{ marginBottom: "2rem" }}>
            <h3 style={{ fontSize: "0.75rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "#6366F1", marginBottom: "1rem" }}>
              {papers.length} Papers Analyzed
            </h3>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {papers.map((p, i) => (
                <div key={i} style={{ background: "#16161F", border: "1px solid #1E1E2E", borderRadius: 8, padding: "0.85rem 1rem", display: "flex", gap: "1rem", alignItems: "flex-start" }}>
                  <span style={{ fontSize: "0.72rem", background: "#1E1E2E", color: "#6366F1", padding: "0.2rem 0.5rem", borderRadius: 4, flexShrink: 0, marginTop: 2 }}>
                    {p.source === "arxiv" ? "Arxiv" : "S2"}
                  </span>
                  <div>
                    <p style={{ fontSize: "0.88rem", color: "#E8E8E8", margin: 0, lineHeight: 1.4 }}>{p.title}</p>
                    <p style={{ fontSize: "0.78rem", color: "#555", margin: "0.25rem 0 0" }}>
                      {p.authors?.slice(0, 2).join(", ")} {p.year ? `· ${p.year}` : ""}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Result */}
        {result && (
          <div style={{ background: "#16161F", border: "1px solid #1E1E2E", borderRadius: 12, padding: "2rem", marginBottom: "2rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
              <h2 style={{ fontFamily: "'DM Serif Display', serif", fontSize: "1.4rem", color: "#fff", margin: 0 }}>
                Literature Review
              </h2>
              <button
                onClick={exportMarkdown}
                style={{ padding: "0.5rem 1rem", background: "transparent", border: "1px solid #2A2A3E", color: "#6366F1", borderRadius: 6, cursor: "pointer", fontSize: "0.82rem" }}
              >
                Export .md ↓
              </button>
            </div>
            <div style={{ color: "#C8C8D8", lineHeight: 1.8, fontSize: "0.95rem", textAlign: "left" }}>
              <ReactMarkdown>{result}</ReactMarkdown>
            </div>
          </div>
        )}

        {/* History */}
        {history.length > 0 && !result && (
          <div>
            <h3 style={{ fontSize: "0.75rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "#555", marginBottom: "1rem" }}>Recent Reviews</h3>
            {history.map((h, i) => (
              <div key={i} onClick={() => { setResult(h.result); setPapers(h.papers); setTopic(h.topic); }}
                style={{ background: "#16161F", border: "1px solid #1E1E2E", borderRadius: 8, padding: "1rem", marginBottom: "0.5rem", cursor: "pointer" }}>
                <p style={{ margin: 0, fontSize: "0.9rem", color: "#E8E8E8" }}>{h.topic}</p>
              </div>
            ))}
          </div>
        )}
      </main>

      <style>{`
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
        input:focus { border-color: #6366F1 !important; }
        * { box-sizing: border-box; }
      `}</style>
      
    </div>
  );
}