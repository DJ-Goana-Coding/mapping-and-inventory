import os, shutil, subprocess
def harvest():
    home, ark = os.path.expanduser('~'), os.path.expanduser('~/ARK_CORE')
    m_map = {'Partition_01': ['vanguard', 'mexc_live', 'hounds.log'], 'Partition_02': ['tia', 'architect'], 'Partition_03': ['trade_ledger', 'precious_metals']}
    print('[!] HARVESTING LOOSE GEAR...')
    for f in os.listdir(home):
        if f.endswith(('.py', '.sh', '.json', '.csv', '.log')):
            for part, keys in m_map.items():
                if any(k in f.lower() for k in keys):
                    shutil.copy2(os.path.join(home, f), os.path.join(ark, part, f))
def run_sync():
    print('[ARK] INITIALIZING SOVEREIGN HARVEST...')
    harvest()
    subprocess.run(['python3', 'services/manifest_generator.py'])
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', 'ark: sovereign harvest sync'], capture_output=True)
    for t in ['origin', 'mapping', 'hf']: 
        print(f'[!] PUSHING TO {t.upper()}...'); subprocess.run(['git', 'push', t, 'main', '--force'], capture_output=True)
    print('[SUCCESS] THE HARVEST IS SECURED.')
if __name__ == '__main__': run_sync()