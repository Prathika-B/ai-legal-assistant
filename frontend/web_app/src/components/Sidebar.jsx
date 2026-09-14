import React, { useState } from "react";
import {
  Scale,
  Plus,
  MessageSquare,
  FileText,
  Edit2,
  Trash2,
  Check,
  X,
  LogOut,
  ChevronLeft,
  Sparkles,
} from "lucide-react";

export function Sidebar({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewChat,
  onOpenAnalyzer,
  onRenameConversation,
  onDeleteConversation,
  userEmail,
  onLogout,
  isCollapsed,
  onToggleCollapse,
}) {
  const [editingId, setEditingId] = useState(null);
  const [editTitleText, setEditTitleText] = useState("");
  const [deletingId, setDeletingId] = useState(null);

  const startEditing = (conv, e) => {
    e.stopPropagation();
    setEditingId(conv.id);
    setEditTitleText(conv.title || "New chat");
  };

  const saveRename = (id, e) => {
    e.stopPropagation();
    if (editTitleText.trim()) {
      onRenameConversation(id, editTitleText.trim());
    }
    setEditingId(null);
  };

  const cancelRename = (e) => {
    e.stopPropagation();
    setEditingId(null);
  };

  const confirmDelete = (id, e) => {
    e.stopPropagation();
    setDeletingId(id);
  };

  const handleDelete = (id, e) => {
    e.stopPropagation();
    onDeleteConversation(id);
    setDeletingId(null);
  };

  return (
    <aside className={`sidebar ${isCollapsed ? "collapsed" : ""}`}>
      {/* Sidebar Header */}
      <div className="sidebar-header">
        <div className="brand-container">
          <div className="brand-logo">
            <Scale size={20} />
          </div>
          <div>
            <div className="brand-name">
              AI Legal Assistant
            </div>
          </div>
        </div>

        <button className="icon-button" onClick={onToggleCollapse} title="Collapse sidebar">
          <ChevronLeft size={18} />
        </button>
      </div>

      {/* New Chat Button */}
      <button className="new-chat-btn" onClick={onNewChat}>
        <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <Plus size={18} style={{ color: "var(--accent-gold)" }} />
          New Conversation
        </span>
        <span className="shortcut-pill">Ctrl K</span>
      </button>

      {/* Document Analyzer Navigation Item */}
      <div
        className="sidebar-nav-item"
        onClick={onOpenAnalyzer}
        style={{ margin: "0.5rem 1rem 0.25rem 1rem", border: "1px solid var(--border-subtle)", background: "rgba(226, 198, 108, 0.05)" }}
      >
        <FileText size={18} style={{ color: "var(--accent-gold)" }} />
        <span>Document Analyzer</span>
        <Sparkles size={14} style={{ color: "var(--accent-gold)", marginLeft: "auto" }} />
      </div>

      {/* History List */}
      <div className="sidebar-history-container">
        <div className="history-section-title">Recent Consultations</div>

        {conversations.length === 0 ? (
          <div style={{ padding: "1rem", textAlign: "center", color: "var(--text-muted)", fontSize: "0.82rem" }}>
            No recent chats found. Start a new legal consultation!
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = conv.id === currentConversationId;
            const isEditing = conv.id === editingId;
            const isDeleting = conv.id === deletingId;

            return (
              <div
                key={conv.id}
                className={`chat-history-item ${isActive ? "active" : ""}`}
                onClick={() => onSelectConversation(conv.id)}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "8px", overflow: "hidden", flex: 1 }}>
                  <MessageSquare size={16} style={{ color: isActive ? "var(--accent-gold)" : "var(--text-muted)", flexShrink: 0 }} />

                  {isEditing ? (
                    <input
                      type="text"
                      className="form-input"
                      style={{ padding: "2px 6px", fontSize: "0.82rem", height: "26px" }}
                      value={editTitleText}
                      onChange={(e) => setEditTitleText(e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                      autoFocus
                    />
                  ) : (
                    <span className="chat-title-text">{conv.title || "Untitled Consultation"}</span>
                  )}
                </div>

                <div className="chat-item-actions">
                  {isEditing ? (
                    <>
                      <button className="chat-action-btn" onClick={(e) => saveRename(conv.id, e)} title="Save">
                        <Check size={14} style={{ color: "#10b981" }} />
                      </button>
                      <button className="chat-action-btn" onClick={cancelRename} title="Cancel">
                        <X size={14} style={{ color: "#ef4444" }} />
                      </button>
                    </>
                  ) : isDeleting ? (
                    <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                      <button
                        className="chat-action-btn"
                        onClick={(e) => handleDelete(conv.id, e)}
                        style={{ color: "#ef4444", fontSize: "0.7rem", fontWeight: "700", padding: "2px 6px" }}
                      >
                        Delete?
                      </button>
                      <button className="chat-action-btn" onClick={(e) => { e.stopPropagation(); setDeletingId(null); }}>
                        <X size={14} />
                      </button>
                    </div>
                  ) : (
                    <>
                      <button className="chat-action-btn" onClick={(e) => startEditing(conv, e)} title="Rename chat">
                        <Edit2 size={13} />
                      </button>
                      <button className="chat-action-btn" onClick={(e) => confirmDelete(conv.id, e)} title="Delete chat">
                        <Trash2 size={13} />
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* User Profile Footer */}
      <div className="sidebar-footer">
        <div className="user-profile-card">
          <div className="user-avatar">
            {userEmail ? userEmail.charAt(0).toUpperCase() : "U"}
          </div>
          <div className="user-details">
            <span className="user-email">{userEmail || "User Account"}</span>
            <span className="user-plan">AI Legal Assistant</span>
          </div>
          <button className="logout-btn" onClick={onLogout} title="Log out">
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
}
