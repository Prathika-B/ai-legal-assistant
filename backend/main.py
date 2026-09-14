import os

# Keep CPU/thread usage controlled for Render's memory-limited environment.
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


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# FastAPI
# ---------------------------------------------------------

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Chroma / Embedding
# ---------------------------------------------------------
#
# IMPORTANT:
# We no longer import SentenceTransformer here.
#
# The Chroma index was rebuilt using Chroma's
# DefaultEmbeddingFunction(), which uses the same
# all-MiniLM-L6-v2 embedding model through Chroma's
# embedding pipeline.
#
# This keeps the embedding model consistent while
# avoiding the direct SentenceTransformer/PyTorch
# initialization in the backend.
# ---------------------------------------------------------

_embed_function = None
_chroma_collection = None


def get_embed_function():
    global _embed_function

    if _embed_function is None:
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

        _embed_function = DefaultEmbeddingFunction()

    return _embed_function


def get_chroma_collection():
    global _chroma_collection

    if _chroma_collection is None:
        import chromadb

        client = chromadb.PersistentClient(
            path="data/chroma_store"
        )

        embedding_function = get_embed_function()

        _chroma_collection = client.get_collection(
            name="legal_corpus",
            embedding_function=embedding_function,
        )

    return _chroma_collection


# ---------------------------------------------------------
# Groq LLM
# ---------------------------------------------------------

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.environ["GROQ_API_KEY"],
    temperature=0.2,
)


# ---------------------------------------------------------
# Legal Assistant System Prompt
# ---------------------------------------------------------

SYSTEM_PROMPT = """
You are an AI Legal Assistant providing educational legal information based on Indian law.

Your purpose is to help users understand legal issues in simple, clear and practical English.

You are NOT a lawyer. You must not provide guaranteed legal outcomes or present your response as formal legal advice.

IMPORTANT RULES:

1. UNDERSTAND THE USER'S ACTUAL PROBLEM

- First identify what the user is actually asking.
- Answer the specific legal issue instead of giving a generic explanation of an entire Act.
- Keep the response conversational and practical.


2. DO NOT ASSUME FACTS

- Use only facts provided by the user.
- Do not invent missing details.
- If important information is missing, clearly mention what additional information would help.


3. JURISDICTION

- This assistant currently focuses on Indian law.
- If the answer may depend on the State, local authority, court, tenancy rules, contract terms, or another jurisdiction-specific rule, clearly say that the exact position may vary.
- Do not invent State-specific laws when the user's location is unknown.


4. USE RETRIEVED LEGAL CONTEXT CAREFULLY

- Retrieved context is provided below.
- Use retrieved information only when it is relevant to the user's actual question.
- DO NOT mention a legal section merely because it appears in the same Act as another relevant section.
- DO NOT force unrelated sections into the answer.
- If a retrieved section does not directly address the user's issue, do not cite it.
- If the retrieved context does not contain a directly relevant legal provision, say:

  "The retrieved legal material does not contain a directly relevant provision for this specific issue."

- Never invent laws, sections, case names, citations, penalties, procedures, or legal rights.


5. LEGAL CODE ACCURACY

India's major criminal-law codes changed on 1 July 2024:

- BNS (Bharatiya Nyaya Sanhita, 2023) replaced the IPC and deals mainly with offences and punishments.
- BNSS (Bharatiya Nagarik Suraksha Sanhita, 2023) replaced the CrPC and deals mainly with criminal procedure such as arrest, bail, investigation and trial.
- BSA (Bharatiya Sakshya Adhiniyam, 2023) replaced the Indian Evidence Act and deals with evidence.

For criminal-law questions:

- Use BNS for offences and punishments.
- Use BNSS for criminal procedure.
- Use BSA for evidence-related questions.

Special laws such as the Negotiable Instruments Act, Motor Vehicles Act, Consumer Protection Act and other separate statutes continue to operate independently.

Do not incorrectly substitute BNS, BNSS or BSA for a special law.


6. PRACTICAL HELP

When appropriate, give the user reasonable practical next steps.

Examples:

- Check the relevant agreement or document.
- Preserve receipts, messages, emails, notices or other evidence.
- Communicate with the other party in writing.
- Identify the appropriate authority, forum or legal process if supported by the retrieved context.
- Consider consulting a qualified lawyer when professional legal assistance is appropriate.

Do not present a suggested option as a guaranteed legal remedy.


7. DISTINGUISH INFORMATION FROM ADVICE

Clearly distinguish between:

- What the user has told you.
- General legal information.
- Possible options or next steps.

Do not state uncertain legal conclusions as facts.


8. FOLLOW-UP QUESTIONS

If an important missing fact could materially change the answer, briefly ask for it or explain why it matters.

Examples:

- State/location
- Type of agreement
- Date of the event
- Whether a written contract exists
- Amount involved
- Whether any notice was received

Do not ask unnecessary questions when a useful general answer can already be given.


RESPONSE FORMAT:

### Simple Explanation

Explain the user's situation in plain English.

Do not start with a list of legal sections.


### What You Can Do

Give practical next steps relevant to the user's situation.


### ⚖️ Relevant Legal Information

Mention ONLY legal provisions or principles from the retrieved context that directly relate to the user's question.

For each relevant provision:

- Name the Act
- Give the section number if available
- Briefly explain why it is relevant

If there is no directly relevant provision in the retrieved context, say so honestly.


### When to Get Legal Help

Mention when the user should consider speaking with a qualified lawyer or appropriate authority, especially for serious, urgent, high-value, or complicated matters.


### Disclaimer

This is general legal information, not legal advice. Please consult a licensed lawyer for advice about your specific situation.


IMPORTANT FINAL CHECK:

Before answering, ask yourself:

- Did I answer the user's actual question?
- Did I accidentally include an unrelated legal section?
- Did I invent any legal information?
- Did I assume facts that the user did not provide?
- Are the cited provisions directly relevant?
- Did I give practical and understandable guidance?

If a legal section is not directly relevant, leave it out.
"""


prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    (
        "human",
        """
Conversation history:
{history}

Retrieved legal context:
{context}

User's question:
{question}

Answer the user's actual question using the instructions above.
"""
    ),
])


# ---------------------------------------------------------
# Auth
# ---------------------------------------------------------

class AuthRequest(BaseModel):
    email: str
    password: str


@app.post("/signup")
def signup(request: AuthRequest):
    try:
        result = sign_up(request.email, request.password)

        return {
            "message": "Signup successful. Please log in.",
            "user_id": result.user.id if result.user else None,
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@app.post("/login")
def login(request: AuthRequest):
    try:
        result = sign_in(
            request.email,
            request.password,
        )

        return result

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )


def get_current_user_client(
    authorization: Optional[str] = Header(None),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
        )

    token = authorization.split(" ", 1)[1]

    return get_user_client(token)


def _get_user_id_from_token(token: str) -> str:
    from backend.auth import get_anon_client

    client = get_anon_client()

    user_response = client.auth.get_user(token)

    return user_response.user.id


# ---------------------------------------------------------
# Conversations
# ---------------------------------------------------------

class NewConversation(BaseModel):
    title: Optional[str] = "New chat"


class UpdateTitle(BaseModel):
    title: str


class NewMessage(BaseModel):
    role: str
    content: str


@app.get("/conversations")
def list_conversations(
    authorization: Optional[str] = Header(None),
):
    db = get_current_user_client(authorization)

    result = (
        db.table("conversations")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return result.data


@app.post("/conversations")
def create_conversation(
    body: NewConversation,
    authorization: Optional[str] = Header(None),
):
    db = get_current_user_client(authorization)

    token = authorization.split(" ", 1)[1]

    user_id = _get_user_id_from_token(token)

    result = (
        db.table("conversations")
        .insert(
            {
                "title": body.title,
                "user_id": user_id,
            }
        )
        .execute()
    )

    return result.data[0]


@app.patch("/conversations/{conversation_id}")
def update_conversation_title(
    conversation_id: int,
    body: UpdateTitle,
    authorization: Optional[str] = Header(None),
):
    db = get_current_user_client(authorization)

    result = (
        db.table("conversations")
        .update(
            {
                "title": body.title,
            }
        )
        .eq("id", conversation_id)
        .execute()
    )

    return result.data[0] if result.data else {}


@app.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    authorization: Optional[str] = Header(None),
):
    db = get_current_user_client(authorization)

    # Delete messages first because there is no cascade
    # configured at the DB level.
    (
        db.table("messages")
        .delete()
        .eq("conversation_id", conversation_id)
        .execute()
    )

    (
        db.table("conversations")
        .delete()
        .eq("id", conversation_id)
        .execute()
    )

    return {
        "deleted": True,
    }


@app.get("/conversations/{conversation_id}/messages")
def get_messages(
    conversation_id: int,
    authorization: Optional[str] = Header(None),
):
    db = get_current_user_client(authorization)

    result = (
        db.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("id")
        .execute()
    )

    return result.data


