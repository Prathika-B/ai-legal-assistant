import textwrap
import streamlit as st
import requests

# ============================================================
# AI LEGAL ASSISTANT - PREMIUM STREAMLIT FRONTEND
# ============================================================

st.set_page_config(
    page_title="AI Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = "http://127.0.0.1:8000"
ASSISTANT_AVATAR = "⚖️"

# ============================================================
# PREMIUM UI STYLING
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background: #0b0f17;
    }

    .main .block-container {
        max-width: 1180px;
        padding: 2rem 2.5rem 8rem 2.5rem;
    }


    /* ============================================================
       SIDEBAR — fixed header/footer, scrollable recent chats only
       ============================================================ */
    [data-testid="stSidebar"] {
        background: #0b0b0c !important;
        border-right: 1px solid #26262a !important;
        min-width: 270px !important;
        max-width: 270px !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        display: flex !important;
        flex-direction: column !important;
        height: 100vh !important;
        padding: 0.75rem 0.55rem 0.55rem 0.55rem !important;
        overflow: hidden !important;
    }

    /* Everything except the conversation list keeps its natural size... */
    [data-testid="stSidebar"] > div:first-child > * {
        flex: 0 0 auto;
    }

    /* ...and the conversation list is the only part that grows/scrolls,
       which keeps the profile + logout footer permanently visible. */
    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
        flex: 1 1 auto !important;
        min-height: 0 !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] > div {
        height: 100% !important;
        overflow-y: auto !important;
    }

    [data-testid="stSidebar"] * {
        color: #f3f4f6;
    }

    .brand {
        padding: 0.25rem 0.45rem 0.75rem 0.45rem;
    }

    .brand-icon {
        display: inline-flex;
        width: 32px;
        height: 32px;
        align-items: center;
        justify-content: center;
        border-radius: 9px;
        background: linear-gradient(135deg, #e3c76b, #a47b20);
        color: #111827;
        font-size: 18px;
        margin-right: 8px;
        vertical-align: middle;
    }

    .brand-title {
        font-size: 17px;
        font-weight: 750;
        color: #ffffff;
        vertical-align: middle;
    }

    .brand-subtitle {
        margin: 7px 0 0 40px;
        color: #8d96a5;
        font-size: 11px;
    }

    .user-chip {
        margin: 0.2rem 0 0.65rem 0;
        padding: 9px 10px;
        border: 1px solid #30343d;
        border-radius: 10px;
        background: #111318;
        color: #b8bec9;
        font-size: 11px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    [data-testid="stSidebar"] .stButton > button {
        min-height: 36px !important;
        border-radius: 9px !important;
        border: 1px solid #30343d !important;
        background: #15171d !important;
        color: #f3f4f6 !important;
        font-size: 12px !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: #202228 !important;
        border-color: #565b66 !important;
    }

    .section-label {
        color: #8d96a5;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.25px;
        margin: 1rem 0 0.45rem 0.35rem;
    }

    /* Only this Streamlit container should scroll. */
    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #30343d !important;
        border-radius: 9px !important;
        background: #0f1116 !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 0.25rem !important;
    }

    [data-testid="stSidebar"] button[kind="tertiary"] {
        border: 0 !important;
        background: transparent !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 7px 8px !important;
        min-height: 32px !important;
        border-radius: 7px !important;
        font-size: 11px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    [data-testid="stSidebar"] button[kind="tertiary"]:hover {
        background: #202228 !important;
    }

    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
        gap: 0.05rem !important;
        margin-bottom: 1px !important;
    }

    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button {
        font-size: 11px !important;
    }

    [data-testid="stSidebar"] [data-testid="stPopover"] > div > button {
        min-width: 25px !important;
        width: 25px !important;
        height: 27px !important;
        padding: 0 !important;
        border-radius: 6px !important;
        background: transparent !important;
        border: 0 !important;
        font-size: 12px !important;
    }

    [data-testid="stSidebar"] [data-testid="stPopover"] svg {
        display: none !important;
    }

    [data-testid="stSidebar"] [data-testid="stPopover"] > div > button:hover {
        background: #202228 !important;
    }

    [data-testid="stSidebar"] [data-testid="stPopoverBody"] {
        min-width: 135px !important;
        width: 135px !important;
        padding: 3px !important;
    }

    [data-testid="stSidebar"] [data-testid="stPopoverBody"] button[kind="tertiary"] {
        font-size: 10px !important;
        min-height: 26px !important;
        height: 26px !important;
        padding: 4px 7px !important;
        border-radius: 5px !important;
        justify-content: flex-start !important;
    }

    .sidebar-bottom {
        padding-top: 0.6rem;
        border-top: 1px solid #292c33;
        margin-top: 0.65rem;
    }

    .avatar-circle {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #e3c76b, #a47b20);
        color: #111827;
        font-size: 13px;
        font-weight: 750;
        margin-top: 2px;
    }


    /* ============================================================
       PROFILE FOOTER / ACCOUNT MENU
       ============================================================ */
    .profile-footer {
        margin-top: 0.7rem;
        padding-top: 0.65rem;
        border-top: 1px solid #292c33;
    }

    .profile-footer [data-testid="stButton"] > button {
        min-height: 52px !important;
        height: 52px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 7px 10px !important;
        border: 1px solid transparent !important;
        background: transparent !important;
        border-radius: 10px !important;
        font-size: 12px !important;
        line-height: 1.2 !important;
    }

    .profile-footer [data-testid="stButton"] > button:hover {
        background: #202228 !important;
        border-color: #30343d !important;
    }

    .profile-menu {
        background: #303030;
        border: 1px solid #4a4a4a;
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 8px;
        color: #f4f4f5;
    }

    .profile-menu .profile-name {
        font-size: 13px;
        font-weight: 650;
    }

    .profile-menu .profile-plan {
        color: #b8b8b8;
        font-size: 11px;
        margin-top: 2px;
    }

    .profile-menu .menu-divider {
        height: 1px;
        background: #505050;
        margin: 10px 0;
    }

    .profile-menu .menu-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 4px;
        font-size: 12px;
        color: #f4f4f5;
    }

    .profile-menu .menu-item .menu-icon {
        width: 20px;
        text-align: center;
        color: #e5e7eb;
    }

    .profile-footer [data-testid="stPopover"] > div > button {
        min-height: 46px !important;
        height: 46px !important;
        width: 100% !important;
        justify-content: flex-start !important;
        text-align: left !important;
        padding: 5px 10px !important;
        border: 1px solid transparent !important;
        background: transparent !important;
        border-radius: 10px !important;
        font-size: 12px !important;
        white-space: pre-line !important;
        line-height: 1.35 !important;
    }

    .profile-footer [data-testid="stPopover"] > div > button p {
        white-space: pre-line !important;
        line-height: 1.35 !important;
        margin: 0 !important;
    }

    .profile-footer [data-testid="stHorizontalBlock"] {
        align-items: center !important;
        gap: 0.4rem !important;
    }

    .profile-footer [data-testid="stPopover"] > div > button:hover {
        background: #202228 !important;
        border-color: #30343d !important;
    }

    .profile-footer [data-testid="stPopoverBody"] {
        width: 230px !important;
        min-width: 230px !important;
        padding: 5px !important;
        background: #303030 !important;
        border: 1px solid #4a4a4a !important;
        border-radius: 16px !important;
    }

    .profile-footer [data-testid="stPopoverBody"] button {
        min-height: 34px !important;
        height: 34px !important;
        border-radius: 8px !important;
        font-size: 12px !important;
        justify-content: flex-start !important;
        text-align: left !important;
        padding: 6px 9px !important;
    }

    .profile-footer [data-testid="stPopoverBody"] button:hover {
        background: #414141 !important;
    }

    /* LOG OUT MENU ITEM */
    .profile-footer [data-testid="stPopoverBody"] button[kind="secondary"] {
        min-height: 34px !important;
        height: 34px !important;
        width: 100% !important;
        border-radius: 8px !important;
        font-size: 12px !important;
        justify-content: flex-start !important;
        text-align: left !important;
        padding: 6px 9px !important;
        background: transparent !important;
        border: 0 !important;
        color: #f4f4f5 !important;
    }

    .profile-footer [data-testid="stPopoverBody"] button[kind="secondary"]:hover {
        background: #414141 !important;
        color: #ffffff !important;
    }

    .sidebar-disclaimer {
        color: #737b89;
        font-size: 9px;
        line-height: 1.45;
        padding: 0.6rem 0.35rem 0;
    }

    .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.8rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #202938;
    }

    .topbar-title {
        color: #f8fafc;
        font-size: 15px;
        font-weight: 650;
    }

    .online {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        color: #9ca3af;
        font-size: 12px;
    }

    .online-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #52c98a;
        box-shadow: 0 0 10px rgba(82, 201, 138, 0.45);
    }

    .welcome {
        text-align: center;
        padding: 3.4rem 1rem 1.5rem 1rem;
    }

    .welcome-icon {
        width: 68px;
        height: 68px;
        margin: 0 auto 1.2rem auto;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 21px;
        background: linear-gradient(135deg, #e2c66c, #a47c20);
        color: #111827;
        font-size: 34px;
        box-shadow: 0 14px 45px rgba(202, 166, 76, 0.12);
    }

    .welcome h1 {
        color: #f8fafc;
        font-size: clamp(28px, 4vw, 42px);
        line-height: 1.1;
        margin: 0;
        letter-spacing: -1px;
    }

    .welcome p {
        max-width: 650px;
        margin: 14px auto 0 auto;
        color: #9ca3af;
        font-size: 15px;
        line-height: 1.65;
    }

    .tagline {
        color: #d6b45c !important;
        font-size: 13px !important;
        font-weight: 650;
        margin-top: 10px !important;
    }

    [data-testid="stChatMessage"] {
        border: 1px solid #222c3a;
        border-radius: 18px;
        padding: 1rem 1.1rem;
        margin: 0.75rem 0;
        background: #111824;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: #171f2c;
        border-color: #273345;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: #101722;
        border-color: #252f3e;
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {
        color: #dbe3ee;
        line-height: 1.65;
    }

    [data-testid="stChatMessage"] h1,
    [data-testid="stChatMessage"] h2,
    [data-testid="stChatMessage"] h3 {
        color: #f8fafc;
    }

    .source-box {
        margin-top: 12px;
        padding: 11px 13px;
        border-radius: 11px;
        background: #0c121c;
        border: 1px solid #263142;
    }

    .source-title {
        color: #d6b45c;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }

    .source-item {
        color: #8995a7;
        font-size: 11px;
        line-height: 1.5;
        padding: 2px 0;
    }

    [data-testid="stChatInput"] {
        background: #111722;
    }


    /* ============================================================
       CHAT COMPOSER
       ============================================================ */
    [data-testid="stChatInput"] {
        background: transparent !important;
        padding: 0 !important;
    }

    [data-testid="stChatInput"] > div {
        background: #17191f !important;
        border: 1px solid #343842 !important;
        border-radius: 15px !important;
        padding: 3px !important;
        box-shadow: none !important;
    }

    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        border: 0 !important;
        color: #f5f5f5 !important;
        min-height: 44px !important;
        max-height: 110px !important;
        padding: 12px 44px 8px 13px !important;
        font-size: 13px !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #8e96a5 !important;
        opacity: 1 !important;
    }

    [data-testid="stChatInput"] textarea:focus {
        border: 0 !important;
        box-shadow: none !important;
        outline: none !important;
    }

    [data-testid="stChatInput"] button {
        border-radius: 9px !important;
    }

    .disclaimer {
        text-align: center;
        color: #626d7e;
        font-size: 10px;
        line-height: 1.5;
        margin: 1rem auto 0 auto;
        max-width: 720px;
    }

    .login-wrap {
        max-width: 420px;
        margin: 6vh auto 1.4rem auto;
        padding: 1.5rem 1.8rem;
        background: #111824;
        border: 1px solid #263142;
        border-radius: 20px;
        box-shadow: 0 20px 70px rgba(0, 0, 0, 0.22);
    }

    .login-logo {
        text-align: center;
        margin-bottom: 1.2rem;
    }

    .login-logo-icon {
        display: inline-flex;
        width: 66px;
        height: 66px;
        align-items: center;
        justify-content: center;
        border-radius: 20px;
        background: linear-gradient(135deg, #e2c66c, #a47c20);
        font-size: 32px;
        color: #111827;
    }

    .login-title {
        text-align: center;
        color: #f8fafc;
        font-size: 27px;
        font-weight: 750;
        margin-top: 14px;
    }

    .login-subtitle {
        text-align: center;
        color: #8d98a8;
        font-size: 13px;
        margin-bottom: 1.4rem;
    }

    .stButton > button {
        transition: all 0.15s ease;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    @media (max-width: 800px) {
        .main .block-container {
            padding: 1rem 1rem 7rem 1rem;
        }

        .welcome {
            padding-top: 2rem;
        }

        .welcome h1 {
            font-size: 29px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "access_token": None,
    "user_email": None,
    "current_conversation_id": None,
    "messages": [],
    "last_sources": {},
    "renaming_id": None,
    "confirming_delete_id": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# API HELPERS
# ============================================================

def auth_headers():
    return {
        "Authorization": f"Bearer {st.session_state.access_token}"
    }


def api_request(method, path, **kwargs):
    try:
        timeout = kwargs.pop("timeout", 30)

        resp = requests.request(
            method,
            f"{BACKEND_URL}{path}",
            timeout=timeout,
            **kwargs,
        )

        if resp.status_code == 401:
            st.session_state.access_token = None
            st.session_state.user_email = None
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.warning("Your session has expired. Please log in again.")
            st.rerun()

        resp.raise_for_status()
        return resp

    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Could not connect to the backend. "
            f"Make sure your FastAPI server is running at {BACKEND_URL}."
        )
    except requests.exceptions.Timeout:
        raise TimeoutError(
            "The backend took too long to respond. Please try again."
        )
    except requests.exceptions.RequestException as e:
        raise e


def load_conversations():
    resp = api_request("GET", "/conversations", headers=auth_headers())
    return resp.json()


def load_messages(conversation_id):
    resp = api_request("GET", f"/conversations/{conversation_id}/messages", headers=auth_headers())
    return resp.json()


def create_conversation(title):
    resp = api_request("POST", "/conversations", json={"title": title}, headers=auth_headers())
    return resp.json()


def rename_conversation(conversation_id, title):
    api_request("PATCH", f"/conversations/{conversation_id}", json={"title": title}, headers=auth_headers())


def delete_conversation(conversation_id):
    api_request("DELETE", f"/conversations/{conversation_id}", headers=auth_headers())


def save_message(conversation_id, role, content):
    api_request(
        "POST",
        f"/conversations/{conversation_id}/save_message",
        json={"role": role, "content": content},
        headers=auth_headers(),
    )


def make_title(text, max_len=40):
    text = text.strip()
    if not text:
        return "New chat"
    return (text[:max_len] + "…") if len(text) > max_len else text


def start_new_chat():
    st.session_state.current_conversation_id = None
    st.session_state.messages = []
    st.session_state.last_sources = {}
    st.session_state.renaming_id = None
    st.session_state.confirming_delete_id = None


# ============================================================
# LOGIN / SIGNUP
# ============================================================

if not st.session_state.access_token:

    _, login_col, _ = st.columns([1, 1.3, 1])

    with login_col:
        st.markdown(
            """
            <div class="login-wrap">
                <div class="login-logo">
                    <div class="login-logo-icon">⚖️</div>
                </div>
                <div class="login-title">AI Legal Assistant</div>
                <div class="login-subtitle">
                    Understand legal information with a smarter, simpler assistant.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_signup = st.tabs(["🔐  Log In", "✨  Create Account"])

        with tab_login:
            with st.form("login_form"):
                login_email = st.text_input("Email", placeholder="you@example.com")
                login_password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Log In", use_container_width=True)

            if submitted:
                if not login_email or not login_password:
                    st.warning("Please enter both email and password.")
                else:
                    try:
                        resp = requests.post(
                            f"{BACKEND_URL}/login",
                            json={"email": login_email, "password": login_password},
                            timeout=30,
                        )
                        resp.raise_for_status()
                        data = resp.json()
                        st.session_state.access_token = data["access_token"]
                        st.session_state.user_email = data["email"]
                        st.rerun()
                    except requests.exceptions.ConnectionError:
                        st.error(f"Backend is not reachable. Start your FastAPI server at {BACKEND_URL}.")
                    except Exception as e:
                        st.error(f"Login failed: {e}")

        with tab_signup:
            with st.form("signup_form"):
                signup_email = st.text_input("Email", key="signup_email", placeholder="you@example.com")
                signup_password = st.text_input("Password", type="password", key="signup_password", placeholder="Create a password")
                signup_submitted = st.form_submit_button("Create Account", use_container_width=True)

            if signup_submitted:
                if not signup_email or not signup_password:
                    st.warning("Please enter both email and password.")
                else:
                    try:
                        resp = requests.post(
                            f"{BACKEND_URL}/signup",
                            json={"email": signup_email, "password": signup_password},
                            timeout=30,
                        )
                        resp.raise_for_status()
                        st.success("Account created successfully. You can now log in.")
                    except requests.exceptions.ConnectionError:
                        st.error(f"Backend is not reachable. Start your FastAPI server at {BACKEND_URL}.")
                    except Exception as e:
                        st.error(f"Signup failed: {e}")

        st.markdown(
            """
            <div class="disclaimer">
                ⚠️ AI-generated information is for general informational purposes only
                and does not constitute legal advice.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.stop()


# ============================================================
# LOAD CONVERSATIONS
# ============================================================

try:
    all_conversations = load_conversations()
    backend_error = None
except Exception as e:
    all_conversations = []
    backend_error = str(e)

# Hide legacy empty "New chat" rows left over from before lazy conversation creation existed
conversations = [c for c in all_conversations if (c.get("title") or "New chat") != "New chat"]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # Fixed top section
    st.markdown(
        """
        <div class="brand">
            <span class="brand-icon">⚖️</span>
            <span class="brand-title">Legal AI</span>
            <div class="brand-subtitle">Your intelligent legal assistant</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="user-chip">👤 {st.session_state.user_email}</div>',
        unsafe_allow_html=True,
    )

    if st.button("＋  New Conversation", use_container_width=True):
        start_new_chat()
        st.rerun()

    st.markdown(
        '<div class="section-label">RECENT CONVERSATIONS</div>',
        unsafe_allow_html=True,
    )

    # Only the recent-conversation list scrolls (see CSS: this wrapper is
    # given flex:1 so it fills the space between the header and the
    # always-visible profile/logout footer below).
    chat_list_area = st.container(height=1, border=False)

    with chat_list_area:
        for conv in conversations:
            conv_id = conv["id"]
            is_active = conv_id == st.session_state.current_conversation_id

            if st.session_state.renaming_id == conv_id:
                new_name = st.text_input(
                    "Rename",
                    value=conv.get("title", ""),
                    key=f"rename_box_{conv_id}",
                    label_visibility="collapsed",
                )
                rc1, rc2 = st.columns(2)
                with rc1:
                    if st.button("Save", key=f"save_{conv_id}", use_container_width=True):
                        if new_name.strip():
                            rename_conversation(conv_id, make_title(new_name))
                        st.session_state.renaming_id = None
                        st.rerun()
                with rc2:
                    if st.button("Cancel", key=f"cancel_r_{conv_id}", use_container_width=True):
                        st.session_state.renaming_id = None
                        st.rerun()
                continue

            if st.session_state.confirming_delete_id == conv_id:
                st.caption(f'Delete "{conv.get("title", "conversation")}"?')
                dc1, dc2 = st.columns(2)
                with dc1:
                    if st.button("Delete", key=f"confirm_d_{conv_id}", use_container_width=True):
                        delete_conversation(conv_id)
                        if is_active:
                            start_new_chat()
                        st.session_state.confirming_delete_id = None
                        st.rerun()
                with dc2:
                    if st.button("Cancel", key=f"cancel_d_{conv_id}", use_container_width=True):
                        st.session_state.confirming_delete_id = None
                        st.rerun()
                continue

            title = conv.get("title") or "New chat"
            display_title = ("● " if is_active else "") + title

            col_title, col_menu = st.columns([8, 1], gap="small")
            with col_title:
                if st.button(
                    display_title,
                    key=f"open_{conv_id}",
                    use_container_width=True,
                    type="tertiary",
                ):
                    st.session_state.current_conversation_id = conv_id
                    st.session_state.messages = load_messages(conv_id)
                    st.session_state.last_sources = {}
                    st.session_state.renaming_id = None
                    st.session_state.confirming_delete_id = None
                    st.rerun()

            with col_menu:
                with st.popover("⋯", use_container_width=False):
                    if st.button(
                        "Rename",
                        key=f"menu_rn_{conv_id}",
                        type="tertiary",
                        use_container_width=True,
                    ):
                        st.session_state.renaming_id = conv_id
                        st.rerun()

                    if st.button(
                        "Delete",
                        key=f"menu_del_{conv_id}",
                        type="tertiary",
                        use_container_width=True,
                    ):
                        st.session_state.confirming_delete_id = conv_id
                        st.rerun()

    # Fixed bottom profile section, outside the scrollable conversation list.
    st.markdown('<div class="sidebar-bottom"></div>', unsafe_allow_html=True)

    st.markdown('<div class="profile-footer">', unsafe_allow_html=True)

    user_initial = (st.session_state.user_email or "?").strip()[0].upper()

    col_avatar, col_trigger = st.columns([1, 5], gap="small")

    with col_avatar:
        st.markdown(f'<div class="avatar-circle">{user_initial}</div>', unsafe_allow_html=True)

    with col_trigger:
        with st.popover(
            f"{st.session_state.user_email}\nFree",
            use_container_width=True,
        ):
            profile_menu_html = f"""
                <div class="profile-menu">
                    <div class="profile-name">
                        {st.session_state.user_email}
                    </div>
                    <div class="profile-plan">Free plan</div>

                    <div class="menu-divider"></div>

                    <div class="menu-item">
                        <span class="menu-icon">⚙</span>
                        Settings
                    </div>

                    <div class="menu-item">
                        <span class="menu-icon">◎</span>
                        Get help
                    </div>

                    <div class="menu-divider"></div>
                </div>
                """
            st.markdown(textwrap.dedent(profile_menu_html).strip(), unsafe_allow_html=True)

            # LOG OUT — always the last item, mirroring the Claude sidebar menu.
            if st.button(
                "↪  Log out",
                key="profile_logout",
                use_container_width=True,
                type="secondary",
            ):
                st.session_state.access_token = None
                st.session_state.user_email = None
                st.session_state.current_conversation_id = None
                st.session_state.messages = []
                st.session_state.last_sources = {}
                st.session_state.renaming_id = None
                st.session_state.confirming_delete_id = None
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="sidebar-disclaimer">
            ⚠️ General legal information only. Not legal advice.
            Consult a licensed lawyer for your specific situation.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    """
    <div class="topbar">
        <div class="topbar-title">⚖️ AI Legal Assistant</div>
        <div class="online">
            <span class="online-dot"></span>
            Assistant ready
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# WELCOME SCREEN (no suggestion cards)
# ============================================================

if not st.session_state.messages:
    st.markdown(
        """
        <div class="welcome">
            <div class="welcome-icon">⚖️</div>
            <h1>How can I help you today?</h1>
            <p class="tagline">Understand the law. Understand your rights.</p>
            <p>
                Ask a question about legal topics, or use the attach button
                in the message box to upload a PDF for a clear, structured summary.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DISPLAY EXISTING CHAT
# ============================================================

for i, message in enumerate(st.session_state.messages):
    role = message["role"]
    avatar = ASSISTANT_AVATAR if role == "assistant" else "👤"

    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

        if i in st.session_state.last_sources:
            sources = st.session_state.last_sources[i]
            source_html = f"""
                <div class="source-box">
                    <div class="source-title">📚 SOURCES USED · {len(sources)}</div>
                    {''.join(f'<div class="source-item">• {s}</div>' for s in sources)}
                </div>
                """
            st.markdown(textwrap.dedent(source_html).strip(), unsafe_allow_html=True)


# ============================================================
# QUESTION / DOCUMENT PROCESSING
# ============================================================

def process_text_question(question_text):
    if not question_text:
        return

    if st.session_state.current_conversation_id is None:
        new_conv = create_conversation(make_title(question_text))
        st.session_state.current_conversation_id = new_conv["id"]

    current_conv_id = st.session_state.current_conversation_id

    st.session_state.messages.append({"role": "user", "content": question_text})
    with st.chat_message("user", avatar="👤"):
        st.markdown(question_text)

    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        with st.spinner("Thinking through your question..."):
            try:
                resp = api_request(
                    "POST",
                    "/chat",
                    json={"question": question_text, "conversation_id": current_conv_id},
                    headers=auth_headers(),
                    timeout=60,
                )
                data = resp.json()
                answer = data["answer"]
                sources = list(dict.fromkeys(data.get("sources", [])))
            except Exception as e:
                answer = f"I'm sorry, I couldn't process that request.\n\n**Details:** {e}"
                sources = []

        st.markdown(answer)

        if sources:
            source_html = f"""
                <div class="source-box">
                    <div class="source-title">📚 SOURCES USED · {len(sources)}</div>
                    {''.join(f'<div class="source-item">• {s}</div>' for s in sources)}
                </div>
                """
            st.markdown(textwrap.dedent(source_html).strip(), unsafe_allow_html=True)

    msg_index = len(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    if sources:
        st.session_state.last_sources[msg_index] = sources

    st.rerun()


def process_document(uploaded_file, question_text=""):
    if st.session_state.current_conversation_id is None:
        seed_title = make_title(question_text) if question_text else f"📄 {uploaded_file.name}"
        new_conv = create_conversation(seed_title)
        st.session_state.current_conversation_id = new_conv["id"]

    current_conv_id = st.session_state.current_conversation_id
    display_text = question_text if question_text else f"📄 Uploaded: {uploaded_file.name}"

    st.session_state.messages.append({"role": "user", "content": display_text})
    with st.chat_message("user", avatar="👤"):
        st.markdown(display_text)

    save_message(current_conv_id, "user", display_text)

    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        with st.spinner("Reading and analyzing your document..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                resp = requests.post(f"{BACKEND_URL}/summarize", files=files, timeout=120)
                resp.raise_for_status()
                result = resp.json()

                if "raw_output" in result:
                    answer = "### Document Analysis\n\n" + result.get("raw_output", "")
                else:
                    parts = []
                    if result.get("summary"):
                        parts.append("### 📋 Summary\n\n" + result.get("summary", ""))
                    if result.get("key_points"):
                        parts.append("### 🔑 Key Points\n\n" + "\n".join(f"- {p}" for p in result["key_points"]))
                    if result.get("key_clauses"):
                        parts.append("### 📌 Key Clauses\n\n" + "\n".join(f"- {c}" for c in result["key_clauses"]))
                    if result.get("legal_terms"):
                        parts.append("### 📚 Legal Terms\n\n" + "\n".join(
                            f"- **{t.get('term', '')}** — {t.get('meaning', '')}" for t in result["legal_terms"]
                        ))
                    if result.get("risks"):
                        parts.append("### ⚠️ Potential Risks\n\n" + "\n".join(f"- {r}" for r in result["risks"]))
                    answer = "\n\n".join(parts) if parts else "The document was analyzed, but no structured result was returned."
            except Exception as e:
                answer = f"### Document analysis failed\n\nI couldn't complete the document analysis.\n\n**Details:** {e}"

        st.markdown(answer)

    save_message(current_conv_id, "assistant", answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Ask your legal question, or attach a PDF...",
    accept_file=True,
    file_type=["pdf"],
)

if user_input:
    question_text = user_input.text or ""
    attached_files = user_input.files if hasattr(user_input, "files") else []

    if attached_files:
        process_document(attached_files[0], question_text)
    elif question_text:
        process_text_question(question_text)


# ============================================================
# FOOTER
# ============================================================

if st.session_state.messages:
    st.markdown(
        """
        <div class="disclaimer">
            ⚠️ AI-generated information is for general informational purposes only
            and does not constitute legal advice. For advice about your specific
            circumstances, consult a qualified legal professional.
        </div>
        """,
        unsafe_allow_html=True,
    )