import React, { useState, useRef, useEffect } from "react";
import { Send, Paperclip, Sparkles } from "lucide-react";

export function ChatInput({ onSendMessage, onOpenAnalyzer, isLoading, initialText = "" }) {
  const [text, setText] = useState(initialText);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (initialText) {
      setText(initialText);
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    }
  }, [initialText]);

  const handleTextChange = (e) => {
    setText(e.target.value);
    // Auto-adjust height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submitMessage();
    }
  };

  const submitMessage = () => {
    if (!text.trim() || isLoading) return;
    onSendMessage(text.trim());
    setText("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  return (
    <div className="input-area-container">
      <div className="composer-box">
        <textarea
          ref={textareaRef}
          className="composer-textarea"
          placeholder="Ask any legal question..."
          rows={1}
          value={text}
          onChange={handleTextChange}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />

        <div className="composer-toolbar">
          <div className="toolbar-left">
            <button className="attach-btn" onClick={onOpenAnalyzer} title="Upload & Analyze Legal Document PDF">
              <Paperclip size={18} />
            </button>
            <button className="attach-btn" onClick={onOpenAnalyzer} title="PDF Contract Analyzer" style={{ fontSize: "0.78rem", gap: "4px" }}>
              <Sparkles size={14} style={{ color: "var(--accent-gold)" }} />
              <span style={{ color: "var(--text-secondary)" }}>Analyze PDF</span>
            </button>
          </div>

          <button
            className="send-btn"
            onClick={submitMessage}
            disabled={!text.trim() || isLoading}
            title="Send Message (Enter)"
          >
            <Send size={16} />
          </button>
        </div>
      </div>

      <div className="disclaimer-text">
        AI Legal Assistant provides general educational legal information based on Indian law, not legal advice. Consult a licensed advocate for specific legal counsel.
      </div>
    </div>
  );
}
