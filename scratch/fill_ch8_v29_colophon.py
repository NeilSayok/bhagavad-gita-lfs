import json

f = 'slok/bhagavadgita_chapter_8_slok_29.json'
d = json.load(open(f))

colophon_data = {
    'hi': '।। अध्याय 8 का महात्म्य / उपसंहार ।। इस प्रकार श्रीमद्भगवद्गीता रूपी उपनिषद्, ब्रह्मविद्या तथा योगशास्त्र स्वरूप श्रीकृष्ण-अर्जुन संवाद में "अक्षरब्रह्मयोग" नामक आठवाँ अध्याय सम्पूर्ण हुआ।',
    'en': '।। Chapter 8 Summary / Colophon ।। Thus ends the eighth chapter entitled "Akshara Brahma Yoga" (The Yoga of the Imperishable Brahman) in the dialogue between Lord Krishna and Arjuna in the Srimad Bhagavad Gita, the Upanishad, the science of Brahman and scriptures of Yoga.',
    'be': '।। অধ্যায় ৮ এর মাহাত্ম্য / উপসংহার ।। এই ভাবে শ্রীমদ্ভগবদ্গীতা রূপী উপনিষদ্, ব্রহ্মবিদ্যা তথা যোগশাস্ত্র স্বরূপ শ্রীকৃষ্ণ-অর্জুন সংবাদে "অক্ষরব্রহ্মযোগ" নামক অষ্টম অধ্যায় সম্পূর্ণ হলো।',
    'ka': '।। ಅಧ್ಯಾಯ ೮ ರ ಮಾಹಾತ್ಮ್ಯ / ಉಪಸಂಹಾರ ।। ಈ ರೀತಿ ಶ್ರೀಮದ್ಭಗವದ್ಗೀತೆಯೆಂಬ ಉಪನಿಷತ್ತು, ಬ್ರಹ್ಮವಿದ್ಯೆಯೂ ಯೋಗಶಾಸ್ತ್ರವೂ ಆದ ಶ್ರೀಕೃಷ್ಣ-ಅರ್ಜುನ ಸಂವಾದದಲ್ಲಿ "ಅಕ್ಷರಬ್ರಹ್ಮಯೋಗ"ವೆಂಬ ಎಂಟನೆಯ ಅಧ್ಯಾಯವು ಸಂಪೂರ್ಣವಾಯಿತು.'
}

for k in d.keys():
    if k in ('_id', 'chapter', 'verse', 'speaker', 'slok', 'transliteration'): continue
    if isinstance(d[k], dict) and 'commentary' in d[k]:
        c = d[k]['commentary']
        c['hi'] = colophon_data['hi']
        c['en'] = colophon_data['en']
        c['be'] = colophon_data['be']
        c['ka'] = colophon_data['ka']

with open(f, 'w', encoding='utf-8') as out:
    json.dump(d, out, ensure_ascii=False, indent=4)
    out.write('\n')

print('Chapter 8 Verse 29 (Colophon) populated successfully!')
