#!/usr/bin/env python3
"""THE UNIVERSE IS CREATED AT EVERY POINT EVERY MOMENT"""
from __future__ import annotations
import argparse, json, math, random, shutil, subprocess
from dataclasses import asdict, dataclass
from pathlib import Path; from typing import Callable
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
ROOT=Path(__file__).resolve().parent
OUTPUT=Path("/mnt/HC_Volume_106427611/goldrender/output_universe_created_every_moment")
FRAMES=OUTPUT/"frames"; SCENES_DIR=OUTPUT/"scenes"
W,H,FPS=1280,720,10
IVORY=(249,247,241); WHITE=(255,254,250); INK=(29,33,39); SOFT_INK=(86,91,98)
SILVER=(180,187,194); PALE_SILVER=(224,228,228); CYAN=(57,156,180); PALE_CYAN=(196,227,233)
GOLD=(194,156,72); PALE_GOLD=(236,219,175); GREEN=(70,139,99)
CRIMSON=(162,58,69); VIOLET=(109,83,153)
FS="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"; FSB=FS.replace("Serif","Serif-Bold")
FNS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FNSB=FNS.replace("Sans","Sans-Bold")
def clamp(x,l=0.0,h=1.0): return max(l,min(h,x))
def lerp(a,b,t): return a+(b-a)*clamp(t)
def mix(a,b,t): return tuple(int(lerp(x,y,t)) for x,y in zip(a,b))
def smoothstep(a,b,x):
    if a==b: return 1.0 if x>=b else 0.0; q=clamp((x-a)/(b-a)); return q*q*(3-2*q)
def ease(t): t=clamp(t); return .5-.5*math.cos(math.pi*t)
def font(p,s):
    for c in (p,FS,FNS):
        try: return ImageFont.truetype(c,s)
        except: pass
    return ImageFont.load_default()
def layer(s): return Image.new("RGBA",s,(0,0,0,0))
def field(w,h,seed):
    r=np.random.default_rng(seed); a=np.empty((h,w,3),dtype=np.float32); a[:]=IVORY
    a+=r.normal(0,.9,(h,w,1)); yy,xx=np.mgrid[0:h,0:w]
    h2=np.exp(-(((xx-w*.5)/(w*.37))**2+((yy-h*.40)/(h*.31))**2)*2)
    a[...,1]+=h2*3.2; a[...,2]+=h2*4.6
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8),"RGB").convert("RGBA")
def centered(d,xy,t,f,fill=INK): d.text(xy,t,font=f,fill=fill,anchor="mm")
def seal(im,t,s="",c=INK):
    w2,h2=im.size; d=ImageDraw.Draw(im)
    tf=font(FSB,max(22,int(h2*.04))); sf=font(FNS,max(13,int(h2*.019)))
    centered(d,(w2/2,h2*.875),t,tf,c)
    if s: centered(d,(w2/2,h2*.923),s,sf,SOFT_INK)
def border(im):
    w2,h2=im.size; d=ImageDraw.Draw(im)
    d.rounded_rectangle((26,26,w2-26,h2-26),radius=18,outline=(*INK,45),width=2)
def glow_circle(im,x,y,r,c,a=170,b=14):
    gl=layer(im.size); ImageDraw.Draw(gl).ellipse((x-r,y-r,x+r,y+r),fill=(*c,int(a)))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(b)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).ellipse((x-r*.34,y-r*.34,x+r*.34,y+r*.34),fill=(*mix(c,WHITE,.35),min(255,int(a)+50)))
    im.alpha_composite(fg)
def glow_line(im,pts,c,w=4,a=210,b2=11):
    if len(pts)<2: return; gl=layer(im.size)
    ImageDraw.Draw(gl).line(pts,fill=(*c,int(a)),width=w*3,joint="curve")
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(b2)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).line(pts,fill=(*mix(c,WHITE,.08),min(255,int(a)+25)),width=w,joint="curve")
    im.alpha_composite(fg)
