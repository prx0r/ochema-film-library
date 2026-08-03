#!/usr/bin/env python3
"""
YOUR DNA IS A SUPERCONDUCTOR PROGRAMMING REALITY
The Cassiopaean Claim That Modern Physics Is Beginning to Prove

CENTRAL CLAIM
-------------
The Cassiopaean transcripts state that DNA is not merely a protein-coding
molecule but a superconducting "neurotransceiver" that maintains the
"program illusion" we experience as linear time and physical reality.

Modern research on DNA charge transport, bioelectrics, and the
electromagnetic properties of living systems is independently converging
on a similar picture: DNA conducts electricity, cells communicate
electrically, and the boundary between "hardware" and "software" in
biology may not exist.

This does not mean reality is fake.
It means the physical world may be more like a process than a thing.

FILM THESIS
-----------
The conventional picture:
DNA → codes proteins → builds body → generates consciousness

The Cassiopaean picture:
consciousness → interacts with DNA → DNA transceives → maintains reality program

The modern bioelectric picture:
bioelectric fields → pattern information → cells navigate morphospace → body forms

All three may be describing the same interface from different angles.

OUTPUT
------
output_dna_superconductor/
"""

from __future__ import annotations
import argparse, json, math, random, shutil, subprocess
from dataclasses import asdict, dataclass
from pathlib import Path; from typing import Callable
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
OUTPUT = Path("/mnt/HC_Volume_106427611/goldrender/output_dna_superconductor")
FRAMES = OUTPUT / "frames"; SCENES_DIR = OUTPUT / "scenes"
W, H, FPS = 1280, 720, 10

IVORY=(249,247,241); WHITE=(255,254,250); INK=(29,33,39); SOFT_INK=(86,91,98)
SILVER=(180,187,194); PALE_SILVER=(224,228,228); CYAN=(57,156,180); PALE_CYAN=(196,227,233)
GOLD=(194,156,72); PALE_GOLD=(236,219,175); GREEN=(70,139,99); CRIMSON=(162,58,69)
VIOLET=(109,83,153); PALE_VIOLET=(218,208,235)
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

def draw_helix(cx,cy,w,h,t,reveal=1.0):
    """Return left and right strand points of a DNA helix."""
    lpts,rpts=[],[]
    steps=60
    for i in range(steps):
        q=i/(steps-1)
        if q>reveal: break
        x=cx-w/2+q*w
        o=math.sin(q*math.tau*4+t)*h*0.4
        lpts.append((x,cy+o-h*0.15))
        rpts.append((x,cy+o+h*0.15))
    return lpts,rpts

def draw_helix_full(im,cx,cy,w,h,t,reveal=1.0):
    d=ImageDraw.Draw(im)
    l,r=draw_helix(cx,cy,w,h,t,reveal)
    if len(l)>1:
        d.line(l,fill=(*CYAN,200),width=3)
        d.line(r,fill=(*CYAN,200),width=3)
        for i in range(0,len(l),3):
            d.line((l[i][0],l[i][1],r[i][0],r[i][1]),fill=(*GOLD,120),width=2)

def draw_wave_signal(im,cx,cy,amp,phase=0.0):
    pts=[]
    for i in range(80):
        x=cx-40+i
        y=cy+math.sin(i*.15+phase)*amp
        pts.append((x,y))
    glow_line(im,pts,GOLD,3,160,8)

# =============================================================================
# VISUALS
# =============================================================================

