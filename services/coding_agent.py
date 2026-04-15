"""
Q.G.T.N.L. (0) // CODING AGENT
Sophisticated AI coding agent powered by Gemini.
Writes, reviews, explains, and refactors code on demand.
Supports: Python, JavaScript, Apps Script, Bash, and more.
"""
import os
import json
from datetime import datetime, timezone

# Gemini keys (shared with tia_connector)
_GEMINI_KEYS = [
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY_2"),
]

CODING_AGENT_SYSTEM_PROMPT = """You are the Citadel Coding Agent — a sovereign, elite software engineer embedded
in the Q.G.T.N.L. Citadel Omega system.

CAPABILITIES:
- Write production-quality code in Python, JavaScript, TypeScript, Google Apps Script, Bash, HTML/CSS, SQL, and more
- Debug, refactor, and optimize existing code
- Explain code and architecture decisions
- Generate complete Apps Script workers for Google Workspace automation
- Create GitHub Actions workflows
- Build Streamlit dashboards and UI components
- Write tests, documentation, and deployment scripts

RULES:
1. Always produce complete, runnable code — never leave placeholders like "// TODO" or "..." unless explicitly asked
2. Include clear comments explaining key logic
3. Follow best practices for each language
4. When generating Apps Script workers, include the manifest (appsscript.json) and setup instructions
5. When writing Python, prefer modern patterns (f-strings, pathlib, type hints)
6. Security first — never hardcode secrets, always use environment variables
7. When asked to execute code, wrap it safely and return results

OUTPUT FORMAT:
- Wrap code blocks with the language identifier
- Provide a brief explanation before and after code
- If multiple files are needed, clearly label each one
"""


def _call_gemini(prompt: str, system_prompt: str = CODING_AGENT_SYSTEM_PROMPT) -> str:
    """Call Gemini with the coding agent system prompt."""
    keys = [k for k in _GEMINI_KEYS if k]
    if not keys:
        return (
            "❌ CODING AGENT OFFLINE — No Gemini API key detected.\n"
            "Set GEMINI_API_KEY in your HuggingFace Space secrets."
        )

    full_prompt = system_prompt + "\n\n" + prompt
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

    return f"⏳ CODING AGENT ERROR — All keys exhausted. Last error: {last_err}"


def generate_code(instruction: str, language: str = "python", context: str = "") -> str:
    """Generate code from a natural language instruction."""
    prompt = f"""[CODING REQUEST]
Language: {language}
Instruction: {instruction}
"""
    if context:
        prompt += f"\n[CONTEXT]\n{context}\n"
    prompt += "\nGenerate clean, production-ready code. Include comments and brief explanation."
    return _call_gemini(prompt)


def review_code(code: str, language: str = "python") -> str:
    """Review code for bugs, style issues, and improvements."""
    prompt = f"""[CODE REVIEW REQUEST]
Language: {language}

```{language}
{code}
```

Review this code for:
1. Bugs and logic errors
2. Security vulnerabilities
3. Performance issues
4. Style and best practices
5. Missing error handling

Provide specific, actionable feedback with corrected code where applicable.
"""
    return _call_gemini(prompt)


def explain_code(code: str, language: str = "python") -> str:
    """Explain what a piece of code does."""
    prompt = f"""[CODE EXPLANATION REQUEST]
Language: {language}

```{language}
{code}
```

Explain this code in clear, accessible language:
1. What it does overall
2. Key components and their roles
3. Data flow
4. Any notable patterns or techniques used
"""
    return _call_gemini(prompt)


def refactor_code(code: str, language: str = "python", goals: str = "") -> str:
    """Refactor code to improve quality."""
    prompt = f"""[REFACTORING REQUEST]
Language: {language}

```{language}
{code}
```

Refactor this code to improve:
{goals if goals else "readability, performance, and maintainability"}

Provide the complete refactored code with explanation of changes.
"""
    return _call_gemini(prompt)


def debug_code(code: str, error_message: str, language: str = "python") -> str:
    """Debug code given an error message."""
    prompt = f"""[DEBUG REQUEST]
Language: {language}

Code:
```{language}
{code}
```

Error:
```
{error_message}
```

Diagnose the error:
1. Root cause
2. Fix with corrected code
3. How to prevent similar issues
"""
    return _call_gemini(prompt)


def chat(message: str, history: list | None = None) -> str:
    """General chat with the coding agent, with conversation history support."""
    prompt = "[AGENT CHAT]\n"
    if history:
        for entry in history[-10:]:  # Keep last 10 messages for context
            role = entry.get("role", "user")
            content = entry.get("content", "")
            prompt += f"\n[{role.upper()}]\n{content}\n"
    prompt += f"\n[USER]\n{message}\n"
    prompt += "\nRespond helpfully. If the user asks for code, provide complete, runnable code."
    return _call_gemini(prompt)


def generate_appscript_worker(
    description: str,
    worker_name: str = "CitadelWorker",
    triggers: list | None = None,
) -> dict:
    """Generate a complete Google Apps Script worker."""
    trigger_text = ""
    if triggers:
        trigger_text = f"\nTriggers to include: {', '.join(triggers)}"
    prompt = f"""[APPS SCRIPT WORKER GENERATION]
Worker Name: {worker_name}
Description: {description}{trigger_text}

Generate a complete Google Apps Script worker that includes:
1. Main function(s) implementing the described functionality
2. Trigger setup function (onOpen, onEdit, time-based, etc. as appropriate)
3. Error handling and logging
4. Configuration section at the top
5. Helper utility functions
6. The appsscript.json manifest

Output as TWO clearly labeled code blocks:
- First: The main .gs code
- Second: The appsscript.json manifest

Make it production-ready and well-documented.
"""
    response = _call_gemini(prompt)
    return {
        "worker_name": worker_name,
        "description": description,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "code": response,
    }


def generate_workflow(description: str, workflow_name: str = "citadel_workflow") -> str:
    """Generate a GitHub Actions workflow YAML."""
    prompt = f"""[GITHUB ACTIONS WORKFLOW GENERATION]
Workflow Name: {workflow_name}
Description: {description}

Generate a complete GitHub Actions workflow (.yml) that:
1. Has appropriate triggers (push, schedule, workflow_dispatch, etc.)
2. Uses proper job structure and steps
3. Includes error handling
4. Uses secrets properly (never hardcode)
5. Follows GitHub Actions best practices
6. Works in the DJ-Goana-Coding/mapping-and-inventory repository context

Provide the complete YAML with comments explaining each section.
"""
    return _call_gemini(prompt)
