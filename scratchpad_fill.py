import json,io,sys

def fill(path, data):
    with open(path,encoding='utf-8') as f:
        d=json.load(f)
    for comm,langs in data.items():
        c=d[comm]['commentary']
        for lang,txt in langs.items():
            if c.get(lang,'')=='':
                c[lang]=txt
            else:
                # do not overwrite existing
                pass
    with open(path,'w',encoding='utf-8') as f:
        json.dump(d,f,ensure_ascii=False,indent=4)
        f.write('\n')
    # verify
    with open(path,encoding='utf-8') as f:
        d2=json.load(f)
    empt=[]
    for k,v in d2.items():
        if isinstance(v,dict) and 'commentary' in v:
            for lang in ('hi','en','be','ka'):
                if v['commentary'].get(lang,'')=='':
                    empt.append(f"{k}.{lang}")
    print(path,"OK, empty:",empt)

print("helper loaded")
