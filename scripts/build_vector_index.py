import json
import chromadb
from sentence_transformers import SentenceTransformer

print("Loading embedding model (first run downloads it to D:\\hf_cache)...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Loading chunks...")
with open("data/processed/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Generating embeddings for {len(chunks)} chunks...")
texts = [c["text"] for c in chunks]
embeddings = model.encode(texts, show_progress_bar=True)

print("Setting up ChromaDB...")
client = chromadb.PersistentClient(path="data/chroma_store")
collection = client.get_or_create_collection("legal_corpus")

print("Adding to vector database...")
collection.add(
    ids=[c["id"] for c in chunks],
    embeddings=embeddings.tolist(),
    documents=[c["text"] for c in chunks],
    metadatas=[{"act": c["act"], "source": c["source"]} for c in chunks],
)

print(f"\nDone. Indexed {len(chunks)} chunks into ChromaDB at data/chroma_store")