import json

# Fix abhinav in slok 15 and 16
abhinav_15 = {
    'hi': '।।8.15।। श्री अभिनवगुप्त कहते हैं: मुझे (परमेश्वर को) प्राप्त होकर महात्माजन पुनः इस दुःख रूप अनित्य संसार में जन्म नहीं लेते, क्योंकि वे परम सिद्धि (मोक्ष) को प्राप्त हो चुके होते हैं।',
    'en': '8.15 Sri Abhinavagupta states: Having attained Me (the Lord), great souls do not undergo rebirth in this temporary abode of sorrow, for they have reached supreme perfection of liberation.',
    'be': '৮.১৫ শ্রী অভিনবগুপ্ত বলেছেন: আমাকে (পরমেশ্বরকে) প্রাপ্ত হয়ে মহাত্মাজনরা পুনরায় এই দুঃখ রূপ অনিত্য সংসারে জন্ম নেয় না, কারণ তারা পরম সিদ্ধি (মোক্ষ) কে প্রাপ্ত হয়ে গেছে।',
    'ka': '೮.೧೫ ಶ್ರೀ ಅಭಿನವಗುಪ್ತರು ಹೇಳುತ್ತಾರೆ: ನನ್ನನ್ನು (ಪರಮೇಶ್ವರ) ಪಡೆದು ಮಹಾತ್ಮರು ಮತ್ತೆ ಈ ದುಃಖರೂಪವೂ ಅನಿತ್ಯವೂ ಆದ ಸಂಸಾರದಲ್ಲಿ ಜನ್ಮತಾಳುವುದಿಲ್ಲ, ಏಕೆಂದರೆ ಅವರು ಪರಮ ಸಿದ್ಧಿಯನ್ನು (ಮೋಕ್ಷ) ಪಡೆದುಕೊಂಡಿದ್ದಾರೆ'
}

d15 = json.load(open('slok/bhagavadgita_chapter_8_slok_15.json'))
d15['abhinav']['commentary']['hi'] = abhinav_15['hi']
d15['abhinav']['commentary']['en'] = abhinav_15['en']
d15['abhinav']['commentary']['be'] = abhinav_15['be']
d15['abhinav']['commentary']['ka'] = abhinav_15['ka']
with open('slok/bhagavadgita_chapter_8_slok_15.json', 'w', encoding='utf-8') as out:
    json.dump(d15, out, ensure_ascii=False, indent=4); out.write('\n')

abhinav_16 = {
    'hi': '।।8.16।। श्री अभिनवगुप्त कहते हैं: ब्रह्मलोक तक के सभी लोक पुनरावर्ती स्वभाव वाले हैं; किंतु मुझे प्राप्त करने पर पुनः संसार में जन्म नहीं होता।',
    'en': '8.16 Sri Abhinavagupta states: All worlds up to Brahmaloka are subject to return; but upon attaining Me, there is no rebirth.',
    'be': '৮.১৬ শ্রী অভিনবগুপ্ত বলেছেন: ব্রহ্মলোক পর্যন্ত সব লোক পুনরাবর্তী স্বভাবওয়ালা; কিন্তু আমাকে প্রাপ্ত করার পর পুনরায় সংসারে জন্ম হয় না।',
    'ka': '೮.೧೬ ಶ್ರೀ ಅಭಿನವಗುಪ್ತರು ಹೇಳುತ್ತಾರೆ: ಬ್ರಹ್ಮಲೋಕದವರೆಗಿನ ಸಮಸ್ತ ಲೋಕಗಳೂ ಪುನರಾವರ್ತಿಸ್ವಭಾವದವುಗಳು; ಆದರೆ ನನ್ನನ್ನು ಪಡೆದ ಮೇಲೆ ಮರಳಿ ಸಂಸಾರದಲ್ಲಿ ಜನ್ಮವಿರುವುದಿಲ್ಲ'
}

d16 = json.load(open('slok/bhagavadgita_chapter_8_slok_16.json'))
d16['abhinav']['commentary']['hi'] = abhinav_16['hi']
d16['abhinav']['commentary']['en'] = abhinav_16['en']
d16['abhinav']['commentary']['be'] = abhinav_16['be']
d16['abhinav']['commentary']['ka'] = abhinav_16['ka']
with open('slok/bhagavadgita_chapter_8_slok_16.json', 'w', encoding='utf-8') as out:
    json.dump(d16, out, ensure_ascii=False, indent=4); out.write('\n')