def partial(pts,a):
    if not pts: return []; a=clamp(a)
    if a>=1: return pts; k=a*(len(pts)-1); i=int(k); f=k-i
    out=list(pts[:i+1])
    if i+1<len(pts): p,q=pts[i],pts[i+1]; out.append((lerp(p[0],q[0],f),lerp(p[1],q[1],f)))
    return out
def arrow(d,a,b,c=INK,w=3,h2=10):
    d.line((*a,*b),fill=c,width=w); ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for s2 in(-1,1): p=(b[0]-math.cos(ang+s2*.52)*h2,b[1]-math.sin(ang+s2*.52)*h2); d.line((*b,*p),fill=c,width=w)

# =============================================================================
# VISUALS
# =============================================================================

def vis_claim(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for i in range(int(30*r)):
        a=random.uniform(0,math.tau); rr=random.uniform(10,130)*r
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.ellipse((x-2,y-2,x+2,y+2),fill=(*GOLD,int(150*pulse(t+i))))
    if r>.5:
        q=(r-.5)/.5
        d.rounded_rectangle((w*.10,h*.26,w*.90,h*.50),radius=14,
                            fill=(*mix(WHITE,GOLD,.08),int(200*q)),
                            outline=(*GOLD,int(160*q)),width=2)
        centered(d,(w*.50,h*.35),'"EVERYWHERE BEING CREATED"',font(FNS,18),(*GOLD,int(220*q)))
        centered(d,(w*.50,h*.44),'"at all of its points at each moment"',font(FNS,14),SOFT_INK)
    seal(im,"SETH'S COSMOLOGY","the universe is not expanding — it is being created at every point at every moment")

def vis_big_bang(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    glow_circle(im,cx,cy,20,GOLD,int(180*r),14)
    for i in range(int(15*r)):
        a=random.uniform(0,math.tau); rr=random.uniform(15,100)*r
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.line((cx,cy,x,y),fill=(*CRIMSON,int(80*r)),width=2)
    if r>.5:
        q=(r-.5)/.5
        centered(d,(cx,cy+55),"THE BIG BANG",font(FNSB,16),(*CRIMSON,int(200*q)))
        centered(d,(cx,cy+65),"a single explosion — then expansion",font(FNS,13),SOFT_INK)
    seal(im,"THE STANDARD STORY","one moment of creation — then 13.8 billion years of aftermath")

def vis_continuous(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for i in range(int(40*r)):
        a=random.uniform(0,math.tau)
        rr=random.uniform(5,120)*r
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        col=[GOLD,CYAN,GREEN,VIOLET][i%4]
        d.ellipse((x-3,y-3,x+3,y+3),fill=(*col,int(100+100*pulse(t+i))))
    if r>.6:
        q=(r-.6)/.4
        centered(d,(cx,cy+55),"CREATION IS NOT PAST",font(FNSB,16),(*GOLD,int(200*q)))
        centered(d,(cx,cy+65),"it is present — happening now",font(FNS,13),SOFT_INK)
    seal(im,"CONTINUOUS CREATION","not one explosion — an eternal unfolding at every point")

def vis_psyche_pulse(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for i in range(int(20*r)):
        a=i*math.tau/20+t*0.1
        pr=lerp(20,90,r)
        x=cx+math.cos(a)*pr; y=cy+math.sin(a)*pr*.5
        d.line((cx,cy,x,y),fill=(*VIOLET,int(80*r)),width=2)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*PALE_GOLD,int(150*r)))
    glow_circle(im,cx,cy,14,GOLD,int(180*r),12)
    if r>.5:
        q=(r-.5)/.5
        centered(d,(cx,cy+55),"YOUR PSYCHE PARTICIPATES",font(FNSB,14),(*GOLD,int(200*q)))
    seal(im,"THE PSYCHOLOGICAL PULSE","your psyche is drawn back into itself — and out again — in pulses")

def vis_electron(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    glow_circle(im,cx,cy,12,GOLD,int(180*r),10)
    for i in range(int(20*r)):
        a=i*math.tau/20+t*0.15
        rr=40+15*math.sin(t*2+i)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.ellipse((x-3,y-3,x+3,y+3),fill=(*CYAN,int(150*pulse(t*2+i))))
    if r>.5:
        q=(r-.5)/.5
        centered(d,(cx,cy+55),"CORRELATES WITH ELECTRON BEHAVIOR",font(FNSB,13),(*CYAN,int(200*q)))
        centered(d,(cx,cy+65),"the pulse of consciousness and the behavior of electrons",font(FNS,13),SOFT_INK)
    seal(im,"THE ELECTRON CORRELATION","Seth: the psyche's pulses have a correlation with electron behavior")

def vis_steady_state(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for i in range(int(25*r)):
        a=random.uniform(0,math.tau); rr=random.uniform(10,110)*r
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.ellipse((x-3,y-3,x+3,y+3),fill=(*GREEN,int(150)))
    if r>.5:
        q=(r-.5)/.5
        centered(d,(cx,cy+55),"THE STEADY STATE OF CONSCIOUSNESS",font(FNSB,14),(*GREEN,int(200*q)))
    seal(im,"STEADY STATE","the universe is not running down — it is being continuously replenished")

def vis_participatory(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    arrow(d,(cx-w*.15,cy+20),(cx,cy-10),GOLD,4,10)
    arrow(d,(cx,cy-10),(cx+w*.15,cy+20),CYAN,4,10)
    glow_circle(im,cx,cy-10,10,GOLD,int(180*r),10)
    if r>.4:
        q=(r-.4)/.6
        centered(d,(cx-w*.15,cy+40),"OBSERVER",font(FNSB,13),GOLD)
        centered(d,(cx+w*.15,cy+40),"UNIVERSE",font(FNSB,13),CYAN)
        centered(d,(cx,cy+55),"PARTICIPATORY",font(FNSB,14),(*GOLD,int(200*q)))
        centered(d,(cx,cy+65),"the observer and the observed create each other",font(FNS,12),SOFT_INK)
    seal(im,"THE PARTICIPATORY UNIVERSE","Wheeler: the universe cannot exist without observers")

def vis_caution(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    rows=[("THE UNIVERSE IS EXPANDING","ESTABLISHED",GREEN),
          ("CREATION IS CONTINUOUS","METAPHYSICAL CLAIM",CRIMSON),
          ("CONSCIOUSNESS PARTICIPATES IN CREATION","PHILOSOPHICAL — NOT PHYSICAL",GOLD),
          ("STEADY STATE COSMOLOGY IS FALSIFIED","THE SETH CLAIM IS DIFFERENT",CYAN)]
    q=ease(u)
    for i,(claim,status,col) in enumerate(rows):
        local=clamp(q*len(rows)-i); y=h*(.23+i*.13)
        d.rounded_rectangle((w*.14,y-28,w*.86,y+28),radius=14,
                            fill=(*mix(WHITE,col,.10),int(220*local)),
                            outline=(*col,int(180*local)),width=2)
        centered(d,(w*.35,y),claim,font(FNSB,12),INK)
        centered(d,(w*.77,y),status,font(FNSB,12),col)
    seal(im,"DISCIPLINE","the universe expanding and being continuously created are not contradictory")

def vis_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for i in range(int(35*r)):
        a=random.uniform(0,math.tau); rr=random.uniform(5,130)*r
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.ellipse((x-2,y-2,x+2,y+2),fill=(*GOLD,int(100+100*pulse(t+i))))
    if r>.7:
        q=(r-.7)/.3
        glow_circle(im,cx,cy,16,GOLD,int(180*q),13)
        centered(d,(cx,cy),"YOU ARE BEING CREATED NOW",font(FSB,20),(*GOLD,int(200*q)))
    seal(im,"CREATION IS PRESENT","not an explosion in the past — an act happening now",GOLD)

VISUALS={}
for k,v in list(locals().items()):
    if k.startswith('vis_'): VISUALS[k[4:]]=v
@dataclass
class Scene:
    title:str; narration:str; duration:float; visual:str; params:dict
SCENES=[
    Scene("Seth's cosmology","'The physical universe was not born through some explosion of energy which is being dispersed.'",9.0,"claim",{}),
    Scene("Created everywhere","'It is everywhere being created at all of its points at each moment.'",8.5,"claim",{}),
    Scene("The Big Bang","The standard story: one moment of creation — then 13.8 billion years of cooling.",7.5,"big_bang",{}),
    Scene("What it explains","The Big Bang explains the cosmic microwave background, element abundances, expansion.",8.0,"big_bang",{}),
    Scene("What it leaves out","Why is there something rather than nothing? And what creates the present moment?",8.5,"big_bang",{}),
    Scene("Continuous creation","Seth: creation is not a past event — it is a present act.",8.5,"continuous",{}),
    Scene("Every point","Every point in space is a node of ongoing creation.",8.0,"continuous",{}),
    Scene("The psyche participates","'Your psyche is being drawn back into itself and out of itself in psychological pulses.'",9.0,"psyche_pulse",{}),
    Scene("In and out","These pulses have a correlation with the behavior of electrons.",8.5,"psyche_pulse",{}),
    Scene("The electron correlation","Electrons are not 'there' — they are events. Their appearance and disappearance mirrors consciousness.",9.0,"electron",{}),
    Scene("Quantum creation","In quantum field theory, particles are constantly created and annihilated in the vacuum.",8.5,"electron",{}),
    Scene("Steady state","The universe is not running down — it is being continuously replenished.",8.0,"steady_state",{}),
    Scene("Not the old cosmology","This is not the 1950s steady state theory — it is a different claim about the nature of creation.",8.5,"steady_state",{}),
    Scene("Participatory universe","Wheeler: 'We are not only observers. We are participators.'",8.5,"participatory",{}),
    Scene("Creation needs consciousness","In this view, consciousness is not an afterthought — it is intrinsic to reality.",9.0,"participatory",{}),
    Scene("Caution","Continuous creation is a metaphysical claim, not a physical theory.",8.5,"caution",{}),
    Scene("The resonance","But it resonates with quantum field theory and the participatory universe.",8.5,"caution",{}),
    Scene("Closing","You are not living in the aftermath of an explosion. You are being created — now.",9.5,"final",{}),
    Scene("Final frame","Creation is not behind you. It is this moment.",7.0,"final",{}),
]

def rf(sc,fi,fc,w2,h2,se):
    u=fi/max(1,fc-1); t=u*sc.duration; im=field(w2,h2,se)
    VISUALS[sc.visual](im,u,t,sc.params); border(im); return im.convert("RGB")
def _ff():
    f2=shutil.which("ffmpeg")
    if not f2: raise RuntimeError("ffmpeg required"); return f2
def es(idx,f2):
    o=SCENES_DIR/f"scene_{idx:03d}.mp4"; d=FRAMES/f"scene_{idx:03d}"
    subprocess.run([_ff(),"-y","-framerate",str(f2),"-i",str(d/"%05d.jpg"),
        "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(o)],
        check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); return o
def rs(idx,s,f2,w2,h2,prev):
    d=FRAMES/f"scene_{idx:03d}"; d.mkdir(parents=True,exist_ok=True)
    SCENES_DIR.mkdir(parents=True,exist_ok=True); cnt=max(2,round(s.duration*f2))
    if prev:
        for oi,fi2 in enumerate([0,int(cnt*.33),int(cnt*.72),cnt-1]):
            rf(s,fi2,cnt,w2,h2,idx*10000+fi2).save(d/f"preview_{oi:02d}.jpg",quality=95); return d
    for fi2 in range(cnt):
        p2=d/f"{fi2:05d}.jpg"
        if p2.exists(): continue
        rf(s,fi2,cnt,w2,h2,idx*10000+fi2).save(p2,quality=95,subsampling=0)
    return es(idx,f2)
def concat(paths):
    cp=OUTPUT/"concat.txt"
    cp.write_text("\n".join(f"file '{p.resolve()}'" for p in paths),encoding="utf-8")
    final=OUTPUT/"universe_created_every_moment.mp4"
    subprocess.run([_ff(),"-y","-f","concat","-safe","0","-i",str(cp),"-c","copy","-movflags","+faststart",str(final)],
        check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); return final
def export_timeline():
    cursor=0.0; recs=[]
    for i,s in enumerate(SCENES,1):
        item=asdict(s); item["scene_id"]=f"scene_{i:03d}"
        item["start_seconds"]=round(cursor,3); cursor+=s.duration; item["end_seconds"]=round(cursor,3); recs.append(item)
    p=OUTPUT/"narration_timeline.json"
    p.write_text(json.dumps({"title":"the universe is created at every point every moment",
        "scene_count":len(SCENES),"runtime_seconds":round(cursor,3),
        "shot_duration_range":[5,10],"scenes":recs},indent=2,ensure_ascii=False),encoding="utf-8"); return p
def contact_sheet(w2,h2):
    tw,th=320,int(320*h2/w2); cols,rows=4,math.ceil(len(SCENES)/4); ch=th+48
    s=Image.new("RGB",(cols*tw,rows*ch),IVORY); d2=ImageDraw.Draw(s); lf=font(FNSB,14)
    for i,sc in enumerate(SCENES,1):
        cnt=max(2,round(sc.duration*FPS))
        im=rf(sc,int(cnt*.72),cnt,w2,h2,i*10000+72); im.thumbnail((tw,th))
        sl=i-1; x=(sl%cols)*tw; y=(sl//cols)*ch; s.paste(im,(x,y))
        d2.text((x+9,y+th+7),f"{i:02d}  {sc.title}",font=lf,fill=INK)
    p=OUTPUT/"contact_sheet.jpg"; s.save(p,quality=94); return p
def parse_args():
    p2=argparse.ArgumentParser()
    p2.add_argument("--fps",type=int,default=FPS); p2.add_argument("--width",type=int,default=W)
    p2.add_argument("--height",type=int,default=H); p2.add_argument("--scene",type=int)
    p2.add_argument("--preview",action="store_true"); p2.add_argument("--no-contact-sheet",action="store_true")
    return p2.parse_args()
def main():
    a2=parse_args()
    OUTPUT.mkdir(parents=True,exist_ok=True); FRAMES.mkdir(parents=True,exist_ok=True); SCENES_DIR.mkdir(parents=True,exist_ok=True)
    tl=export_timeline(); total=sum(s.duration for s in SCENES)
    print(f"Timeline: {tl}\nScenes: {len(SCENES)}\nRuntime: {total/60:.2f} min")
    if a2.scene:
        if not 1<=a2.scene<=len(SCENES): raise ValueError("scene range")
        print(rs(a2.scene,SCENES[a2.scene-1],a2.fps,a2.width,a2.height,a2.preview)); return
    rendered=[]
    for i,s in enumerate(SCENES,1):
        print(f"[{i:02d}/{len(SCENES):02d}] {s.title} ({s.duration:.1f}s)")
        rendered.append(rs(i,s,a2.fps,a2.width,a2.height,a2.preview))
    final=concat(rendered); print(f"Final: {final}")
    if not a2.no_contact_sheet: print(f"Contact: {contact_sheet(a2.width,a2.height)}")
    print("Done.")
if __name__=="__main__": main()
