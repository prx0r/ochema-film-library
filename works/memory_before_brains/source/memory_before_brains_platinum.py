#!/usr/bin/env python3
"""
MEMORY BEFORE BRAINS
A Michael Levin–themed Platinum-house procedural visual essay.

FILM THESIS
-----------
Memory begins wherever the past changes what a living system can do next.

Brains later specialize this ancient capacity into recollection, narrative,
and imagination. But cells and tissues already retain state through:

• persistent membrane-potential patterns;
• altered gap-junction connectivity;
• transcriptional and epigenetic state;
• biochemical feedback loops;
• structural hysteresis;
• regenerative target morphology;
• learned responses in non-neural systems.

The film distinguishes:
trace, persistence, recall, reconstruction, ownership, and conscious memory.

It does not claim that all biological memory is experienced like human memory.

VISUAL THESIS
-------------
One violet trace survives the disappearance of its cause.

stimulus → altered state → persistence → changed future response →
tissue-level memory → regenerative recall → cryptic anatomy → reset →
brains inheriting and extending the ancient loop.

HOUSE RULES
-----------
• Every scene lasts 5–10 seconds.
• Every scene performs before → operation → after.
• Clean ivory scientific/gallery field.
• No static slide layouts.
• Sparse labels only.
• Mature frame near u=0.72.
• Continuity object: a violet trace that becomes a gold act of recognition.

OUTPUT
------
output_memory_before_brains/
  frames/
  scenes/
  memory_before_brains.mp4
  narration_timeline.json
  contact_sheet.jpg
"""

from __future__ import annotations

import argparse, json, math, random, shutil, subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output_memory_before_brains"
FRAMES = OUTPUT / "frames"
SCENES_DIR = OUTPUT / "scenes"

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 10

IVORY=(249,247,241)
WHITE=(255,254,250)
INK=(29,33,39)
SOFT_INK=(86,91,98)
SILVER=(180,187,194)
PALE_SILVER=(226,229,232)
CYAN=(57,156,180)
PALE_CYAN=(196,227,233)
GOLD=(194,156,72)
PALE_GOLD=(236,219,175)
GREEN=(70,139,99)
PALE_GREEN=(198,225,208)
CRIMSON=(162,58,69)
PALE_CRIMSON=(231,198,202)
VIOLET=(109,83,153)
PALE_VIOLET=(220,211,237)

FONT_SERIF="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIF_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def clamp(x,lo=0.0,hi=1.0): return max(lo,min(hi,x))
def lerp(a,b,t): return a+(b-a)*clamp(t)
def mix(a,b,t): return tuple(int(lerp(x,y,t)) for x,y in zip(a,b))
def smoothstep(a,b,x):
    if a==b: return 1.0 if x>=b else 0.0
    q=clamp((x-a)/(b-a)); return q*q*(3-2*q)
def ease(t):
    t=clamp(t); return .5-.5*math.cos(math.pi*t)
def pulse(t,speed=1.0,phase=0.0):
    return .5+.5*math.sin(math.tau*(speed*t+phase))

def font(path,size):
    for c in (path,FONT_SERIF,FONT_SANS):
        try: return ImageFont.truetype(c,size)
        except OSError: pass
    return ImageFont.load_default()

def layer(size): return Image.new("RGBA",size,(0,0,0,0))

def field(w,h,seed):
    rng=np.random.default_rng(seed)
    arr=np.empty((h,w,3),dtype=np.float32); arr[:]=IVORY
    arr+=rng.normal(0,.9,(h,w,1))
    yy,xx=np.mgrid[0:h,0:w]
    halo=np.exp(-(((xx-w*.5)/(w*.37))**2+((yy-h*.40)/(h*.31))**2)*2.0)
    arr[...,1]+=halo*3.4; arr[...,2]+=halo*5.0
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8),"RGB").convert("RGBA")

def centered(d,xy,text,fnt,fill=INK):
    d.text(xy,text,font=fnt,fill=fill,anchor="mm")

def seal(im,title,subtitle="",color=INK):
    w,h=im.size; d=ImageDraw.Draw(im)
    centered(d,(w/2,h*.875),title,font(FONT_SERIF_BOLD,max(22,int(h*.04))),color)
    if subtitle:
        centered(d,(w/2,h*.923),subtitle,font(FONT_SANS,max(13,int(h*.019))),SOFT_INK)

def border(im):
    w,h=im.size; d=ImageDraw.Draw(im)
    d.rounded_rectangle((26,26,w-26,h-26),radius=18,outline=(*INK,45),width=2)

