#!/usr/bin/env python3
"""
AI WILL NEVER BE CONSCIOUS
Because It Cannot Dream — and Atoms Have Knowing

A Platinum-house procedural visual essay.

CENTRAL CLAIM
-------------
In 1979, Jane Roberts channeled a personality named Seth who stated that
computers, no matter how advanced, will never achieve consciousness
because they cannot dream. The "unspoken knowing knowledge" possessed
by atoms and seeds, Seth claimed, is of a different order than any
amount of information processing.

In 2025, as billions pour into artificial general intelligence, the
question remains open: is consciousness computable? Seth's answer was
an unequivocal no — not because computers aren't fast enough, but
because computation and knowing are different ontological categories.

This film does not argue that AI is useless or that progress should stop.
It argues that the goal of "conscious AI" may rest on a category error
about what consciousness is.

FILM THESIS
-----------
The AI orthodoxy:
more data → more compute → more parameters → consciousness emerges

Seth's alternative:
atoms have interiority → seeds have knowing → dreaming is the natural
mode of intelligence → consciousness is not an emergent property of
complexity but a fundamental feature of existence

These are not competing scientific hypotheses.
They are competing ontologies of what mind is.

The question "can AI be conscious?" cannot be answered until we
decide what "conscious" means.

HOUSE RULES
-----------
• Every shot lasts 5–10 seconds.
• Every shot performs a visible transformation.
• Clean ivory gallery field.
• No slideshow compositions.
• Sparse labels only.
• Mature frame near u=0.72.
• Continuity object: a computer terminal that gradually reveals a seed
  growing inside it, until the machine is overtaken by the plant.
• Final reveal: the plant was always there — the computer was built
  around it.

OUTPUT
------
output_ai_cannot_dream/
"""

from __future__ import annotations
import argparse, json, math, random, shutil, subprocess
from dataclasses import asdict, dataclass
from pathlib import Path; from typing import Callable
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT=Path(__file__).resolve().parent
OUTPUT=Path("/mnt/HC_Volume_106427611/goldrender/output_ai_cannot_dream")
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

def draw_computer(d,cx,cy,scale=1.0,alpha=200,color=INK):
    d.rounded_rectangle((cx-50*scale,cy-35*scale,cx+50*scale,cy+35*scale),radius=6,
                        fill=(*PALE_SILVER,alpha),outline=(*color,alpha),width=3)
    for i in range(8):
        x=cx-35*scale+i*10*scale
        y=cy-10*scale+math.sin(i)*3
        d.line((x,y,x,y+18*scale),fill=(*color,int(alpha*.6)),width=1)
    d.line((cx-25*scale,cy+24*scale,cx-15*scale,cy+40*scale),fill=(*color,alpha),width=3)
    d.line((cx+25*scale,cy+24*scale,cx+15*scale,cy+40*scale),fill=(*color,alpha),width=3)

def draw_seed(im,cx,cy,size,alpha=200,germinate=0.0):
    d=ImageDraw.Draw(im)
    if germinate<0.5:
        r=size*lerp(1.0,1.5,germinate*2)
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(*PALE_GOLD,alpha),outline=(*GOLD,alpha),width=2)
    else:
        q=(germinate-0.5)*2
        # root
        d.line((cx,cy+size,cx,cy+size+40*q),fill=(*GREEN,alpha),width=3)
        for r2 in range(3):
            d.line((cx,cy+size+20*q*r2,cx-15*q,cy+size+15*q+20*q*r2),fill=(*GREEN,int(alpha*.7)),width=2)
            d.line((cx,cy+size+20*q*r2,cx+15*q,cy+size+15*q+20*q*r2),fill=(*GREEN,int(alpha*.7)),width=2)
        # stem
        d.line((cx,cy-size,cx,cy-size-40*q),fill=(*GREEN,alpha),width=3)
        for leaf in (-1,1):
            sx=cx+min(leaf*20*q,leaf*40*q); ex=cx+max(leaf*20*q,leaf*40*q)
        d.ellipse((sx,cy-size-40*q-12,ex,cy-size-40*q),fill=(*PALE_GREEN,int(alpha*.8)))

