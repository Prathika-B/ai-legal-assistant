import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from backend.summarizer import summarize_document
from backend.auth import sign_up, sign_in, get_user_client

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_embed_model = None
_chroma_collection = None

def get_embed_model():
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embed_model

def get_chroma_collection():
    global _chroma_collection
    if _chroma_collection is None:
        import chromadb
        client = chromadb.PersistentClient(path="data/chroma_store")
        _chroma_collection = client.get_collection("legal_corpus")
    return _chroma_collection

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.environ["GROQ_API_KEY"],
    temperature=0.2,
)

SYSTEM_PROMPT = """You are an AI Legal Assistant providing EDUCATIONAL legal information only, based on Indian law.

Rules:
- Only use the information given in the "Retrieved context" below. Do not invent laws or sections not shown there.
- Never claim to be a lawyer or guarantee any legal outcome.
- If the retrieved context doesn't actually answer the question, say so honestly instead of guessing.
- Use the "Conversation history" below to understand follow-up questions. If there is no relevant history, ignore this section.

IMPORTANT — India's criminal law system changed on 1 July 2024. Be precise about which new code does what:
- BNS (Bharatiya Nyaya Sanhita), 2023 replaced the IPC — this defines WHAT is a crime and its punishment. Use BNS for substantive offence/punishment questions that used to be IPC sections.
- BNSS (Bharatiya Nagarik Suraksha Sanhita), 2023 replaced the CrPC — this governs court PROCEDURE (arrests, bail, filing complaints, trial process). Only cite BNSS for procedural questions, never as the source of a punishment or offence definition.
- BSA (Bharatiya Sakshya Adhiniyam), 2023 replaced the Indian Evidence Act — this governs how evidence is handled in court.
- Acts like the Negotiable Instruments Act, Motor Vehicles Act, Consumer Protection Act, etc. are SEPARATE special laws that were NOT replaced by BNS/BNSS/BSA — their own sections and punishments still apply directly. Do not claim BNS/BNSS/BSA replaced or now governs these unless the retrieved context explicitly says so.
- For questions specifically about IPC/CrPC/Evidence Act-era matters (general crimes like murder, theft, assault), prioritize BNS/BNSS/BSA over the old codes.

Structure every answer like this:
1. Simple Explanation
2. Relevant Law/Section (name the Act and section number from the context)
3. Disclaimer: "This is general legal information, not legal advice. Please consult a licensed lawyer for your specific situation."
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Conversation history:\n{history}\n\nRetrieved context:\n{context}\n\nQuestion: {question}"),
])


# ---------------- Auth ----------------

class AuthRequest(BaseModel):
    email: str
    password: str


@app.post("/signup")
def signup(request: AuthRequest):
    try:
        result = sign_up(request.email, request.password)
        return {"message": "Signup successful. Please log in.", "user_id": result.user.id if result.user else None}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login")
def login(request: AuthRequest):
    try:
        result = sign_in(request.email, request.password)
        return result
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid email or password")


def get_current_user_client(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    return get_user_client(token)


def _get_user_id_from_token(token: str) -> str:
    from backend.auth import get_anon_client
    client = get_anon_client()
    user_response = client.auth.get_user(token)
    return user_response.user.id


# ---------------- Conversations ----------------

class NewConversation(BaseModel):
    title: Optional[str] = "New chat"


class UpdateTitle(BaseModel):
    title: str


class NewMessage(BaseModel):
    role: str
    content: str


@app.get("/conversations")
def list_conversations(authorization: Optional[str] = Header(None)):
    db = get_current_user_client(authorization)
    result = db.table("conversations").select("*").order("created_at", desc=True).execute()
    return result.data


@app.post("/conversations")
def create_conversation(body: NewConversation, authorization: Optional[str] = Header(None)):
    db = get_current_user_client(authorization)
    token = authorization.split(" ", 1)[1]
    user_id = _get_user_id_from_token(token)
    result = db.table("conversations").insert({"title": body.title, "user_id": user_id}).execute()
    return result.data[0]


@app.patch("/conversations/{conversation_id}")
def update_conversation_title(conversation_id: int, body: UpdateTitle, authorization: Optional[str] = Header(None)):
    db = get_current_user_client(authorization)
    result = db.table("conversations").update({"title": body.title}).eq("id", conversation_id).execute()
    return result.data[0] if result.data else {}


@app.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int, authorization: Optional[str] = Header(None)):
    db = get_current_user_client(authorization)
    # delete messages first (no cascade configured at the DB level)
    db.table("messages").delete().eq("conversation_id", conversation_id).execute()
    db.table("conversations").delete().eq("id", conversation_id).execute()
    return {"deleted": True}


@app.get("/conversations/{conversation_id}/messages")
def get_messages(conversation_id: int, authorization: Optional[str] = Header(None)):
    db = get_current_user_client(authorization)
    result = db.table("messages").select("*").eq("conversation_id", conversation_id).order("id").execute()
    return result.data


@app.post("/conversations/{conversation_id}/save_message")
def save_message(conversation_id: int, body: NewMessage, authorization: Optional[str] = Header(None)):
    db = get_current_user_client(authorization)
    result = db.table("messages").insert({
        "conversation_id": conversation_id,
        "role": body.role,
        "content": body.content,
    }).execute()
    return result.data[0] if result.data else {}


# ---------------- Chat ----------------

def retrieve(query, k=5):
    try:
        model = get_embed_model()
        collection = get_chroma_collection()
        query_embedding = model.encode([query]).tolist()
        results = collection.query(query_embeddings=query_embedding, n_results=k)
        chunks = []
        if results and "ids" in results and results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                chunks.append({
                    "act": results["metadatas"][0][i]["act"],
                    "text": results["documents"][0][i],
                })
        return chunks
    except Exception as e:
        print(f"Retrieval error/fallback: {e}")
        return []


def format_history(messages, max_turns=6):
    if not messages:
        return "(no earlier messages)"
    recent = messages[-max_turns:]
    lines = []
    for msg in recent:
        speaker = "User" if msg["role"] == "user" else "Assistant"
        lines.append(f"{speaker}: {msg['content']}")
    return "\n".join(lines)


class ChatRequest(BaseModel):
    question: str
    conversation_id: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest, authorization: Optional[str] = Header(None)):
    db = get_current_user_client(authorization)

    prior = db.table("messages").select("*").eq("conversation_id", request.conversation_id).order("id").execute()
    history_text = format_history(prior.data)

    db.table("messages").insert({
        "conversation_id": request.conversation_id,
        "role": "user",
        "content": request.question,
    }).execute()

    chunks = retrieve(request.question)
    context = "\n\n".join(f"[{c['act']}]\n{c['text']}" for c in chunks)

    chain = prompt | llm
    response = chain.invoke({
        "history": history_text,
        "context": context,
        "question": request.question,
    })
    answer = response.content

    db.table("messages").insert({
        "conversation_id": request.conversation_id,
        "role": "assistant",
        "content": answer,
    }).execute()

    return {
        "answer": answer,
        "sources": [c["act"] for c in chunks],
    }


@app.post("/summarize")
async def summarize(file: UploadFile = File(...)):
    file_bytes = await file.read()
    result = summarize_document(file_bytes)
    return result


# ---------------- Unified Static Frontend Serving ----------------
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "web_app", "dist"))
if os.path.exists(dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        file_path = os.path.join(dist_path, full_path)
        if full_path and os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_path, "index.html"))