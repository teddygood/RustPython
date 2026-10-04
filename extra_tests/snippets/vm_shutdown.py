"""Interpreter shutdown and the threading module.

Shutdown waits for the non-daemon threads of a program that imported
threading. It must not import the module on behalf of a program that never
did.
"""

import subprocess
import sys


def run(code):
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", code],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        timeout=30,
    )
    assert result.returncode == 0, result
    return result.stdout.split()


# atexit callbacks run right after the wait for threads.
never_imported = """
import atexit, sys
atexit.register(lambda: print("threading" in sys.modules))
"""
output = run(never_imported)
assert output == ["False"], output

# The worker can only finish once shutdown has marked the main thread done.
imported = """
import threading
def worker():
    threading.main_thread().join()
    print("worker")
threading.Thread(target=worker).start()
print("main")
"""
output = run(imported)
assert output == ["main", "worker"], output
