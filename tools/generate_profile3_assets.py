from PIL import Image, ImageDraw, ImageFilter, ImageOps
from pathlib import Path
import hashlib, json, math, random

REPO = "spawn53/NuvioTVCS"
BRANCH = "profile3-visual-assets"
ROOT = Path("assets/collections/profile3")

ASSETS = [
    ("genres", "action-adventure", "landscape", ((12,18,28),(112,58,28))),
    ("genres", "history-period", "period", ((25,20,20),(126,78,42))),
    ("moods-and-vibes", "cerebral-thought-provoking", "network", ((7,15,28),(34,55,82))),
    ("moods-and-vibes", "atmospheric", "mist", ((7,14,20),(45,62,64))),
    ("moods-and-vibes", "suspenseful-intense", "corridor", ((7,8,12),(40,31,34))),
    ("moods-and-vibes", "melancholic-bittersweet", "window", ((15,25,37),(96,62,52))),
    ("moods-and-vibes", "weird-strange", "surreal", ((13,12,30),(70,37,79))),
    ("themes", "artificial-intelligence", "network", ((5,12,23),(25,49,66))),
    ("themes", "parallel-worlds", "portal", ((12,28,49),(89,42,32))),
    ("themes", "alternate-reality", "surreal", ((12,23,34),(63,35,67))),
    ("themes", "dystopia", "city", ((15,18,22),(70,62,50))),
    ("themes", "post-apocalyptic", "ruins", ((29,42,47),(117,94,63))),
    ("themes", "cyberpunk", "neon-city", ((4,8,17),(35,14,39))),
    ("themes", "aliens-first-contact", "alien", ((7,15,24),(70,65,62))),
    ("themes", "human-vs-technology", "screens", ((6,9,15),(41,50,55))),
    ("themes", "conspiracy", "evidence", ((22,17,15),(72,53,42))),
    ("themes", "heist", "vault", ((7,11,17),(48,35,31))),
    ("themes", "prison-escape", "bars", ((7,9,13),(37,39,40))),
    ("themes", "serial-killers", "evidence", ((11,9,11),(50,32,32))),
    ("themes", "organized-crime", "table", ((7,10,14),(54,36,28))),
    ("themes", "political-intrigue", "corridor", ((12,15,20),(66,57,43))),
    ("themes", "cults-secret-societies", "ritual", ((18,11,17),(76,45,30))),
    ("themes", "survival", "landscape", ((20,35,45),(121,100,70))),
    ("themes", "disaster", "storm-city", ((38,43,47),(122,75,42))),
    ("themes", "lost-stranded", "island", ((14,36,45),(99,99,65))),
    ("themes", "memory-identity", "portrait", ((10,18,29),(66,47,61))),
    ("themes", "obsession", "rings", ((14,12,15),(72,45,42))),
    ("themes", "hidden-identity", "portrait", ((8,14,22),(60,42,52))),
    ("themes", "dreams-reality", "surreal", ((11,21,34),(75,48,82))),
    ("themes", "family-secrets", "house", ((22,17,16),(85,62,45))),
    ("themes", "found-family", "group", ((15,25,38),(96,62,43))),
    ("themes", "redemption", "landscape", ((8,12,19),(126,102,68))),
    ("themes", "forbidden-love", "barrier", ((15,18,27),(88,49,58))),
    ("themes", "mythology", "period", ((21,24,35),(126,83,42))),
    ("themes", "zombies", "ruins", ((15,22,25),(75,63,43))),
]

def rng_for(slug, variant):
    seed = int(hashlib.sha256(f"{slug}:{variant}".encode()).hexdigest()[:16], 16)
    return random.Random(seed)

def gradient(size, a, b):
    g = Image.linear_gradient("L").resize(size)
    return ImageOps.colorize(g, a, b).convert("RGB")

