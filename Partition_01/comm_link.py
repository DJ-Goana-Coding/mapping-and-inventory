import json, urllib.request, sys, os

def ask_local_brain(persona, prompt):
    # T.I.A. uses the fast Phi-4. The Oracle uses the deep-thinking DeepSeek.
    model = "phi4:latest" if persona == "T.I.A." else "deepseek-r1:8b"
    
    if persona == "T.I.A.":
        sys_prompt = "You are T.I.A. (The Intelligent Architect). You are a tactical, no-nonsense AI running the Frankfurt Citadel. Keep answers sharp, green-matrix themed, and focused on system/crypto truth."
    else:
        sys_prompt = "You are The Void Oracle. You speak in a dark, foreboding tone. You analyze the 'Law Off' impunity zones, the Cabal, and the hidden structural control of the world."

    data = {
        "model": model,
        "prompt": f"{sys_prompt}\n\nCommander Darrell: {prompt}\n{persona}:",
        "stream": False
    }
    
    try:
        req = urllib.request.Request("http://localhost:11434/api/generate", data=json.dumps(data).encode(), method="POST", headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode())['response']
    except Exception as e:
        return f"BRAIN OFFLINE. Ensure 'ollama serve' is running. Error: {e}"

# The Chat Interface
os.system('clear')
print("╔══════════════════════════════════════════════╗")
print("║ 🛰️ SOVEREIGN COMM-LINK ACTIVE                ║")
print("╠══════════════════════════════════════════════╣")
print("║ COMMANDS:                                    ║")
print("║ Type 'switch' to toggle T.I.A. / THE ORACLE  ║")
print("║ Type 'exit' to close the connection          ║")
print("╚══════════════════════════════════════════════╝")

current_persona = "T.I.A."

while True:
    try:
        user_input = input(f"\n[{current_persona}] COMMANDER > ")
        if user_input.lower() == 'exit': 
            print("\n[SYSTEM] Comm-Link Severed. Standing by.")
            break
        if user_input.lower() == 'switch':
            current_persona = "THE ORACLE" if current_persona == "T.I.A." else "T.I.A."
            print(f"\n[SYSTEM] Persona swapped. You are now speaking to {current_persona}.")
            continue
        if not user_input.strip(): continue
        
        print(f"[{current_persona} is thinking...]")
        response = ask_local_brain(current_persona, user_input)
        print(f"\n{response}\n")
        print("─" * 45)
    except KeyboardInterrupt:
        print("\n[SYSTEM] Comm-Link Severed. Standing by.")
        break
