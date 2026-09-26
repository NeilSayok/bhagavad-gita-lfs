import os
import json
import argparse

def process_file(filepath, out_base_dir):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error reading JSON from {filepath}")
            return
    
    chapter = data.get('chapter')
    verse = data.get('verse')
    if chapter is None or verse is None:
        print(f"Skipping {filepath}, missing chapter or verse.")
        return

    # Discover available languages dynamically
    langs = set()
    for key in ['speaker', 'slok', 'life_application']:
        if key in data and isinstance(data[key], dict):
            langs.update(data[key].keys())
    
    # Check commentaries for languages too
    for key, value in data.items():
        if isinstance(value, dict) and 'commentary' in value and isinstance(value['commentary'], dict):
            langs.update(value['commentary'].keys())
            
    for lang in langs:
        content = []
        
        # Speaker
        speaker = data.get('speaker', {}).get(lang)
        if speaker:
            content.append(f"Speaker: {speaker}")
            
        # Slok
        slok = data.get('slok', {}).get(lang)
        if slok:
            content.append(f"Slok:\n{slok}")
            

        # Word Meanings
        word_meanings = data.get('word_meanings', [])
        if word_meanings:
            wm_lines = []
            for wm in word_meanings:
                sanskrit = wm.get('sanskrit', '')
                meaning = wm.get('meaning', {}).get(lang)
                if sanskrit and meaning:
                    wm_lines.append(f"{sanskrit} - {meaning}")
            if wm_lines:
                content.append("Word Meanings:\n" + "\n".join(wm_lines))
                
        # Life Application
        life_app = data.get('life_application', {}).get(lang)
        if life_app:
            content.append(f"Life Application:\n{life_app}")
            
        # Commentaries
        commentaries = []
        for key, value in data.items():
            if isinstance(value, dict) and 'author' in value and 'commentary' in value:
                author = value['author']
                comm = value['commentary'].get(lang)
                if comm:
                    commentaries.append(f"Commentary by {author}:\n{comm}")
        
        if commentaries:
            content.append("\n\n".join(commentaries))
            
        if not content:
            continue
            
        final_text = "\n\n".join(content)
        
        # Write to file
        lang_dir = os.path.join(out_base_dir, lang)
        os.makedirs(lang_dir, exist_ok=True)
        out_file = os.path.join(lang_dir, f"plain_chapter_{chapter}_slok_{verse}.txt")
        
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(final_text)

def main():
    parser = argparse.ArgumentParser(description="Generate RAG text files from slok JSONs")
    parser.add_argument('--test', action='store_true', help='Run only for chapter 1 slok 1')
    parser.add_argument('--input_dir', type=str, default='api/slok', help='Input directory containing JSON files')
    parser.add_argument('--output_dir', type=str, default='rag/slok', help='Output base directory for text files')
    
    args = parser.parse_args()
    
    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)
    
    if not os.path.exists(input_dir):
        print(f"Error: Input directory {input_dir} does not exist.")
        return

    if args.test:
        test_file = os.path.join(input_dir, 'bhagavadgita_chapter_1_slok_1.json')
        if os.path.exists(test_file):
            print(f"Running in test mode for: {test_file}")
            process_file(test_file, output_dir)
            print(f"Test mode completed. Check output in {output_dir}")
        else:
            print(f"Error: Test file {test_file} not found.")
    else:
        count = 0
        for filename in os.listdir(input_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(input_dir, filename)
                process_file(filepath, output_dir)
                count += 1
        print(f"Completed processing {count} files. Check output in {output_dir}")

if __name__ == "__main__":
    main()
