import os
import json
import requests
import math
import time
from pypdf import PdfReader

# --- ⚙️ OMNI-BRAIN CONFIG ---
OLLAMA_URL = "http://127.0.0.1:11434"
LLM_MODEL = "phi4" 
LORE_DIR = "13th_Zone_Lore" 
VECTOR_DB_FILE = "omni_vector_mesh.json" 

def get_embedding(text):
    url = f"{OLLAMA_URL}/api/embeddings"
    payload = {"model": "llama3.2", "prompt": text}
    try:
        res = requests.post(url, json=payload, timeout=30)
        return res.json().get("embedding", [])
    except: return []

def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0

def build_mesh():
    os.system('clear')
    print("\033[96m[+] BUILDING NEURAL MESH FROM HARVESTED LORE...\033[0m")
    memory_mesh = []
    
    for filename in os.listdir(LORE_DIR):
        filepath = os.path.join(LORE_DIR, filename)
        text = ""
        
        # --- PDF X-RAY LOGIC ---
        if filename.endswith(".pdf"):
            print(f"\033[38;5;214m[PDF] Reading Law Stack: {filename}\033[0m")
            try:
                reader = PdfReader(filepath)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            except: continue
        
        # --- TEXT/JSON LOGIC ---
        elif filename.endswith((".md", ".txt", ".json")):
            print(f"\033[90m[TEXT] Ingesting: {filename}\033[0m")
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        if len(text) > 100:
            chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 100]
            for i, chunk in enumerate(chunks):
                vector = get_embedding(chunk)
                if vector:
                    memory_mesh.append({"source": filename, "text": chunk, "vector": vector})
                    
    with open(VECTOR_DB_FILE, "w") as f:
        json.dump(memory_mesh, f)
    print(f"\n\033[92m[✓] OMNI-BRAIN SYNCHRONIZED. {len(memory_mesh)} Nodes Active.\033[0m")

def query_mesh(prompt):
    if not os.path.exists(VECTOR_DB_FILE): return
    with open(VECTOR_DB_FILE, "r") as f:
        memory_mesh = json.load(f)
    
    prompt_vector = get_embedding(prompt)
    for node in memory_mesh:
        node["score"] = cosine_similarity(prompt_vector, node["vector"])
    
    memory_mesh.sort(key=lambda x: x["score"], reverse=True)
    context = "\n\n".join([f"Source ({m['source']}): {m['text']}" for m in memory_mesh[:3]])
    
    system_prompt = f"Use these 13th Zone records to answer: {prompt}\n\nRecords:\n{context}"
    res = requests.post(f"{OLLAMA_URL}/api/generate", json={"model": LLM_MODEL, "prompt": system_prompt, "stream": True})
    
    print("\033[96m[T.I.A.]:\033[0m ", end="")
    for line in res.iter_lines():
        if line:
            print(f"\033[92m{json.loads(line).get('response', '')}\033[0m", end="", flush=True)
    print("\n")

if __name__ == "__main__":
    while True:
        print("\n1. Build Mesh | 2. Query T.I.A. | X. Exit")
        choice = input(">> ").upper()
        if choice == "1": build_mesh()
        elif choice == "2": query_mesh(input("Query: "))
        elif choice == "X": break
