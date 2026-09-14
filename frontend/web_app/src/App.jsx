
import React, { useState, useEffect } from "react";

import { api } from "./services/api";
import { AuthModal } from "./components/AuthModal";
import { Sidebar } from "./components/Sidebar";
import { ChatArea } from "./components/ChatArea";
import { ChatInput } from "./components/ChatInput";
import { DocumentAnalyzerModal } from "./components/DocumentAnalyzerModal";

export default function App() {
  const [token, setToken] = useState(() =>
    localStorage.getItem("legal_ai_token")
  );

  const [userEmail, setUserEmail] = useState(() =>
    localStorage.getItem("legal_ai_email")
  );

  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Sidebar starts collapsed on mobile
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(
    () => window.innerWidth < 768
  );

  const [isAnalyzerOpen, setIsAnalyzerOpen] = useState(false);
  const [composerPrompt, setComposerPrompt] = useState("");

  const isMobile = () => window.innerWidth < 768;

  // Load conversations when logged in
  useEffect(() => {
    if (token) {
      loadConversations();
    }
  }, [token]);

  // Load messages when conversation changes
  useEffect(() => {
    if (token && currentConversationId) {
      loadMessages(currentConversationId);
    } else {
      setMessages([]);
    }
  }, [currentConversationId, token]);

  const loadConversations = async () => {
    try {
      const data = await api.fetchConversations(token);
      setConversations(data || []);
    } catch (err) {
      console.error("Error loading conversations:", err);
    }
  };

  const loadMessages = async (convId) => {
    try {
      const data = await api.fetchMessages(token, convId);
      setMessages(data || []);
    } catch (err) {
      console.error("Error loading messages:", err);
    }
  };

  const handleLogin = async (email, password) => {
    const res = await api.login(email, password);

    setToken(res.access_token);
    setUserEmail(res.email);

    localStorage.setItem("legal_ai_token", res.access_token);
    localStorage.setItem("legal_ai_email", res.email);
  };

  const handleSignup = async (email, password) => {
    await api.signup(email, password);
  };

  const handleLogout = () => {
    setToken(null);
    setUserEmail(null);
    setConversations([]);
    setCurrentConversationId(null);
    setMessages([]);

    localStorage.removeItem("legal_ai_token");
    localStorage.removeItem("legal_ai_email");
  };

  const handleNewChat = () => {
    setCurrentConversationId(null);
    setMessages([]);
    setComposerPrompt("");
  };

  const handleSelectConversation = (convId) => {
    setCurrentConversationId(convId);

    if (isMobile()) {
      setIsSidebarCollapsed(true);
    }
  };

  const handleRenameConversation = async (convId, newTitle) => {
    try {
      await api.renameConversation(token, convId, newTitle);

      setConversations((prev) =>
        prev.map((c) =>
          c.id === convId ? { ...c, title: newTitle } : c
        )
      );
    } catch (err) {
      console.error("Error renaming conversation:", err);
    }
  };

  const handleDeleteConversation = async (convId) => {
    try {
      await api.deleteConversation(token, convId);

      setConversations((prev) =>
        prev.filter((c) => c.id !== convId)
      );

      if (currentConversationId === convId) {
        handleNewChat();
      }
    } catch (err) {
      console.error("Error deleting conversation:", err);
    }
  };

  const handleSendMessage = async (text) => {
    if (!token || !text.trim() || isLoading) return;

    let activeId = currentConversationId;

    setIsLoading(true);

    try {
      // Create a conversation if none is selected
      if (!activeId) {
        const titleSnippet =
          text.length > 30
            ? text.substring(0, 30) + "..."
            : text;

        const newConv = await api.createConversation(
          token,
          titleSnippet
        );

        activeId = newConv.id;

        setCurrentConversationId(activeId);
        setConversations((prev) => [newConv, ...prev]);
      }

      // Add user message immediately
      const userMessage = {
        role: "user",
        content: text,
      };

      setMessages((prev) => [...prev, userMessage]);

      // Send message to FastAPI backend
      const response = await api.sendChatMessage(
        token,
        activeId,
        text
      );

      // Add assistant response
      const assistantMessage = {
        role: "assistant",
        content: response.answer,
        sources: response.sources || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Error sending message:", err);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "❌ Sorry, an error occurred while connecting to the legal assistant engine. Please make sure the FastAPI backend is running.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePromptCardClick = (promptText) => {
    handleSendMessage(promptText);
  };

  const handleSummarizeDocument = async (file) => {
    return await api.summarizeDocument(token, file);
  };

  const currentConv = conversations.find(
    (c) => c.id === currentConversationId
  );

  return (
    <div className="app-container">
      {!token ? (
        <AuthModal
          onLogin={handleLogin}
          onSignup={handleSignup}
        />
      ) : (
        <>
          {/* Mobile sidebar backdrop */}
          {!isSidebarCollapsed && (
            <div
              className="sidebar-backdrop"
              onClick={() => setIsSidebarCollapsed(true)}
            />
          )}

          <Sidebar
            conversations={conversations}
            currentConversationId={currentConversationId}
            onSelectConversation={handleSelectConversation}
            onNewChat={() => {
              handleNewChat();

              if (isMobile()) {
                setIsSidebarCollapsed(true);
              }
            }}
            onOpenAnalyzer={() => {
              setIsAnalyzerOpen(true);

              if (isMobile()) {
                setIsSidebarCollapsed(true);
              }
            }}
            onRenameConversation={handleRenameConversation}
            onDeleteConversation={handleDeleteConversation}
            userEmail={userEmail}
            onLogout={handleLogout}
            isCollapsed={isSidebarCollapsed}
            onToggleCollapse={() =>
              setIsSidebarCollapsed(!isSidebarCollapsed)
            }
          />

          {/* Main content */}
          <main
            className={`main-content ${
              isSidebarCollapsed ? "sidebar-collapsed" : ""
            }`}
          >
            <ChatArea
              messages={messages}
              isLoading={isLoading}
              currentTitle={currentConv?.title}
              onSelectPromptCard={handlePromptCardClick}
              onOpenAnalyzer={() => setIsAnalyzerOpen(true)}
              isSidebarCollapsed={isSidebarCollapsed}
              onToggleSidebar={() =>
                setIsSidebarCollapsed(!isSidebarCollapsed)
              }
              userEmail={userEmail}
            />

            <ChatInput
              onSendMessage={handleSendMessage}
              onOpenAnalyzer={() => setIsAnalyzerOpen(true)}
              isLoading={isLoading}
              initialText={composerPrompt}
            />
          </main>

          <DocumentAnalyzerModal
            isOpen={isAnalyzerOpen}
            onClose={() => setIsAnalyzerOpen(false)}
            onSummarize={handleSummarizeDocument}
          />
        </>
      )}
    </div>
  );
}