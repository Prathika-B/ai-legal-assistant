const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "";

const getHeaders = (token) => {
  const headers = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
};

export const api = {
  async login(email, password) {
    const res = await fetch(`${BACKEND_URL}/login`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(err.detail || "Invalid email or password");
    }
    return res.json();
  },

  async signup(email, password) {
    const res = await fetch(`${BACKEND_URL}/signup`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Signup failed" }));
      throw new Error(err.detail || "Signup failed");
    }
    return res.json();
  },

  async fetchConversations(token) {
    const res = await fetch(`${BACKEND_URL}/conversations`, {
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error("Failed to fetch conversations");
    return res.json();
  },

  async createConversation(token, title = "New chat") {
    const res = await fetch(`${BACKEND_URL}/conversations`, {
      method: "POST",
      headers: getHeaders(token),
      body: JSON.stringify({ title }),
    });
    if (!res.ok) throw new Error("Failed to create conversation");
    return res.json();
  },

  async renameConversation(token, conversationId, title) {
    const res = await fetch(`${BACKEND_URL}/conversations/${conversationId}`, {
      method: "PATCH",
      headers: getHeaders(token),
      body: JSON.stringify({ title }),
    });
    if (!res.ok) throw new Error("Failed to rename conversation");
    return res.json();
  },

  async deleteConversation(token, conversationId) {
    const res = await fetch(`${BACKEND_URL}/conversations/${conversationId}`, {
      method: "DELETE",
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error("Failed to delete conversation");
    return res.json();
  },

  async fetchMessages(token, conversationId) {
    const res = await fetch(`${BACKEND_URL}/conversations/${conversationId}/messages`, {
      headers: getHeaders(token),
    });
    if (!res.ok) throw new Error("Failed to fetch messages");
    return res.json();
  },

  async sendChatMessage(token, conversationId, question) {
    const res = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: getHeaders(token),
      body: JSON.stringify({ conversation_id: conversationId, question }),
    });
    if (!res.ok) throw new Error("Failed to generate AI response");
    return res.json();
  },

  async summarizeDocument(token, file) {
    const formData = new FormData();
    formData.append("file", file);

    const headers = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${BACKEND_URL}/summarize`, {
      method: "POST",
      headers,
      body: formData,
    });
    if (!res.ok) throw new Error("Failed to summarize document");
    return res.json();
  },
};
