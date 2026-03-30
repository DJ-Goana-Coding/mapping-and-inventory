import os, subprocess, datetime

def get_pulse():
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Check Python Processes
    procs = subprocess.run("ps -ef | grep python | grep -v grep", shell=True, capture_output=True, text=True).stdout
    proc_status = procs if procs else "NO ENGINES DETECTED"
    
    # Check Ports
    ports = subprocess.run("netstat -tuln | grep -E '7860|7861'", shell=True, capture_output=True, text=True).stdout
    port_status = ports if ports else "ALL BRIDGES OFFLINE"
    
    # Check Inventory
    ark_dir = os.path.expanduser("~/ARK_CORE")
    file_count = sum([len(files) for r, d, files in os.walk(ark_dir)])
    
    return f"""
    [00000000Hz] --- THE ARK PULSE: {ts} ---
    --------------------------------------------------
    🚀 ACTIVE ENGINES:
    {proc_status}
    
    🌐 OPEN BRIDGES:
    {port_status}
    
    📚 KINGDOM ENTITIES:
    Total Files in ARK_CORE: {file_count}
    
    📍 PATH: {os.getcwd()}
    --------------------------------------------------
    """

if __name__ == "__main__":
    print(get_pulse())
