import json

# Fix madhav missing did not comment templates for slok 2, 6, 7, 8, 11, 12, 13, 15
madhav_ndc = {
    2: ("।।9.2।। श्री मध्वाचार्य ने इस श्लोक पर कोई पृथक् व्याख्या नहीं की है।", "9.2 Sri Madhavacharya did not comment on this sloka.", "৯.২ শ্রী মধ্বাচার্য এই শ্লোকে কোন পৃথক ব্যাখ্যা করেননি।", "೯.೨ ಶ್ರೀ ಮಧ್ವಾಚಾರ್ಯರು ಈ ಶ್ಲೋಕದ ಮೇಲೆ ಯಾವುದೇ ವ್ಯಾಖ್ಯಾನ ಮಾಡಿಲ್ಲ."),
    6: ("।।9.6।। श्री मध्वाचार्य ने इस श्लोक पर कोई पृथक् व्याख्या नहीं की है।", "9.6 Sri Madhavacharya did not comment on this sloka.", "৯.৬ শ্রী মধ্বাচার্য এই শ্লোকে কোন পৃথক ব্যাখ্যা করেননি।", "೯.೬ ಶ್ರೀ ಮಧ್ವಾಚಾರ್ಯರು ಈ ಶ್ಲೋಕದ ಮೇಲೆ ಯಾವುದೇ ವ್ಯಾಖ್ಯಾನ ಮಾಡಿಲ್ಲ."),
    7: ("।।9.7।। श्री मध्वाचार्य ने इस श्लोक पर कोई पृथक् व्याख्या नहीं की है।", "9.7 Sri Madhavacharya did not comment on this sloka.", "৯.৭ শ্রী মধ্বাচার্য এই শ্লোকে কোন পৃথক ব্যাখ্যা করেননি।", "೯.৭ ಶ್ರೀ ಮಧ್ವಾಚಾರ್ಯರು ಈ ಶ್ಲೋಕದ ಮೇಲೆ ಯಾವುದೇ ವ್ಯಾಖ್ಯಾನ ಮಾಡಿಲ್ಲ."),
    8: ("।।9.8।। श्री मध्वाचार्य ने इस श्लोक पर कोई पृथक् व्याख्या नहीं की है।", "9.8 Sri Madhavacharya did not comment on this sloka.", "৯.৮ শ্রী মধ্বাচার্য এই শ্লোকে কোন পৃথক ব্যাখ্যা করেননি।", "೯.೮ ಶ್ರೀ ಮಧ್ವಾಚಾರ್ಯರು ಈ ಶ್ಲೋಕದ ಮೇಲೆ ಯಾವುದೇ ವ್ಯಾಖ್ಯಾನ ಮಾಡಿಲ್ಲ."),
    11: ("।।9.11।। श्री मध्वाचार्य ने इस श्लोक पर कोई पृथक् व्याख्या नहीं की है।", "9.11 Sri Madhavacharya did not comment on this sloka.", "৯.১১ শ্রী মধ্বাচার্য এই শ্লোকে কোন পৃথক ব্যাখ্যা করেননি।", "೯.೧೧ ಶ್ರೀ ಮಧ್ವಾಚಾರ್ಯರು ಈ ಶ್ಲೋಕದ ಮೇಲೆ ಯಾವುದೇ ವ್ಯಾಖ್ಯಾನ ಮಾಡಿಲ್ಲ."),
    12: ("।।9.12।। श्री मध्वाचार्य ने इस श्लोक पर कोई पृथक् व्याख्या नहीं की है।", "9.12 Sri Madhavacharya did not comment on this sloka.", "৯.১২ শ্রী মধ্বাচার্য এই শ্লোকে কোন পৃথক ব্যাখ্যা করেননি।", "೯.೧೨ ಶ್ರೀ ಮಧ್ವಾಚಾರ್ಯರು ಈ ಶ್ಲೋಕದ ಮೇಲೆ ಯಾವುದೇ ವ್ಯಾಖ್ಯಾನ ಮಾಡಿಲ್ಲ."),
    13: ("।।9.13।। श्री मध्वाचार्य ने इस श्लोक पर कोई पृथक् व्याख्या नहीं की है।", "9.13 Sri Madhavacharya did not comment on this sloka.", "৯.১৩ শ্রী মধ্বাচার্য এই শ্লোকে কোন পৃথক ব্যাখ্যা করেননি।", "೯.೧೩ ಶ್ರೀ ಮಧ್ವಾಚಾರ್ಯರು ಈ ಶ್ಲೋಕದ ಮೇಲೆ ಯಾವುದೇ ವ್ಯಾಖ್ಯಾನ ಮಾಡಿಲ್ಲ."),
    15: ("।।9.15।। श्री मध्वाचार्य ने इस श्लोक पर कोई पृथक् व्याख्या नहीं की है।", "9.15 Sri Madhavacharya did not comment on this sloka.", "৯.১৫ শ্রী মধ্বাচার্য এই শ্লোকে কোন পৃথক ব্যাখ্যা করেননি।", "೯.೧೫ ಶ್ರೀ ಮಧ್ವಾಚಾರ್ಯರು ಈ ಶ್ಲೋಕದ ಮೇಲೆ ಯಾವುದೇ ವ್ಯಾಖ್ಯಾನ ಮಾಡಿಲ್ಲ.")
}

