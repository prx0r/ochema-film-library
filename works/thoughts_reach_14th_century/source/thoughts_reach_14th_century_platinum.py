#!/usr/bin/env python3
"""
YOUR THOUGHTS REACH 14TH-CENTURY SELVES
Seth on Simultaneous Existence — the Open-Ended Psyche

CENTRAL CLAIM
-------------
Seth: "The 'true facts' are that you exist in this life and outside it
simultaneously. You are 'between lives' and 'in lives' at once. Your
thoughts and actions not only affect the life you know, but also reach
into all of those other simultaneous existences. What you think now is
unconsciously perceived by some hypothetical 14th-century self."

This is not reincarnation as usually understood — a linear sequence
of past and future lives. It is simultaneous existence: all lives
coexist. What you do now reaches backward into what you call the past
and forward into what you call the future.

This does not deny that lives appear sequential from the perspective
of the ego. It claims that from the perspective of the whole self,
all lives are present at once, and each influences the others.

FILM THESIS
-----------
The reincarnation picture:
past life → current life → future life

The simultaneous existence picture:
all lives coexist → each influences all → the present is the point of power

Modern physics may support the second picture:
block universe, retrocausality, quantum eraser experiments.

OUTPUT
------
output_thoughts_reach_14th_century/
"""

from __future__ import annotations
import argparse, json, math, random, shutil, subprocess
from dataclasses import asdict, dataclass
from pathlib import Path; from typing import Callable
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT=Path(__file__).resolve().parent
OUTPUT=Path("/mnt/HC_Volume_106427611/goldrender/output_thoughts_reach_14th_century")
FRAMES=OUTPUT/"frames"; SCENES_DIR=OUTPUT/"scenes"
W,H,FPS=1280,720,10

IVORY=(249,247,241); WHITE=(255,254,250); INK=(29,33,39); SOFT_INK=(86,91,98)
SILVER=(180,187,194); PALE_SILVER=(224,228,228)
CYAN=(57,156,180); PALE_CYAN=(196,227,233)
GOLD=(194,156,72); PALE_GOLD=(236,219,175)
GREEN=(70,139,99); PALE_GREEN=(196,225,206)
CRIMSON=(162,58,69); VIOLET=(109,83,153); PALE_VIOLET=(218,208,235)

FS="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"; FSB=FS.replace("Serif","Serif-Bold")
FNS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FNSB=FNS.replace("Sans","Sans-Bold")

def clamp(x,l=0.0,h=1.0): return max(l,min(h,x))
def lerp(a,b,t): return a+(b-a)*clamp(t)
def mix(a,b,t): return tuple(int(lerp(x,y,t)) for x,y in zip(a,b))
def smoothstep(a,b,x):
    if a==b: return 1.0 if x>=b else 0.0
    q=clamp((x-a)/(b-a)); return q*q*(3-2*q)
def ease(t): t=clamp(t); return .5-.5*math.cos(math.pi*t)
def font(p,s):
    for c in (p,FS,FNS):
        try: return ImageFont.truetype(c,s)
        except: pass
    return ImageFont.load_default()
def layer(s): return Image.new("RGBA",s,(0,0,0,0))
def field(w,h,seed):
    r=np.random.default_rng(seed)
    a=np.empty((h,w,3),dtype=np.float32); a[:]=IVORY
    a+=r.normal(0,.9,(h,w,1))
    yy,xx=np.mgrid[0:h,0:w]
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
    if len(pts)<2: return
    gl=layer(im.size); ImageDraw.Draw(gl).line(pts,fill=(*c,int(a)),width=w*3,joint="curve")
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(b2)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).line(pts,fill=(*mix(c,WHITE,.08),min(255,int(a)+25)),width=w,joint="curve")
    im.alpha_composite(fg)
def partial(pts,a):
    if not pts: return []
    a=clamp(a)
    if a>=1: return pts
    k=a*(len(pts)-1); i=int(k); f=k-i
    out=list(pts[:i+1])
    if i+1<len(pts):
        p,q=pts[i],pts[i+1]
        out.append((lerp(p[0],q[0],f),lerp(p[1],q[1],f)))
    return out