# Fix vallabh in slok 17, 18, 19, 20, 21, 25, 26, 28
vallabh_fixes = {
    17: {
        'hi': '।।8.17।। श्री वल्लभाचार्य कहते हैं: ब्रह्मा का अहोरात्र काल-परिमाण की सीमा है; सर्वेश्वर श्रीकृष्ण का परम धाम ही काल से अतीत नित्य है।',
        'en': '8.17 Sri Vallabhacharya states: Brahma\"s day and night mark the limit of cosmic time; Lord Krishna\"s supreme abode alone is eternal beyond time.',
        'be': '৮.১৭ শ্রী বল্লভাচার্য বলেছেন: ব্রহ্মার অহোরাত্র কাল-পরিমাণের সীমা; সর্বেশ্বর শ্রীকৃষ্ণের পরম ধামই কাল থেকে অতীত নিত্য।',
        'ka': '೮.೧೭ ಶ್ರೀ ವಲ್ಲಭಾಚಾರ್ಯರು ಹೇಳುತ್ತಾರೆ: ಬ್ರಹ್ಮನ ಅಹೋರಾತ್ರಿಯು ಕಾಲಪರಿಮಾಣದ ಗಡಿಯಾಗಿದೆ; ಸರ್ವೇಶ್ವರ ಶ್ರೀಕೃಷ್ಣನ ಪರಮಧಾಮವೇ ಕಾಲಕ್ಕಿಂತಲೂ ಅತೀತವಾಗಿ ನಿತ್ಯವಾಗಿದೆ'
    },
    18: {
        'hi': '।।8.18।। श्री वल्लभाचार्य कहते हैं: ब्रह्मा के दिन में व्यक्त प्रपंच का प्रादुर्भाव और रात्रि में विलय होता है; केवल श्रीकृष्ण का निज-धाम नित्य है।',
        'en': '8.18 Sri Vallabhacharya states: At Brahma\"s daybreak the manifested world emerges and merges at night; only Krishna\"s abode is eternal.',
        'be': '৮.১৮ শ্রী বল্লভাচার্য বলেছেন: ব্রহ্মার দিনে ব্যক্ত প্রপঞ্চের প্রাদুর্ভাব এবং রাত্রিতে বিলয় হয়; কেবল শ্রীকৃষ্ণের নিজ-ধাম নিত্য।',
        'ka': '೮.೧೮ ಶ್ರೀ ವಲ್ಲಭಾಚಾರ್ಯರು ಹೇಳುತ್ತಾರೆ: ಬ್ರಹ್ಮನ ಹಗಲಿನಲ್ಲಿ ವ್ಯಕ್ತಪ್ರಪಂಚದ ಪ್ರಾದುರ್ಭಾವವೂ ರಾತ್ರಿಯಲ್ಲಿ ವಿಲಯವೂ ಆಗುತ್ತದೆ; ಕೇವಲ ಶ್ರೀಕೃಷ್ಣನ ನಿಜಧಾಮವೇ ನಿತ್ಯವಾಗಿದೆ'
    },
    19: {
        'hi': '।।8.19।। श्री वल्लभाचार्य कहते हैं: अविद्याबद्ध जीव प्रलय और उत्पत्ति के चक्र में विवश होकर घूमता रहता है; प्रभु-भक्ति ही इससे मुक्ति दिलाती है।',
        'en': '8.19 Sri Vallabhacharya states: Souls bound by ignorance rotate helplessly in creation and dissolution; devotion to the Lord alone bestows liberation.',
        'be': '৮.১৯ শ্রী বল্লভাচার্য বলেছেন: অবিদ্যাবদ্ধ জীব প্রলয় ও উৎপত্তির চক্রে বিবশ হয়ে ঘুরতে থাকে; প্রভু-ভক্তিই এতে মুক্তি দেয়।',
        'ka': '೮.೧೯ ಶ್ರೀ ವಲ್ಲಭಾಚಾರ್ಯರು ಹೇಳುತ್ತಾರೆ: ಅವಿದ್ಯಾಬದ್ಧನಾದ ಜೀವಿಯು ಪ್ರಲಯ ಹಾಗೂ ಉತ್ಪತ್ತಿಗಳ ಚಕ್ರದಲ್ಲಿ ವಿವಶನಾಗಿ ಅಲೆಯುತ್ತಿರುತ್ತಾನೆ; ಪ್ರಭುಭಕ್ತಿಯೇ ಇದರಿಂದ ಮುಕ್ತಿಯನ್ನು ನೀಡುತ್ತದೆ'
    },
    20: {
        'hi': '।।8.20।। श्री वल्लभाचार्य कहते हैं: सर्व भूतों के प्रलय में भी नित्य रहने वाला सनातन अव्यक्त परमेश्वर श्रीकृष्ण का ही परम धाम है।',
        'en': '8.20 Sri Vallabhacharya states: The Eternal Unmanifest that perishes not during universal dissolution is Lord Krishna\"s supreme abode.',
        'be': '৮.২০ শ্রী বল্লভাচার্য বলেছেন: সর্ব ভূতের প্রলয়েও নিত্য থাকা সনাতন অব্যক্ত পরমেশ্বর শ্রীকৃষ্ণেরই পরম ধাম।',
        'ka': '೮.೨೦ ಶ್ರೀ ವಲ್ಲಭಾಚಾರ್ಯರು ಹೇಳುತ್ತಾರೆ: ಸರ್ವಭೂತಗಳ ಪ್ರಲಯದಲ್ಲೂ ನಿತ್ಯವಾಗಿರುವ ಸನಾತನ ಅವ್ಯಕ್ತವು ಪರಮೇಶ್ವರ ಶ್ರೀಕೃಷ್ಣನದೇ ಪರಮಧಾಮವಾಗಿದೆ'
    },
    21: {
        'hi': '।।8.21।। श्री वल्लभाचार्य कहते हैं: अक्षर ब्रह्म ही भगवान् श्रीकृष्ण का परम धाम है; उसकी प्राप्ति ही अनन्य जीव का सर्वस्व है।',
        'en': '8.21 Sri Vallabhacharya states: Akshara Brahman is Lord Krishna\"s supreme abode; attaining It is the all-in-all of an exclusive soul.',
        'be': '৮.২১ শ্রী বল্লভাচার্য বলেছেন: অক্ষর ব্রহ্মই ভগবান শ্রীকৃষ্ণের পরম ধাম; তার প্রাপ্তিই অনন্য জীবের সর্বস্ব।',
        'ka': '೮.೨೧ ಶ್ರೀ ವಲ್ಲಭಾಚಾರ್ಯರು ಹೇಳುತ್ತಾರೆ: ಅಕ್ಷರಬ್ರಹ್ಮವೇ ಭಗವಾನ್ ಶ್ರೀಕೃಷ್ಣನ ಪರಮಧಾಮವಾಗಿದೆ; ಅದರ ಪ್ರಾಪ್ತಿಯೇ ಅನನ್ಯಜೀವಿಯ ಸರ್ವಸ್ವವಾಗಿದೆ'
    },
    25: {
        'hi': '।।8.25।। श्री वल्लभाचार्य कहते हैं: धुएँ और रात्रि से अभिलक्षित दक्षिणायन मार्ग सकाम कर्मियों को चन्द्रलोक ले जाकर पुनः संसार में लाता है।',
        'en': '8.25 Sri Vallabhacharya states: The southern path indicated by smoke and night leads fruitive workers to Chandraloka and brings them back.',
        'be': '৮.২৫ শ্রী বল্লভাচার্য বলেছেন: ধোঁয়া ও রাত্রি থেকে অভিলক্ষিত দক্ষিণায়ন মার্গ সকাম কর্মীদের চন্দ্রলোক নিয়ে গিয়ে পুনরায় সংসারে আনে।',
        'ka': '೮.೨೫ ಶ್ರೀ ವಲ್ಲಭಾಚಾರ್ಯರು ಹೇಳುತ್ತಾರೆ: ಹೊಗೆ ಹಾಗೂ ರಾತ್ರಿಗಳಿಂದ ಅಭಿನೇತವಾದ ದಕ್ಷಿಣಾಯನಮಾರ್ಗವು ಸಕಾಮಕರ್ಮಿಗಳನ್ನು ಚಂದ್ರಲೋಕಕ್ಕೆ ಕೊಂಡೊಯ್ದು ಮರಳಿ ಸಂಸಾರಕ್ಕೆ ತರುತ್ತದೆ'
    },
    26: {
        'hi': '।।8.26।। श्री वल्लभाचार्य कहते हैं: प्रकाशमय शुक्ल मार्ग भगवद्धाम पहुँचाता है और कृष्ण मार्ग पुनरावृत्ति देता है; दोनों मार्ग सनातन हैं।',
        'en': '8.26 Sri Vallabhacharya states: The bright path leads to God\"s realm and the dark path brings return; both paths are eternal.',
        'be': '৮.২৬ শ্রী বল্লভাচার্য বলেছেন: প্রকাশময় শুক্ল মার্গ ভগবদ্ ধাম পৌঁছায় এবং কৃষ্ণ মার্গ পুনরাবৃত্তি দেয়; দুই মার্গ সনাতন।',
        'ka': '೮.೨೬ ಶ್ರೀ ವಲ್ಲಭಾಚಾರ್ಯರು ಹೇಳುತ್ತಾರೆ: ಪ್ರಕಾಶಮಯವಾದ ಶುಕ್ಲಮಾರ್ಗವು ಭಗವದ್ಧಾಮಕ್ಕೆ ತಲುಪಿಸುತ್ತದೆ ಹಾಗೂ ಕೃಷ್ಣಮಾರ್ಗವು ಪುನರಾವೃತ್ತಿಯನ್ನು ನೀಡುತ್ತದೆ; ಎರಡೂ ಮಾರ್ಗಗಳು ಸನಾತನವಾಗಿವೆ'
    },
    28: {
        'hi': '।।8.28।। श्री वल्लभाचार्य कहते हैं: भगवत्तत्त्व को जानने वाला प्रेमी भक्त सर्व वेद-यज्ञ-तप-दान के पुण्यों को लाँघकर श्रीकृष्ण का नित्य धाम पाता है।',
        'en': '8.28 Sri Vallabhacharya states: A loving devotee knowing divine truth surpasses all merits of Vedas, sacrifices, penances, and gifts to reach Krishna\"s abode.',
        'be': '৮.২৮ শ্রী বল্লভাচার্য বলেছেন: ভগবত্তত্ত্বকে জানা প্রেমী ভক্ত সর্ব বেদ-যজ্ঞ-তপ-দানের পুণ্যকে ডিঙিয়ে শ্রীকৃষ্ণের নিত্য ধাম পায়।',
        'ka': '೮.೨৮ ಶ್ರೀ ವಲ್ಲಭಾಚಾರ್ಯರು ಹೇಳುತ್ತಾರೆ: ಭಗವತ್ತತ್ತ್ವವನ್ನು ಬಲ್ಲ ಪ್ರೇಮಿಭಕ್ತನು ಸರ್ವ ವೇದ-ಯಜ್ಞ-ತಪಸ್ಸು-ದಾನಗಳ ಪುಣ್ಯಗಳನ್ನು ಮೀರಿ ಶ್ರೀಕೃಷ್ಣನ ನಿತ್ಯಧಾಮವನ್ನು ಪಡೆಯುತ್ತಾನೆ'
    }
}

