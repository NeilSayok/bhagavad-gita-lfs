import json

colophon_data = {
    'hi': '।।6.48।। श्रीमद्भगवद्गीता रूपी उपनिषद् एवं ब्रह्मविद्यान्तर्गत योगशास्त्र में श्रीकृष्ण और अर्जुन के संवाद का "आत्मसंयमयोग" नामक छठा अध्याय सम्पूर्ण हुआ।',
    'en': '6.48 Thus ends the sixth chapter of Srimad Bhagavad Gita, entitled "Atma Samyama Yoga", in the dialogue between Sri Krishna and Arjuna.',
    'be': '৬.৪৮ শ্রীমদ্ভগবদ্গীতা রূপী উপনিষদ্ এবং ব্রহ্মবিদ্যা অন্তর্গত যোগশাস্ত্রে শ্রীকৃষ্ণ ও অর্জুনের সংবাদের "আত্মসংযমযোগ" নামক ষষ্ঠ অধ্যায় সম্পূর্ণ হলো।',
    'ka': '೬.೪೮ ಶ್ರೀಮದ್ಭಗವದ್ಗೀತಾರೂಪದ ಉಪನಿಷತ್ತಿನ ಹಾಗೂ ಬ್ರಹ್ಮವಿದ್ಯಾ ಅಂತರ್ಗತವಾದ ಯೋಗಶಾಸ್ತ್ರದಲ್ಲಿ ಶ್ರೀಕೃಷ್ಣ ಮತ್ತು ಅರ್ಜುನರ ಸಂವಾದದ "ಆತ್ಮಸಂಯಮಯೋಗ"ವೆಂಬ ಆರನೆಯ ಅಧ್ಯಾಯವು ಮುಕ್ತಾಯವಾಯಿತು.'
}

commentators = [
    'tej', 'siva', 'purohit', 'chinmay', 'san', 'adi', 'gambir', 'anand',
    'rams', 'raman', 'abhinav', 'sankar', 'madhav', 'jaya', 'vallabh', 'ms',
    'srid', 'dhan', 'venkat', 'puru', 'neel', 'prabhu'
]

d48 = json.load(open('slok/bhagavadgita_chapter_6_slok_48.json'))
for comm in commentators:
    d48[comm] = {
        'commentary': {
            'hi': colophon_data['hi'],
            'en': colophon_data['en'],
            'be': colophon_data['be'],
            'ka': colophon_data['ka']
        }
    }

with open('slok/bhagavadgita_chapter_6_slok_48.json', 'w', encoding='utf-8') as out:
    json.dump(d48, out, ensure_ascii=False, indent=4)
    out.write('\n')

print('Successfully populated Chapter 6 Colophon (slok_48.json)!')