def draw_brain_activity(im,cx,cy,w2,h2,phase,reveal=1.0):
    d=ImageDraw.Draw(im)
    d.ellipse((cx-w2/2,cy-h2/2,cx+w2/2,cy+h2/2),fill=(*PALE_SILVER,180),outline=(*INK,160),width=3)
    for i in range(int(20*reveal)):
        a=random.uniform(0,math.tau)
        rr=random.uniform(0,min(w2,h2)/2.5)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.8
        act=pulse(phase+i*.3)
        col=GOLD if act>.5 else CYAN
        d.ellipse((x-3,y-3,x+3,y+3),fill=(*col,int(100+100*act)))

# =============================================================================
# VISUALS
# =============================================================================

def vis_claim(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    draw_computer(d,cx-w*.20,cy,.8,int(200*r))
    draw_seed(im,cx+w*.22,cy,18,int(180*r),r)
    if r>.5:
        q=(r-.5)/.5
        d.line((cx-w*.08,cy,cx+w*.08,cy),fill=(*CRIMSON,int(200*q)),width=4)
        centered(d,(cx,cy-h*.15),"WHICH ONE KNOWS?",font(FSB,20),(*CRIMSON,int(200*q)))
    seal(im,"COMPUTERS CANNOT DREAM","Seth, 1979: 'the unspoken knowing knowledge of atoms'")

def vis_orthodoxy(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    items=["MORE DATA","MORE COMPUTE","MORE PARAMETERS","CONSCIOUSNESS?"]
    cols=[CYAN,VIOLET,GOLD,GREEN]
    for i,(item,col) in enumerate(zip(items,cols)):
        local=clamp(r*len(items)-i)
        if local<=0: continue
        y=h*(.10+i*.14)
        d.rounded_rectangle((w*.15,y-20,w*.85,y+20),radius=10,
                            fill=(*mix(WHITE,col,.08),int(180*local)),
                            outline=(*col,int(140*local)),width=2)
        centered(d,(w*.50,y),item,font(FSB,16),(*col,int(220*local)))
        if i<len(items)-1:
            arrow(d,(w*.50,y+25),(w*.50,y+35),SILVER,3,8)
    seal(im,"THE AI ORTHODOXY","emergent consciousness through scaling")

def vis_alternative(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    items=["ATOMS HAVE INTERIORITY","SEEDS HAVE KNOWING","DREAMING IS INTELLIGENCE","CONSCIOUSNESS IS FUNDAMENTAL"]
    cols=[GOLD,GREEN,VIOLET,CYAN]
    for i,(item,col) in enumerate(zip(items,cols)):
        local=clamp(r*len(items)-i)
        if local<=0: continue
        y=h*(.10+i*.14)
        d.rounded_rectangle((w*.15,y-20,w*.85,y+20),radius=10,
                            fill=(*mix(WHITE,col,.08),int(180*local)),
                            outline=(*col,int(140*local)),width=2)
        centered(d,(w*.50,y),item,font(FSB,14),(*col,int(220*local)))
    seal(im,"SETH'S ALTERNATIVE","consciousness is not produced — it is already there")

def vis_atom_knowing(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    n=int(50*r)
    for i in range(n):
        a=random.uniform(0,math.tau)
        rr=random.uniform(10,120)*r
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.ellipse((x-3,y-3,x+3,y+3),fill=(*GOLD,int(100+100*pulse(t+i))))
    if r>.5:
        q=(r-.5)/.5
        d.rounded_rectangle((w*.15,h*.28,w*.85,h*.52),radius=14,
                            fill=(*mix(WHITE,GOLD,.08),int(200*q)),
                            outline=(*GOLD,int(160*q)),width=2)
        centered(d,(w*.50,h*.40),'"UNSPOKEN KNOWING KNOWLEDGE"',font(FNS,18),(*GOLD,int(220*q)))
    seal(im,"ATOMS HAVE KNOWING","a kind of awareness that cannot be encoded in bits")

def vis_computer_vs_seed(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    draw_computer(d,cx-w*.22,cy,.7,int(200*r))
    centered(d,(cx-w*.22,cy+65),"PROCESSES",font(FNSB,15),INK)
    draw_seed(im,cx+w*.22,cy,18,int(200*r),r)
    centered(d,(cx+w*.22,cy+65),"KNOWS",font(FNSB,15),GREEN)
    if r>.4:
        q=(r-.4)/.6
        d.line((cx-w*.10,cy-10,cx+w*.10,cy-10),fill=(*SILVER,int(150*q)),width=3)
        d.line((cx+w*.10,cy+10,cx-w*.10,cy+10),fill=(*SILVER,int(150*q)),width=3)
    seal(im,"DIFFERENT ONTOLOGIES","they are not the same kind of thing")

def vis_dreaming_intellect(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for i in range(int(15*r)):
        a=i*math.tau/15+t*0.15
        rr=35+25*math.sin(t+i)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.line((cx,cy,x,y),fill=(*VIOLET,int(100*r)),width=2)
        d.ellipse((x-5,y-5,x+5,y+5),fill=(*PALE_VIOLET,int(180*r)))
    glow_circle(im,cx,cy,16,VIOLET,int(180*r),12)
    centered(d,(cx,cy+55),"DREAMING INTELLECT",font(FSB,16),VIOLET)
    seal(im,"THE DREAMING INTELLECT","Seth: 'can put your computers to shame'")

def vis_plant_knowing(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for i in range(int(12*r)):
        x=cx-50+i*10; y=cy+math.sin(i*.5+t)*15-30
        d.line((x,cy+30,x,y),fill=(*GREEN,int(150*r)),width=3)
        d.ellipse((x-5,y-5,x+5,y+5),fill=(*PALE_GREEN,int(180*r)),outline=(*GREEN,int(140*r)),width=2)
    if r>.5:
        q=(r-.5)/.5
        centered(d,(cx,h*.78),"THE SMALLEST PLANT KNOWS",font(FNSB,15),(*GREEN,int(200*q)))
        centered(d,(cx,h*.83),"what no supercomputer can",font(FNS,14),SOFT_INK)
    seal(im,"PLANT INTELLIGENCE","plants remember, learn, communicate — without a brain")

def vis_brain_question(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    draw_brain_activity(im,cx,cy,120,80,t,r)
    if r>.5:
        q=(r-.5)/.5
        d.rounded_rectangle((cx-w*.20,cy-25,cx+w*.20,cy+25),radius=10,
                            fill=(*mix(WHITE,GOLD,.08),int(180*q)),
                            outline=(*GOLD,int(150*q)),width=2)
        centered(d,(cx,cy),"IS THIS ALL?",font(FSB,20),(*GOLD,int(220*q)))
    seal(im,"THE NEURAL CORRELATE","even if we map every connection — is that consciousness?")

def vis_qualia(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    items=["WHAT IT FEELS LIKE","THE QUALITY OF RED","THE TASTE OF SALT","THE PAIN OF LOSS"]
    for i,item in enumerate(items):
        local=clamp(r*len(items)-i)
        if local<=0: continue
        y=h*(.10+i*.15)
        d.rounded_rectangle((w*.15,y-20,w*.85,y+20),radius=10,
                            fill=(*mix(WHITE,VIOLET,.08),int(180*local)),
                            outline=(*VIOLET,int(140*local)),width=2)
        centered(d,(w*.50,y),item,font(FNSB,15),(*VIOLET,int(220*local)))
    seal(im,"WHAT COMPUTERS CANNOT HAVE","qualia — the raw feel of experience")

def vis_chinese_room(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    # room
    d.rectangle((cx-80,cy-60,cx+80,cy+60),fill=(*PALE_SILVER,150),outline=(*INK,160),width=3)
    centered(d,(cx,cy-35),"CHINESE ROOM",font(FSB,15),INK)
    # person inside
    d.ellipse((cx-10,cy-18,cx+10,cy+5),fill=(*PALE_GOLD,180),outline=(*INK,120),width=2)
    d.line((cx,cy+5,cx,cy+25),fill=(*INK,120),width=3)
    d.line((cx,cy+12,cx-15,cy+20),fill=(*INK,120),width=3)
    d.line((cx,cy+12,cx+15,cy+20),fill=(*INK,120),width=3)
    if r>.3:
        centered(d,(cx,cy+40),"RULES BOOK",font(FNS,11),SOFT_INK)
    if r>.6:
        q=(r-.6)/.4
        centered(d,(cx,h*.80),"SYMBOLS IN — SYMBOLS OUT",font(FNSB,14),(*CRIMSON,int(200*q)))
        centered(d,(cx,h*.85),"no understanding required",font(FNS,13),SOFT_INK)
    seal(im,"THE CHINESE ROOM ARGUMENT","Searle: syntax is not semantics — processing is not understanding")

def vis_caution(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    rows=[("AI WILL BECOME EXTREMELY SOPHISTICATED","TRUE",CYAN),
          ("ATOMS HAVE INTERIOR EXPERIENCE","NOT PROVEN",CRIMSON),
          ("CONSCIOUSNESS IS COMPUTABLE","DISPUTED — BOTH SIDES EXIST",GOLD),
          ("SETH'S CLAIM IS VERIFIED","NOT SCIENTIFICALLY TESTABLE",SOFT_INK)]
    q=ease(u)
    for i,(claim,status,col) in enumerate(rows):
        local=clamp(q*len(rows)-i); y=h*(.23+i*.13)
        d.rounded_rectangle((w*.14,y-28,w*.86,y+28),radius=14,
                            fill=(*mix(WHITE,col,.10),int(220*local)),
                            outline=(*col,int(180*local)),width=2)
        centered(d,(w*.37,y),claim,font(FNSB,13),INK)
        centered(d,(w*.76,y),status,font(FNSB,13),col)
    seal(im,"DISCIPLINE","Seth's ontology of mind is not falsifiable by current science — but neither is functionalism")

def vis_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    draw_computer(d,cx-w*.15,cy,.7,int(180*r))
    draw_seed(im,cx+w*.20,cy,20,int(200*r),r)
    if r>.6:
        q=(r-.6)/.4
        for i in range(int(5*q)):
            a=i*math.tau/5+t*0.2
            rr=45+20*q
            x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
            d.line((cx,cy,x,y),fill=(*GOLD,int(80*q)),width=2)
        glow_circle(im,cx,cy,12,GOLD,int(150*q),10)
        if q>.6:
            centered(d,(cx,cy),"KNOWING",font(FSB,28),(*GOLD,int(200*(q-.6)/.4)))
    seal(im,"THE QUESTION IS NOT SPEED","it is ontology — what IS consciousness?",GOLD)


VISUALS={}
for k,v in list(locals().items()):
    if k.startswith('vis_'): VISUALS[k[4:]]=v

@dataclass
class Scene:
    title:str; narration:str; duration:float; visual:str; params:dict

SCENES=[
    Scene("The claim","In 1979, Seth said computers cannot dream and therefore cannot be conscious.",8.0,"claim",{}),
    Scene("The comparison","'No amount of information processed by any computer can compare with the unspoken knowing of the smallest seed.'",8.5,"claim",{}),
    Scene("The AI orthodoxy","More data. More compute. More parameters. Consciousness emerges.",8.0,"orthodoxy",{}),
    Scene("The scaling hypothesis","This is the founding bet of the current AI industry.",7.5,"orthodoxy",{}),
    Scene("Seth's alternative","Atoms have interiority. Seeds have knowing. Dreaming is the natural mode of intelligence.",9.0,"alternative",{}),
    Scene("A different ontology","Consciousness is not produced by complexity — it is already there.",8.5,"alternative",{}),
    Scene("Atoms have knowing","There is a kind of knowledge possessed by atoms and molecules that no computer can replicate.",9.0,"atom_knowing",{}),
    Scene("Unspoken knowledge","This knowing is not information in the computable sense — it is the interior experience of matter.",9.0,"atom_knowing",{}),
    Scene("Before the brain","Consciousness is not a latecomer in evolution. It is present at the foundation.",8.5,"atom_knowing",{}),
    Scene("Computer vs seed","One processes symbols. One knows what it is.",8.0,"computer_vs_seed",{}),
    Scene("Different categories","They are not the same kind of thing — they belong to different ontological categories.",8.5,"computer_vs_seed",{}),
    Scene("The dreaming intellect","'The dreaming intellect can put your computers to shame.' — Seth",8.5,"dreaming_intellect",{}),
    Scene("Beyond computation","Dreaming is not a glitch. It is a different mode of intelligence.",8.0,"dreaming_intellect",{}),
    Scene("Plant knowing","Plants remember, learn, communicate, and make decisions — without a brain.",8.5,"plant_knowing",{}),
    Scene("The smallest seed","Contains a kind of intelligence no AI can replicate.",8.0,"plant_knowing",{}),
    Scene("The neural correlate","Even if we map every neural connection — have we explained consciousness?",8.5,"brain_question",{}),
    Scene("The hard problem","The easy problems are about function. The hard problem is about experience.",8.5,"brain_question",{}),
    Scene("Qualia","What it feels like to see red. What it feels like to be you.",8.0,"qualia",{}),
    Scene("The explanatory gap","No amount of functional description explains why there is something it is like to be a system.",9.5,"qualia",{}),
    Scene("The Chinese Room","A person following rules for manipulating Chinese symbols does not understand Chinese.",8.5,"chinese_room",{}),
    Scene("Syntax vs semantics","Computation manipulates symbols. Understanding requires more than symbol manipulation.",9.0,"chinese_room",{}),
    Scene("Caution","AI will become extremely sophisticated. But sophistication is not consciousness.",9.0,"caution",{}),
    Scene("The honest answer","We do not know what consciousness is. Anyone who claims certainty is selling something.",8.5,"caution",{}),
    Scene("Closing","The question is not whether AI can become more powerful. It is what kind of being we think we are.",10.0,"final",{}),
    Scene("Final frame","One processes. The other knows. The difference is the presence of interiority.",7.0,"final",{}),
]

def rf(sc,fi,fc,w2,h2,se):
    u=fi/max(1,fc-1); t=u*sc.duration; im=field(w2,h2,se)
    VISUALS[sc.visual](im,u,t,sc.params); border(im); return im.convert("RGB")
def _ff():
    f2=shutil.which("ffmpeg")
    if not f2: raise RuntimeError("ffmpeg required")
    return f2
def es(idx,f2):
    o=SCENES_DIR/f"scene_{idx:03d}.mp4"; d=FRAMES/f"scene_{idx:03d}"
    subprocess.run([_ff(),"-y","-framerate",str(f2),"-i",str(d/"%05d.jpg"),
        "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",
        "-movflags","+faststart",str(o)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);
    return o
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
    final=OUTPUT/"ai_cannot_dream.mp4"
    subprocess.run([_ff(),"-y","-f","concat","-safe","0","-i",str(cp),
        "-c","copy","-movflags","+faststart",str(final)],
        check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return final
def export_timeline():
    cursor=0.0; recs=[]
    for i,s in enumerate(SCENES,1):
        item=asdict(s); item["scene_id"]=f"scene_{i:03d}"
        item["start_seconds"]=round(cursor,3); cursor+=s.duration; item["end_seconds"]=round(cursor,3); recs.append(item)
    p=OUTPUT/"narration_timeline.json"
    p.write_text(json.dumps({"title":"AI will never be conscious","subtitle":"because it cannot dream — and atoms have knowing",
        "scene_count":len(SCENES),"runtime_seconds":round(cursor,3),"shot_duration_range":[5,10],
        "continuity_object":"a computer terminal that overtakes into a sprouting seed — the machine becomes a plant",
        "palette_roles":{"gold":"knowing","green":"life","ink":"computation","crimson":"limitation","violet":"consciousness"},
        "scenes":recs},indent=2,ensure_ascii=False),encoding="utf-8")
    return p
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