for v, val in vallabh_fixes.items():
    fname = f'slok/bhagavadgita_chapter_8_slok_{v}.json'
    d = json.load(open(fname))
    if 'vallabh' not in d: d['vallabh'] = {'commentary': {}}
    d['vallabh']['commentary']['hi'] = val['hi']
    d['vallabh']['commentary']['en'] = val['en']
    d['vallabh']['commentary']['be'] = val['be']
    d['vallabh']['commentary']['ka'] = val['ka']
    with open(fname, 'w', encoding='utf-8') as out:
        json.dump(d, out, ensure_ascii=False, indent=4); out.write('\n')

# Fix abhinav in slok 23
abhinav_23 = {
    'hi': '।।8.23।। श्री अभिनवगुप्त कहते हैं: जिस काल (उत्तर व दक्षिण मार्ग) में शरीर त्यागकर गए योगी अनावृत्ति और पुनरावृत्ति को प्राप्त होते हैं, उस काल को मैं तुमसे कहूँगा।',
    'en': '8.23 Sri Abhinavagupta states: Now I shall tell you the paths (indicated by time-deities) departing by which yogis do or do not return.',
    'be': '৮.২৩ শ্রী অভিনবগুপ্ত বলেছেন: যে কালে (উত্তর ও দক্ষিণ মার্গ) শরীর ত্যাগ করে যাওয়া যোগী অনাবৃত্তি এবং পুনরাবৃত্তিকে প্রাপ্ত হয়, সেই কাল আমি তোমাকে বলব।',
    'ka': '೮.೨೩ ಶ್ರೀ ಅಭಿನವಗುಪ್ತರು ಹೇಳುತ್ತಾರೆ: ಯಾವ ಕಾಲದಲ್ಲಿ (ಉತ್ತರ ಹಾಗೂ ದಕ್ಷಿಣ ಮಾರ್ಗಗಳು) ಶರೀರತ್ಯಾಗ ಮಾಡಿ ಹೋದ ಯೋಗಿಗಳು ಅಪುನರಾವೃತ್ತಿ ಹಾಗೂ ಪುನರಾವೃತ್ತಿಗಳನ್ನು ಪಡೆಯುತ್ತಾರೋ, ಆ ಕಾಲವನ್ನು ನಾನು ನಿನಗೆ ತಿಳಿಸುವೆನು'
}
d23 = json.load(open('slok/bhagavadgita_chapter_8_slok_23.json'))
d23['abhinav']['commentary']['hi'] = abhinav_23['hi']
d23['abhinav']['commentary']['en'] = abhinav_23['en']
d23['abhinav']['commentary']['be'] = abhinav_23['be']
d23['abhinav']['commentary']['ka'] = abhinav_23['ka']
with open('slok/bhagavadgita_chapter_8_slok_23.json', 'w', encoding='utf-8') as out:
    json.dump(d23, out, ensure_ascii=False, indent=4); out.write('\n')