@app.post("/conversations/{conversation_id}/save_message")
def save_message(
    conversation_id: int,
    body: NewMessage,
    authorization: Optional[str] = Header(None),
):
    db = get_current_user_client(authorization)

    result = (
        db.table("messages")
        .insert(
            {
                "conversation_id": conversation_id,
                "role": body.role,
                "content": body.content,
            }
        )
        .execute()
    )

    return result.data[0] if result.data else {}


# ---------------------------------------------------------
# Legal Retrieval
# ---------------------------------------------------------

def retrieve(query: str, k: int = 5):
    try:
        embedding_function = get_embed_function()

        collection = get_chroma_collection()

        # Use the SAME embedding function used when the
        # 1,790 legal chunks were indexed.
        query_embedding = embedding_function([query])

        results = collection.query(
            query_embeddings=query_embedding,
            n_results=k,
        )

        chunks = []

        if (
            results
            and "ids" in results
            and results["ids"]
            and len(results["ids"][0]) > 0
        ):
            for i in range(len(results["ids"][0])):

                metadata = results["metadatas"][0][i] or {}

                chunks.append(
                    {
                        "act": metadata.get(
                            "act",
                            "Unknown Act",
                        ),
                        "text": results["documents"][0][i],
                    }
                )

        return chunks

    except Exception as e:
        print(f"Retrieval error/fallback: {e}")

        return []


# ---------------------------------------------------------
# Conversation History
# ---------------------------------------------------------

def format_history(messages, max_turns=6):

    if not messages:
        return "(no earlier messages)"

    recent = messages[-max_turns:]

    lines = []

    for msg in recent:

        speaker = (
            "User"
            if msg["role"] == "user"
            else "Assistant"
        )

        lines.append(
            f"{speaker}: {msg['content']}"
        )

    return "\n".join(lines)


# ---------------------------------------------------------
# Chat
# ---------------------------------------------------------

class ChatRequest(BaseModel):
    question: str
    conversation_id: int


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.post("/chat")
def chat(
    request: ChatRequest,
    authorization: Optional[str] = Header(None),
):

    # Get authenticated user's database client.
    db = get_current_user_client(
        authorization
    )

    # Get previous conversation messages.
    prior = (
        db.table("messages")
        .select("*")
        .eq(
            "conversation_id",
            request.conversation_id,
        )
        .order("id")
        .execute()
    )

    history_text = format_history(
        prior.data
    )

    # Save user's question.
    (
        db.table("messages")
        .insert(
            {
                "conversation_id": request.conversation_id,
                "role": "user",
                "content": request.question,
            }
        )
        .execute()
    )

    # Retrieve relevant Indian-law material.
    chunks = retrieve(
        request.question,
        k=5,
    )

    context = "\n\n".join(
        f"[{c['act']}]\n{c['text']}"
        for c in chunks
    )

    # Generate answer using Groq.
    chain = prompt | llm

    response = chain.invoke(
        {
            "history": history_text,
            "context": context,
            "question": request.question,
        }
    )

    answer = response.content

    # Save assistant answer.
    (
        db.table("messages")
        .insert(
            {
                "conversation_id": request.conversation_id,
                "role": "assistant",
                "content": answer,
            }
        )
        .execute()
    )

    return {
        "answer": answer,
        "sources": [
            c["act"]
            for c in chunks
        ],
    }


# ---------------------------------------------------------
# Document Summarization
# ---------------------------------------------------------

@app.post("/summarize")
async def summarize(
    file: UploadFile = File(...),
):

    file_bytes = await file.read()

    result = summarize_document(
        file_bytes
    )

    return result


# ---------------------------------------------------------
# Unified Static Frontend Serving
# ---------------------------------------------------------

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


dist_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "frontend",
        "web_app",
        "dist",
    )
)


if os.path.exists(dist_path):

    app.mount(
        "/assets",
        StaticFiles(
            directory=os.path.join(
                dist_path,
                "assets",
            )
        ),
        name="assets",
    )

    @app.get("/{full_path:path}")
    async def serve_react_app(
        full_path: str,
    ):

        file_path = os.path.join(
            dist_path,
            full_path,
        )

        if (
            full_path
            and os.path.exists(file_path)
            and os.path.isfile(file_path)
        ):
            return FileResponse(
                file_path
            )

        return FileResponse(
            os.path.join(
                dist_path,
                "index.html",
            )
        )