import json

colophon_data = {
    'hi': '।।7.31।। श्रीमद्भगवद्गीता रूपी उपनिषद् एवं ब्रह्मविद्यान्तर्गत योगशास्त्र में श्रीकृष्ण और अर्जुन के संवाद का "ज्ञानविज्ञानयोग" नामक सातवाँ अध्याय सम्पूर्ण हुआ।',
    'en': '7.31 Thus ends the seventh chapter of Srimad Bhagavad Gita, entitled "Jnana Vijnana Yoga", in the dialogue between Sri Krishna and Arjuna.',
    'be': '৭.৩১ শ্রীমদ্ভগবদ্গীতা রূপী উপনিষদ্ এবং ব্রহ্মবিদ্যা অন্তর্গত যোগশাস্ত্রে শ্রীকৃষ্ণ ও অর্জুনের সংবাদের "জ্ঞানবিজ্ঞানযোগ" নামক সপ্তম অধ্যায় সম্পূর্ণ হলো।',
    'ka': '೭.೩೧ ಶ್ರೀಮದ್ಭಗವದ್ಗೀತಾರೂಪದ ಉಪನಿಷತ್ತಿನ ಹಾಗೂ ಬ್ರಹ್ಮವಿದ್ಯಾ ಅಂತರ್ಗತವಾದ ಯೋಗಶಾಸ್ತ್ರದಲ್ಲಿ ಶ್ರೀಕೃಷ್ಣ ಮತ್ತು ಅರ್ಜುನರ ಸಂವಾದದ "ಜ್ಞಾನವಿಜ್ಞಾನಯೋಗ"ವೆಂಬ ಏಳನೆಯ ಅಧ್ಯಾಯವು ಮುಕ್ತಾಯವಾಯಿತು.'
}

commentators = [
    'tej', 'siva', 'purohit', 'chinmay', 'san', 'adi', 'gambir', 'anand',
    'rams', 'raman', 'abhinav', 'sankar', 'madhav', 'jaya', 'vallabh', 'ms',
    'srid', 'dhan', 'venkat', 'puru', 'neel', 'prabhu'
]

d31 = json.load(open('slok/bhagavadgita_chapter_7_slok_31.json'))
for comm in commentators:
    d31[comm] = {
        'commentary': {
            'hi': colophon_data['hi'],
            'en': colophon_data['en'],
            'be': colophon_data['be'],
            'ka': colophon_data['ka']
        }
    }

with open('slok/bhagavadgita_chapter_7_slok_31.json', 'w', encoding='utf-8') as out:
    json.dump(d31, out, ensure_ascii=False, indent=4)
    out.write('\n')

print('Successfully populated Chapter 7 Colophon (slok_31.json)!')
