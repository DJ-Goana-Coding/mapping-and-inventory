import os, json

def search_atlas(query):
    root = os.path.expanduser("~/ARK_CORE")
    results = []
    
    for r, d, f in os.walk(root):
        for file in f:
            if query.lower() in file.lower():
                results.append(f"📍 {file}\n   PATH: {os.path.join(r, file)}")
    
    if not results:
        return "Librarian: No logic found in the 72-Branch Matrix."
    
    return "\n\n".join(results[:15]) # Limit to top 15 results

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(search_atlas(" ".join(sys.argv[1:])))