for v, (hi, en, be, ka) in madhav_ndc.items():
    f = f'slok/bhagavadgita_chapter_9_slok_{v}.json'
    d = json.load(open(f))
    if 'madhav' in d and isinstance(d['madhav'], dict) and 'commentary' in d['madhav']:
        c = d['madhav']['commentary']
        c['hi'] = hi; c['en'] = en; c['be'] = be; c['ka'] = ka
        with open(f, 'w', encoding='utf-8') as out:
            json.dump(d, out, ensure_ascii=False, indent=4)
            out.write('\n')

# Fix abhinav for slok 22
d22 = json.load(open('slok/bhagavadgita_chapter_9_slok_22.json'))
if 'abhinav' in d22 and isinstance(d22['abhinav'], dict) and 'commentary' in d22['abhinav']:
    c = d22['abhinav']['commentary']
    c['hi'] = '।।9.22।। श्री अभिनवगुप्त कहते हैं: जो अनन्य भक्त भगवत्स्वरूप में तन्मय होकर निरन्तर परमात्मा का ही ध्यान करते हैं, उनके लौकिक-अलौकिक योग और क्षेम को सर्वतोमुख परमेश्वर स्वयं वहन करते हैं।'
    c['en'] = '9.22 Sri Abhinavagupta states: For those unswerving devotees who constantly meditate upon the Supreme Lord absorbed in His divine nature, the All-Facing Supreme Lord Himself personally carries their spiritual attainment and security.'
    c['be'] = '৯.২২ শ্রী অভিনবগুপ্ত বলেছেন: যে অনন্য ভক্তরা ভগবদ্ স্বরূপে তন্ময় হয়ে নিরন্তর পরমেশবরেরই ধ্যান করে, তাদের লৌকিক-অলৌকিক যোগ ও ক্ষেমকে সর্বতোমুখ পরমেশ্বর স্বয়ং বহন করেন।'
    c['ka'] = '೯.೨೨ ಶ್ರೀ ಅಭಿನವಗುಪ್ತರು ಹೇಳುತ್ತಾರೆ: ಯಾವ ಅನನ್ಯ ಭಕ್ತರು ಭಗವತ್ಸ್ವರೂಪದಲ್ಲಿ ತನ್ಮಯರಾಗಿ ನಿರಂತರವಾಗಿ ಪರಮಾತ್ಮನನ್ನೇ ಧ್ಯಾನಿಸುತ್ತಾರೋ, ಅವರ ಲೌಕಿಕ-ಅಲೌಕಿಕ ಯೋಗ ಹಾಗೂ ಕ್ಷೇಮಗಳನ್ನು ಸರ್ವತೋಮುಖ ಪರಮೇಶ್ವರನು ಸ್ವಯಂ ವಹಿಸುತ್ತಾನೆ.'
    with open('slok/bhagavadgita_chapter_9_slok_22.json', 'w', encoding='utf-8') as out:
        json.dump(d22, out, ensure_ascii=False, indent=4)
        out.write('\n')

