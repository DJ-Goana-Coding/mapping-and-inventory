import os
import google.generativeai as genai

# --- Q.G.T.N.L. (0) // INTEL SUMMARIZER V61.7 ---
# Function: Use Gemini to summarize tagged Aetheric Logs

def summarize_intel(log_text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "❌ Gemini Key Missing in Environment."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Analyze the following sovereign logs. 
    Summarize the #GRID probe hits and any #PROFIT alerts. 
    Provide a concise 'Architect's Briefing' on current system resonance.
    
    LOGS:
    {log_text}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Intelligence Link Failed: {e}"
