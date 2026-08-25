from pathlib import Path
import json
from tools.generate_profile3_assets import gradient, add_glow, add_vignette, motif, rng_for, ROOT, REPO, BRANCH

ASSETS = [
    ("kids-family", "kids-adventure", ["landscape"], ((48,88,122),(214,147,78))),
    ("kids-family", "animation-favorites", ["surreal"], ((41,41,96),(164,79,141))),
    ("kids-family", "learning-educational", ["network"], ((27,68,86),(106,164,141))),
    ("kids-family", "feel-good-family", ["group"], ((55,83,111),(222,151,82))),
    ("kids-family", "fantasy-magic", ["surreal","ritual"], ((35,26,73),(116,67,149))),
    ("kids-family", "family-classics", ["period"], ((65,47,37),(164,111,67))),
    ("reality-tv", "trending-reality", ["screens"], ((15,20,32),(92,47,93))),
    ("reality-tv", "competition-talent", ["group","screens"], ((21,26,42),(132,74,80))),
    ("reality-tv", "travel-adventure", ["landscape"], ((25,57,78),(168,113,68))),
    ("reality-tv", "social-experiment-survival", ["landscape","group"], ((24,39,48),(100,83,61))),
    ("reality-tv", "docu-reality-real-lives", ["portrait","group"], ((23,28,39),(88,63,65))),
]


def render_batch(section, slug, kinds, palette, variant):
    size=(1280,720) if variant=="cover" else (1920,1080)
    rng=rng_for(slug,variant)
    img=gradient(size,*palette)
    img=add_glow(img,(int(size[0]*.72),int(size[1]*.28)),int(min(size)*.22),(236,178,108),72)
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
            made.append({
                "section":section,
                "slug":slug,
                "variant":variant,
                "path":str(out),
                "rawUrl":f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{out.as_posix()}"
            })
    manifest=ROOT/"manifest-batch3.json"
    manifest.write_text(json.dumps({"count":len(made),"assets":made},indent=2),encoding="utf-8")
    print(f"Generated {len(made)} batch3 assets")

if __name__=="__main__":
    main()
