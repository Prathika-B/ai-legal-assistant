
import React, { useState, useRef, useEffect } from "react";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import {
  Menu,
  Scale,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  BookOpen,
  FileText,
  User,
} from "lucide-react";

export function ChatArea({
  messages,
  isLoading,
  currentTitle,
  onSelectPromptCard,
  onOpenAnalyzer,
  isSidebarCollapsed,
  onToggleSidebar,
  userEmail,
}) {
  const [copiedIndex, setCopiedIndex] = useState(null);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleCopy = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);

      setTimeout(() => {
        setCopiedIndex(null);
      }, 2000);
    } catch (err) {
      console.error("Copy failed:", err);
    }
  };

  const samplePrompts = [
    {
      icon: "📜",
      title: "BNS vs IPC Criminal Laws",
      desc: "Explain the key differences between BNS 2023 and IPC for theft & offences.",
      prompt:
        "What are the major differences between the new BNS (Bharatiya Nyaya Sanhita) 2023 and the old IPC regarding theft and criminal intimidation?",
    },
    {
      icon: "🛡️",
      title: "Bail Procedure under BNSS",
      desc: "What are the legal procedure rules for bail and filing complaints under BNSS 2023?",
      prompt:
        "What are the procedures for filing complaints and applying for bail under the new BNSS (Bharatiya Nagarik Suraksha Sanhita) 2023?",
    },
    {
      icon: "⚖️",
      title: "Contract & Notice Rules",
      desc: "What is the legal process for issuing legal notices for breach of contract in India?",
      prompt:
        "What is the standard procedure and legal requirements for issuing a Legal Notice for breach of contract in India?",
    },
    {
      icon: "📄",
      title: "PDF Document Analyzer",
      desc: "Upload contracts, agreements or court documents for AI summary & risk analysis.",
      action: "analyzer",
    },
  ];

  return (
    <div className="chat-area">
      {/* Top Header */}
      <header className="top-header">
        <div className="header-left">
          {/* Hamburger on mobile and when sidebar is collapsed */}
          <button
            className={`icon-button menu-toggle-btn ${
              isSidebarCollapsed ? "" : "desktop-only-hidden"
            }`}
            onClick={onToggleSidebar}
            title="Toggle sidebar"
          >
            <Menu size={18} />
          </button>

          <span
            style={{
              fontWeight: 650,
              fontSize: "0.95rem",
              color: "var(--text-primary)",
            }}
          >
            {currentTitle || "New Consultation"}
          </span>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
          }}
        >
          <div className="model-selector">
            <span className="model-dot"></span>
            <span>AI Legal Assistant</span>
          </div>

          <button
            className="icon-button"
            onClick={onOpenAnalyzer}
            title="Analyze PDF Document"
            style={{
              width: "auto",
              padding: "0 10px",
              gap: "6px",
              fontSize: "0.82rem",
            }}
          >
            <FileText
              size={16}
              style={{ color: "var(--accent-gold)" }}
            />
            <span>Analyze PDF</span>
          </button>
        </div>
      </header>

      {/* Messages Stream */}
      <div className="messages-container">
        <div className="chat-wrapper">
          {messages.length === 0 ? (
            /* Welcome Hero View */
            <div className="welcome-hero">
              <div className="hero-icon">
                <Scale size={34} />
              </div>

              <h1 className="hero-title">
                How can I assist you today?
              </h1>

              {/* Prompt Suggestion Cards */}
              <div className="prompt-cards-grid">
                {samplePrompts.map((item, idx) => (
                  <div
                    key={idx}
                    className="prompt-card"
                    onClick={() => {
                      if (item.action === "analyzer") {
                        onOpenAnalyzer();
                      } else {
                        onSelectPromptCard(item.prompt);
                      }
                    }}
                  >
                    <div>
                      <div className="prompt-card-icon">
                        {item.icon}
                      </div>

                      <div className="prompt-card-title">
                        {item.title}
                      </div>

                      <div className="prompt-card-desc">
                        {item.desc}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            /* Message List */
            messages.map((msg, index) => {
              const isUser = msg.role === "user";

              return (
                <div
                  key={index}
                  className="message-bubble-wrapper"
                >
                  <div
                    className={`message-bubble ${
                      isUser ? "user" : "assistant"
                    }`}
                  >
                    <div
                      className={`msg-avatar ${
                        isUser ? "user-av" : "assistant-av"
                      }`}
                    >
                      {isUser ? (
                        userEmail ? (
                          userEmail.charAt(0).toUpperCase()
                        ) : (
                          <User size={16} />
                        )
                      ) : (
                        <Scale size={18} />
                      )}
                    </div>

                    <div className="msg-content">
                      {isUser ? (
                        <div style={{ whiteSpace: "pre-wrap" }}>
                          {msg.content}
                        </div>
                      ) : (
                        <>
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                          >
                            {msg.content}
                          </ReactMarkdown>

                          {/* Source Citations */}
                          {msg.sources &&
                            msg.sources.length > 0 && (
                              <div className="sources-box">
                                <div className="sources-header">
                                  <BookOpen size={14} />
                                  <span>
                                    Retrieved Statutory Context & Acts
                                  </span>
                                </div>

                                <div className="sources-list">
                                  {[...new Set(msg.sources)].map(
                                    (src, sIdx) => (
                                      <span
                                        key={sIdx}
                                        className="source-chip"
                                      >
                                        ⚖️ {src}
                                      </span>
                                    )
                                  )}
                                </div>
                              </div>
                            )}

                          {/* Action Toolbar */}
                          <div className="msg-actions">
                            <button
                              className="action-btn"
                              onClick={() =>
                                handleCopy(msg.content, index)
                              }
                            >
                              {copiedIndex === index ? (
                                <>
                                  <Check
                                    size={14}
                                    style={{ color: "#10b981" }}
                                  />
                                  <span style={{ color: "#10b981" }}>
                                    Copied
                                  </span>
                                </>
                              ) : (
                                <>
                                  <Copy size={14} />
                                  <span>Copy</span>
                                </>
                              )}
                            </button>

                            <button
                              className="action-btn"
                              title="Helpful answer"
                            >
                              <ThumbsUp size={13} />
                            </button>

                            <button
                              className="action-btn"
                              title="Needs improvement"
                            >
                              <ThumbsDown size={13} />
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}

          {/* Loading Pulse Indicator */}
          {isLoading && (
            <div className="message-bubble-wrapper">
              <div className="message-bubble assistant">
                <div className="msg-avatar assistant-av">
                  <Scale size={18} />
                </div>

                <div
                  className="msg-content"
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                  }}
                >
                  <span
                    style={{
                      color: "var(--text-secondary)",
                      fontSize: "0.9rem",
                    }}
                  >
                    Searching Indian Law Corpus & generating response...
                  </span>

                  <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>
    </div>
  );
}