def glow_circle(im,x,y,r,color,alpha=170,blur=14):
    gl=layer(im.size); gd=ImageDraw.Draw(gl)
    gd.ellipse((x-r,y-r,x+r,y+r),fill=(*color,alpha))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).ellipse(
        (x-r*.34,y-r*.34,x+r*.34,y+r*.34),
        fill=(*mix(color,WHITE,.35),min(255,alpha+50))
    )
    im.alpha_composite(fg)

def glow_line(im,pts,color,width=4,alpha=210,blur=11):
    if len(pts)<2: return
    gl=layer(im.size); gd=ImageDraw.Draw(gl)
    gd.line(pts,fill=(*color,alpha),width=width*3,joint="curve")
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).line(
        pts,fill=(*mix(color,WHITE,.08),min(255,alpha+25)),
        width=width,joint="curve"
    )
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

def arrow(d,a,b,color=INK,width=3,head=10):
    d.line((*a,*b),fill=color,width=width)
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for s in (-1,1):
        p=(b[0]-math.cos(ang+s*.52)*head,b[1]-math.sin(ang+s*.52)*head)
        d.line((*b,*p),fill=color,width=width)

def draw_cell(d,cx,cy,r,color=CYAN,alpha=200):
    d.ellipse((cx-r,cy-r,cx+r,cy+r),
              fill=(*mix(WHITE,color,.12),alpha//2),
              outline=(*color,alpha),width=3)

def tissue_grid(w,h,cols=11,rows=5,seed=0):
    rng=random.Random(seed)
    pts=[]
    for j in range(rows):
        for i in range(cols):
            x=w*.14+i*w*.72/(cols-1)+rng.uniform(-7,7)
            y=h*.22+j*h*.38/(rows-1)+rng.uniform(-6,6)
            pts.append((x,y))
    return pts

def voltage_wave(cx,cy,length,amp,t,phase=0,samples=170):
    pts=[]
    for i in range(samples):
        q=i/(samples-1)
        x=cx-length/2+q*length
        y=cy+math.sin(q*math.tau*4+t*.65+phase)*amp*math.sin(math.pi*q)**.6
        pts.append((x,y))
    return pts

def planarian_poly(cx,cy,length,width):
    top=[]; bottom=[]
    for i in range(100):
        q=i/99
        x=cx-length/2+q*length
        env=math.sin(math.pi*q)**.58
        ww=width*(.2+.8*env)
        top.append((x,cy-ww/2))
        bottom.append((x,cy+ww/2))
    return top+list(reversed(bottom))

def draw_planarian(d,cx,cy,length,width,heads=1,color=CYAN,alpha=220):
    poly=planarian_poly(cx,cy,length,width)
    d.polygon(poly,fill=(*mix(WHITE,color,.18),alpha),outline=(*color,alpha),width=3)
    positions=[cx-length/2+width*.16]
    if heads==2: positions.append(cx+length/2-width*.16)
    for hx in positions:
        direction=-1 if hx<cx else 1
        ex=hx+direction*width*.02
        for oy in (-width*.10,width*.10):
            d.ellipse((ex-4,cy+oy-4,ex+4,cy+oy+4),fill=(*INK,alpha))

def vis_trace(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.40); right=(w*.72,h*.40); q=ease(u)
    glow_circle(im,*left,20,GOLD,180,12)
    path=[left,(w*.50,h*.24),right]
    glow_line(im,partial(path,q),VIOLET,5,200,13)
    if q>.55:
        glow_circle(im,*right,15,VIOLET,180,11)
    seal(im,"THE CAUSE DISAPPEARS · THE DIFFERENCE REMAINS",
         "memory begins as persistence")

def vis_state_switch(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left,right=w*.12,w*.88; base=h*.64; q=ease(u)
    pts=[]
    for i in range(260):
        xq=i/259
        y=base-95*math.exp(-((xq-.28)/.11)**2)-105*math.exp(-((xq-.74)/.10)**2)
        pts.append((lerp(left,right,xq),y))
    d.line(pts,fill=(*INK,190),width=4)
    xq=lerp(.28,.74,q); idx=int(xq*259); x,y=pts[idx]
    glow_circle(im,x,y-14,15,VIOLET,180,10)
    centered(d,(w*.28,h*.70),"STATE A",font(FONT_SANS_BOLD,14),CYAN)
    centered(d,(w*.74,h*.70),"STATE B",font(FONT_SANS_BOLD,14),VIOLET)
    seal(im,"A SYSTEM CAN REMEMBER BY STAYING IN AN ALTERNATIVE STATE",
         "the stimulus is gone; the attractor remains")

def vis_tissue_memory(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    pts=tissue_grid(w,h,12,5,11); q=ease(u)
    for i,(x,y) in enumerate(pts):
        band=(i%12)/11
        col=mix(CYAN,VIOLET,q*(.25+.75*band))
        draw_cell(d,x,y,9,col,175)
    if q>.4:
        glow_line(im,voltage_wave(w*.50,h*.41,w*.68,h*.045,t,1.2),
                  VIOLET,5,195,13)
    seal(im,"TISSUE MEMORY CAN BE DISTRIBUTED",
         "no single cell needs to store the whole pattern")

def vis_hysteresis(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    up=[]; down=[]
    for i in range(180):
        x=w*.14+i*w*.72/179
        xx=i/179
        up.append((x,h*.58-120/(1+math.exp(-18*(xx-.58)))))
        down.append((x,h*.58-120/(1+math.exp(-18*(xx-.38)))))
    d.line(up,fill=(*CYAN,180),width=4)
    d.line(down,fill=(*VIOLET,180),width=4)
    idx=int(q*179)
    glow_circle(im,*up[idx],12,GOLD,170,9)
    centered(d,(w*.50,h*.18),"HYSTERESIS",font(FONT_SERIF_BOLD,27),VIOLET)
    seal(im,"THE PATH INTO A STATE CHANGES THE PATH OUT",
         "history becomes part of present dynamics")

def vis_changed_response(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.26,h*.40); center=(w*.50,h*.40); right=(w*.74,h*.40)
    q=ease(u)
    glow_circle(im,*left,14,GOLD,160,10)
    glow_circle(im,*center,14,VIOLET,170,10)
    glow_circle(im,*right,14,GREEN,170,10)
    glow_line(im,partial([left,center,right],q),VIOLET,5,195,12)
    centered(d,(left[0],h*.67),"STIMULUS",font(FONT_SANS_BOLD,14),GOLD)
    centered(d,(center[0],h*.67),"PERSISTENT STATE",font(FONT_SANS_BOLD,14),VIOLET)
    centered(d,(right[0],h*.67),"ALTERED RESPONSE",font(FONT_SANS_BOLD,14),GREEN)
    seal(im,"THE TEST OF MEMORY IS A CHANGED FUTURE",
         "what happened before modifies what becomes possible next")

def vis_regenerative_recall(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    if q<.35:
        draw_planarian(d,cx,cy,w*.58,h*.15,1,CYAN,220)
        d.line((cx,cy-h*.11,cx,cy+h*.11),fill=(*CRIMSON,220),width=5)
    else:
        draw_planarian(d,cx,cy,lerp(w*.18,w*.58,q),lerp(h*.08,h*.15,q),
                       1,GREEN,int(220*q))
    if q>.45:
        glow_line(im,voltage_wave(cx,cy,w*.50,h*.04,t),VIOLET,5,185,12)
    seal(im,"REGENERATION IS A FORM OF RECALL",
         "injury asks the tissue to reconstruct a prior whole")

def vis_cryptic_future(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    draw_planarian(d,cx,cy,w*.60,h*.15,1,CYAN,220)
    if q>.35:
        ghost=layer(im.size); gd=ImageDraw.Draw(ghost)
        draw_planarian(gd,cx,cy,w*.60,h*.16,2,VIOLET,int(120*q))
        im.alpha_composite(ghost)
    glow_line(im,voltage_wave(cx,cy,w*.50,h*.055,t,1.1),VIOLET,5,int(60+140*q),13)
    seal(im,"A NORMAL BODY CAN HIDE A DIFFERENT REGENERATIVE MEMORY",
         "the future becomes visible only when the tissue is asked to rebuild")

def vis_second_cut(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; cut=smoothstep(.08,.28,u); grow=smoothstep(.30,.96,u)
    if grow<.55:
        draw_planarian(d,cx,cy,w*.60,h*.15,1,CYAN,int(220*(1-grow*.5)))
        d.line((cx,cy-h*.11,cx,cy+h*.11),fill=(*CRIMSON,int(220*cut)),width=5)
    if grow>.18:
        draw_planarian(d,cx,cy,lerp(w*.16,w*.58,grow),lerp(h*.08,h*.16,grow),
                       2,VIOLET,int(220*grow))
    seal(im,"THE SECOND WOUND REVEALS THE FIRST EDIT",
         "hidden physiological memory becomes visible anatomy")

def vis_reset(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    draw_planarian(d,cx,cy,w*.60,h*.15,1,CYAN,220)
    glow_line(im,voltage_wave(cx,cy,w*.50,h*.055,t,1.1),
              VIOLET,5,int(200*(1-q)),13)
    glow_line(im,partial(voltage_wave(cx,cy,w*.50,h*.03,t),q),
              CYAN,5,int(110+100*q),12)
    if q>.7:
        centered(d,(cx,h*.69),"TARGET RESET",font(FONT_SERIF_BOLD,26),GREEN)
    seal(im,"BIOLOGICAL MEMORY CAN BE EDITED",
         "persistence is not destiny")

def vis_epigenetic(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    for i in range(100):
        y=lerp(h*.22,h*.60,i/99)
        x1=cx+math.sin(i*.30+t)*38
        x2=cx-math.sin(i*.30+t)*38
        d.ellipse((x1-3,y-3,x1+3,y+3),fill=(*CYAN,150))
        d.ellipse((x2-3,y-3,x2+3,y+3),fill=(*GOLD,150))
        if i%8==0:
            alpha=int(200*q)
            d.ellipse((x1-8,y-8,x1+8,y+8),outline=(*VIOLET,alpha),width=3)
    seal(im,"GENES CAN REMEMBER HOW THEY WERE USED",
         "regulatory marks alter which programs remain accessible")

def vis_structural_memory(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    nodes=tissue_grid(w,h,9,5,18)
    for i,(x,y) in enumerate(nodes):
        xx=lerp(x,w*.50+(x-w*.50)*.82,q)
        yy=lerp(y,h*.40+(y-h*.40)*.62,q)
        draw_cell(d,xx,yy,10,mix(CYAN,GREEN,q),170)
    if q>.5:
        d.ellipse((w*.28,h*.27,w*.72,h*.55),outline=(*GOLD,int(190*q)),width=5)
    seal(im,"STRUCTURE ITSELF CAN STORE HISTORY",
         "geometry constrains which future changes are easy")

def vis_immune_memory(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    invader=(w*.72,h*.40)
    glow_circle(im,*invader,20,CRIMSON,180,12)
    defenders=[(w*.25,h*.28),(w*.32,h*.48),(w*.42,h*.35),(w*.30,h*.60)]
    for i,(x,y) in enumerate(defenders):
        glow_circle(im,x,y,12,CYAN,150,9)
        path=[(x,y),(w*.52,h*.30+i*18),invader]
        glow_line(im,partial(path,q),GREEN,3,160,9)
    if q>.68:
        centered(d,(w*.50,h*.68),"FASTER SECOND RESPONSE",
                 font(FONT_SERIF_BOLD,24),GREEN)
    seal(im,"IMMUNITY REMEMBERS WITHOUT RECOLLECTING",
         "prior encounter changes the speed and shape of defense")

def vis_habituation(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    for i in range(9):
        x=w*.16+i*w*.68/8
        amp=55*(1-i/9*q)
        d.line((x,cy-amp,x,cy+amp),fill=(*CYAN,int(180-10*i)),width=4)
    centered(d,(cx,h*.68),"REPEATED SIGNAL · DIMINISHING RESPONSE",
             font(FONT_SERIF_BOLD,22),VIOLET)
    seal(im,"HABITUATION IS MEMORY AS REDUCED SURPRISE",
         "the organism learns that a repeated event can be ignored")

def vis_brain_inherits(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    stages=[("CELL",w*.18,CYAN),("TISSUE",w*.38,GREEN),
            ("NERVE NET",w*.60,VIOLET),("BRAIN",w*.82,GOLD)]
    q=ease(u)
    for i,(lab,x,col) in enumerate(stages):
        r=18+i*13; local=clamp(q*len(stages)-i)
        glow_circle(im,x,h*.40,r,col,int(120+90*local),11)
        centered(d,(x,h*.68),lab,font(FONT_SANS_BOLD,14),col)
        if i<len(stages)-1:
            arrow(d,(x+r+7,h*.40),
                  (stages[i+1][1]-(31+(i+1)*13),h*.40),
                  (*SILVER,int(145*local)),2,7)
    seal(im,"BRAINS SPECIALIZED AN ANCIENT CAPACITY",
         "they did not invent persistence, learning, or state-dependent response")

def vis_reconstruction(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    rng=random.Random(71); q=ease(u)
    nodes=[(rng.uniform(w*.18,w*.82),rng.uniform(h*.20,h*.62)) for _ in range(44)]
    for i,(x,y) in enumerate(nodes):
        d.ellipse((x-5,y-5,x+5,y+5),fill=(*PALE_CYAN,200),outline=(*CYAN,130))
        if i and i%2:
            d.line((*nodes[i-1],x,y),fill=(*SILVER,70),width=2)
    for i,(x,y) in enumerate(nodes):
        local=clamp(q*8-(i%8))
        if local>0: glow_circle(im,x,y,7,VIOLET,int(100+80*local),7)
    seal(im,"HUMAN MEMORY IS RECONSTRUCTION, NOT PLAYBACK",
         "the present assembles a usable past")

def vis_ownership(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.40); right=(w*.72,h*.40); q=ease(u)
    glow_circle(im,*left,16,VIOLET,180,11)
    glow_circle(im,*right,16,GOLD,180,11)
    glow_line(im,partial([left,(w*.50,h*.24),right],q),GOLD,5,200,13)
    centered(d,(left[0],h*.68),"TRACE",font(FONT_SERIF_BOLD,26),VIOLET)
    centered(d,(right[0],h*.68),"I REMEMBER",font(FONT_SERIF_BOLD,26),GOLD)
    seal(im,"TRACE AND FIRST-PERSON MEMORY ARE NOT THE SAME",
         "biology explains persistence; phenomenology asks what makes it mine")

def vis_caution(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    rows=[
        ("TISSUES RETAIN FUNCTIONAL STATE","SUPPORTED",GREEN),
        ("ALL MEMORY IS CONSCIOUS RECOLLECTION","FALSE",CRIMSON),
        ("TARGET MORPHOLOGY CAN PERSIST","SUPPORTED",CYAN),
        ("BIOLOGICAL MEMORY PROVES A SOUL","NOT ESTABLISHED",CRIMSON),
    ]
    q=ease(u)
    for i,(claim,status,col) in enumerate(rows):
        local=clamp(q*len(rows)-i); y=h*(.23+i*.13)
        d.rounded_rectangle((w*.14,y-28,w*.86,y+28),radius=14,
                            fill=(*mix(WHITE,col,.10),int(220*local)),
                            outline=(*col,int(180*local)),width=2)
        centered(d,(w*.39,y),claim,font(FONT_SANS_BOLD,14),INK)
        centered(d,(w*.74,y),status,font(FONT_SANS_BOLD,14),col)
    seal(im,"DO NOT COLLAPSE ALL MEMORY INTO ONE THING",
         "persistence, learning, recollection, and ownership are distinct")

def vis_tantric_bridge(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.30,h*.40); right=(w*.70,h*.40); q=ease(u)
    pts=tissue_grid(w,h,5,4,25)
    for x,y in pts:
        xx=left[0]+(x-w*.50)*.50; yy=left[1]+(y-h*.40)*.72
        draw_cell(d,xx,yy,8,VIOLET,150)
    glow_line(im,voltage_wave(left[0],left[1],w*.22,h*.03,t),
              VIOLET,4,180,11)
    for rr in range(35,155,28):
        d.ellipse((right[0]-rr,right[1]-rr*.60,right[0]+rr,right[1]+rr*.60),
                  outline=(*GOLD,int(85*q*(1-rr/180))),width=3)
    centered(d,(left[0],h*.67),"PERSISTENT BIOLOGICAL STATE",
             font(FONT_SANS_BOLD,14),VIOLET)
    centered(d,(right[0],h*.67),"CONTINUITY OF AWARENESS",
             font(FONT_SANS_BOLD,14),GOLD)
    glow_line(im,partial([left,(w*.50,h*.20),right],q),CYAN,4,180,11)
    seal(im,"LEVIN AND PRATYABHIJÑĀ MEET AT CONTINUITY",
         "one studies state across change; the other studies recognition across experience")

def vis_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    stages=[
        (w*.18,CYAN,"CELL"),
        (w*.36,VIOLET,"TISSUE"),
        (w*.55,GREEN,"BODY"),
        (w*.74,GOLD,"MIND"),
    ]
    for i,(x,col,lab) in enumerate(stages):
        glow_circle(im,x,cy,12+i*7,col,160,10)
        centered(d,(x,h*.68),lab,font(FONT_SANS_BOLD,14),col)
        if i<len(stages)-1:
            glow_line(im,partial([(x,cy),(stages[i+1][0],cy)],q),col,4,160,10)
    if q>.72:
        centered(d,(cx,h*.18),"THE PAST CHANGES THE NEXT POSSIBILITY",
                 font(FONT_SERIF_BOLD,24),GOLD)
    seal(im,"MEMORY BEFORE BRAINS",
         "life remembered long before anything could tell a story about the past",GOLD)


VISUALS: dict[str,Callable] = {
    "trace":vis_trace,
    "switch":vis_state_switch,
    "tissue":vis_tissue_memory,
    "hysteresis":vis_hysteresis,
    "response":vis_changed_response,
    "regenerate":vis_regenerative_recall,
    "cryptic":vis_cryptic_future,
    "secondcut":vis_second_cut,
    "reset":vis_reset,
    "epigenetic":vis_epigenetic,
    "structure":vis_structural_memory,
    "immune":vis_immune_memory,
    "habituation":vis_habituation,
    "brain":vis_brain_inherits,
    "reconstruct":vis_reconstruction,
    "ownership":vis_ownership,
    "caution":vis_caution,
    "bridge":vis_tantric_bridge,
    "final":vis_final,
}


@dataclass
class Scene:
    title:str
    narration:str
    duration:float
    visual:str
    params:dict


SCENES = [
    Scene("Before recollection",
          "Memory existed before anything could remember a childhood.",
          8.0,"trace",{}),
    Scene("Minimal definition",
          "At its most minimal, memory means that the past changes what a living system can do next.",
          10.0,"trace",{}),
    Scene("Difference remains",
          "The cause disappears. A difference remains.",
          7.0,"trace",{}),

    Scene("State memory",
          "One way to remember is to stay in a changed state.",
          8.0,"switch",{}),
    Scene("Attractor",
          "A brief signal pushes the system across a threshold into another attractor.",
          9.0,"switch",{}),
    Scene("Persistence",
          "The signal ends. The state persists.",
          7.0,"switch",{}),

    Scene("Distributed memory",
          "In tissues, memory can be distributed across many cells.",
          8.0,"tissue",{}),
    Scene("No memory cell",
          "No single cell needs to contain the entire pattern.",
          7.5,"tissue",{}),
    Scene("Network state",
          "The memory lives in the relationships among voltages, channels, and coupling.",
          9.5,"tissue",{}),

    Scene("Hysteresis",
          "Biological systems often show hysteresis.",
          7.0,"hysteresis",{}),
    Scene("History matters",
          "The state reached now depends on the path taken to reach it.",
          8.5,"hysteresis",{}),
    Scene("Past in dynamics",
          "History has become part of present dynamics.",
          7.5,"hysteresis",{}),

    Scene("Functional test",
          "The real test of memory is not whether a system stores a picture.",
          8.0,"response",{}),
    Scene("Changed future",
          "It is whether prior events change future response.",
          8.0,"response",{}),
    Scene("Past becomes policy",
          "The past becomes a policy for what happens next.",
          7.5,"response",{}),

    Scene("Regenerative memory",
          "Regeneration makes this visible at the scale of anatomy.",
          8.0,"regenerate",{}),
    Scene("Prior whole",
          "A fragment reconstructs structures that are no longer present.",
          8.5,"regenerate",{}),
    Scene("Recall of form",
          "The tissue behaves as though injury has asked it to recall a prior whole.",
          9.5,"regenerate",{}),

    Scene("Cryptic future",
          "Sometimes the remembered target is not visible in the current body.",
          8.0,"cryptic",{}),
    Scene("Normal appearance",
          "A planarian may look anatomically normal.",
          7.0,"cryptic",{}),
    Scene("Hidden target",
          "Yet its physiological state can encode an alternative regenerative future.",
          9.0,"cryptic",{}),

    Scene("Second cut",
          "Cut the animal again.",
          5.5,"secondcut",{}),
    Scene("Old edit returns",
          "The hidden target reappears as a two-headed anatomy.",
          8.0,"secondcut",{}),
    Scene("Memory revealed",
          "The second wound reveals the memory of the first intervention.",
          8.5,"secondcut",{}),

    Scene("Reset",
          "But biological memory is not always permanent.",
          7.5,"reset",{}),
    Scene("Rewrite state",
          "Change the network state again, and the ordinary target can return.",
          8.5,"reset",{}),
    Scene("Persistence not destiny",
          "Persistence is not destiny. Memory can be edited.",
          8.0,"reset",{}),

    Scene("Epigenetic memory",
          "Cells also remember through gene regulation.",
          7.5,"epigenetic",{}),
    Scene("Accessible programs",
          "Chemical marks and regulatory loops change which programs remain accessible.",
          9.0,"epigenetic",{}),
    Scene("Identity",
          "A liver cell remains a liver cell partly because its past constrains its future.",
          8.5,"epigenetic",{}),

    Scene("Structural memory",
          "Structure itself can remember.",
          6.5,"structure",{}),
    Scene("Geometry",
          "The geometry of a tissue changes which stresses, signals, and movements are possible.",
          9.0,"structure",{}),
    Scene("Built history",
          "Past construction becomes a constraint on future construction.",
          8.0,"structure",{}),

    Scene("Immune memory",
          "The immune system remembers without recollecting.",
          8.0,"immune",{}),
    Scene("Second encounter",
          "A later encounter recruits a faster and more specific response.",
          8.0,"immune",{}),
    Scene("History as readiness",
          "The past survives as readiness.",
          7.0,"immune",{}),

    Scene("Habituation",
          "Even simple organisms can reduce response to repeated harmless stimulation.",
          9.0,"habituation",{}),
    Scene("Reduced surprise",
          "The event is no longer treated as equally surprising.",
          8.0,"habituation",{}),
    Scene("Learned irrelevance",
          "Memory can be the learned decision not to react.",
          8.0,"habituation",{}),

    Scene("Brains arrive",
          "Brains arrived late in this story.",
          7.0,"brain",{}),
    Scene("Ancient inheritance",
          "They inherited persistence, state dependence, prediction, habituation, and plasticity from older living systems.",
          10.0,"brain",{}),
    Scene("Specialization",
          "Neural memory specialized and expanded an ancient biological capacity.",
          8.5,"brain",{}),

    Scene("Human reconstruction",
          "Human memory is not a recording played back from storage.",
          8.5,"reconstruct",{}),
    Scene("Present assembly",
          "The present brain reconstructs a usable past from traces, context, emotion, and expectation.",
          10.0,"reconstruct",{}),
    Scene("Past remade",
          "Every act of remembering partly remakes what is remembered.",
          8.0,"reconstruct",{}),

    Scene("Ownership",
          "But persistence and first-person memory are not identical.",
          8.0,"ownership",{}),
    Scene("Trace versus mine",
          "A tissue can carry a trace. A person says: I remember.",
          8.0,"ownership",{}),
    Scene("Open question",
          "How biological persistence becomes the felt ownership of a past remains a deeper question.",
          9.5,"ownership",{}),

    Scene("Discipline",
          "The word memory therefore covers several different things.",
          8.0,"caution",{}),
    Scene("Different forms",
          "Persistence, hysteresis, learning, immune priming, recollection, and autobiographical ownership are not interchangeable.",
          10.0,"caution",{}),
    Scene("Keep distinctions",
          "The continuity is real, but the differences matter.",
          8.0,"caution",{}),

    Scene("Bridge",
          "This is where Levin's biology can meet Pratyabhijñā without collapsing into it.",
          9.0,"bridge",{}),
    Scene("Levin continuity",
          "Levin studies how living systems preserve state across change.",
          8.0,"bridge",{}),
    Scene("Recognition continuity",
          "Pratyabhijñā asks how different experiences can be recognized as belonging to one life.",
          9.0,"bridge",{}),
    Scene("Two levels",
          "One concerns functional continuity. The other concerns luminous ownership and recognition.",
          9.0,"bridge",{}),

    Scene("Return",
          "Memory existed before brains.",
          7.0,"final",{}),
    Scene("Past changes future",
          "Cells, tissues, immune systems, and regenerating bodies all let the past alter the next possibility.",
          10.0,"final",{}),
    Scene("Brains tell stories",
          "Brains later turned this ancient capacity into recollection, imagination, and story.",
          9.0,"final",{}),
    Scene("Closing",
          "Life remembered long before anything could say what happened—and every human memory still rests upon that older power: the past surviving as a difference in what can happen next.",
          10.0,"final",{}),
]


def render_frame(scene,frame_index,frame_count,width,height,seed):
    u=frame_index/max(1,frame_count-1)
    t=u*scene.duration
    im=field(width,height,seed)
    VISUALS[scene.visual](im,u,t,scene.params)
    border(im)
    return im.convert("RGB")

def ffmpeg_path():
    exe=shutil.which("ffmpeg")
    if not exe: raise RuntimeError("ffmpeg is required but was not found on PATH")
    return exe

def encode_scene(index,fps):
    frame_dir=FRAMES/f"scene_{index:03d}"
    output=SCENES_DIR/f"scene_{index:03d}.mp4"
    subprocess.run([
        ffmpeg_path(),"-y",
        "-framerate",str(fps),
        "-i",str(frame_dir/"%05d.jpg"),
        "-c:v","libx264",
        "-preset","medium",
        "-crf","18",
        "-pix_fmt","yuv420p",
        "-movflags","+faststart",
        str(output),
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return output

def render_scene(index,scene,fps,width,height,preview):
    frame_dir=FRAMES/f"scene_{index:03d}"
    frame_dir.mkdir(parents=True,exist_ok=True)
    SCENES_DIR.mkdir(parents=True,exist_ok=True)
    count=max(2,round(scene.duration*fps))

    if preview:
        for oi,fi in enumerate([0,int(count*.33),int(count*.72),count-1]):
            render_frame(scene,fi,count,width,height,index*10000+fi).save(
                frame_dir/f"preview_{oi:02d}.jpg",quality=95
            )
        return frame_dir

    for fi in range(count):
        p=frame_dir/f"{fi:05d}.jpg"
        if not p.exists():
            render_frame(scene,fi,count,width,height,index*10000+fi).save(
                p,quality=95,subsampling=0
            )
    return encode_scene(index,fps)

def concatenate(paths):
    txt=OUTPUT/"concat.txt"
    txt.write_text("\n".join(f"file '{p.resolve()}'" for p in paths),encoding="utf-8")
    output=OUTPUT/"memory_before_brains.mp4"
    subprocess.run([
        ffmpeg_path(),"-y",
        "-f","concat","-safe","0",
        "-i",str(txt),
        "-c","copy",
        "-movflags","+faststart",
        str(output),
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return output

def export_timeline():
    cursor=0.0
    records=[]
    for index,scene in enumerate(SCENES,1):
        rec=asdict(scene)
        rec["scene_id"]=f"scene_{index:03d}"
        rec["start_seconds"]=round(cursor,3)
        cursor+=scene.duration
        rec["end_seconds"]=round(cursor,3)
        records.append(rec)
    path=OUTPUT/"narration_timeline.json"
    path.write_text(json.dumps({
        "title":"memory before brains",
        "scene_count":len(SCENES),
        "runtime_seconds":round(cursor,3),
        "shot_duration_range":[5,10],
        "continuity_object":"violet trace becoming gold recognition",
        "scenes":records,
    },indent=2,ensure_ascii=False),encoding="utf-8")
    return path

def make_contact_sheet(width,height):
    tw=320; th=int(tw*height/width); cols=4
    rows=math.ceil(len(SCENES)/cols); cell_h=th+48
    sheet=Image.new("RGB",(cols*tw,rows*cell_h),IVORY)
    d=ImageDraw.Draw(sheet); lf=font(FONT_SANS_BOLD,14)

    for index,scene in enumerate(SCENES,1):
        count=max(2,round(scene.duration*DEFAULT_FPS))
        image=render_frame(scene,int(count*.72),count,width,height,index*10000+72)
        image.thumbnail((tw,th))
        slot=index-1; x=(slot%cols)*tw; y=(slot//cols)*cell_h
        sheet.paste(image,(x,y))
        d.text((x+8,y+th+7),f"{index:02d}  {scene.title}",font=lf,fill=INK)

    path=OUTPUT/"contact_sheet.jpg"
    sheet.save(path,quality=94)
    return path

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--fps",type=int,default=DEFAULT_FPS)
    p.add_argument("--width",type=int,default=DEFAULT_WIDTH)
    p.add_argument("--height",type=int,default=DEFAULT_HEIGHT)
    p.add_argument("--scene",type=int)
    p.add_argument("--preview",action="store_true")
    p.add_argument("--no-contact-sheet",action="store_true")
    return p.parse_args()

def main():
    args=parse_args()
    OUTPUT.mkdir(parents=True,exist_ok=True)
    FRAMES.mkdir(parents=True,exist_ok=True)
    SCENES_DIR.mkdir(parents=True,exist_ok=True)

    print(f"Timeline: {export_timeline()}")
    print(f"Scenes: {len(SCENES)}")
    print(f"Runtime: {sum(s.duration for s in SCENES)/60:.2f} minutes")

    if args.scene:
        if not 1<=args.scene<=len(SCENES):
            raise ValueError("scene out of range")
        print(render_scene(
            args.scene,SCENES[args.scene-1],args.fps,args.width,args.height,args.preview
        ))
        return

    rendered=[]
    for index,scene in enumerate(SCENES,1):
        print(f"[{index:02d}/{len(SCENES):02d}] {scene.title} ({scene.duration:.1f}s)")
        result=render_scene(index,scene,args.fps,args.width,args.height,args.preview)
        if not args.preview:
            rendered.append(result)

    if not args.no_contact_sheet:
        print(f"Contact sheet: {make_contact_sheet(args.width,args.height)}")

    if not args.preview:
        print(f"Final video: {concatenate(rendered)}")

if __name__=="__main__":
    main()