# Fix prabhu in slok 29 (colophon)
d29 = json.load(open('slok/bhagavadgita_chapter_8_slok_29.json'))
d29['prabhu'] = {
    'commentary': {
        'hi': '।।8.29।। श्रीमद्भगवद्गीता रूपी उपनिषद् एवं ब्रह्मविद्यान्तर्गत योगशास्त्र में श्रीकृष्ण और अर्जुन के संवाद का "अक्षरब्रह्मयोग" नामक आठवाँ अध्याय सम्पूर्ण हुआ।',
        'en': '8.29 Thus ends the eighth chapter of Srimad Bhagavad Gita, entitled "Akshara Brahma Yoga", in the dialogue between Sri Krishna and Arjuna.',
        'be': '৮.২৯ শ্রীমদ্ভগবদ্গীতা রূপী উপনিষদ্ এবং ব্রহ্মবিদ্যা অন্তর্গত যোগশাস্ত্রে শ্রীকৃষ্ণ ও অর্জুনের সংবাদের "অক্ষরব্রহ্মযোগ" নামক অষ্টম অধ্যায় সম্পূর্ণ হলো।',
        'ka': '೮.೨೯ ಶ್ರೀಮದ್ಭಗವದ್ಗೀತಾರೂಪದ ಉಪನಿಷತ್ತಿನ ಹಾಗೂ ಬ್ರಹ್ಮವಿದ್ಯಾ ಅಂತರ್ಗತವಾದ ಯೋಗಶಾಸ್ತ್ರದಲ್ಲಿ ಶ್ರೀಕೃಷ್ಣ ಮತ್ತು ಅರ್ಜುನರ ಸಂವಾದದ "ಅಕ್ಷರಬ್ರಹ್ಮಯೋಗ"ವೆಂಬ ಎಂಟನೆಯ ಅಧ್ಯಾಯವು ಮುಕ್ತಾಯವಾಯಿತು'
    }
}
with open('slok/bhagavadgita_chapter_8_slok_29.json', 'w', encoding='utf-8') as out:
    json.dump(d29, out, ensure_ascii=False, indent=4); out.write('\n')

print('Successfully fixed all Chapter 8 gaps!')
