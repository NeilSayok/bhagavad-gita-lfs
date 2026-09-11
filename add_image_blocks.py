"""Add an "image" block to every chapter/*.json and slok/*.json file.

Paths only (no base URL), matching db/schema.sql's convention:
  chapters/{size}/chapter_<C>/{landscape,portrait,square}/img.png
  sloks/{size}/chapter_<C>/slok_<V>/{landscape,portrait,square}/img.png
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
        "landscape": f"chapters/{{size}}/chapter_{c}/landscape/img.png",
        "portrait": f"chapters/{{size}}/chapter_{c}/portrait/img.png",
        "square": f"chapters/{{size}}/chapter_{c}/square/img.png",
    }


def slok_image(data):
    c, v = data["chapter"], data["verse"]
    return {
        "landscape": f"sloks/{{size}}/chapter_{c}/slok_{v}/landscape/img.png",
        "portrait": f"sloks/{{size}}/chapter_{c}/slok_{v}/portrait/img.png",
        "square": f"sloks/{{size}}/chapter_{c}/slok_{v}/square/img.png",
    }


def main():
    add_images("api/chapter/*.json", chapter_image)
    add_images("api/slok/*.json", slok_image)
    print("done")


if __name__ == "__main__":
    main()