def add_glow(img, xy, radius, color, alpha=100):
    layer = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    x,y = xy
    d.ellipse((x-radius,y-radius,x+radius,y+radius), fill=(*color,alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(max(10,radius//2)))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

def add_vignette(img):
    w,h = img.size
    mask = Image.radial_gradient("L").resize((w,h))
    mask = ImageOps.invert(mask).point(lambda p: int(p*0.58))
    dark = Image.new("RGB", (w,h), (0,0,0))
    return Image.composite(dark, img, mask)

def human(d, x, y, scale=1.0, color=(4,5,7)):
    r=max(4,int(10*scale)); hh=max(20,int(64*scale))
    d.ellipse((x-r,y-hh,x+r,y-hh+2*r), fill=color)
    d.polygon([(x-r,y-hh+2*r+2),(x+r,y-hh+2*r+2),(x+2*r,y),(x-2*r,y)], fill=color)

def skyline(d,w,h,base,rng,count=15,color=(14,16,19)):
    step=w/count
    for i in range(count):
        x=int(i*step); bw=max(8,int(step*rng.uniform(.65,1.0))); bh=int(h*rng.uniform(.10,.32))
        d.rectangle((x,base-bh,x+bw,base), fill=color)

def motif(img, kind, rng):
    w,h=img.size; d=ImageDraw.Draw(img); base=int(h*.80)
    if kind in {"landscape","island"}:
        pts=[(0,h)] + [(int(i*w/8), int(h*(.60-rng.uniform(.06,.24)))) for i in range(9)] + [(w,h)]
        d.polygon(pts, fill=(27,36,39))
        pts=[(0,h)] + [(int(i*w/8), int(h*(.72-rng.uniform(.03,.13)))) for i in range(9)] + [(w,h)]
        d.polygon(pts, fill=(15,24,26))
        if kind=="island": d.rectangle((0,int(h*.78),w,h), fill=(26,60,69))
        human(d,int(w*.52),int(h*.80),1.0)
    elif kind=="period":
        floor=int(h*.80); d.rectangle((0,floor,w,h), fill=(20,17,17))
        left,right,top=int(w*.10),int(w*.58),int(h*.25)
        d.rectangle((left,top,right,top+int(h*.055)), fill=(45,36,31))
        for i in range(7):
            x=left+int(i*(right-left)/7); d.rectangle((x,top+int(h*.055),x+int(w*.024),floor), fill=(34,29,27))
        for a in range(0,360,45):
            cx,cy=int(w*.72),int(h*.28); r=int(min(w,h)*.08)
            x1=cx+int(math.cos(math.radians(a))*r*.6); y1=cy+int(math.sin(math.radians(a))*r*.6)
            x2=cx+int(math.cos(math.radians(a))*r*1.2); y2=cy+int(math.sin(math.radians(a))*r*1.2)
            d.line((x1,y1,x2,y2), fill=(175,142,91), width=2)
    elif kind=="network":
        pts=[(rng.randint(int(w*.42),int(w*.90)),rng.randint(int(h*.12),int(h*.82))) for _ in range(30)]
        for i,p in enumerate(pts):
            for q in pts[i+1:]:
                if (p[0]-q[0])**2+(p[1]-q[1])**2 < (min(w,h)*.13)**2:
                    d.line((*p,*q), fill=(54,120,143), width=1)
        for x,y in pts: d.ellipse((x-3,y-3,x+3,y+3), fill=(151,225,231))
        human(d,int(w*.24),int(h*.78),1.6)
    elif kind=="mist":
        for i in range(28):
            x=int(i*w/27+rng.randint(-15,15)); top=int(h*rng.uniform(.12,.42))
            d.line((x,top,x,h), fill=(10,18,20), width=rng.randint(3,8))
        img.paste(img.filter(ImageFilter.GaussianBlur(3)))
    elif kind=="corridor":
        van=(int(w*.62),int(h*.47))
        d.polygon([(0,0),(w,0),van],fill=(24,26,29)); d.polygon([(0,h),(w,h),van],fill=(10,11,14))
        for p in [(0,0),(w,0),(0,h),(w,h)]: d.line((*p,*van), fill=(58,57,55), width=2)
        human(d,int(w*.59),int(h*.79),1.0)
    elif kind=="window":
        d.rectangle((int(w*.10),int(h*.10),int(w*.48),int(h*.82)), fill=(9,13,18))
        d.rectangle((int(w*.12),int(h*.12),int(w*.46),int(h*.80)), fill=(43,58,72))
        for _ in range(120):
            x=rng.randint(int(w*.12),int(w*.46)); y=rng.randint(int(h*.12),int(h*.80)); d.line((x,y,x+5,y+18), fill=(117,139,153), width=1)
        human(d,int(w*.68),int(h*.80),1.5)
    elif kind in {"surreal","portal"}:
        if kind=="portal":
            d.rectangle((0,0,w//2,h),fill=(15,34,54)); d.rectangle((w//2,0,w,h),fill=(77,40,29))
            d.line((w//2,0,w//2,h), fill=(185,148,190), width=max(3,w//400))
        for i in range(10):
            x=rng.randint(int(w*.18),int(w*.88)); y=rng.randint(int(h*.10),int(h*.68)); r=rng.randint(max(8,w//160),max(15,w//55))
            d.ellipse((x-r,y-r,x+r,y+r), fill=(rng.randint(50,115),rng.randint(40,85),rng.randint(90,160)))
        d.rectangle((int(w*.58),int(h*.24),int(w*.72),int(h*.68)), fill=(25,20,38), outline=(158,134,184), width=3)
    elif kind in {"city","neon-city","storm-city"}:
        skyline(d,w,h,base,rng,18,(16,18,20))
        if kind=="neon-city":
            for _ in range(26):
                x=rng.randint(0,w); y=rng.randint(int(h*.16),int(h*.70)); col=rng.choice([(235,42,130),(37,206,218),(126,68,222)])
                d.line((x,y,x,y+rng.randint(40,150)), fill=col, width=rng.randint(2,5))
        if kind=="storm-city":
            d.ellipse((int(w*.52),int(h*.02),int(w*1.12),int(h*.72)), fill=(55,58,60))
            for _ in range(45):
                x=rng.randint(int(w*.45),w); y=rng.randint(int(h*.08),int(h*.72)); d.line((x,y,x-rng.randint(10,45),y+rng.randint(15,55)),fill=(95,98,99),width=2)
        human(d,int(w*.25),base,1.0)
    elif kind=="ruins":
        for i in range(13):
            x=int(i*w/12); bw=int(w*.075); top=int(h*rng.uniform(.28,.58))
            d.polygon([(x,base),(x,top),(x+bw//2,top+rng.randint(-20,20)),(x+bw,top+rng.randint(20,60)),(x+bw,base)],fill=(34,37,36))
        for _ in range(65):
            x=rng.randint(0,w); y=rng.randint(int(h*.66),h); d.line((x,y,x+rng.randint(-12,12),y-rng.randint(12,55)), fill=(48,72,45), width=rng.randint(1,3))
    elif kind=="alien":
        cx,cy=int(w*.64),int(h*.28); rw=int(w*.18); rh=int(h*.07)
        d.ellipse((cx-rw,cy-rh,cx+rw,cy+rh), fill=(32,36,42), outline=(132,145,151), width=3)
        for x in [int(w*.28),int(w*.36),int(w*.44)]: human(d,x,base,0.9)
    elif kind=="screens":
        for r in range(4):
            for c in range(7):
                x=int(w*(.38+c*.085)); y=int(h*(.10+r*.18)); bw=int(w*.07); bh=int(h*.13)
                d.rectangle((x,y,x+bw,y+bh), fill=(29,52,59), outline=(75,111,117), width=2)
        human(d,int(w*.20),int(h*.84),1.8)
    elif kind=="evidence":
        cards=[]
        for _ in range(14):
            x=rng.randint(int(w*.08),int(w*.80)); y=rng.randint(int(h*.10),int(h*.64)); bw=rng.randint(int(w*.06),int(w*.12)); bh=rng.randint(int(h*.06),int(h*.13))
            d.rectangle((x,y,x+bw,y+bh), fill=(139,126,106)); cards.append((x+bw//2,y+bh//2))
        for i,p in enumerate(cards[:-1]): d.line((*p,*cards[rng.randint(i+1,len(cards)-1)]), fill=(106,33,28), width=2)
        human(d,int(w*.85),int(h*.82),1.7)
    elif kind=="vault":
        cx,cy=int(w*.70),int(h*.48); r=int(min(w,h)*.24)
        d.ellipse((cx-r,cy-r,cx+r,cy+r), fill=(36,40,44), outline=(118,122,124), width=5)
        d.ellipse((cx-r//2,cy-r//2,cx+r//2,cy+r//2), outline=(108,112,116), width=4)
        for a in range(0,360,45):
            d.line((cx+int(math.cos(math.radians(a))*r*.25),cy+int(math.sin(math.radians(a))*r*.25),cx+int(math.cos(math.radians(a))*r*.57),cy+int(math.sin(math.radians(a))*r*.57)),fill=(98,102,105),width=5)
    elif kind=="bars":
        for i in range(12):
            x=int(i*w/11); d.rectangle((x,0,x+int(w*.018),h), fill=(6,7,9))
        human(d,int(w*.60),int(h*.81),1.0)
    elif kind=="table":
        skyline(d,w,h,base,rng,14,(13,15,17)); d.polygon([(int(w*.14),int(h*.63)),(int(w*.80),int(h*.63)),(int(w*.94),h),(int(w*.03),h)],fill=(10,9,9))
        for sx in [.25,.38,.52,.66,.78]: human(d,int(w*sx),int(h*.64),.8)
    elif kind=="ritual":
        cx,cy=int(w*.52),int(h*.50)
        for i in range(14):
            a=2*math.pi*i/14; x=int(cx+math.cos(a)*w*.20); y=int(cy+math.sin(a)*h*.20); d.rectangle((x-2,y-10,x+2,y+6),fill=(216,174,102)); d.ellipse((x-3,y-16,x+3,y-9),fill=(255,207,101))
        for sx in [.25,.36,.69,.80]: human(d,int(w*sx),int(h*.82),1.2)
    elif kind=="portrait":
        cx,cy=int(w*.48),int(h*.48)
        for _ in range(12):
            x=rng.randint(int(w*.14),int(w*.72)); y=rng.randint(int(h*.08),int(h*.70)); bw=rng.randint(int(w*.07),int(w*.15)); bh=rng.randint(int(h*.07),int(h*.18)); d.rectangle((x,y,x+bw,y+bh), fill=rng.choice([(48,60,76),(75,53,68),(41,47,58),(89,64,72)]))
        d.ellipse((cx-int(w*.10),cy-int(h*.22),cx+int(w*.10),cy+int(h*.22)), outline=(143,145,156), width=3)
    elif kind=="rings":
        cx,cy=int(w*.60),int(h*.48)
        for r in range(int(min(w,h)*.04),int(min(w,h)*.31),max(8,int(min(w,h)*.026))): d.ellipse((cx-r,cy-r,cx+r,cy+r), outline=(120,82,75), width=2)
        human(d,int(w*.24),int(h*.76),1.7)
    elif kind=="house":
        d.rectangle((int(w*.08),int(h*.12),int(w*.92),int(h*.90)), fill=(38,29,26)); d.rectangle((int(w*.37),int(h*.22),int(w*.63),int(h*.88)), fill=(19,15,15))
        for _ in range(8):
            x=rng.randint(int(w*.12),int(w*.78)); y=rng.randint(int(h*.16),int(h*.62)); bw=rng.randint(int(w*.05),int(w*.09)); bh=rng.randint(int(h*.07),int(h*.12)); d.rectangle((x,y,x+bw,y+bh),outline=(116,93,69),width=3)
    elif kind=="group":
        for sx,sc in zip([.28,.39,.50,.61,.72],[1.0,1.2,1.1,1.3,1.0]): human(d,int(w*sx),base,sc)
    elif kind=="barrier":
        d.rectangle((int(w*.49),0,int(w*.51),h),fill=(128,120,132)); human(d,int(w*.36),int(h*.78),1.5); human(d,int(w*.64),int(h*.78),1.5)
    return img

def render(section, slug, kind, palette, variant):
    size=(1280,720) if variant=="cover" else (1920,1080)
    rng=rng_for(slug,variant)
    img=gradient(size,*palette)
    img=add_glow(img,(int(size[0]*.72),int(size[1]*.30)),int(min(size)*.22),(220,160,95),70)
    img=motif(img,kind,rng)
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
    manifest=ROOT/"manifest.json"
    manifest.write_text(json.dumps({"count":len(made),"assets":made},indent=2),encoding="utf-8")
    print(f"Generated {len(made)} assets")

if __name__=="__main__":
    main()
