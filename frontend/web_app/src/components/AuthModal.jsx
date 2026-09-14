import React, { useState } from "react";
import { Scale, Lock, Mail, AlertCircle, Loader2 } from "lucide-react";

export function AuthModal({ onLogin, onSignup }) {
  const [activeTab, setActiveTab] = useState("login"); // 'login' | 'signup'
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError("Please fill in both email and password.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      if (activeTab === "login") {
        await onLogin(email, password);
      } else {
        await onSignup(email, password);
        setActiveTab("login");
        setError("Account created! Please log in with your credentials.");
      }
    } catch (err) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          <div className="hero-icon" style={{ margin: "0 auto 1rem auto" }}>
            <Scale size={32} />
          </div>
          <h2 className="modal-title">AI Legal Assistant</h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", marginTop: "4px" }}>
            Sign in to access your legal conversations & document analysis
          </p>
        </div>

        <div className="tab-buttons">
          <button
            className={`tab-btn ${activeTab === "login" ? "active" : ""}`}
            onClick={() => {
              setActiveTab("login");
              setError(null);
            }}
          >
            Log In
          </button>
          <button
            className={`tab-btn ${activeTab === "signup" ? "active" : ""}`}
            onClick={() => {
              setActiveTab("signup");
              setError(null);
            }}
          >
            Create Account
          </button>
        </div>

        {error && (
          <div
            style={{
              padding: "0.75rem",
              borderRadius: "8px",
              background: error.includes("created") ? "rgba(16, 185, 129, 0.1)" : "rgba(239, 68, 68, 0.1)",
              border: `1px solid ${error.includes("created") ? "#10b981" : "#ef4444"}`,
              color: error.includes("created") ? "#10b981" : "#f87171",
              fontSize: "0.85rem",
              marginBottom: "1.25rem",
              display: "flex",
              alignItems: "center",
              gap: "8px",
            }}
          >
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <div style={{ position: "relative" }}>
              <input
                type="email"
                className="form-input"
                placeholder="advocate@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <div style={{ position: "relative" }}>
              <input
                type="password"
                className="form-input"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? (
              <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                <Loader2 className="animate-spin" size={18} /> Processing...
              </span>
            ) : activeTab === "login" ? (
              "Sign In to Dashboard"
            ) : (
              "Create Free Account"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
