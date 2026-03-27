import subprocess
def run_sync():
    print('[ARK] INITIALIZING TRIPLE-SYNC...')
    subprocess.run(['python3', 'services/manifest_generator.py'])
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', 'ark: triple-vault broadcast'], capture_output=True)
    targets = ['origin', 'mapping', 'hf']
    for t in targets:
        print(f'[!] PUSHING TO {t.upper()}...')
        result = subprocess.run(['git', 'push', t, 'main', '--force'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f'[ERROR] {t.upper()} FAILED: {result.stderr}')
        else:
            print(f'[V] {t.upper()} SYNCHRONIZED.')
    print('[FINALISED] ARK MISSION COMPLETE.')
if __name__ == '__main__': run_sync()