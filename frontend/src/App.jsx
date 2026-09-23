import { useRef, useState } from "react";

const MAX_PDF_BYTES = 10 * 1024 * 1024;
const API_BASE = import.meta.env.DEV ? "/api" : "";

function DocumentIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M7 2.75h6.7L18.25 7v14.25H7z" />
      <path d="M13.5 2.75V7h4.75M9.5 11h6M9.5 14.5h6M9.5 18h4" />
    </svg>
  );
}

function ArrowIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M5 12h13M13 7l5 5-5 5" />
    </svg>
  );
}

function SourceIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 10.5v5M12 7.5v.1" />
    </svg>
  );
}

function App() {
  const fileInput = useRef(null);
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(false);

  function chooseFile(selectedFile) {
    setError("");
    setResult(null);

    if (!selectedFile) return;
    if (!selectedFile.name.toLowerCase().endsWith(".pdf")) {
      setFile(null);
      setError("Bitte wähle eine PDF-Datei aus.");
      return;
    }
    if (selectedFile.size > MAX_PDF_BYTES) {
      setFile(null);
      setError("Das PDF darf höchstens 10 MiB groß sein.");
      return;
    }

    setFile(selectedFile);
  }

  function handleDrop(event) {
    event.preventDefault();
    setDragging(false);
    chooseFile(event.dataTransfer.files[0]);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const cleanQuestion = question.trim();
    if (!file || !cleanQuestion || loading) return;

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("question", cleanQuestion);

    try {
      const response = await fetch(`${API_BASE}/documents/answer`, {
        method: "POST",
        body: formData,
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(body.detail || "Die Frage konnte nicht beantwortet werden.");
      }
      setResult(body);
    } catch (requestError) {
      setError(
        requestError instanceof TypeError
          ? "Das Backend ist nicht erreichbar. Prüfe, ob FastAPI läuft."
          : requestError.message,
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Jarvis Lite Startseite">
          <span className="brand-mark">J</span>
          <span>Jarvis Lite</span>
        </a>
        <span className="privacy-badge">
          <span className="status-dot" /> Lokale KI
        </span>
      </header>

      <main>
        <section className="intro" aria-labelledby="page-title">
          <p className="eyebrow">Dokumentenassistent</p>
          <h1 id="page-title">
            Frag dein PDF.
            <br />
            <span>Prüf die Quelle.</span>
          </h1>
          <p className="intro-copy">
            Lade ein textbasiertes PDF hoch und erhalte eine kurze Antwort mit
            genauer Seitenangabe und Originaltext.
          </p>
        </section>

        <section className="workspace" aria-label="PDF befragen">
          <form className="question-panel" onSubmit={handleSubmit}>
            <div className="step-heading">
              <span>01</span>
              <div>
                <h2>Dokument auswählen</h2>
                <p>Textbasiertes PDF, maximal 10 MiB</p>
              </div>
            </div>

            <div
              className={`dropzone ${dragging ? "is-dragging" : ""} ${file ? "has-file" : ""}`}
              onClick={() => fileInput.current?.click()}
              onDragEnter={(event) => {
                event.preventDefault();
                setDragging(true);
              }}
              onDragOver={(event) => event.preventDefault()}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  fileInput.current?.click();
                }
              }}
              role="button"
              tabIndex="0"
            >
              <input
                ref={fileInput}
                type="file"
                accept="application/pdf,.pdf"
                onChange={(event) => chooseFile(event.target.files[0])}
                hidden
              />
              <span className="document-icon">
                <DocumentIcon />
              </span>
              {file ? (
                <div className="file-details">
                  <strong>{file.name}</strong>
                  <span>{(file.size / 1024 / 1024).toFixed(2)} MiB · Bereit</span>
                </div>
              ) : (
                <div className="file-details">
                  <strong>PDF hier ablegen</strong>
                  <span>oder zum Auswählen klicken</span>
                </div>
              )}
              <span className="file-action">{file ? "Ändern" : "Auswählen"}</span>
            </div>

            <div className="step-heading question-heading">
              <span>02</span>
              <div>
                <h2>Frage stellen</h2>
                <p>Je genauer die Frage, desto besser die Fundstelle</p>
              </div>
            </div>

            <label className="question-field">
              <span className="sr-only">Frage zum PDF</span>
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Zum Beispiel: Welche Kündigungsfrist wird genannt?"
                rows="4"
                maxLength="500"
              />
              <small>{question.length}/500</small>
            </label>

            {error && (
              <p className="error-message" role="alert">
                {error}
              </p>
            )}

            <button
              className="submit-button"
              type="submit"
              disabled={!file || !question.trim() || loading}
            >
              <span>{loading ? "Dokument wird durchsucht …" : "Antwort finden"}</span>
              {!loading && <ArrowIcon />}
              {loading && <span className="spinner" aria-hidden="true" />}
            </button>
            <p className="processing-note">
              Die erste Antwort kann beim Laden der lokalen Modelle etwas länger dauern.
            </p>
          </form>

          <section className="answer-panel" aria-live="polite" aria-busy={loading}>
            <div className="answer-header">
              <span>03</span>
              <p>Antwort &amp; Quellen</p>
            </div>

            {loading ? (
              <div className="answer-state loading-state">
                <div className="search-animation">
                  <span />
                  <span />
                  <span />
                </div>
                <h2>Ich suche die passende Stelle.</h2>
                <p>Seiten werden verglichen und die Antwort wird formuliert.</p>
              </div>
            ) : result ? (
              <div className="result-content">
                <p className="result-label">Antwort</p>
                <h2>{result.antwort}</h2>

                <div className="sources-heading">
                  <SourceIcon />
                  <span>{result.quellen.length === 1 ? "1 Quelle" : `${result.quellen.length} Quellen`}</span>
                </div>

                {result.quellen.length > 0 ? (
                  <div className="source-list">
                    {result.quellen.map((source, index) => (
                      <article
                        className="source-card"
                        key={`${source.dateiname}-${source.seitenzahl}-${source.abschnitt_nummer}`}
                      >
                        <div className="source-meta">
                          <span>Quelle {index + 1}</span>
                          <span className="relevance">
                            {Math.round(Math.max(0, source.aehnlichkeit) * 100)}% passend
                          </span>
                        </div>
                        <h3>{source.dateiname}</h3>
                        <p className="page-number">Seite {source.seitenzahl}</p>
                        <blockquote>{source.inhalt}</blockquote>
                      </article>
                    ))}
                  </div>
                ) : (
                  <p className="no-source">
                    Zu dieser Frage wurde keine ausreichend passende Stelle gefunden.
                  </p>
                )}
              </div>
            ) : (
              <div className="answer-state empty-state">
                <div className="empty-illustration" aria-hidden="true">
                  <span className="page page-back" />
                  <span className="page page-front">
                    <i />
                    <i />
                    <i />
                  </span>
                  <span className="lens" />
                </div>
                <h2>Deine Antwort erscheint hier.</h2>
                <p>Wähle ein Dokument und stelle deine erste Frage.</p>
              </div>
            )}
          </section>
        </section>
      </main>

      <footer>
        <p>Antworten werden mit Originalstellen aus deinem Dokument belegt.</p>
        <span>Jarvis Lite · Portfolio MVP</span>
      </footer>
    </div>
  );
}

export default App;
