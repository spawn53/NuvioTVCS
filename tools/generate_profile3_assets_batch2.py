from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont
from pathlib import Path
import hashlib, json, random, math

REPO='spawn53/NuvioTVCS'; BRANCH='profile3-visual-assets'; ROOT=Path('assets/collections/profile3')
ASSETS=[
('streaming-services','turkiye-streaming','turkiye',((10,18,28),(45,58,78))),
('international-cinema','british-irish-cinema','city',((18,26,34),(79,67,51))),
('international-cinema','western-european-cinema','period',((22,24,31),(103,76,51))),
('international-cinema','eastern-european-cinema','city',((16,22,29),(69,57,52))),
('international-cinema','balkan-cinema','landscape',((18,31,38),(106,76,49))),
('international-cinema','oceania-cinema','island',((12,34,45),(104,101,66))),
('international-cinema','romanian-cinema','city',((18,20,26),(76,56,48))),
('international-cinema','new-zealand-cinema','landscape',((14,31,39),(92,95,68))),
('documentaries','politics-society','documents',((20,20,24),(70,58,47))),
('documentaries','biography-portraits','portrait',((15,20,29),(72,57,62))),
('anime','seinen-dark','anime-dark',((10,12,18),(48,30,35))),
('anime','shojo-josei','anime-soft',((28,20,31),(105,66,85))),
('anime','psychological-sci-fi','anime-sci',((8,15,28),(42,54,76))),
('anime','classics-essentials','anime-classic',((25,22,20),(104,77,48))),
]

def rng(slug,var):
 return random.Random(int(hashlib.sha256(f'{slug}:{var}'.encode()).hexdigest()[:16],16))
def grad(size,a,b):
 return ImageOps.colorize(Image.linear_gradient('L').resize(size),a,b).convert('RGB')
