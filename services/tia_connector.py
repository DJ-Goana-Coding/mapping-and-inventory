"""
Q.G.T.N.L. (0) // TIA CONNECTOR
T.I.A. (Tactical Intelligence Architecture) — Gemini AI interface.
Connects to Gemini 2.0 Flash via google-genai for oracle queries.
"""
from .gemini_rotator import generate_content, get_rotator

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
    Send a prompt to T.I.A. via Gemini.

    Uses the round-robin Gemini key rotator with automatic 429 / ResourceExhausted
    failover across all configured ``GEMINI_API_KEY*`` values.
    Returns the response text, or an error message.
    """
    if not get_rotator():
        return "❌ T.I.A. OFFLINE — No Gemini API key detected (GEMINI_API_KEY)."

    full_prompt = TIA_SYSTEM_PROMPT
    if system_context:
        full_prompt += f"\n\n[SYSTEM CONTEXT]\n{system_context}"
    full_prompt += f"\n\n[USER]\n{user_prompt}"

    try:
        response = generate_content(model="gemini-2.0-flash", contents=full_prompt)
        return response.text
    except Exception as e:  # noqa: BLE001 — surface a friendly error to callers
        return f"⏳ T.I.A. CORES OVERHEATED — All keys exhausted. Last error: {e}"


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
