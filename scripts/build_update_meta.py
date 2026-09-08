"""Build api/meta/update.json: last-modified epoch (seconds) for every file
under api/, keyed by path relative to api/. Run after all randomizers, before
committing, so it reflects the state produced by this run.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_DIR = os.path.join(ROOT, "api")
OUT_PATH = os.path.join(API_DIR, "meta", "update.json")


def main():
    files = {}
    for dirpath, _dirnames, filenames in os.walk(API_DIR):
        for name in filenames:
            path = os.path.join(dirpath, name)
            if os.path.abspath(path) == os.path.abspath(OUT_PATH):
                continue
            rel = os.path.relpath(path, API_DIR)
            files[rel] = int(os.path.getmtime(path))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(files, f, ensure_ascii=False, indent=2, sort_keys=True)
    with open(OUT_PATH, encoding="utf-8") as f:
        json.load(f)  # round-trip validity check

    print(f"wrote update epochs for {len(files)} files to {OUT_PATH}")


if __name__ == "__main__":
    main()
