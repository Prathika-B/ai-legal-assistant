import React, { useState } from "react";
import {
  FileText,
  UploadCloud,
  X,
  Loader2,
  AlertTriangle,
  BookOpen,
  CheckCircle2,
  HelpCircle,
  FileCheck,
} from "lucide-react";

export function DocumentAnalyzerModal({ isOpen, onClose, onSummarize }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === "application/pdf") {
      setSelectedFile(file);
      setError(null);
    } else {
      setError("Please select a valid PDF file.");
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setError(null);

    try {
      const data = await onSummarize(selectedFile);
      setResult(data);
    } catch (err) {
      setError(err.message || "Failed to analyze document.");
    } finally {
      setLoading(false);
    }
  };

  const resetModal = () => {
    setSelectedFile(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card" style={{ maxWidth: "720px" }}>
        {/* Header */}
        <div className="modal-header">
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div className="brand-logo" style={{ width: "32px", height: "32px", borderRadius: "8px" }}>
              <FileText size={18} />
            </div>
            <div>
              <h2 className="modal-title" style={{ fontSize: "1.15rem" }}>Legal Document AI Analyzer</h2>
              <p style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>
                Extract key clauses, plain language summaries, legal terms, and risk flags from PDF contracts or notices.
              </p>
            </div>
          </div>

          <button className="close-btn" onClick={() => { resetModal(); onClose(); }}>
            <X size={20} />
          </button>
        </div>

        {error && (
          <div
            style={{
              padding: "0.75rem",
              borderRadius: "8px",
              background: "rgba(239, 68, 68, 0.1)",
              border: "1px solid #ef4444",
              color: "#f87171",
              fontSize: "0.85rem",
              marginBottom: "1rem",
            }}
          >
            {error}
          </div>
        )}

        {!result ? (
          /* Upload View */
          <div>
            <div
              style={{
                border: "2px dashed var(--border-subtle)",
                borderRadius: "var(--radius-md)",
                padding: "2.5rem 1.5rem",
                textAlign: "center",
                background: "var(--bg-primary)",
                cursor: "pointer",
                position: "relative",
              }}
            >
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                style={{
                  position: "absolute",
                  inset: 0,
                  opacity: 0,
                  cursor: "pointer",
                  width: "100%",
                  height: "100%",
                }}
              />
              <UploadCloud size={44} style={{ color: "var(--accent-gold)", marginBottom: "0.85rem" }} />
              <div style={{ fontWeight: 600, fontSize: "0.95rem", color: "var(--text-primary)" }}>
                {selectedFile ? selectedFile.name : "Click or drag PDF legal document here"}
              </div>
              <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "6px" }}>
                Supports contracts, court orders, legal notices, and agreements (PDF up to 15MB)
              </div>
            </div>

            {selectedFile && (
              <div style={{ marginTop: "1.25rem", display: "flex", gap: "10px", justifyContent: "flex-end" }}>
                <button
                  className="tab-btn"
                  onClick={resetModal}
                  style={{ width: "auto", padding: "0.6rem 1.2rem", background: "var(--bg-primary)" }}
                >
                  Cancel
                </button>
                <button
                  className="submit-btn"
                  onClick={handleUpload}
                  disabled={loading}
                  style={{ width: "auto", padding: "0.6rem 1.4rem", marginTop: 0 }}
                >
                  {loading ? (
                    <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <Loader2 className="animate-spin" size={18} /> Analyzing Document...
                    </span>
                  ) : (
                    "Run AI Legal Breakdown"
                  )}
                </button>
              </div>
            )}
          </div>
        ) : (
          /* Structured Result Dashboard */
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <span style={{ fontSize: "0.85rem", color: "var(--accent-gold)", fontWeight: 700 }}>
                ✓ Document Analysis Complete ({selectedFile?.name})
              </span>
              <button
                className="action-btn"
                onClick={resetModal}
                style={{ border: "1px solid var(--border-subtle)", padding: "4px 10px" }}
              >
                Analyze Another PDF
              </button>
            </div>

            <div className="summary-container">
              {/* Summary */}
              {result.summary && (
                <div className="summary-card-section">
                  <div className="section-badge">
                    <FileCheck size={16} /> Plain Language Summary
                  </div>
                  <p style={{ fontSize: "0.9rem", color: "var(--text-primary)", lineHeight: 1.6 }}>{result.summary}</p>
                </div>
              )}

              {/* Key Points */}
              {result.key_points && result.key_points.length > 0 && (
                <div className="summary-card-section">
                  <div className="section-badge">
                    <CheckCircle2 size={16} /> Key Points
                  </div>
                  <ul style={{ paddingLeft: "1.2rem", color: "var(--text-secondary)", fontSize: "0.88rem" }}>
                    {result.key_points.map((pt, idx) => (
                      <li key={idx} style={{ marginBottom: "4px" }}>
                        {pt}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Key Clauses */}
              {result.key_clauses && result.key_clauses.length > 0 && (
                <div className="summary-card-section">
                  <div className="section-badge">
                    <BookOpen size={16} /> Important Clauses
                  </div>
                  <ul style={{ paddingLeft: "1.2rem", color: "var(--text-secondary)", fontSize: "0.88rem" }}>
                    {result.key_clauses.map((clause, idx) => (
                      <li key={idx} style={{ marginBottom: "4px" }}>
                        {clause}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Legal Terms Glossary */}
              {result.legal_terms && result.legal_terms.length > 0 && (
                <div className="summary-card-section">
                  <div className="section-badge">
                    <HelpCircle size={16} /> Legal Terms Glossary
                  </div>
                  <div style={{ display: "grid", gap: "8px" }}>
                    {result.legal_terms.map((termItem, idx) => (
                      <div key={idx} style={{ padding: "8px 10px", background: "var(--bg-card)", borderRadius: "6px" }}>
                        <strong style={{ color: "var(--accent-gold)", fontSize: "0.85rem" }}>{termItem.term}: </strong>
                        <span style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>{termItem.meaning}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Risks */}
              {result.risks && result.risks.length > 0 && (
                <div className="summary-card-section" style={{ borderColor: "rgba(239, 68, 68, 0.3)", background: "rgba(239, 68, 68, 0.04)" }}>
                  <div className="section-badge" style={{ color: "#ef4444" }}>
                    <AlertTriangle size={16} /> Potential Risks & Red Flags
                  </div>
                  <ul style={{ paddingLeft: "1.2rem", color: "#f87171", fontSize: "0.88rem" }}>
                    {result.risks.map((risk, idx) => (
                      <li key={idx} style={{ marginBottom: "4px" }}>
                        {risk}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
