with open('scratch/fill_ch9_v31_to_v34.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\\"', '"')

lines = text.splitlines()
out = []
for line in lines:
    l = line.strip()
    if l.startswith("'en': '9.31 Sri Ramanuja"):
        out.append('        "en": "9.31 Sri Ramanuja states: By the power of devotion, all sins are expelled and the soul swiftly becomes righteous, attaining eternal peace. O Kaunteya, declare boldly: My devotee never perishes!",')
    elif l.startswith("'be': '৯.৩১ শ্রী রামানুজ"):
        out.append('        "be": "৯.৩১ শ্রী রামানুজ বলেছেন: ভগবদ্ ভক্তির প্রভাবে জীবের সমস্ত পাপ নিরস্ত হয়ে যায় এবং সে শীঘ্র ই পরমকল্যাণময় ধর্মাচ্ছা হয়ে নিত্য শান্তি পায়। হে কৌন্তেয়! তুমি সভায় প্রতিজ্ঞা করো যে প্রভুর ভক্ত কখনো বিনষ্ট হয় না।",')
    elif l.startswith("'ka': '೧೦.೩೧ ಶ್ರೀ ರಾಮಾನುಜರು"):
        out.append('        "ka": "೧೦.೩೧ ಶ್ರೀ ರಾಮಾನುಜರು ಹೇಳುತ್ತಾರೆ: ಭಗವದ್ಭಕ್ತಿಯ ಪ್ರಭಾವದಿಂದ ಜೀವಿಯ ಸಮಸ್ತ ಪಾಪಗಳೂ ನಿರಸ್ತವಾಗುತ್ತವೆ ಹಾಗೂ ಅವನು ಶೀಘ್ರದಲ್ಲೇ ಪರಮಕಲ್ಯಾಣಮಯ ಧರ್ಮಾತ್ಮನಾಗಿ ನಿತ್ಯ ಶಾಂತಿಯನ್ನು ಪಡೆಯುತ್ತಾನೆ. ಹೇ ಕೌಂತೇಯ! ನೀನು ಸಭೆಯಲ್ಲಿ ಪ್ರತಿಜ್ಞೆ ಮಾಡು: ಪ್ರಭುವಿನ ಭಕ್ತನು ಎಂದಿಗೂ ವಿನಾಶ ಹೊಂದುವುದಿಲ್ಲ.",')
    elif l.startswith("'ka': '೧೦.೩೧ ಅವನು ಶೀಘ್ರವಾಗಿಯೇ"):
        out.append('        "ka": "೧೦.೩೧ ಅವನು ಶೀಘ್ರವಾಗಿಯೇ ಧರ್ಮಾತ್ಮನಾಗುತ್ತಾನೆ ಹಾಗೂ ಶಾಶ್ವತವಾದ ಪರಮ ಶಾಂತಿಯನ್ನು ಪಡೆಯುತ್ತಾನೆ. ಹೇ ಕೌಂತೇಯ! ನೀನು ಪ್ರತಿಜ್ಞಾಪೂರ್ವಕವಾಗಿ ನಿಶ್ಚಯವಾಗಿ ತಿಳಿ, ನನ್ನ ಭಕ್ತನು ಎಂದಿಗೂ ನಷ್ಟ ಹೊಂದುವುದಿಲ್ಲ.",')
    else:
        out.append(line)

with open('scratch/fill_ch9_v31_to_v34.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out) + '\n')
