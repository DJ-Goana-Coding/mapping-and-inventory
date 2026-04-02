import json
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

def load_map(path):
    """Load the master intelligence map."""
    if not os.path.exists(path):
        print(f"Warning: {path} not found. Creating empty map.")
        return []
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().splitlines()

def main():
    """Ingest master intelligence map into RAG vector store."""
    print("🧠 RAG Ingestion Engine")
    print("━" * 60)
    
    # Load embedding model
    print("Loading sentence transformer model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✅ Model loaded")
    
    # Load intelligence map
    print("\nLoading master intelligence map...")
    lines = load_map("master_intelligence_map.txt")
    
    if not lines:
        print("⚠️  No data to ingest. Exiting.")
        return
    
    print(f"✅ Loaded {len(lines)} lines")
    
    # Generate embeddings
    print("\nGenerating embeddings...")
    embeddings = model.encode(lines, convert_to_numpy=True, show_progress_bar=True)
    print(f"✅ Generated {embeddings.shape[0]} embeddings of dimension {embeddings.shape[1]}")
    
    # Create FAISS index
    print("\nBuilding FAISS index...")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    print(f"✅ Index built with {index.ntotal} vectors")
    
    # Save to RAG store
    print("\nSaving to rag_store/...")
    os.makedirs("rag_store", exist_ok=True)
    
    np.save("rag_store/vectors.npy", embeddings)
    print("✅ Saved vectors.npy")
    
    with open("rag_store/lines.json", "w", encoding='utf-8') as f:
        json.dump(lines, f, indent=2)
    print("✅ Saved lines.json")
    
    faiss.write_index(index, "rag_store/index.faiss")
    print("✅ Saved index.faiss")
    
    # Save metadata
    metadata = {
        "total_lines": len(lines),
        "embedding_dimension": embeddings.shape[1],
        "model": "all-MiniLM-L6-v2",
        "generated": np.datetime64('now').astype(str)
    }
    
    with open("rag_store/metadata.json", "w", encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print("✅ Saved metadata.json")
    
    print("\n━" * 60)
    print("🔮 RAG ingestion complete.")
    print(f"📊 Total vectors: {index.ntotal}")
    print(f"📐 Dimension: {embeddings.shape[1]}")
    print("🎯 Oracle memory updated and ready for semantic search")

if __name__ == "__main__":
    main()
