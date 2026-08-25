from pathlib import Path
import json
from tools.generate_profile3_assets import gradient, add_glow, add_vignette, motif, rng_for, ROOT, REPO, BRANCH

ASSETS = [
    ("production-studios-movies", "dreamworks-animation", ["surreal"], ((26,42,72),(93,78,126))),
    ("production-studios-movies", "neon", ["neon-city"], ((5,9,18),(47,19,52))),
    ("production-studios-movies", "studiocanal", ["city","landscape"], ((18,42,59),(91,93,80))),
    ("production-studios-movies", "pathe", ["period"], ((46,35,31),(135,89,55))),
    ("production-studios-movies", "working-title-films", ["indie"], ((20,31,42),(111,79,60))),
    ("production-studios-movies", "toho", ["city"], ((18,24,31),(97,66,52))),
    ("production-studios-movies", "cj-enm-entertainment", ["city","screens"], ((16,30,42),(68,76,102))),
    ("production-studios-movies", "bkm-film", ["city","group"], ((24,31,38),(111,71,49))),
    ("production-studios-series", "bbc-studios", ["screens"], ((17,28,42),(77,73,94))),
    ("production-studios-series", "sky-studios", ["landscape","screens"], ((13,31,52),(69,91,130))),
    ("production-studios-series", "itv-studios", ["screens","group"], ((25,24,39),(99,60,78))),
    ("production-studios-series", "banijay", ["network"], ((12,26,42),(59,79,118))),
    ("production-studios-series", "studio-dragon", ["surreal","city"], ((19,20,44),(91,55,106))),
    ("production-studios-series", "fifth-season", ["landscape"], ((31,50,58),(130,97,63))),
    ("production-studios-series", "ay-yapim", ["city","group"], ((24,31,40),(107,70,53))),
    ("production-studios-series", "ogm-pictures", ["house","group"], ((40,31,31),(119,78,59))),
    ("production-studios-series", "medyapim", ["screens","group"], ((19,26,39),(85,58,73))),
    ("production-studios-series", "tims-b", ["period","group"], ((45,34,29),(123,82,53))),
]


def render_batch(section, slug, kinds, palette, variant):
    size=(1280,720) if variant=="cover" else (1920,1080)
    rng=rng_for(slug,variant)
    img=gradient(size,*palette)
    img=add_glow(img,(int(size[0]*.72),int(size[1]*.28)),int(min(size)*.22),(225,167,103),68)
    for kind in kinds:
        img=motif(img,kind,rng)
    img=add_vignette(img)
    out=ROOT/section/slug/f"{slug}-{variant}.webp"
    out.parent.mkdir(parents=True,exist_ok=True)
    img.save(out,"WEBP",quality=82,method=6)
    return out


def main():
    made=[]
    for section,slug,kinds,palette in ASSETS:
        for variant in ("cover","backdrop"):
            out=render_batch(section,slug,kinds,palette,variant)
            made.append({"section":section,"slug":slug,"variant":variant,"path":str(out),"rawUrl":f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{out.as_posix()}"})
    manifest=ROOT/"manifest-batch5-studios.json"
    manifest.write_text(json.dumps({"count":len(made),"assets":made},indent=2),encoding="utf-8")
    print(f"Generated {len(made)} studio assets")

if __name__=="__main__":
    main()
