from sentence_transformers import SentenceTransformer
import chromadb
import os

def load_chunks(file_path):
    with open(file_path, encoding='utf-8') as f:
        raw = f.read()
    # Split by your chunk delimiter
    chunks = [x.strip() for x in raw.split('---chunk---') if x.strip()]
    return chunks

if __name__ == "__main__":
    # Path to  newly OCR-extracted chunk file
    chunks = load_chunks('vector_store/chunks.txt')
    print(f"Loaded {len(chunks)} chunks.")

    # Load a multilingual embedding model suitable for Bangla and English
    print("Loading embedding model...")
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

    print("Embedding all chunks...")
    embeddings = model.encode(chunks, show_progress_bar=True)

    # Set up ChromaDB (persistent)
    persist_dir = "vector_store/chroma_db"
    os.makedirs(persist_dir, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=persist_dir)

    # Remove old collection if it exists (for clean re-run)
    existing = [c.name for c in chroma_client.list_collections()]
    if "hsc26_chunks" in existing:
        chroma_client.delete_collection("hsc26_chunks")
    collection = chroma_client.create_collection(name="hsc26_chunks")

    print("Storing vectors in ChromaDB...")
    ids = [f"chunk_{i}" for i in range(len(chunks))]

    collection.add(
        embeddings=embeddings.tolist(),
        documents=chunks,
        ids=ids
       
    )

    print("Vector store built and saved in vector_store/chroma_db!")
