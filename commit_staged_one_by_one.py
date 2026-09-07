#!/usr/bin/env python3
import subprocess
import sys


def sh(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True)


def staged_files():
    out = subprocess.run(["git", "diff", "--cached", "--name-only"],
                          check=True, capture_output=True, text=True).stdout
    return [f for f in out.splitlines() if f]


BATCH_SIZE = 10


def main():
    files = staged_files()
    if not files:
        print("No staged files.")
        return
    for i in range(0, len(files), BATCH_SIZE):
        batch = files[i:i + BATCH_SIZE]
        print(f"Committing batch: {batch}")
        try:
            sh("git", "commit", "-m", f"Commited {', '.join(batch)}", "--", *batch)
            sh("git", "push")
            print(f"  pushed ok: {batch}")
        except subprocess.CalledProcessError as e:
            print(f"  FAILED on {batch}: {e.stderr.strip()}")
            sys.exit(1)


if __name__ == "__main__":
    main()