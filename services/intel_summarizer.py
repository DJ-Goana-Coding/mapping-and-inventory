from .gemini_rotator import generate_content, get_rotator, _is_rate_limit_error

# --- Q.G.T.N.L. (0) // INTEL SUMMARIZER V61.7 ---
# Function: Use Gemini to summarize tagged Aetheric Logs

_MODEL_NAME = "gemini-1.5-flash"


def _legacy_client_factory(api_key: str):
    """Adapter so the legacy ``google.generativeai`` SDK plugs into the rotator.

    Returns a shim with a ``models.generate_content(model=..., contents=...)``
    API matching the new ``google-genai`` client used by the rotator.
    """
    import google.generativeai as genai

    genai.configure(api_key=api_key)

    class _ModelsShim:
        @staticmethod
        def generate_content(model: str, contents, **_kwargs):
            return genai.GenerativeModel(model).generate_content(contents)

    class _ClientShim:
        models = _ModelsShim()

    return _ClientShim()


def summarize_intel(log_text):
    if not get_rotator():
        return "❌ Gemini Key Missing in Environment."

    prompt = f"""
    Analyze the following sovereign logs.
    Summarize the #GRID probe hits and any #PROFIT alerts.
    Provide a concise 'Architect's Briefing' on current system resonance.

    LOGS:
    {log_text}
    """

    try:
        response = generate_content(
            model=_MODEL_NAME,
            contents=prompt,
            client_factory=_legacy_client_factory,
        )
        return response.text
    except Exception as e:  # noqa: BLE001
        if _is_rate_limit_error(e):
            return "⏳ Intelligence Link Throttled — all keys exhausted."
        return f"❌ Intelligence Link Failed: {e}"
