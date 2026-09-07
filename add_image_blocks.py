"""Add an "image" block to every chapter/*.json and slok/*.json file.

Paths only (no base URL), matching db/schema.sql's convention:
  chapters/chapter_<C>/{landscape,portrait,square}/img.jpeg
  sloks/chapter_<C>/slok_<V>/{landscape,portrait,square}/img.jpeg
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def add_images(pattern, path_fn):
    for path in sorted(glob.glob(os.path.join(ROOT, pattern))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        data["image"] = path_fn(data)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.write("\n")


def chapter_image(data):
    c = data["chapter_number"]
    return {
        "landscape": f"chapters/chapter_{c}/landscape/img.jpeg",
        "portrait": f"chapters/chapter_{c}/portrait/img.jpeg",
        "square": f"chapters/chapter_{c}/square/img.jpeg",
    }


def slok_image(data):
    c, v = data["chapter"], data["verse"]
    return {
        "landscape": f"sloks/chapter_{c}/slok_{v}/landscape/img.jpeg",
        "portrait": f"sloks/chapter_{c}/slok_{v}/portrait/img.jpeg",
        "square": f"sloks/chapter_{c}/slok_{v}/square/img.jpeg",
    }


def main():
    add_images("chapter/*.json", chapter_image)
    add_images("slok/*.json", slok_image)
    print("done")


if __name__ == "__main__":
    main()