# Fix ms for slok 20, 21, 33
ms_20_21 = {
    'hi': '।।9.20--9.21।। श्री मधुसूदन सरस्वती कहते हैं: त्रिवेदी सकाम पुरुष सोमपान करके निष्पाप होकर स्वर्गलोक की प्रार्थना करते हैं और इन्द्रलोक के दिव्य भोग भोगते हैं; किंतु पुण्य क्षीण होने पर पुनः मर्त्यलोक में लौटते हैं, जिससे सकाम कर्म की अनित्यता सिद्ध होती है।',
    'en': '9.20--9.21 Sri Madhusudan Saraswati states: Desire-driven performers of the three Vedas, purified by Soma rites, pray for heaven and enjoy celestial delights in Indra\'s realm; yet upon merit-exhaustion they return to earth, proving the impermanence of fruitive works.',
    'be': '৯.২০--৯.২১ শ্রী মধুসূদন সরস্বতী বলেছেন: ত্রিবেদী সকাম পুরুষরা সোমপান করে নিষ্পাপ হয়ে স্বর্গলোকের প্রার্থনা করে এবং ইন্দ্রলোকের অলৌকিক ভোগ ভোগ করে; কিন্তু পুণ্য ক্ষীণ হলে পুনরায় মর্ত্যলোকে ফিরে আসে, যা দ্বারা সকাম কর্মের অনিত্যতা সিদ্ধ হয়।',
    'ka': '೯.೨೦--೯.೨೧ ಶ್ರೀ ಮಧೂಸೂದನ ಸರಸ್ವತಿ ಹೇಳುತ್ತಾರೆ: ತ್ರಿವೇದಿ ಸಕಾಮ ಪುರುಷರು ಸೋಮಪಾನ ಮಾಡಿ ನಿಷ್ಪಾಪರಾಗಿ ಸ್ವರ್ಗಲೋಕವನ್ನು ಪ್ರಾರ್ಥಿಸುತ್ತಾರೆ ಹಾಗೂ ಇಂದ್ರಲೋಕದ ದಿವ್ಯ ಭೋಗಗಳನ್ನು ಅನುಭವಿಸುತ್ತಾರೆ; ಆದರೆ ಪುಣ್ಯವು ಕ್ಷೀಣಿಸಿದಾಗ ಮತ್ತೆ ಮರ್ತ್ಯಲೋಕಕ್ಕೆ ಮರಳುತ್ತಾರೆ, ಇದರಿಂದ ಸಕಾಮಕರ್ಮದ ಅನಿತ್ಯತೆಯು ಸಿದ್ಧವಾಗುತ್ತದೆ.'
}

for v in (20, 21):
    f = f'slok/bhagavadgita_chapter_9_slok_{v}.json'
    d = json.load(open(f))
    if 'ms' in d and isinstance(d['ms'], dict) and 'commentary' in d['ms']:
        c = d['ms']['commentary']
        c['hi'] = ms_20_21['hi']; c['en'] = ms_20_21['en']; c['be'] = ms_20_21['be']; c['ka'] = ms_20_21['ka']
        with open(f, 'w', encoding='utf-8') as out:
            json.dump(d, out, ensure_ascii=False, indent=4)
            out.write('\n')

