import os, json, datetime
def generate_manifest():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest = {'timestamp': datetime.datetime.now().isoformat(), 'origin': 'OPPO_FORGE', 'inventory': []}
    for r, d, f in os.walk(root):
        d[:] = [x for x in d if x != '.git']
        for file in f:
            if file.endswith(('.py', '.sh', '.json', '.csv', '.log')):
                manifest['inventory'].append(os.path.relpath(os.path.join(r, file), root))
    os.makedirs(os.path.join(root, 'Partition_01'), exist_ok=True)
    path = os.path.join(root, 'Partition_01/master_inventory.json')
    with open(path, 'w') as f: json.dump(manifest, f, indent=4)
    print(f'[V] ARK_CORE INDEXED: {len(manifest["inventory"])} FILES SECURED.')
if __name__ == '__main__': generate_manifest()