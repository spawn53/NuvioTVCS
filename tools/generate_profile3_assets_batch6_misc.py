from pathlib import Path
import json
from PIL import ImageDraw
from tools.generate_profile3_assets import gradient, add_glow, add_vignette, motif, rng_for, ROOT, REPO, BRANCH

ASSETS = [
    ("based-on", "manga", "manga", ((24,25,38),(91,66,105))),
    ("based-on", "stage-theatre", "theatre", ((34,18,24),(121,67,52))),
    ("holiday-specials", "new-year", "newyear", ((12,18,34),(70,55,98))),
]


def custom(img,kind,rng):
    w,h=img.size
    d=ImageDraw.Draw(img)
    if kind=="manga":
        for i in range(12):
            x=int(w*(.08+(i%4)*.22)); y=int(h*(.10+(i//4)*.25)); bw=int(w*.17); bh=int(h*.18)
            d.rectangle((x,y,x+bw,y+bh),fill=(42,42,50),outline=(135,126,150),width=2)
            d.line((x+10,y+bh-15,x+bw-10,y+15),fill=(92,82,111),width=2)
        motif(img,"surreal",rng)
    elif kind=="theatre":
        d.polygon([(0,0),(int(w*.23),0),(int(w*.34),h),(0,h)],fill=(93,27,36))
        d.polygon([(w,0),(int(w*.77),0),(int(w*.66),h),(w,h)],fill=(93,27,36))
        d.ellipse((int(w*.37),int(h*.18),int(w*.63),int(h*.68)),outline=(178,137,88),width=5)
        d.arc((int(w*.41),int(h*.30),int(w*.49),int(h*.43)),0,180,fill=(201,166,111),width=3)
        d.arc((int(w*.51),int(h*.30),int(w*.59),int(h*.43)),0,180,fill=(201,166,111),width=3)
        d.arc((int(w*.44),int(h*.40),int(w*.56),int(h*.57)),0,180,fill=(201,166,111),width=3)
    elif kind=="newyear":
        cx,cy=int(w*.50),int(h*.38)
        colors=[(221,171,87),(146,111,193),(92,148,196)]
        for i in range(18):
            x=rng.randint(int(w*.08),int(w*.92)); y=rng.randint(int(h*.08),int(h*.55)); col=rng.choice(colors)
            d.line((x,y,x+rng.randint(-25,25),y+rng.randint(30,85)),fill=col,width=3)
        for a in range(0,360,20):
            import math
            x=cx+int(math.cos(math.radians(a))*w*.18); y=cy+int(math.sin(math.radians(a))*h*.24)
            d.line((cx,cy,x,y),fill=(225,181,96),width=2)
        d.rectangle((0,int(h*.78),w,h),fill=(12,15,22))
    return img


def render(section,slug,kind,palette,variant):
    size=(1280,720) if variant=="cover" else (1920,1080)
    rng=rng_for(slug,variant)
    img=gradient(size,*palette)
    img=add_glow(img,(int(size[0]*.70),int(size[1]*.26)),int(min(size)*.22),(227,175,103),72)
    img=custom(img,kind,rng)
    img=add_vignette(img)
    out=ROOT/section/slug/f"{slug}-{variant}.webp"
    out.parent.mkdir(parents=True,exist_ok=True)
    img.save(out,"WEBP",quality=82,method=6)
    return out


def main():
    made=[]
    for section,slug,kind,palette in ASSETS:
        for variant in ("cover","backdrop"):
            out=render(section,slug,kind,palette,variant)
            made.append({"section":section,"slug":slug,"variant":variant,"path":str(out),"rawUrl":f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{out.as_posix()}"})
    manifest=ROOT/"manifest-batch6-misc.json"
    manifest.write_text(json.dumps({"count":len(made),"assets":made},indent=2),encoding="utf-8")
    print(f"Generated {len(made)} misc assets")

if __name__=="__main__":
    main()
