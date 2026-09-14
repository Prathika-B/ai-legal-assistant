import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="data/chroma_store")
collection = client.get_collection("legal_corpus")

query = "What happens if someone doesn't pay back money they borrowed?"
query_embedding = model.encode([query]).tolist()

results = collection.query(
    query_embeddings=query_embedding,
    n_results=5,
)

for i in range(len(results["ids"][0])):
    print(f"\n--- Match {i+1} ---")
    print(f"Act: {results['metadatas'][0][i]['act']}")
    print(f"Distance: {results['distances'][0][i]:.4f}")
    print(results["documents"][0][i][:200])