def vis_conventional(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    d.ellipse((cx-50,cy-55,cx+50,cy+55),fill=(*PALE_GOLD,80),outline=(*INK,170),width=4)
    centered(d,(cx,cy-10),"DNA → PROTEIN → BODY",font(FSB,18),INK)
    arrow(d,(cx,cy+30),(cx,cy+60),INK,3,8)
    d.ellipse((cx-30,cy+65,cx+30,cy+105),fill=(*PALE_SILVER,80),outline=(*INK,120),width=3)
    centered(d,(cx,cy+85),"CONSCIOUSNESS?",font(FNS,14),SOFT_INK)
    if r>.55:
        d.rounded_rectangle((w*.12,h*.08,w*.88,h*.22),radius=10,
                            fill=(*mix(WHITE,CRIMSON,.06),int(180*(r-.55)/.45)),
                            outline=(*CRIMSON,int(150*(r-.55)/.45)),width=2)
        centered(d,(w*.50,h*.15),"THE STANDARD STORY LEAVES SOMETHING OUT",font(FNSB,14),CRIMSON)
    seal(im,"DNA AS BLUEPRINT","the conventional view — a code that builds a machine")

def vis_charge_transport(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    draw_helix_full(im,cx,cy,w*.50,h*.10,t*.3,r)
    if r>.3:
        q=(r-.3)/.7
        ex=lerp(cx-w*.15,cx+w*.15,math.sin(t*.5)*.5+.5)
        ey=cy+math.sin(t*.3)*8
        d.ellipse((ex-6,ey-6,ex+6,ey+6),fill=(*GOLD,int(180*q)),outline=(*PALE_GOLD,int(120*q)),width=2)
        if q>.5:
            centered(d,(cx,h*.76),"DNA CONDUCTS ELECTRICITY",font(FNSB,16),GOLD)
            centered(d,(cx,h*.81),"charge transport is real — electrons move through the helix",font(FNS,13),SOFT_INK)
    seal(im,"DNA CHARGE TRANSPORT","electrons move through the stacked base pairs — a molecular wire")

def vis_superconductor(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    draw_helix_full(im,cx,cy,w*.44,h*.08,t*.4,r)
    if r>.4:
        q=(r-.4)/.6
        for i in range(6):
            a=i*math.tau/6+t*0.2
            rr=lerp(35,90,q)
            x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
            d.line((cx,cy,x,y),fill=(*GOLD,int(80*q)),width=2)
            d.ellipse((x-5,y-5,x+5,y+5),fill=(*PALE_GOLD,int(150*q)),outline=(*GOLD,int(120*q)),width=2)
    seal(im,"THE CASSIOPAEAN CLAIM","DNA acts as a superconductor — a neurotransceiver for consciousness")

def vis_neurotransceiver(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    draw_helix_full(im,cx,cy,w*.40,h*.07,t*.2,r)
    if r>.5:
        q=(r-.5)/.5
        for side in [-1,1]:
            for i in range(3):
                a=i*math.tau/3+t*0.3
                x=cx+side*w*.12+math.cos(a)*30*q
                y=cy+math.sin(a)*20*q
                d.line((cx+side*w*.20,cy,x,y),fill=(*VIOLET,int(100*q)),width=2)
                d.ellipse((x-3,y-3,x+3,y+3),fill=(*PALE_VIOLET,int(150*q)))
    seal(im,"NEUROTRANSCEIVER","receiving and transmitting — DNA as an antenna for consciousness")

def vis_program_illusion(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    # grid
    for i in range(10):
        x=w*.10+i*w*.80/9
        d.line((x,h*.12,x,h*.72),fill=(*INK,int(40+30*math.sin(t+i))),width=1)
    for j in range(8):
        y=h*.12+j*h*.60/7
        d.line((w*.10,y,w*.90,y),fill=(*INK,int(40+30*math.sin(t+j))),width=1)
    if r>.4:
        q=(r-.4)/.6
        d.rounded_rectangle((cx-w*.25,cy-22,cx+w*.25,cy+22),radius=10,
                            fill=(*mix(WHITE,VIOLET,.08),int(180*q)),
                            outline=(*VIOLET,int(150*q)),width=2)
        centered(d,(cx,cy),"PERCEPTION IS PART OF THE ILLUSION",font(FNSB,14),(*VIOLET,int(220*q)))
    seal(im,"THE PROGRAM ILLUSION","the Cassiopaeans: what you see as solid is a program readout")

def viz_time_illusion(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    pts=[]
    for i in range(160):
        x=w*.12+i*w*.76/159
        y=cy+math.sin(i*.1+t*.3)*25
        pts.append((x,y))
    glow_line(im,partial(pts,r),CYAN,4,180,10)
    if r>.5:
        q=(r-.5)/.5
        d.ellipse((cx-35*q,cy-20*q,cx+35*q,cy+20*q),outline=(*GOLD,int(150*q)),width=3)
        centered(d,(cx,cy),"ALL TIME IS NOW",font(FSB,18),(*GOLD,int(200*q)))
    seal(im,"LINEAR TIME IS A DNA READOUT","the illusion of sequence is maintained by the hardware of the body")

def vis_levin_bridge(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    draw_helix_full(im,cx-w*.18,cy,w*.20,h*.06,t*.2,r)
    # bioelectric field
    for rr in range(20,90,20):
        d.ellipse((cx+w*.12-rr,cy-rr*.5,cx+w*.12+rr,cy+rr*.5),
                  outline=(*GOLD,int(60*(1-rr/100))),width=2)
    glow_circle(im,cx+w*.12,cy,10,GOLD,160,9)
    if r>.5:
        q=(r-.5)/.5
        labels=["DNA CHARGE TRANSPORT","BIOELECTRIC FIELD","PATTERN MEMORY"]
        cols=[CYAN,GOLD,GREEN]
        for i,(lb,c) in enumerate(zip(labels,cols)):
            yp=h*(.14+i*.10)
            d.rounded_rectangle((w*.15,yp-14,w*.85,yp+14),radius=8,
                                fill=(*mix(WHITE,c,.08),int(180*q)),
                                outline=(*c,int(140*q)),width=2)
            centered(d,(w*.50,yp),lb,font(FNSB,13),c)
    seal(im,"MODERN SCIENCE CONVERGES","Levin's bioelectric work shows cells communicate electrically — DNA is part of a larger field")

def vis_osiris(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    # body outline
    d.ellipse((cx-20,cy-120,cx+20,cy-76),outline=(*INK,160),width=4)
    d.line((cx,cy-76,cx,cy+45),fill=(*INK,160),width=5)
    d.line((cx-50,cy-45,cx+50,cy-45),fill=(*INK,160),width=4)
    d.line((cx,cy+45,cx-40,cy+120),fill=(*INK,160),width=4)
    d.line((cx,cy+45,cx+40,cy+120),fill=(*INK,160),width=4)
    if r>.2:
        cut=min(1.0,(r-.2)/.3)
        for x in [cx-20,cx+20]:
            d.line((x,cy-30,x,cy+10),fill=(*CRIMSON,int(200*cut)),width=5)
    if r>.6:
        q=(r-.6)/.4
        centered(d,(cx,h*.78),"THE BODY OF OSIRIS CUT APART",font(FNSB,14),CRIMSON)
        centered(d,(cx,h*.83),"knowledge centers removed from DNA",font(FNS,13),SOFT_INK)
    seal(im,"THE OSIRIAN CYCLE","the myth encodes the reduction of human frequency range")

def vis_upgrade(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    draw_helix_full(im,cx,cy,w*.44,h*.08,t*.5,r)
    if r>.5:
        q=(r-.5)/.5
        pts=[]
        for i in range(40):
            x=w*.10+i*w*.80/39
            y=cy+math.sin(i*.2+t*.5)*45
            pts.append((x,y))
        glow_line(im,partial(pts,q),GOLD,5,int(150*q),12)
    if r>.7:
        q2=(r-.7)/.3
        centered(d,(cx,cy-h*.12),"YOU DON'T GET — YOU RECEIVE",font(FNSB,14),(*GOLD,int(200*q2)))
    seal(im,"THE UPGRADE","interaction with the Wave adds frequency — if vibration is aligned")

def viz_caution(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    rows=[("DNA CHARGE TRANSPORT IS EXPERIMENTALLY VERIFIED","SUPPORTED",GREEN),
          ("DNA CAN ACT AS A MOLECULAR WIRE","SUPPORTED",CYAN),
          ("DNA IS A ROOM-TEMPERATURE SUPERCONDUCTOR","NOT ESTABLISHED",CRIMSON),
          ("DNA TRANSCEIVES CONSCIOUSNESS DIRECTLY","NOT ESTABLISHED",CRIMSON)]
    q=ease(u)
    for i,(claim,status,col) in enumerate(rows):
        local=clamp(q*len(rows)-i); y=h*(.23+i*.13)
        d.rounded_rectangle((w*.14,y-28,w*.86,y+28),radius=14,
                            fill=(*mix(WHITE,col,.10),int(220*local)),
                            outline=(*col,int(180*local)),width=2)
        centered(d,(w*.39,y),claim,font(FNSB,13),INK)
        centered(d,(w*.74,y),status,font(FNSB,13),col)
    seal(im,"DISCIPLINE","DNA is extraordinary — but we must distinguish verified from speculative")

def vis_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    draw_helix_full(im,cx,cy,w*.55,h*.10,t*.4,r)
    for rr in range(45,260,30):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(55*(1-rr/280))),width=2)
    if r>.6:
        q=(r-.6)/.4
        glow_circle(im,cx,cy,16,GOLD,int(180*q),13)
        if q>.5:
            centered(d,(cx,cy),"I AM THE HARDWARE",font(FSB,22),(*GOLD,int(200*(q-.5)*2)))
            centered(d,(cx,cy+35),"AND THE SOFTWARE",font(FSB,18),(*CYAN,int(160*(q-.5)*2)))
    seal(im,"YOUR DNA IS A SUPERCONDUCTOR","the body is not a machine — it is an antenna",GOLD)


VISUALS={}
for k,v in list(locals().items()):
    if k.startswith('vis_') or k.startswith('viz_'):
        VISUALS[k[4:]]=v

@dataclass
class Scene:
    title:str; narration:str; duration:float; visual:str; params:dict

SCENES = [
    Scene("The standard story","DNA codes proteins. Proteins build the body. The body houses consciousness.",7.0,"conventional",{}),
    Scene("What's missing","This story leaves out something essential: DNA conducts electricity.",8.0,"conventional",{}),
    Scene("Charge transport","In the 1990s, researchers discovered that electrons move through DNA's stacked base pairs.",8.5,"charge_transport",{}),
    Scene("Molecular wire","DNA can act as a conductor, semiconductor, or insulator depending on its environment.",8.5,"charge_transport",{}),
    Scene("The Cassiopaean claim","In 1994, a channeled source stated that DNA is a superconductor — a neurotransceiver for consciousness.",9.0,"superconductor",{}),
    Scene("Not just a blueprint","DNA, they said, is 'the method used for creation and maintenance of program illusions.'",8.5,"superconductor",{}),
    Scene("Neurotransceiver","Receiving and transmitting — DNA as an antenna between consciousness and the physical world.",8.5,"neurotransceiver",{}),
    Scene("Thought pattern programs","Electromagnetic wave transmission facilitates thought patterns through the DNA infrastructure.",9.0,"neurotransceiver",{}),
    Scene("The program illusion","'That perception is part of the illusion. What you perceive as solid is a program readout.'",8.0,"program_illusion",{}),
    Scene("Perception is programmed","The Cassiopaeans: your perception of linear time is maintained by how DNA interacts with electromagnetic fields.",9.5,"program_illusion",{}),
    Scene("Linear time","If DNA is a clock, what is it measuring? And what if the clock is also the clockmaker?",8.5,"time_illusion",{}),
    Scene("Simultaneity","All time is now. Sequence is a readout — not a fundamental feature of reality.",8.0,"time_illusion",{}),
    Scene("Modern convergence","Michael Levin's lab shows that bioelectric fields carry pattern information across cellular networks.",9.0,"levin_bridge",{}),
    Scene("The field","Cells communicate electrically. DNA is part of a larger bioelectric field that navigates morphospace.",9.5,"levin_bridge",{}),
    Scene("Levin bridge","Levin: 'The bioelectric field is the hardware of the body's memory.' The Cassiopaeans: 'DNA is a superconductor.'",9.0,"levin_bridge",{}),
    Scene("Osiris","The cutting up of Osiris' body represents the reduction of human knowledge capacity — the removal of frequencies from DNA.",9.5,"osiris",{}),
    Scene("The myth encodes","Ancient knowledge encoded as myth: the fall was a reduction in the number of accessible DNA strands.",9.0,"osiris",{}),
    Scene("The upgrade","'You don't get added strands. You receive. Interaction with the upcoming wave, if vibration is aligned.'",9.5,"upgrade",{}),
    Scene("Alignment","The Wave is coming. Your DNA must be tuned to receive it. Knowledge protects.",9.0,"upgrade",{}),
    Scene("Caution","DNA charge transport is real. DNA as a superconductor is not established. The boundary matters.",9.0,"caution",{}),
    Scene("The distinction","The Cassiopaean claim is extraordinary. But extraordinary claims require disciplined scrutiny.",8.5,"caution",{}),
    Scene("Closing","Your DNA is not a blueprint. It is an antenna. The program is running — and you are the programmer.",9.5,"final",{}),
    Scene("Final frame","You don't get. You receive. The Wave is here. Align your vibration.",7.0,"final",{}),
]

def rf(sc,fi,fc,w2,h2,se):
    u=fi/max(1,fc-1); t=u*sc.duration
    im=field(w2,h2,se)
    VISUALS[sc.visual](im,u,t,sc.params); border(im)
    return im.convert("RGB")
def _ff():
    f2=shutil.which("ffmpeg")
    if not f2: raise RuntimeError("ffmpeg required")
    return f2
def es(idx,f2):
    o=SCENES_DIR/f"scene_{idx:03d}.mp4"; d=FRAMES/f"scene_{idx:03d}"
    subprocess.run([_ff(),"-y","-framerate",str(f2),"-i",str(d/"%05d.jpg"),
        "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",
        "-movflags","+faststart",str(o)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return o
def rs(idx,s,f2,w2,h2,prev):
    d=FRAMES/f"scene_{idx:03d}"; d.mkdir(parents=True,exist_ok=True)
    SCENES_DIR.mkdir(parents=True,exist_ok=True)
    cnt=max(2,round(s.duration*f2))
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
    final=OUTPUT/"dna_superconductor.mp4"
    subprocess.run([_ff(),"-y","-f","concat","-safe","0","-i",str(cp),
        "-c","copy","-movflags","+faststart",str(final)],
        check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return final
def export_timeline():
    cursor=0.0; recs=[]
    for i,s in enumerate(SCENES,1):
        item=asdict(s); item["scene_id"]=f"scene_{i:03d}"
        item["start_seconds"]=round(cursor,3); cursor+=s.duration
        item["end_seconds"]=round(cursor,3); recs.append(item)
    p=OUTPUT/"narration_timeline.json"
    p.write_text(json.dumps({"title":"your DNA is a superconductor",
        "subtitle":"programming reality — the Cassiopaean claim meets modern physics",
        "scene_count":len(SCENES),"runtime_seconds":round(cursor,3),
        "shot_duration_range":[5,10],
        "continuity_object":"DNA helix transforming into an antenna",
        "visual_arc":["conventional","charge transport","superconductor","program","time","convergence","upgrade","caution"],
        "scenes":recs},indent=2,ensure_ascii=False),encoding="utf-8")
    return p
def contact_sheet(w2,h2):
    tw,th=320,int(320*h2/w2); cols,rows=4,math.ceil(len(SCENES)/4); ch=th+48
    s=Image.new("RGB",(cols*tw,rows*ch),IVORY); d2=ImageDraw.Draw(s)
    lf=font(FNSB,14)
    for i,sc in enumerate(SCENES,1):
        cnt=max(2,round(sc.duration*FPS))
        im=rf(sc,int(cnt*.72),cnt,w2,h2,i*10000+72)
        im.thumbnail((tw,th)); sl=i-1
        x,y=(sl%cols)*tw,(sl//cols)*ch
        s.paste(im,(x,y)); d2.text((x+9,y+th+7),f"{i:02d}  {sc.title}",font=lf,fill=INK)
    p=OUTPUT/"contact_sheet.jpg"; s.save(p,quality=94); return p
def parse_args():
    p2=argparse.ArgumentParser()
    p2.add_argument("--fps",type=int,default=FPS)
    p2.add_argument("--width",type=int,default=W); p2.add_argument("--height",type=int,default=H)
    p2.add_argument("--scene",type=int); p2.add_argument("--preview",action="store_true")
    p2.add_argument("--no-contact-sheet",action="store_true")
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
