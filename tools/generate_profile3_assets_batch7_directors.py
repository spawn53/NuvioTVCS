from pathlib import Path
import json
from tools.generate_profile3_assets import gradient, add_glow, add_vignette, motif, rng_for, ROOT, REPO, BRANCH

ASSETS = [
    ("nuri-bilge-ceylan", ["landscape","window"], ((20,31,39),(100,77,56))),
    ("yilmaz-guney", ["landscape","city"], ((30,31,29),(107,66,43))),
    ("zeki-demirkubuz", ["corridor","window"], ((11,15,21),(57,42,42))),
    ("yesim-ustaoglu", ["landscape","house"], ((24,39,44),(96,76,58))),
    ("ingmar-bergman", ["portrait","surreal"], ((12,12,15),(63,61,66))),
    ("andrei-tarkovsky", ["landscape","surreal"], ((18,31,31),(84,76,57))),
    ("federico-fellini", ["surreal","period"], ((29,23,35),(116,70,74))),
    ("agnes-varda", ["portrait","city"], ((29,36,50),(123,80,92))),
    ("krzysztof-kieslowski", ["portrait","window"], ((20,28,45),(89,55,69))),
    ("michael-haneke", ["house","corridor"], ((17,19,22),(67,62,58))),
    ("chantal-akerman", ["house","window"], ((23,26,31),(79,67,61))),
    ("yasujiro-ozu", ["house","period"], ((31,31,29),(108,84,62))),
    ("hirokazu-kore-eda", ["house","group"], ((29,42,49),(116,84,62))),
    ("lee-chang-dong", ["city","landscape"], ((22,34,43),(101,69,54))),
    ("wong-kar-wai", ["neon-city","window"], ((8,12,23),(77,30,64))),
    ("edward-yang", ["city","window"], ((18,29,42),(79,68,70))),
    ("hou-hsiao-hsien", ["city","period"], ((26,33,36),(105,78,58))),
    ("abbas-kiarostami", ["landscape"], ((29,45,49),(124,98,63))),
    ("asghar-farhadi", ["house","corridor"], ((26,27,31),(88,61,53))),
    ("jafar-panahi", ["city","portrait"], ((22,29,38),(91,63,54))),
    ("satyajit-ray", ["period","city"], ((35,31,27),(124,85,53))),
    ("ousmane-sembene", ["landscape","group"], ((38,43,36),(127,80,47))),
    ("lucrecia-martel", ["house","surreal"], ((27,35,37),(98,66,63))),
]


def render(slug,kinds,palette,variant):
    size=(1280,720) if variant=="cover" else (1920,1080)
    rng=rng_for(slug,variant)
    img=gradient(size,*palette)
    img=add_glow(img,(int(size[0]*.72),int(size[1]*.28)),int(min(size)*.22),(220,163,100),58)
    for kind in kinds:
        img=motif(img,kind,rng)
    img=add_vignette(img)
    out=ROOT/"legendary-directors"/slug/f"{slug}-{variant}.webp"
    out.parent.mkdir(parents=True,exist_ok=True)
    img.save(out,"WEBP",quality=82,method=6)
    return out


def main():
    made=[]
    for slug,kinds,palette in ASSETS:
        for variant in ("cover","backdrop"):
            out=render(slug,kinds,palette,variant)
            made.append({"section":"legendary-directors","slug":slug,"variant":variant,"path":str(out),"rawUrl":f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{out.as_posix()}"})
    manifest=ROOT/"manifest-batch7-directors.json"
    manifest.write_text(json.dumps({"count":len(made),"assets":made},indent=2),encoding="utf-8")
    print(f"Generated {len(made)} director assets")

if __name__=="__main__":
    main()
