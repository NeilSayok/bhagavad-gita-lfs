"""Build api/commentators/commentator-list.json (static, precomputed)

Generates the list of all 22 canonical commentators with their author keys,
display order, and names translated/transliterated into all 4 supported languages
(English, Hindi, Bengali, and Kannada).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "api", "commentators", "commentator-list.json")

COMMENTATORS = [
    {
        "id": 1,
        "key": "tej",
        "code": "tej",
        "author": "Swami Tejomayananda",
        "display_order": 0,
        "name": {
            "en": "Swami Tejomayananda",
            "hi": "स्वामी तेजोमयानन्द",
            "be": "স্বামী তেজোময়ানন্দ",
            "ka": "ಸ್ವಾಮಿ ತೇಜೋಮಯಾನಂದ"
        }
    },
    {
        "id": 2,
        "key": "siva",
        "code": "siva",
        "author": "Swami Sivananda",
        "display_order": 1,
        "name": {
            "en": "Swami Sivananda",
            "hi": "स्वामी शिवानन्द",
            "be": "স্বামী শিবানন্দ",
            "ka": "ಸ್ವಾಮಿ ಶಿವಾನಂದ"
        }
    },
    {
        "id": 3,
        "key": "purohit",
        "code": "purohit",
        "author": "Shri Purohit Swami",
        "display_order": 2,
        "name": {
            "en": "Shri Purohit Swami",
            "hi": "श्री पुरोहित स्वामी",
            "be": "শ্রী পুরোহিত স্বামী",
            "ka": "ಶ್ರೀ ಪುರೋಹಿತ ಸ್ವಾಮಿ"
        }
    },
    {
        "id": 4,
        "key": "chinmay",
        "code": "chinmay",
        "author": "Swami Chinmayananda",
        "display_order": 3,
        "name": {
            "en": "Swami Chinmayananda",
            "hi": "स्वामी चिन्मयानन्द",
            "be": "স্বামী চিন্ময়ানন্দ",
            "ka": "ಸ್ವಾಮಿ ಚಿನ್ಮಯಾನಂದ"
        }
    },
    {
        "id": 5,
        "key": "san",
        "code": "san",
        "author": "Dr.S.Sankaranarayan",
        "display_order": 4,
        "name": {
            "en": "Dr. S. Sankaranarayan",
            "hi": "डॉ. एस. शंकरनारायण",
            "be": "ড. এস. শঙ্করনারায়ণ",
            "ka": "ಡಾ. ಎಸ್. ಶಂಕರನಾರಾಯಣ"
        }
    },
    {
        "id": 6,
        "key": "adi",
        "code": "adi",
        "author": "Swami Adidevananda",
        "display_order": 5,
        "name": {
            "en": "Swami Adidevananda",
            "hi": "स्वामी आदिदेवानन्द",
            "be": "স্বামী আদিদেবানন্দ",
            "ka": "ಸ್ವಾಮಿ ಆದಿದೇವಾನಂದ"
        }
    },
    {
        "id": 7,
        "key": "gambir",
        "code": "gambir",
        "author": "Swami Gambirananda",
        "display_order": 6,
        "name": {
            "en": "Swami Gambirananda",
            "hi": "स्वामी गंभीरानन्द",
            "be": "স্বামী গম্ভীরানন্দ",
            "ka": "ಸ್ವಾಮಿ ಗಂಭೀರಾನಂದ"
        }
    },
    {
        "id": 8,
        "key": "madhav",
        "code": "madhav",
        "author": "Sri Madhavacharya",
        "display_order": 7,
        "name": {
            "en": "Sri Madhavacharya",
            "hi": "श्री मध्वाचार्य",
            "be": "শ্রী মধ্বাচার্য",
            "ka": "ಶ್ರೀ ಮಧ್ವಾಚಾರ್ಯ"
        }
    },
    {
        "id": 9,
        "key": "anand",
        "code": "anand",
        "author": "Sri Anandgiri",
        "display_order": 8,
        "name": {
            "en": "Sri Anandgiri",
            "hi": "श्री आनंदगिरि",
            "be": "শ্রী আনন্দগিরি",
            "ka": "ಶ್ರೀ ಆನಂದಗಿರಿ"
        }
    },
    {
        "id": 10,
        "key": "rams",
        "code": "rams",
        "author": "Swami Ramsukhdas",
        "display_order": 9,
        "name": {
            "en": "Swami Ramsukhdas",
            "hi": "स्वामी रामसुखदास",
            "be": "স্বামী রামসুখদাস",
            "ka": "ಸ್ವಾಮಿ ರಾಮಸುಖದಾಸ"
        }
    },
    {
        "id": 11,
        "key": "raman",
        "code": "raman",
        "author": "Sri Ramanuja",
        "display_order": 10,
        "name": {
            "en": "Sri Ramanuja",
            "hi": "श्री रामानुज",
            "be": "শ্রী রামানুজ",
            "ka": "ಶ್ರೀ ರಾಮಾನುಜ"
        }
    },
    {
        "id": 12,
        "key": "abhinav",
        "code": "abhinav",
        "author": "Sri Abhinav Gupta",
        "display_order": 11,
        "name": {
            "en": "Sri Abhinav Gupta",
            "hi": "श्री अभिनवगुप्त",
            "be": "শ্রী অভিনবগুপ্ত",
            "ka": "ಶ್ರೀ ಅಭಿನವಗುಪ್ತ"
        }
    },
    {
        "id": 13,
        "key": "sankar",
        "code": "sankar",
        "author": "Sri Shankaracharya",
        "display_order": 12,
        "name": {
            "en": "Sri Shankaracharya",
            "hi": "श्री शंकराचार्य",
            "be": "শ্রী শংকরাচার্য",
            "ka": "ಶ್ರೀ ಶಂಕರಾಚಾರ್ಯ"
        }
    },
    {
        "id": 14,
        "key": "jaya",
        "code": "jaya",
        "author": "Sri Jayatritha",
        "display_order": 13,
        "name": {
            "en": "Sri Jayatritha",
            "hi": "श्री जयतीर्थ",
            "be": "শ্রী জয়তীর্থ",
            "ka": "ಶ್ರೀ ಜಯತೀರ್ಥ"
        }
    },
    {
        "id": 15,
        "key": "vallabh",
        "code": "vallabh",
        "author": "Sri Vallabhacharya",
        "display_order": 14,
        "name": {
            "en": "Sri Vallabhacharya",
            "hi": "श्री वल्लभाचार्य",
            "be": "শ্রী বল্লভাচার্য",
            "ka": "ಶ್ರೀ ವಲ್ಲಭಾಚಾರ್ಯ"
        }
    },
    {
        "id": 16,
        "key": "ms",
        "code": "ms",
        "author": "Sri Madhusudan Saraswati",
        "display_order": 15,
        "name": {
            "en": "Sri Madhusudan Saraswati",
            "hi": "श्री मधुसूदन सरस्वती",
            "be": "শ্রী মধুসূদন সরস্বতী",
            "ka": "ಶ್ರೀ ಮಧುಸೂದನ ಸರಸ್ವತಿ"
        }
    },
    {
        "id": 17,
        "key": "srid",
        "code": "srid",
        "author": "Sri Sridhara Swami",
        "display_order": 16,
        "name": {
            "en": "Sri Sridhara Swami",
            "hi": "श्री श्रीधर स्वामी",
            "be": "শ্রী শ্রীধর স্বামী",
            "ka": "ಶ್ರೀ ಶ್ರೀಧರ ಸ್ವಾಮಿ"
        }
    },
    {
        "id": 18,
        "key": "dhan",
        "code": "dhan",
        "author": "Sri Dhanpati",
        "display_order": 17,
        "name": {
            "en": "Sri Dhanpati",
            "hi": "श्री धनपति",
            "be": "শ্রী ধনপতি",
            "ka": "ಶ್ರೀ ಧನಪತಿ"
        }
    },
    {
        "id": 19,
        "key": "venkat",
        "code": "venkat",
        "author": "Vedantadeshikacharya Venkatanatha",
        "display_order": 18,
        "name": {
            "en": "Vedantadeshikacharya Venkatanatha",
            "hi": "वेदान्तदेशिकाचार्य वेंकटनाथ",
            "be": "বেদান্তদেশিকাচার্য ভেঙ্কটনাথ",
            "ka": "ವೇದಾಂತದೇಶಿಕಾಚಾರ್ಯ ವೆಂಕಟನಾಥ"
        }
    },
    {
        "id": 20,
        "key": "puru",
        "code": "puru",
        "author": "Sri Purushottamji",
        "display_order": 19,
        "name": {
            "en": "Sri Purushottamji",
            "hi": "श्री पुरुषोत्तमजी",
            "be": "শ্রী পুরুষোত্তমজী",
            "ka": "ಶ್ರೀ ಪುರುಷೋತ್ತಮಜೀ"
        }
    },
    {
        "id": 21,
        "key": "neel",
        "code": "neel",
        "author": "Sri Neelkanth",
        "display_order": 20,
        "name": {
            "en": "Sri Neelkanth",
            "hi": "श्री नीलकंठ",
            "be": "শ্রী নীলকণ্ঠ",
            "ka": "ಶ್ರೀ ನೀಲಕಂಠ"
        }
    },
    {
        "id": 22,
        "key": "prabhu",
        "code": "prabhu",
        "author": "A.C. Bhaktivedanta Swami Prabhupada",
        "display_order": 21,
        "name": {
            "en": "A.C. Bhaktivedanta Swami Prabhupada",
            "hi": "ए.सी. भक्तिवेदान्त स्वामी प्रभुपाद",
            "be": "এ.সি. ভক্তিবেদান্ত স্বামী প্রভুপাদ",
            "ka": "ಎ.ಸಿ. ಭಕ್ತಿವೇದಾಂತ ಸ್ವಾಮಿ ಪ್ರಭುಪಾದ"
        }
    }
]


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(COMMENTATORS, f, ensure_ascii=False, indent=2)
        f.write("\n")

    with open(OUT_PATH, encoding="utf-8") as f:
        loaded = json.load(f)

    assert len(loaded) == 22, f"Expected 22 commentators, got {len(loaded)}"
    print(f"Successfully wrote {len(loaded)} commentators to {OUT_PATH}")


if __name__ == "__main__":
    main()