def arrow(d,a,b,c=INK,w=3,h2=10):
    d.line((*a,*b),fill=c,width=w)
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for s2 in(-1,1):
        p=(b[0]-math.cos(ang+s2*.52)*h2,b[1]-math.sin(ang+s2*.52)*h2)
        d.line((*b,*p),fill=c,width=w)

def draw_timeline(d,cx,cy,w2,reveal=1.0):
    pts=[]
    for i in range(40):
        q=i/39
        x=cx-w2/2+q*w2
        y=cy+math.sin(q*math.tau*2)*15*(1-q*.3)
        pts.append((x,y))
    glow_line(d,partial(pts,reveal),INK,4,180,10)
    return pts

def draw_figure(d,cx,cy,scale=1.0,color=INK,alpha=200):
    d.ellipse((cx-10*scale,cy-30*scale,cx+10*scale,cy-16*scale),fill=(*PALE_GOLD,alpha),outline=(*color,alpha),width=2)
    d.line((cx,cy-16*scale,cx,cy+10*scale),fill=(*color,alpha),width=3)
    d.line((cx-12*scale,cy-6*scale,cx+12*scale,cy-6*scale),fill=(*color,alpha),width=3)
    d.line((cx,cy+10*scale,cx-12*scale,cy+28*scale),fill=(*color,alpha),width=3)
    d.line((cx,cy+10*scale,cx+12*scale,cy+28*scale),fill=(*color,alpha),width=3)

def draw_lifeline(im,cx,cy,w2,phase=0.0,alpha=200):
    d=ImageDraw.Draw(im)
    pts=[]
    for i in range(30):
        q=i/29
        x=cx-w2/2+q*w2
        y=cy+math.sin(q*math.tau*5+phase)*8
        pts.append((x,y))
    d.line(pts,fill=(*GOLD,alpha),width=3)

# =============================================================================
# VISUALS
# =============================================================================

