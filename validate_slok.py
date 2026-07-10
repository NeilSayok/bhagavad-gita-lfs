import sys, json, re

def validate(f):
    dev = re.compile(r'[ऀ-ॿ]')
    beng = re.compile(r'[ঀ-৿]')
    kan = re.compile(r'[ಀ-೿]')
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        print(f"FAIL: {f} is not valid JSON. Error: {e}")
        return False
        
    bad = []
    empt = 0
    for k, v in d.items():
        if isinstance(v, dict) and 'commentary' in v:
            c = v['commentary']
            for l in ('hi', 'en', 'be', 'ka'):
                if not c.get(l, '').strip():
                    empt += 1
            if c.get('en', '').strip().startswith('[Translation'):
                bad.append(k+'.en')
            be = c.get('be', '').strip()
            ka = c.get('ka', '').strip()
            if be and dev.search(be) and not beng.search(be):
                bad.append(k+'.be')
            if ka and dev.search(ka) and not kan.search(ka):
                bad.append(k+'.ka')
            for l in ('hi', 'en', 'be', 'ka'):
                val = c.get(l)
                if not isinstance(val, str):
                    bad.append(f'{k}.{l} (type {type(val)})')
                    
    if empt == 0 and len(bad) == 0:
        print(f"SUCCESS: {f} validated successfully. 0 empty, 0 bogus.")
        return True
    else:
        print(f"FAIL: {f} has {empt} empty slots, {len(bad)} bogus/bad fields: {bad}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_slok.py <path_to_json>")
        sys.exit(1)
    validate(sys.argv[1])
