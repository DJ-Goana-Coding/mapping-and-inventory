import json, os, sys
def calc(p):
 print(f"\n[+] INITIATING 144-GRID RESONANCE AT {p}...")
 l, s = [], p * 0.0144
 for i in range(1, 5): l.append({"node":f"L{i}_UP", "price":round(p+s*i,4), "action":"SELL"})
 for i in range(1, 5): l.append({"node":f"L{i}_DOWN", "price":round(p-s*i,4), "action":"BUY"})
 path = os.path.expanduser("~/ARK_CORE/Districts/D03_VORTEX_ENGINE/active_grid.json")
 with open(path, 'w') as f: json.dump({"asset":"XRP", "base":p, "grid_144":l}, f, indent=2)
 print(f"[SUCCESS] 144-Grid ledger secured in D03: active_grid.json\n")
if __name__ == "__main__":
 p = float(sys.argv[1]) if len(sys.argv) > 1 else 1.3373
 calc(p)
