from pathlib import Path
import json, math
from PIL import ImageDraw
from tools.generate_profile3_assets import gradient, add_glow, add_vignette, rng_for, ROOT, REPO, BRANCH, human, skyline

ASSETS = [
    ("venice-film-festival", "venice", ((29,45,62),(158,102,54))),
    ("berlin-international-film-festival", "berlin", ((30,24,30),(142,48,43))),
    ("bafta", "mask", ((18,20,27),(125,91,49))),
    ("critics-choice-awards", "crystal", ((18,31,48),(95,109,148))),
    ("independent-spirit-awards", "indie", ((29,42,54),(124,91,67))),
    ("european-film-awards", "europe", ((18,29,48),(80,73,123))),
    ("cesar-awards", "sculpture", ((22,23,28),(125,112,90))),
    ("sundance-film-festival", "sundance", ((24,40,58),(123,103,72))),
    ("tiff-peoples-choice", "tiff", ((21,28,42),(118,66,77))),
]


def award_motif(img, kind, rng):
    w,h=img.size
    d=ImageDraw.Draw(img)
    base=int(h*.80)
    if kind=="venice":
        d.rectangle((0,int(h*.70),w,h),fill=(31,66,78))
        for y in range(int(h*.72),h,18):
            d.line((0,y,w,y+rng.randint(-2,2)),fill=(75,108,116),width=1)
        for i in range(6):
            x=int(w*(.08+i*.13)); d.rectangle((x,int(h*.38),x+int(w*.025),base),fill=(46,39,35))
            d.arc((x-int(w*.025),int(h*.30),x+int(w*.05),int(h*.47)),180,360,fill=(128,101,70),width=3)
        human(d,int(w*.72),base,.95)
    elif kind=="berlin":
        skyline(d,w,h,base,rng,17,(18,18,22))
        for _ in range(24):
            x=rng.randint(int(w*.12),int(w*.88)); y=rng.randint(int(h*.10),int(h*.68))
            d.polygon([(x,y-10),(x+9,y),(x,y+10),(x-9,y)],fill=(150,50,45))
        d.polygon([(int(w*.20),base),(int(w*.80),base),(int(w*.63),h),(int(w*.37),h)],fill=(74,24,24))
    elif kind=="mask":
        cx,cy=int(w*.62),int(h*.46); rw=int(w*.13); rh=int(h*.22)
        d.ellipse((cx-rw,cy-rh,cx+rw,cy+rh),fill=(157,127,76))
        d.polygon([(cx-rw,cy),(cx,cy+rh),(cx+rw,cy)],fill=(114,88,54))
        d.ellipse((cx-int(rw*.55),cy-int(rh*.25),cx-int(rw*.15),cy+int(rh*.05)),fill=(23,24,28))
        d.ellipse((cx+int(rw*.15),cy-int(rh*.25),cx+int(rw*.55),cy+int(rh*.05)),fill=(23,24,28))
    elif kind=="crystal":
        cx,cy=int(w*.62),int(h*.46); r=int(min(w,h)*.23)
        for a in range(0,360,30):
            x=cx+int(math.cos(math.radians(a))*r); y=cy+int(math.sin(math.radians(a))*r)
            d.line((cx,cy,x,y),fill=(137,163,204),width=3)
        for rr in [r//3,2*r//3,r]:
            d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=(102,128,170),width=2)
    elif kind=="indie":
        d.rectangle((int(w*.18),int(h*.44),int(w*.45),int(h*.66)),fill=(33,35,39),outline=(118,100,78),width=3)
        d.ellipse((int(w*.22),int(h*.34),int(w*.32),int(h*.46)),fill=(57,60,64),outline=(137,119,91),width=2)
        d.ellipse((int(w*.34),int(h*.34),int(w*.44),int(h*.46)),fill=(57,60,64),outline=(137,119,91),width=2)
        for i in range(14):
            x=int(w*(.08+i*.065)); y=int(h*(.20+.04*math.sin(i*.8))); d.ellipse((x-5,y-5,x+5,y+5),fill=(234,182,108))
        human(d,int(w*.70),base,1.0)
    elif kind=="europe":
        pts=[]
        for _ in range(28):
            pts.append((rng.randint(int(w*.25),int(w*.85)),rng.randint(int(h*.18),int(h*.72))))
        for i,p in enumerate(pts):
            q=pts[(i+rng.randint(1,6))%len(pts)]; d.line((*p,*q),fill=(91,111,163),width=1)
        for x,y in pts: d.ellipse((x-3,y-3,x+3,y+3),fill=(177,184,222))
        d.arc((int(w*.30),int(h*.14),int(w*.82),int(h*.80)),190,330,fill=(151,136,194),width=4)
    elif kind=="sculpture":
        cx,cy=int(w*.64),int(h*.48)
        d.polygon([(cx,cy-int(h*.28)),(cx-int(w*.08),cy-int(h*.06)),(cx-int(w*.03),cy+int(h*.24)),(cx+int(w*.07),cy+int(h*.22)),(cx+int(w*.09),cy-int(h*.05))],fill=(137,130,111))
        d.line((cx-int(w*.03),cy-int(h*.05),cx+int(w*.06),cy+int(h*.12)),fill=(71,69,66),width=4)
    elif kind=="sundance":
        pts=[(0,h)] + [(int(i*w/8),int(h*(.58-rng.uniform(.08,.24)))) for i in range(9)] + [(w,h)]
        d.polygon(pts,fill=(34,48,58))
        for i in range(9):
            x=int(i*w/8); y=int(h*(.50-rng.uniform(.03,.16)))
            d.polygon([(x,y),(x+int(w*.09),int(h*.58)),(x-int(w*.09),int(h*.58))],fill=(196,196,188))
        for i in range(12):
            x=int(w*(.12+i*.065)); y=int(h*.22); d.ellipse((x-5,y-5,x+5,y+5),fill=(233,181,103))
        human(d,int(w*.55),base,.9)
    elif kind=="tiff":
        skyline(d,w,h,base,rng,18,(18,20,24))
        d.polygon([(0,h),(w,h),(int(w*.66),base),(int(w*.34),base)],fill=(61,30,37))
        for i in range(8):
            x=int(w*(.18+i*.08)); d.rectangle((x,int(h*.27),x+int(w*.055),int(h*.42)),outline=(173,101,111),width=3)
        for sx in [.34,.42,.50,.58,.66]: human(d,int(w*sx),base,.75)
    return img


def render(slug,kind,palette,variant):
    size=(1280,720) if variant=="cover" else (1920,1080)
    rng=rng_for(slug,variant)
    img=gradient(size,*palette)
    img=add_glow(img,(int(size[0]*.72),int(size[1]*.28)),int(min(size)*.24),(229,178,105),82)
    img=award_motif(img,kind,rng)
    img=add_vignette(img)
    out=ROOT/"awards"/slug/f"{slug}-{variant}.webp"
    out.parent.mkdir(parents=True,exist_ok=True)
    img.save(out,"WEBP",quality=82,method=6)
    return out


def main():
    made=[]
    for slug,kind,palette in ASSETS:
        for variant in ("cover","backdrop"):
            out=render(slug,kind,palette,variant)
            made.append({"section":"awards","slug":slug,"variant":variant,"path":str(out),"rawUrl":f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{out.as_posix()}"})
    manifest=ROOT/"manifest-batch4-awards.json"
    manifest.write_text(json.dumps({"count":len(made),"assets":made},indent=2),encoding="utf-8")
    print(f"Generated {len(made)} award assets")

if __name__=="__main__":
    main()
