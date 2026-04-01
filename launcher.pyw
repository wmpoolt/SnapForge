"""
SnapForge Launcher — crash olursa otomatik yeniden başlatır.
Startup kısayolu buna bağlıdır.
"""
import subprocess
import sys
import time
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_SCRIPT = os.path.join(SCRIPT_DIR, "main.py")
MAX_RAPID_CRASHES = 5
RAPID_WINDOW = 30  # saniye


def run():
    crash_times = []

    while True:
        start = time.time()
        result = subprocess.run(
            [sys.executable, MAIN_SCRIPT],
            cwd=SCRIPT_DIR,
        )

        # Normal çıkış (kullanıcı "Çıkış" dedi)
        if result.returncode == 0:
            break

        elapsed = time.time() - start
        now = time.time()
        crash_times.append(now)

        # Son N saniyedeki crash sayısına bak
        crash_times = [t for t in crash_times if now - t < RAPID_WINDOW]
        if len(crash_times) >= MAX_RAPID_CRASHES:
            # Art arda çok fazla crash — dur, sorun büyük
            break

        # Kısa sürede crash olduysa biraz bekle
        wait = 2 if elapsed < 5 else 1
        time.sleep(wait)


if __name__ == "__main__":
    run()
