import os, subprocess, json, datetime, psutil

def get_status():
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. SCAN ACTIVE ENGINES (Python Processes)
    py_procs = [p.info for p in psutil.process_iter(['pid', 'name', 'cmdline']) if 'python' in p.info['name']]
    proc_list = "\n".join([f"PID: {p['pid']} | CMD: {' '.join(p['cmdline'][:3])}" for p in py_procs]) if py_procs else "NO ENGINES DETECTED"

    # 2. SCAN THE KINGDOM (Librarian Count)
    atlas_p = os.path.expanduser("~/ARK_CORE/Partition_01/universal_atlas.json")
    count = 0
    if os.path.exists(atlas_p):
        with open(atlas_p, 'r') as f: count = len(json.load(f))

    # 3. SCAN THE PORTS (Gradio Bridge)
    ports = subprocess.run("netstat -tuln | grep -E '7860|7861'", shell=True, capture_output=True, text=True).stdout
    port_status = ports if ports else "ALL BRIDGES OFFLINE"

    return f"""
    [00000000Hz] --- THE ARK HUD: {ts} ---
    --------------------------------------------------
    🚀 ACTIVE PYTHON ENGINES:
    {proc_list}
    
    🌐 GRADIO BRIDGES (NETSTAT):
    {port_status}
    
    📚 THE KINGDOM (ATLAS):
    Total Secured Entities: {count}
    
    🛠️ ARK CORE LOCATION: {os.getcwd()}
    --------------------------------------------------
    [!] T.I.A. RECOMMENDATION: { "System Overloaded" if len(py_procs) > 4 else "Flow Stable" }
    """

if __name__ == "__main__":
    print(get_status())
