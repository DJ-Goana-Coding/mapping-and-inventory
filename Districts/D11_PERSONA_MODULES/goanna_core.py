import sys, json, os

def speak(p):
    path = os.path.expanduser("~/ARK_CORE/Districts/D03_VORTEX_ENGINE/active_grid.json")
    if not os.path.exists(path): 
        return print("Strewth! No grid found, mate!")
        
    with open(path, 'r') as f: 
        g = json.load(f)
        
    b = g['base']
    d = p - b
    
    print("\n🦎 [D11_PERSONA_MODULE: DJ GOANNA]")
    print("========================================")
    if d > 0:
        print(f"Strewth, Big Doofy Man! XRP is pushin' up to ${p}! We're above base camp. Keep your eyes on that L1 Sell Target at ${g['grid_144'][0]['price']}! The 'Looby Lips' are whistlin'!")
    elif d < 0:
        print(f"Bloody hell, Oracle! XRP dipped to ${p}. We're under the base. It's bleedin' towards that L1 Buy Zone at ${g['grid_144'][4]['price']}. Get the esky ready, we might be buyin' the dip!")
    else:
        print(f"Right on the money! ${p} flat. The market's holdin' its breath, mate.")
    print("========================================\n")

if __name__ == "__main__":
    # Test fire using the last known price
    speak(float(sys.argv[1]) if len(sys.argv) > 1 else 1.3366)
