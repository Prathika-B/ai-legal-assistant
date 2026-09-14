import json
import os
import shutil
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

print("Loading Chroma's default embedding function...")
embedding_function = DefaultEmbeddingFunction()

print("Loading chunks...")
with open("data/processed/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} chunks.")

# Remove the old index because it was created with the
# SentenceTransformer/PyTorch embedding pipeline.
chroma_path = "data/chroma_store"

if os.path.exists(chroma_path):
    print("Removing old Chroma index...")
    shutil.rmtree(chroma_path)

print("Creating Chroma database...")
client = chromadb.PersistentClient(path=chroma_path)

collection = client.create_collection(
    name="legal_corpus",
    embedding_function=embedding_function,
)

print("Adding legal documents to Chroma...")

collection.add(
    ids=[c["id"] for c in chunks],
    documents=[c["text"] for c in chunks],
    metadatas=[
        {
            "act": c["act"],
            "source": c["source"],
        }
        for c in chunks
    ],
)

print(f"\nDone! Indexed {len(chunks)} chunks.")
print(f"Chroma database: {chroma_path}")