def glow(img,xy,r,c,alpha=80):
 lay=Image.new('RGBA',img.size,(0,0,0,0)); d=ImageDraw.Draw(lay); x,y=xy
 d.ellipse((x-r,y-r,x+r,y+r),fill=(*c,alpha)); lay=lay.filter(ImageFilter.GaussianBlur(max(12,r//2)))
 return Image.alpha_composite(img.convert('RGBA'),lay).convert('RGB')
def vignette(img):
 w,h=img.size; m=ImageOps.invert(Image.radial_gradient('L').resize((w,h))).point(lambda p:int(p*.55)); return Image.composite(Image.new('RGB',(w,h),(0,0,0)),img,m)
def skyline(d,w,h,base,R,col=(18,20,23)):
 for i in range(15):
  step=w/15; x=int(i*step); bw=int(step*R.uniform(.6,1.0)); bh=int(h*R.uniform(.10,.30)); d.rectangle((x,base-bh,x+bw,base),fill=col)
def human(d,x,y,s=1,col=(4,5,7)):
 r=max(4,int(10*s)); hh=max(20,int(64*s)); d.ellipse((x-r,y-hh,x+r,y-hh+2*r),fill=col); d.polygon([(x-r,y-hh+2*r+2),(x+r,y-hh+2*r+2),(x+2*r,y),(x-2*r,y)],fill=col)
def font(sz):
 for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf']:
  if Path(p).exists(): return ImageFont.truetype(p,sz)
 return ImageFont.load_default()

def motif(img,kind,R):
 w,h=img.size; d=ImageDraw.Draw(img); base=int(h*.80)
 if kind=='turkiye':
  skyline(d,w,h,base,R,(16,20,25)); img=glow(img,(int(w*.55),int(h*.38)),int(min(w,h)*.20),(214,153,91),70); d=ImageDraw.Draw(img)
  cards=[('GAİN',(210,28,36)),('EXXEN',(239,174,25)),('TOD',(25,58,78))]
  xs=[.22,.50,.78]; f=font(max(28,int(h*.075)))
  for (txt,col),sx in zip(cards,xs):
   cx=int(w*sx); cw=int(w*.22); ch=int(h*.26); y=int(h*.46)
   d.rounded_rectangle((cx-cw//2,y-ch//2,cx+cw//2,y+ch//2),radius=int(h*.035),fill=col)
   box=d.textbbox((0,0),txt,font=f); tw=box[2]-box[0]; th=box[3]-box[1]; d.text((cx-tw//2,y-th//2-2),txt,font=f,fill='white')
 elif kind in {'city','period'}:
  skyline(d,w,h,base,R,(20,22,24))
  if kind=='period':
   for x in [int(w*.12),int(w*.22),int(w*.32)]: d.rectangle((x,int(h*.28),x+int(w*.028),base),fill=(49,42,37))
   d.rectangle((int(w*.09),int(h*.24),int(w*.40),int(h*.29)),fill=(61,51,43))
  human(d,int(w*.62),base,1.0)
 elif kind in {'landscape','island'}:
  pts=[(0,h)]+[(int(i*w/8),int(h*(.58-R.uniform(.04,.22)))) for i in range(9)]+[(w,h)]; d.polygon(pts,fill=(34,45,44))
  pts=[(0,h)]+[(int(i*w/8),int(h*(.72-R.uniform(.02,.10)))) for i in range(9)]+[(w,h)]; d.polygon(pts,fill=(20,29,30))
  if kind=='island': d.rectangle((0,int(h*.78),w,h),fill=(28,66,76))
  human(d,int(w*.52),base,.9)
 elif kind=='documents':
  for _ in range(15):
   x=R.randint(int(w*.08),int(w*.78)); y=R.randint(int(h*.08),int(h*.62)); bw=R.randint(int(w*.06),int(w*.12)); bh=R.randint(int(h*.06),int(h*.12)); d.rectangle((x,y,x+bw,y+bh),fill=(144,132,112))
  d.rectangle((int(w*.62),int(h*.18),int(w*.82),int(h*.62)),fill=(38,40,44)); human(d,int(w*.72),int(h*.72),1.2)
 elif kind=='portrait':
  cx,cy=int(w*.50),int(h*.48); d.ellipse((cx-int(w*.11),cy-int(h*.22),cx+int(w*.11),cy+int(h*.22)),outline=(160,150,148),width=3)
  for _ in range(12):
   x=R.randint(int(w*.08),int(w*.82)); y=R.randint(int(h*.08),int(h*.70)); bw=R.randint(int(w*.05),int(w*.11)); bh=R.randint(int(h*.06),int(h*.15)); d.rectangle((x,y,x+bw,y+bh),outline=(99,91,88),width=2)
 elif kind.startswith('anime'):
  if kind=='anime-dark': cols=[(23,24,31),(72,37,43),(112,48,49)]
  elif kind=='anime-soft': cols=[(80,55,78),(166,102,135),(224,176,192)]
  elif kind=='anime-sci': cols=[(19,30,50),(49,84,126),(76,173,183)]
  else: cols=[(63,51,39),(132,90,52),(197,157,100)]
  for i in range(7):
   x=int(w*(.10+i*.12)); y=int(h*(.18+(.08 if i%2 else .02))); d.polygon([(x,y),(x+int(w*.10),y-int(h*.05)),(x+int(w*.14),y+int(h*.22)),(x-int(w*.02),y+int(h*.24))],fill=cols[i%len(cols)])
  cx,cy=int(w*.52),int(h*.78); human(d,cx,cy,1.7,(7,8,12))
  for a in range(0,360,45):
   r=int(min(w,h)*.13); x1=cx+int(math.cos(math.radians(a))*r*.7); y1=int(h*.40)+int(math.sin(math.radians(a))*r*.7); x2=cx+int(math.cos(math.radians(a))*r); y2=int(h*.40)+int(math.sin(math.radians(a))*r); d.line((x1,y1,x2,y2),fill=cols[-1],width=2)
 return img

def render(section,slug,kind,palette,var):
 size=(1280,720) if var=='cover' else (1920,1080); R=rng(slug,var); img=grad(size,*palette); img=glow(img,(int(size[0]*.72),int(size[1]*.28)),int(min(size)*.20),(220,165,100),55); img=motif(img,kind,R); img=vignette(img)
 out=ROOT/section/slug/f'{slug}-{var}.webp'; out.parent.mkdir(parents=True,exist_ok=True); img.save(out,'WEBP',quality=82,method=6); return out

def main():
 made=[]
 for section,slug,kind,palette in ASSETS:
  for var in ('cover','backdrop'):
   out=render(section,slug,kind,palette,var); made.append({'section':section,'slug':slug,'variant':var,'path':str(out),'rawUrl':f'https://raw.githubusercontent.com/{REPO}/{BRANCH}/{out.as_posix()}'})
 mf=ROOT/'manifest-batch2.json'; mf.write_text(json.dumps({'count':len(made),'assets':made},indent=2),encoding='utf-8'); print(f'Generated {len(made)} assets')
if __name__=='__main__': main()
