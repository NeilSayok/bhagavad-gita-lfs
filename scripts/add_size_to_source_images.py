"""One-off: insert {size} path param into image.* fields of api/chapter/*.json
and api/slok/*.json (raw source mirrors), matching the same {size} convention
already applied to the generated static APIs (db/build_db.py).
"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 'chapters/chapter_1/landscape/img.jpeg' -> 'chapters/{size}/chapter_1/landscape/img.jpeg'
# 'sloks/chapter_1/slok_1/landscape/img.jpeg' -> 'sloks/{size}/chapter_1/slok_1/landscape/img.jpeg'
PATTERN = re.compile(r"^(chapters|sloks)/(?!\{size\})")


def patch(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    image = d.get("image")
    if not image:
        return False
    changed = False
    for variant, value in image.items():
        if isinstance(value, str) and PATTERN.match(value):
            image[variant] = PATTERN.sub(r"\1/{size}/", value)
            changed = True
    if changed:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=4)
            f.write("\n")
    return changed


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "api", "chapter", "*.json"))) + \
            sorted(glob.glob(os.path.join(ROOT, "api", "slok", "*.json")))
    n = sum(patch(p) for p in files)
    print(f"patched {n}/{len(files)} files")


if __name__ == "__main__":
    main()
