import os
import time

SIGNAL_FILE = '/sdcard/Download/trinity_status.txt'

def check_perimeter():
    print("[v] HOUNDS DEPLOYED. Watching...")
    while True:
        if os.path.exists(SIGNAL_FILE):
             print("\n [***] CRITICAL: BREACH DETECTED.")
        time.sleep(5)

if __name__ == '__main__':
    check_perimeter()