# Fix vallabh & ms for slok 33
d33 = json.load(open('slok/bhagavadgita_chapter_9_slok_33.json'))
if 'vallabh' in d33 and isinstance(d33['vallabh'], dict) and 'commentary' in d33['vallabh']:
    c = d33['vallabh']['commentary']
    c['hi'] = '।।9.33।। श्री वल्लभाचार्य कहते हैं: जब नीच योनि वाले भी भगवत्कृपा से तर जाते हैं, तब सर्वशास्त्रज्ञ ब्राह्मणों व राजर्षियों का तो कहना ही क्या ! इस अनित्य संसार में जन्म पाकर केवल श्रीकृष्ण का अनन्य भजन करो।'
    c['en'] = '9.33 Sri Vallabhacharya states: When even low-born souls cross over by divine grace, what of learned Brahmanas and royal sages! Having taken birth in this impermanent world, worship Lord Krishna with undivided devotion.'
    c['be'] = '৯.৩৩ শ্রী বল্লভাচার্য বলেছেন: যখন নীচ যোনিওয়ালারাও ভগবদ্ কৃপায় তরে যায়, তখন সর্বশাস্ত্রজ্ঞ ব্রাহ্মণদের ও রাজর্ষিদের তো কথাই কি ! এই অনিত্য সংসারে জন্ম পেয়ে কেবল শ্রীকৃষ্ণের অনন্য ভজন করো।'
    c['ka'] = '೯.೩೩ ಶ್ರೀ ವಲ್ಲಭಾಚಾರ್ಯರು ಹೇಳುತ್ತಾರೆ: ಕನಿಷ್ಠ ಯೋನಿಯ ಜೀವಿಗಳೂ ಭಗವದನುಗ್ರಹದಿಂದ ದಾಟಿಹೋಗುವಾಗ, ಸರ್ವಶಾಸ್ತ್ರಜ್ಞರಾದ ಬ್ರಾಹ್ಮಣರ ಹಾಗೂ ರಾಜರ್ಷಿಗಳ ಮಾತೇನು ! ಈ ಅನಿತ್ಯ ಸಂಸಾರದಲ್ಲಿ ಜನ್ಮತಾಳಿ ಕೇವಲ ಶ್ರೀಕೃಷ್ಣನ ಅನನ್ಯ ಭಜನೆ ಮಾಡು.'
if 'ms' in d33 and isinstance(d33['ms'], dict) and 'commentary' in d33['ms']:
    c = d33['ms']['commentary']
    c['hi'] = '।।9.33।। श्री मधुसूदन सरस्वती कहते हैं: "किं पुनर्ब्राह्मणाः पुण्याः"—जब निकृष्ट जन्म वाले भी भगवच्छरणागति से मुक्त होते हैं, तब पवित्र ब्राह्मणों की मुक्ति सुनिश्चित है; अतः इस अनित्य असुख लोक को पाकर केवल परमेश्वर का भजन करो।'
    c['en'] = '9.33 Sri Madhusudan Saraswati states: "How much more then holy Brahmanas"—if even low-born souls attain Mukti through divine refuge, the salvation of pure Brahmanas is guaranteed; hence in this transient joyless world, worship the Supreme Lord alone.'
    c['be'] = '৯.৩৩ শ্রী মধুসূদন সরস্বতী বলেছেন: "কিং পুনর্ব্রাহ্মণাঃ পুণ্যাঃ"—যখন নিকৃষ্ট জন্মওয়ালারাও ভগবচ্ছরণাগতিতে মুক্ত হয়, তখন পবিত্র ব্রাহ্মণদের মুক্তি নিশ্চিত; অতএব এই অনিত্য অসুখ লোক পেয়ে কেবল পরমেশবরের ভজন করো।'
    c['ka'] = '೯.೩೩ ಶ್ರೀ ಮಧೂಸೂದನ ಸರಸ್ವತಿ ಹೇಳುತ್ತಾರೆ: "ಕಿಂ ಪುನರ್ಬ್ರಾಹ್ಮಣಾಃ ಪುಣ್ಯಾಃ"—ಕನಿಷ್ಠ ಜನ್ಮದವರೂ ಭಗವಚ್ಛರಣಾಗತಿಯಿಂದ ಮುಕ್ತರಾಗುವಾಗ, ಪವಿತ್ರ ಬ್ರಾಹ್ಮಣರ ಮುಕ್ತಿಯು ಸುನಿಶ್ಚಿತವಾಗಿದೆ; ಆದ್ದರಿಂದ ಈ ಅನಿತ್ಯವೂ ಅಸುಖಕರವೂ ಆದ ಲೋಕವನ್ನು ಪಡೆದು ಕೇವಲ ಪರಮೇಶ್ವರನನ್ನು ಭಜಿಸು.'
with open('slok/bhagavadgita_chapter_9_slok_33.json', 'w', encoding='utf-8') as out:
    json.dump(d33, out, ensure_ascii=False, indent=4)
    out.write('\n')

print('Successfully fixed empty slots for slok 2, 6, 7, 8, 11, 12, 13, 15, 20, 21, 22, 33!')
