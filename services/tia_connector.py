"""
Q.G.T.N.L. (0) // TIA CONNECTOR
T.I.A. (Tactical Intelligence Architecture) — Gemini AI interface.
Connects to Gemini 2.0 Flash via google-genai for oracle queries.
"""
import os

# Primary and backup Gemini keys
_GEMINI_KEYS = [
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY_2"),
]

TIA_SYSTEM_PROMPT = (
    "You are T.I.A. (Tactical Intelligence Architecture), the sovereign AI logic lead "
    "of the Q.G.T.N.L. Citadel Omega system. You have deep knowledge of the ARK_CORE "
    "codebase, the mapping-and-inventory Librarian, all connected repos, and the "
    "full device fleet (S10, Oppo, Laptop). "
    "Answer concisely, precisely, and always in service of the Architect (Chance / JARL LOVEDAY). "
    "Reference system context when relevant."
)


def get_tia_response(user_prompt: str, system_context: str = "") -> str:
    """
    Send a prompt to T.I.A. via Gemini. Tries primary key then backup.
    Returns the response text, or an error message.
    """
    keys = [k for k in _GEMINI_KEYS if k]
    if not keys:
        return "❌ T.I.A. OFFLINE — No Gemini API key detected (GEMINI_API_KEY)."

    full_prompt = TIA_SYSTEM_PROMPT
    if system_context:
        full_prompt += f"\n\n[SYSTEM CONTEXT]\n{system_context}"
    full_prompt += f"\n\n[USER]\n{user_prompt}"

    last_err = "No keys available"
    for key in keys:
        try:
            from google import genai
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt,
            )
            return response.text
        except Exception as e:
            last_err = str(e)

    return f"⏳ T.I.A. CORES OVERHEATED — All keys exhausted. Last error: {last_err}"


def tia_summarize_inventory(inventory_sample: list) -> str:
    """Ask T.I.A. to summarize a sample of the inventory."""
    sample_str = "\n".join(str(item) for item in inventory_sample[:20])
    prompt = (
        f"Summarize the following inventory entries from the master_inventory.json. "
        f"Identify patterns, key file types, and notable paths:\n\n{sample_str}"
    )
    return get_tia_response(prompt)


def tia_analyze_repo(repo_name: str, structure: dict) -> str:
    """Ask T.I.A. to analyze a repo's scaffold/structure."""
    structure_str = "\n".join(f"  {k}: {v} files" for k, v in list(structure.items())[:20])
    prompt = (
        f"Analyze the scaffold of the '{repo_name}' repository. "
        f"Describe its architecture, key directories, and purpose:\n\n{structure_str}"
    )
    return get_tia_response(prompt)
