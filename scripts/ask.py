import os
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="data/chroma_store")
collection = client.get_collection("legal_corpus")

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

Structure every answer like this:
1. Simple Explanation
2. Relevant Law/Section (name the Act and section number from the context)
3. Disclaimer: "This is general legal information, not legal advice. Please consult a licensed lawyer for your specific situation."
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Retrieved context:\n{context}\n\nQuestion: {question}"),
])

def retrieve(query, k=5):
    query_embedding = embed_model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=k)
    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "act": results["metadatas"][0][i]["act"],
            "text": results["documents"][0][i],
        })
    return chunks

def ask(question):
    chunks = retrieve(question)
    context = "\n\n".join(f"[{c['act']}]\n{c['text']}" for c in chunks)

    chain = prompt | llm
    response = chain.invoke({"context": context, "question": question})
    return response.content

if __name__ == "__main__":
    question = input("Ask a legal question: ")
    print("\n--- Answer ---\n")
    print(ask(question))