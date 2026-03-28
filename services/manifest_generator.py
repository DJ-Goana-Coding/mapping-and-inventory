import os, json, datetime

def generate_manifest():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    now = datetime.datetime.now()
    manifest = {
        'timestamp': now.isoformat(),
        'origin': 'OPPO_FORGE',
        'architect': 'Chance',
        'inventory': [],
    }
    for r, d, f in os.walk(root):
        d[:] = [x for x in d if x not in ('.git',)]
        for file in f:
            if file.endswith(('.py', '.sh', '.json', '.csv', '.log')):
                abs_path = os.path.join(r, file)
                rel_path = os.path.relpath(abs_path, root)
                stat = os.stat(abs_path)
                manifest['inventory'].append({
                    'path': rel_path,
                    'size_bytes': stat.st_size,
                    'modified': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })
    manifest['total_files'] = len(manifest['inventory'])
    os.makedirs(os.path.join(root, 'Partition_01'), exist_ok=True)
    path = os.path.join(root, 'Partition_01/master_inventory.json')
    with open(path, 'w') as f:
        json.dump(manifest, f, indent=4)
    print(f'[V] ARK_CORE INDEXED: {len(manifest["inventory"])} FILES SECURED.')

if __name__ == '__main__':
    generate_manifest()