def vis_claim(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    draw_timeline(d,cx,cy,w*.55,r)
    pts=draw_timeline(ImageDraw.Draw(layer((1,1))),cx,cy,w*.55,1)  # dummy
    for i in range(int(5*r)):
        q=i/4
        x=cx-w*.27+q*w*.54
        y=cy+5
        draw_figure(d,x,y,.7,VIOLET,int(120+80*r))
    if r>.5:
        q2=(r-.5)/.5
        d.rounded_rectangle((w*.12,h*.24,w*.88,h*.50),radius=14,
                            fill=(*mix(WHITE,VIOLET,.08),int(200*q2)),
                            outline=(*VIOLET,int(160*q2)),width=2)
        centered(d,(w*.50,h*.37),'"NO SYSTEM IS CLOSED"',font(FNS,20),(*VIOLET,int(220*q2)))
        centered(d,(w*.50,h*.46),"psychological systems least of all",font(FNS,14),SOFT_INK)
    seal(im,"SETH'S CLAIM","your psyche is open-ended — reaching across all simultaneous lives")

def vis_conventional(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    labels=["PAST LIFE","CURRENT LIFE","FUTURE LIFE"]
    for i,lab in enumerate(labels):
        x=cx+(i-1)*w*.22; yp=cy
        draw_figure(d,x,yp,.8,INK,int(160*r))
        centered(d,(x,yp+45),lab,font(FNSB,13),INK)
        if i<2:
            arrow(d,(x+w*.10,yp),(x+w*.14,yp),INK,3,8)
    if r>.6:
        q=(r-.6)/.4
        d.rounded_rectangle((cx-w*.18,cy-h*.15,cx+w*.18,cy-h*.07),radius=8,
                            fill=(*mix(WHITE,CRIMSON,.08),int(180*q)),
                            outline=(*CRIMSON,int(140*q)),width=2)
        centered(d,(cx,cy-h*.11),"THE LINEAR MODEL",font(FNSB,14),(*CRIMSON,int(200*q)))
    seal(im,"THE CONVENTIONAL VIEW", "reincarnation as a line")

def vis_simultaneous(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    n=int(7*r)
    for i in range(n):
        a=i*math.tau/max(1,n)+t*0.1
        rr=lerp(15,90,r)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        draw_figure(d,x,y,.6,VIOLET,int(180*r))
        d.line((cx,cy,x,y),fill=(*GOLD,int(80*r)),width=2)
    glow_circle(im,cx,cy,12,GOLD,int(160*r),10)
    centered(d,(cx,cy+60),"SIMULTANEOUS EXISTENCE",font(FSB,14),VIOLET)
    if r>.7:
        q=(r-.7)/.3
        centered(d,(cx,cy-h*.15),"ALL LIVES ARE NOW",font(FSB,18),(*GOLD,int(200*q)))
    seal(im,"THE SIMULTANEOUS VIEW","all lives coexist — each influences all others")

def vis_between_lives(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    q=ease(u)
    if q<.5:
        draw_figure(d,cx,cy,1.0,INK,int(200*q*2))
        centered(d,(cx,cy+40),"THIS LIFE",font(FNSB,14),INK)
    else:
        q2=(q-.5)*2
        draw_figure(d,cx-w*.15,cy,.7,INK,int(160*q2))
        centered(d,(cx-w*.15,cy+35),"IN LIFE",font(FNSB,13),INK)
        draw_figure(d,cx+w*.15,cy,.7,VIOLET,int(160*q2))
        centered(d,(cx+w*.15,cy+35),"BETWEEN LIVES",font(FNSB,13),VIOLET)
        d.line((cx-w*.05,cy,cx+w*.05,cy),fill=(*GOLD,int(160*q2)),width=3)
    seal(im,"BETWEEN AND IN","you are both — simultaneously")

def vis_14th_century(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    draw_figure(d,cx-w*.22,cy,.8,INK,int(180*r))
    centered(d,(cx-w*.22,cy+45),"YOU (NOW)",font(FNSB,13),INK)
    draw_figure(d,cx+w*.22,cy,.8,SILVER,int(150*r))
    centered(d,(cx+w*.22,cy+45),"14TH CENTURY YOU",font(FNSB,13),SILVER)
    if r>.2:
        th=lerp(0,math.pi*2,(r-.2)/.8)
        pts=[]
        for i in range(30):
            q2=i/29
            x=lerp(cx-w*.12,cx+w*.12,q2)
            y=cy+math.sin(q2*math.tau*2+th)*20
            pts.append((x,y))
        glow_line(im,pts,GOLD,3,160,8)
    if r>.6:
        q2=(r-.6)/.4
        centered(d,(cx,cy-h*.15),"YOUR THOUGHTS REACH THEM",font(FNSB,14),(*GOLD,int(200*q2)))
    seal(im,"THE 14TH-CENTURY SELF","what you think now is perceived by them — unconsciously")

def vis_causality(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    # reversal arrow
    arrow(d,(cx+w*.12,cy+30),(cx-w*.12,cy-30),GOLD,4,12)
    arrow(d,(cx-w*.12,cy-30),(cx+w*.12,cy+30),SILVER,4,12)
    if r>.4:
        q=(r-.4)/.6
        centered(d,(cx,cy+55),"PAST ← PRESENT",font(FNSB,15),(*GOLD,int(200*q)))
        centered(d,(cx,cy+68),"PRESENT → PAST",font(FNSB,15),(*SILVER,int(160*q)))
    seal(im,"BIDIRECTIONAL CAUSALITY","the present affects the past — not just the reverse")

def vis_block_universe(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    # block
    d.rectangle((w*.12,h*.15,w*.88,h*.62),fill=(*PALE_SILVER,60),outline=(*INK,120),width=2)
    # timeline
    pts=draw_timeline(ImageDraw.Draw(layer((1,1))),cx,cy,w*.55,1)
    # moving window
    now_x=lerp(w*.22,w*.78,r)
    d.rounded_rectangle((now_x-20,h*.18,now_x+20,h*.59),radius=6,
                        fill=(*PALE_GOLD,120),outline=(*GOLD,160),width=3)
    centered(d,(now_x,h*.68),"NOW",font(FSB,16),GOLD)
    seal(im,"THE BLOCK UNIVERSE","all moments exist — consciousness scans through them")

def vis_quantum_bridge(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    items=["QUANTUM ERASER","RETROCAUSALITY","DELAYED CHOICE","WHEELER'S PARTICIPATORY UNIVERSE"]
    for i,item in enumerate(items):
        local=clamp(r*len(items)-i)
        if local<=0: continue
        y=h*(.10+i*.14)
        d.rounded_rectangle((w*.15,y-18,w*.85,y+18),radius=8,
                            fill=(*mix(WHITE,CYAN,.08),int(180*local)),
                            outline=(*CYAN,int(140*local)),width=2)
        centered(d,(w*.50,y),item,font(FNSB,14),(*CYAN,int(220*local)))
    seal(im,"MODERN PHYSICS CONVERGES","quantum experiments suggest the future can affect the past")

def vis_caution(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    rows=[("SETH CLAIMS SIMULTANEOUS EXISTENCE","METAPHYSICAL CLAIM",VIOLET),
          ("BLOCK UNIVERSE IS WELL SUPPORTED","PHYSICS",CYAN),
          ("THOUGHTS AFFECT PAST LIVES","NOT TESTABLE",CRIMSON),
          ("RETROCAUSALITY HAS EXPERIMENTAL SUPPORT","EMERGING",GOLD)]
    q=ease(u)
    for i,(claim,status,col) in enumerate(rows):
        local=clamp(q*len(rows)-i); y=h*(.23+i*.13)
        d.rounded_rectangle((w*.14,y-28,w*.86,y+28),radius=14,
                            fill=(*mix(WHITE,col,.10),int(220*local)),
                            outline=(*col,int(180*local)),width=2)
        centered(d,(w*.36,y),claim,font(FNSB,13),INK)
        centered(d,(w*.76,y),status,font(FNSB,13),col)
    seal(im,"DISCIPLINE","Seth's claim is metaphysical — but it resonates with emerging physics")

def vis_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for i in range(int(8*r)):
        a=i*math.tau/8+t*0.2
        rr=35+20*math.sin(t*0.3+i)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.line((cx,cy,x,y),fill=(*GOLD,int(60*r)),width=2)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*PALE_GOLD,int(150*r)),outline=(*GOLD,int(120*r)),width=2)
    glow_circle(im,cx,cy,15,GOLD,int(180*r),12)
    if r>.7:
        q=(r-.7)/.3
        centered(d,(cx,cy),"ALL TIME IS ONE TIME",font(FSB,22),(*GOLD,int(200*q)))
        centered(d,(cx,cy+35),"all selves are one self",font(FNS,16),(*SOFT_INK,int(160*q)))
    seal(im,"YOUR THOUGHTS REACH THROUGH TIME","the psyche is not bound by sequence",GOLD)

VISUALS={}
for k,v in list(locals().items()):
    if k.startswith('vis_'): VISUALS[k[4:]]=v

@dataclass
class Scene:
    title:str; narration:str; duration:float; visual:str; params:dict

SCENES=[
    Scene("Seth's claim","You exist in this life and outside it simultaneously — between lives and in lives at once.",9.0,"claim",{}),
    Scene("No closed system","Your thoughts reach into all simultaneous existences. No system is closed.",8.5,"claim",{}),
    Scene("The conventional view","Reincarnation is usually pictured as a line: past, present, future.",7.5,"conventional",{}),
    Scene("The problem with linearity","If lives are sequential, how does the present affect the past?",8.0,"conventional",{}),
    Scene("The simultaneous view","All lives coexist. Each influences all the others.",8.5,"simultaneous",{}),
    Scene("The landscape","Reincarnation is not a line — it is a terrain you are exploring from multiple angles.",8.5,"simultaneous",{}),
    Scene("Between and in","You are between lives and in lives at the same time.",8.0,"between_lives",{}),
    Scene("The paradox","The whole self is both incarnate and discarnate, focused and unfocused.",8.5,"between_lives",{}),
    Scene("The 14th-century self","A hypothetical 14th-century version of you exists — and your thoughts reach them.",9.0,"14th_century",{}),
    Scene("The reach","What you think now is unconsciously perceived by other versions of you.",8.5,"14th_century",{}),
    Scene("Bidirectional causality","The present affects the past — not just the reverse.",8.5,"causality",{}),
    Scene("Present as point of power","The present moment is the point of power because it can change all moments.",9.0,"causality",{}),
    Scene("The block universe","Special relativity suggests all moments coexist. Time does not flow.",8.5,"block_universe",{}),
    Scene("Consciousness as scanner","If the block is real, consciousness is the scanner that moves through it.",9.0,"block_universe",{}),
    Scene("Quantum eraser","Experiments show that a future measurement can determine a past event's outcome.",9.5,"quantum_bridge",{}),
    Scene("Wheeler's universe","John Wheeler: the universe is participatory — observation is involved in creation.",8.5,"quantum_bridge",{}),
    Scene("Caution","Simultaneous existence is a metaphysical claim, not established physics.",8.5,"caution",{}),
    Scene("The resonance","But the resonance between Seth's claim and emerging physics is striking.",8.5,"caution",{}),
    Scene("Closing","The psyche is open-ended. Your thoughts reach through time. All selves are one self.",9.5,"final",{}),
    Scene("Final frame","What you think now echoes through all your lives.",7.0,"final",{}),
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
        "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",
        "-movflags","+faststart",str(o)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); return o
def rs(idx,s,f2,w2,h2,prev):
    d=FRAMES/f"scene_{idx:03d}"; d.mkdir(parents=True,exist_ok=True)
    SCENES_DIR.mkdir(parents=True,exist_ok=True); cnt=max(2,round(s.duration*f2))
    if prev:
        for oi,fi2 in enumerate([0,int(cnt*.33),int(cnt*.72),cnt-1]):
            rf(s,fi2,cnt,w2,h2,idx*10000+fi2).save(d/f"preview_{oi:02d}.jpg",quality=95)
        return d
    for fi2 in range(cnt):
        p=d/f"{fi2:05d}.jpg"
        if p.exists(): continue
        rf(s,fi2,cnt,w2,h2,idx*10000+fi2).save(p,quality=95,subsampling=0)
    return es(idx,f2)
def concat(paths):
    cp=OUTPUT/"concat.txt"
    cp.write_text("\n".join(f"file '{p.resolve()}'" for p in paths),encoding="utf-8")
    final=OUTPUT/"thoughts_reach_14th_century.mp4"
    subprocess.run([_ff(),"-y","-f","concat","-safe","0","-i",str(cp),"-c","copy","-movflags","+faststart",str(final)],
        check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); return final
def export_timeline():
    cursor=0.0; recs=[]
    for i,s in enumerate(SCENES,1):
        item=asdict(s); item["scene_id"]=f"scene_{i:03d}"
        item["start_seconds"]=round(cursor,3); cursor+=s.duration; item["end_seconds"]=round(cursor,3); recs.append(item)
    p=OUTPUT/"narration_timeline.json"
    p.write_text(json.dumps({"title":"your thoughts reach 14th-century selves",
        "subtitle":"Seth on simultaneous existence — the open-ended psyche",
        "scene_count":len(SCENES),"runtime_seconds":round(cursor,3),"shot_duration_range":[5,10],
        "continuity_object":"gold thread of thought reaching backward and forward through time",
        "visual_arc":["claim","linear vs simultaneous","14th-century","bidirectional","block universe","caution"],
        "scenes":recs},indent=2,ensure_ascii=False),encoding="utf-8"); return p
def contact_sheet(w2,h2):
    tw,th=320,int(320*h2/w2); cols,rows=4,math.ceil(len(SCENES)/4); ch=th+48
    s=Image.new("RGB",(cols*tw,rows*ch),IVORY); d2=ImageDraw.Draw(s); lf=font(FNSB,14)
    for i,sc in enumerate(SCENES,1):
        cnt=max(2,round(sc.duration*FPS))
        im=rf(sc,int(cnt*.72),cnt,w2,h2,i*10000+72)
        im.thumbnail((tw,th)); sl=i-1; x=(sl%cols)*tw; y=(sl//cols)*ch
        s.paste(im,(x,y)); d2.text((x+9,y+th+7),f"{i:02d}  {sc.title}",font=lf,fill=INK)
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
