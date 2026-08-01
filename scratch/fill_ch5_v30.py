import json

d30 = json.load(open('slok/bhagavadgita_chapter_5_slok_30.json'))

colophon_hi = "ॐ तत्सदिति श्रीमद्भगवद्गीतासूपनिषत्सु ब्रह्मविद्यायां योगशास्त्रे श्रीकृष्णार्जुनसंवादे 'संन्यासयोगो' नाम पञ्चमोऽध्यायः ॥५॥"
colophon_en = "Thus ends the fifth chapter, titled 'Samnyasa Yoga', of the Srimad Bhagavad Gita, the Upanishad, the science of the Absolute, the scripture of Yoga, and the dialogue between Sri Krishna and Arjuna."
colophon_be = "ওঁ তত্সদিতি শ্রীমদ্ভগবদ্গীতাসূপনিষত্সু ব্রহ্মবিদ্যাযাং যোগশাস্ত্রে শ্রীকৃষ্ণার্জুনসংবাদে 'সংন্যাসযোগো' নাম পঞ্চমোঽধ্যাযঃ ॥৫॥"
colophon_ka = "ಓಂ ತತ್ಸದಿತಿ ಶ್ರೀಮದ್ಭಗವದ್ಗೀತಾಸೂಪನಿಷತ್ಸು ಬ್ರಹ್ಮವಿದ್ಯಾಯಾಂ ಯೋಗಶಾಸ್ತ್ರೇ ಶ್ರೀಕೃಷ್ಣಾರ್ಜುನಸಂವಾದೇ 'ಸಂನ್ಯಾಸಯೋಗೋ' ನಾಮ ಪಞ್ಚಮೋಽಧ್ಯಾಯಃ ॥೫॥"

for k in d30.keys():
    if k in ('_id', 'chapter', 'verse', 'speaker', 'slok', 'transliteration'): continue
    if isinstance(d30[k], dict) and 'commentary' in d30[k]:
        c = d30[k]['commentary']
        c['hi'] = colophon_hi
        c['en'] = colophon_en
        c['be'] = colophon_be
        c['ka'] = colophon_ka

with open('slok/bhagavadgita_chapter_5_slok_30.json', 'w', encoding='utf-8') as out:
    json.dump(d30, out, ensure_ascii=False, indent=4)
    out.write('\n')

print('Chapter 5 Colophon (slok_30.json) successfully filled!')
