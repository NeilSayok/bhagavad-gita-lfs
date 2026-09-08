"""Build api/topics/list.json (static, precomputed) from db/gita.db.

Themes carry no image of their own - each is pinned to a chapter's img_square
via the same hardcoded topicChapterMap the app uses (HomeScreen.kt), falling
back to chapter 1 for any theme missing from the map.
"""
import json
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "db", "gita.db")
OUT_PATH = os.path.join(ROOT, "api", "topics", "list.json")

# Mirrors topicChapterMap in HomeScreen.kt exactly.
TOPIC_CHAPTER_MAP = {
    "Karma": 3, "Dharma": 2, "Purpose": 3, "Devotion": 12,
    "Knowledge": 7, "Self-Realization": 6, "Mindfulness": 6,
    "Leadership": 18, "Duty": 2, "Death": 2, "Equanimity": 2,
    "Fear": 1, "Detachment": 3, "Mind": 6, "Attachment": 2,
}
FALLBACK_CHAPTER = 1

THEME_QUERY = """
SELECT t.theme_id, tt.name
FROM theme t
JOIN theme_translation tt ON tt.theme_id = t.theme_id AND tt.lang_code = 'en'
ORDER BY t.theme_id
"""
VERSE_COUNT_QUERY = "SELECT count(*) FROM verse_theme WHERE theme_id = ?"
CHAPTER_IMG_QUERY = "SELECT img_square FROM chapter WHERE chapter_number = ?"


def main():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    themes = db.execute(THEME_QUERY).fetchall()

    out = []
    for t in themes:
        name = t["name"]
        chapter_number = TOPIC_CHAPTER_MAP.get(name, FALLBACK_CHAPTER)
        img_square = db.execute(CHAPTER_IMG_QUERY, (chapter_number,)).fetchone()[0]
        verse_count = db.execute(VERSE_COUNT_QUERY, (t["theme_id"],)).fetchone()[0]
        out.append({
            "name": name,
            "image_square": img_square,
            "verse_count": verse_count,
        })
    db.close()

    assert len(out) == 15, f"expected 15 topics, got {len(out)}"
    assert all(o["verse_count"] > 0 for o in out)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open(OUT_PATH, encoding="utf-8") as f:
        json.load(f)  # round-trip validity check

    print(f"wrote {len(out)} topics to {OUT_PATH}")


if __name__ == "__main__":
    main()
