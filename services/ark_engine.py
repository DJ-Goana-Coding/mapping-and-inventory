import subprocess
def run_sync():
    print('[ARK] INITIALIZING TRIPLE-SYNC...')
    subprocess.run(['python3', 'services/manifest_generator.py'])
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', 'ark: triple-vault broadcast'], capture_output=True)
    print('[!] PUSHING TO GITHUB ARK...')
    subprocess.run(['git', 'push', 'origin', 'main', '--force'])
    print('[!] PUSHING TO MAPPING...')
    subprocess.run(['git', 'push', 'mapping', 'main', '--force'])
    print('[!] PUSHING TO HUGGING FACE BRAIN...')
    subprocess.run(['git', 'push', 'hf', 'main', '--force'])
    print('[SUCCESS] ALL VAULTS ARE STAINLESS.')
if __name__ == '__main__': run_sync()