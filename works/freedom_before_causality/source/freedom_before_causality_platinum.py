#!/usr/bin/env python3
"""
FREEDOM COMES BEFORE CAUSALITY
Abhinavagupta on Svātantrya, Spanda, and the Birth of Law

An original dark-spectrum Platinum-house procedural visual essay.

CENTRAL CLAIM
-------------
Modern thought usually begins with law:

    laws
      ↓
    events
      ↓
    organisms
      ↓
    apparent choice

Abhinavagupta reverses the order:

    svātantrya — absolute freedom
      ↓
    self-limitation
      ↓
    stable regularities
      ↓
    causality
      ↓
    worlds, bodies, and finite agents

Freedom is not an exception that occasionally interrupts causality.
It is the power by which any ordered field can appear at all.

This does NOT mean random miracles, personal omnipotence, or a denial of physics.
It means that causality is a mode of manifestation inside consciousness,
not the final explanation of consciousness.

FILM THESIS
-----------
A law-bound universe can describe how one state follows another.
It cannot, by itself, explain why there is an appearing field,
why regularity is intelligible, or why any system can initiate a new pattern.

Abhinavagupta names the deeper power svātantrya:
the capacity of consciousness to manifest, differentiate, conceal, reveal,
stabilize, and transform itself.

The film follows:

undetermined luminosity
→ pulse
→ choice of pattern
→ repetition
→ law
→ causal chain
→ finite agency
→ apparent imprisonment
→ rupture
→ recognition
→ freedom within law

HOUSE RULES
-----------
• Every shot lasts 5–10 seconds.
• Every shot performs a visible transformation.
• Dark, saturated palette: black, electric cyan, ultraviolet, crimson,
  acid green, molten gold, and white recognition.
• No static slide layouts.
• Mature frame near u=0.72.
• Continuity object: a gold pulse that crystallizes into a cyan causal grid,
  then breaks open without destroying the grid.

OUTPUT
------
output_freedom_before_causality/
  frames/
  scenes/
  freedom_before_causality.mp4
  narration_timeline.json
  contact_sheet.jpg

USAGE
-----
python freedom_before_causality_platinum.py
python freedom_before_causality_platinum.py --preview
python freedom_before_causality_platinum.py --scene 12
python freedom_before_causality_platinum.py --fps 12 --width 1920 --height 1080
"""

from __future__ import annotations

import argparse
import json
import math
import random
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output_freedom_before_causality"
FRAMES = OUTPUT / "frames"
SCENES_DIR = OUTPUT / "scenes"

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 10

BLACK=(5,4,10)
DEEP_BLACK=(1,1,4)
WHITE=(255,253,246)
IVORY=(247,244,235)
INK=(24,22,30)
SILVER=(150,153,170)
CYAN=(35,190,219)
GOLD=(225,168,57)
CRIMSON=(198,34,61)
VIOLET=(121,54,202)
GREEN=(78,210,120)
VENOM=(135,220,69)
ORANGE=(236,93,37)
MAGENTA=(224,42,156)
BLUE=(44,84,190)

FONT_SERIF="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIF_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def clamp(x,lo=0.0,hi=1.0): return max(lo,min(hi,x))
def lerp(a,b,t): return a+(b-a)*clamp(t)
def mix(a,b,t): return tuple(int(lerp(x,y,t)) for x,y in zip(a,b))
def smoothstep(a,b,x):
    if a==b: return 1.0 if x>=b else 0.0
    q=clamp((x-a)/(b-a))
    return q*q*(3-2*q)
def ease(t):
    t=clamp(t)
    return .5-.5*math.cos(math.pi*t)
def pulse(t,speed=1.0,phase=0.0):
    return .5+.5*math.sin(math.tau*(speed*t+phase))

def font(path,size):
    for c in (path,FONT_SERIF,FONT_SANS):
        try: return ImageFont.truetype(c,size)
        except OSError: pass
    return ImageFont.load_default()

def layer(size): return Image.new("RGBA",size,(0,0,0,0))

def dark_field(w,h,seed,light=0.0):
    rng=np.random.default_rng(seed)
    base=np.array(mix(BLACK,IVORY,light),dtype=np.float32)
    arr=np.empty((h,w,3),dtype=np.float32)
    arr[:]=base
    arr+=rng.normal(0,1.7,(h,w,1))
    yy,xx=np.mgrid[0:h,0:w]
    halo=np.exp(-(((xx-w*.5)/(w*.40))**2+((yy-h*.40)/(h*.34))**2)*2.2)
    arr[...,0]+=halo*(12+30*light)
    arr[...,1]+=halo*(4+24*light)
    arr[...,2]+=halo*(18+20*light)
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8),"RGB").convert("RGBA")

def centered(d,xy,text,fnt,fill=WHITE):
    d.text(xy,text,font=fnt,fill=fill,anchor="mm")

def seal(im,title,subtitle="",color=WHITE):
    w,h=im.size
    d=ImageDraw.Draw(im)
    centered(d,(w/2,h*.875),title,font(FONT_SERIF_BOLD,max(22,int(h*.04))),color)
    if subtitle:
        centered(d,(w/2,h*.923),subtitle,font(FONT_SANS,max(13,int(h*.019))),mix(color,SILVER,.55))

def border(im):
    w,h=im.size
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((26,26,w-26,h-26),radius=18,outline=(*GOLD,55),width=2)

def glow_circle(im,x,y,r,color,alpha=180,blur=16):
    gl=layer(im.size)
    gd=ImageDraw.Draw(gl)
    gd.ellipse((x-r,y-r,x+r,y+r),fill=(*color,alpha))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).ellipse(
        (x-r*.30,y-r*.30,x+r*.30,y+r*.30),
        fill=(*mix(color,WHITE,.18),min(255,alpha+45))
    )
    im.alpha_composite(fg)

def glow_line(im,pts,color,width=4,alpha=210,blur=12):
    if len(pts)<2: return
    gl=layer(im.size)
    gd=ImageDraw.Draw(gl)
    gd.line(pts,fill=(*color,alpha),width=width*3,joint="curve")
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).line(
        pts,fill=(*color,min(255,alpha+20)),
        width=width,joint="curve"
    )
    im.alpha_composite(fg)

def partial(pts,a):
    if not pts: return []
    a=clamp(a)
    if a>=1: return pts
    k=a*(len(pts)-1)
    i=int(k)
    f=k-i
    out=list(pts[:i+1])
    if i+1<len(pts):
        p,q=pts[i],pts[i+1]
        out.append((lerp(p[0],q[0],f),lerp(p[1],q[1],f)))
    return out

def arrow(d,a,b,color=WHITE,width=3,head=10):
    d.line((*a,*b),fill=color,width=width)
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for s in (-1,1):
        p=(b[0]-math.cos(ang+s*.52)*head,b[1]-math.sin(ang+s*.52)*head)
        d.line((*b,*p),fill=color,width=width)

def draw_body(d,cx,cy,scale=1.0,color=WHITE,alpha=205):
    d.ellipse((cx-27*scale,cy-145*scale,cx+27*scale,cy-91*scale),
              outline=(*color,alpha),width=max(2,int(4*scale)))
    d.line((cx,cy-91*scale,cx,cy+55*scale),
           fill=(*color,alpha),width=max(3,int(6*scale)))
    d.line((cx-68*scale,cy-54*scale,cx+68*scale,cy-54*scale),
           fill=(*color,alpha),width=max(3,int(5*scale)))
    d.line((cx,cy+55*scale,cx-52*scale,cy+160*scale),
           fill=(*color,alpha),width=max(3,int(5*scale)))
    d.line((cx,cy+55*scale,cx+52*scale,cy+160*scale),
           fill=(*color,alpha),width=max(3,int(5*scale)))

def grid_points(w,h,cols=12,rows=6):
    pts=[]
    for j in range(rows):
        for i in range(cols):
            pts.append((w*.13+i*w*.74/(cols-1), h*.20+j*h*.42/(rows-1)))
    return pts

def spiral(cx,cy,r,turns=2.2,count=180,phase=0.0):
    pts=[]
    for i in range(count):
        q=i/(count-1)
        a=q*math.tau*turns+phase
        rr=r*q
        pts.append((cx+math.cos(a)*rr,cy+math.sin(a)*rr*.62))
    return pts


# =============================================================================
# VISUALS
# =============================================================================

def vis_law_machine(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    pts=grid_points(w,h,12,6)
    q=ease(u)
    for i,(x,y) in enumerate(pts):
        glow_circle(im,x,y,5,CYAN,100,5)
        if i%12!=11:
            d.line((x,y,pts[i+1][0],pts[i+1][1]),fill=(*CYAN,70),width=2)
        if i+12<len(pts):
            d.line((x,y,pts[i+12][0],pts[i+12][1]),fill=(*CYAN,50),width=2)
    wave_x=lerp(w*.13,w*.87,q)
    gl=layer(im.size)
    ImageDraw.Draw(gl).rectangle((wave_x-22,h*.15,wave_x+22,h*.68),fill=(*GOLD,55))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14)))
    seal(im,"THE MODERN UNIVERSE BEGINS AS A MACHINE",
         "laws determine transitions from one state to the next",CYAN)

def vis_chain(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    xs=[w*.15,w*.29,w*.43,w*.57,w*.71,w*.85]
    q=ease(u)
    colors=[CYAN,VIOLET,GREEN,CRIMSON,ORANGE,GOLD]
    for i,x in enumerate(xs):
        glow_circle(im,x,h*.40,12,colors[i],150,8)
        if i<len(xs)-1:
            arrow(d,(x+15,h*.40),(xs[i+1]-15,h*.40),
                  (*colors[i+1],int(170*q)),3,8)
    seal(im,"CAUSE BECOMES EFFECT · EFFECT BECOMES CAUSE",
         "the chain appears complete because every event points elsewhere")

def vis_missing_source(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    ring=spiral(cx,cy,230,2.6,220,t*.08)
    glow_line(im,partial(ring,q),CYAN,4,180,11)
    glow_circle(im,cx,cy,15,GOLD,190,12)
    if q>.6:
        centered(d,(cx,h*.68),"WHY THIS ORDER?",font(FONT_SERIF_BOLD,25),GOLD)
    seal(im,"A CHAIN EXPLAINS TRANSITIONS, NOT ITS OWN APPEARING",
         "regularity still presupposes a field in which regularity can be known")

def vis_svatantrya(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    glow_circle(im,cx,cy,18,GOLD,200,14)
    colors=[CRIMSON,VIOLET,CYAN,GREEN,ORANGE,MAGENTA]
    for i,col in enumerate(colors):
        pts=spiral(cx,cy,lerp(20,240,q),1.1+i*.18,120,t*.10+i)
        glow_line(im,pts,col,3,140,9)
    centered(d,(cx,h*.68),"SVĀTANTRYA",font(FONT_SERIF_BOLD,29),GOLD)
    seal(im,"FREEDOM IS THE POWER TO MANIFEST A FIELD",
         "not random choice, but self-determining appearance")

def vis_spanda(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    r=90+40*math.sin(t*1.2)
    glow_circle(im,cx,cy,r,GOLD,115,20)
    for rr in range(45,280,30):
        alpha=int(70*q*(1-rr/310))
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*[VIOLET,CYAN,GREEN][(rr//30)%3],alpha),width=3)
    seal(im,"SPANDA IS THE PULSE OF SELF-DIFFERENTIATION",
         "the field remains itself while moving into expression")

def vis_pattern_choice(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    possibilities=[]
    for k in range(8):
        pts=[]
        for i in range(80):
            x=w*.18+i*w*.64/79
            y=cy+math.sin(i*.12+k*.8)*45+math.sin(i*.035+k)*35
            pts.append((x,y))
        possibilities.append(pts)
    for i,pts in enumerate(possibilities):
        alpha=190 if i==5 else int(90*(1-q))
        col=GOLD if i==5 else VIOLET
        glow_line(im,partial(pts,q),col,4 if i==5 else 2,alpha,9)
    seal(im,"FREEDOM SELECTS A PATTERN WITHOUT EXTERNAL COMPULSION",
         "one possibility becomes the rule for what follows")

def vis_repetition_law(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    q=ease(u)
    for j in range(6):
        pts=[]
        for i in range(140):
            x=w*.13+i*w*.74/139
            y=h*.20+j*h*.08+math.sin(i*.13)*12*(1-q)
            pts.append((x,y))
        glow_line(im,pts,mix(GOLD,CYAN,q),3,150,8)
    if q>.6:
        centered(d,(w*.50,h*.68),"REPETITION BECOMES LAW",
                 font(FONT_SERIF_BOLD,25),CYAN)
    seal(im,"STABILITY IS FREEDOM HOLDING A FORM",
         "regularity is not the absence of power but its persistence")

def vis_grid_crystal(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    pts=grid_points(w,h,12,6)
    q=ease(u)
    for i,(x,y) in enumerate(pts):
        col=mix(GOLD,CYAN,q)
        glow_circle(im,x,y,5,col,110,5)
        if i%12!=11:
            d.line((x,y,pts[i+1][0],pts[i+1][1]),fill=(*col,70),width=2)
        if i+12<len(pts):
            d.line((x,y,pts[i+12][0],pts[i+12][1]),fill=(*col,50),width=2)
    seal(im,"THE FREE PULSE CRYSTALLIZES AS CAUSAL ORDER",
         "law is frozen rhythm")

def vis_kanchuka_niyati(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    draw_body(d,cx,cy,.72,WHITE,175)
    labels=[
        ("THIS CAUSE",CRIMSON,-170,-100),
        ("THIS PLACE",CYAN,170,-100),
        ("THIS CAPACITY",GREEN,-170,110),
        ("THIS RESULT",VIOLET,170,110),
    ]
    for lab,col,ox,oy in labels:
        x=lerp(cx+ox,cx+ox*.63,q)
        y=lerp(cy+oy,cy+oy*.63,q)
        centered(d,(x,y),lab,font(FONT_SANS_BOLD,13),col)
        glow_line(im,[(x,y),(cx,cy)],col,3,110,8)
    r=lerp(240,105,q)
    d.ellipse((cx-r,cy-r*.68,cx+r,cy+r*.68),
              outline=(*CYAN,205),width=5)
    seal(im,"NIYATI IS FREEDOM EXPERIENCED AS NECESSITY",
         "the finite subject inherits one constrained causal position")

def vis_finite_choice(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    origin=(w*.28,h*.42)
    q=ease(u)
    draw_body(d,*origin,.58,WHITE,175)
    branches=[
        [(origin[0]+35,origin[1]),(w*.52,h*.25),(w*.78,h*.22)],
        [(origin[0]+35,origin[1]),(w*.56,h*.42),(w*.82,h*.42)],
        [(origin[0]+35,origin[1]),(w*.50,h*.58),(w*.74,h*.62)],
    ]
    for i,pts in enumerate(branches):
        glow_line(im,partial(pts,q),[GREEN,GOLD,CRIMSON][i],4,160,9)
    seal(im,"FINITE CHOICE OCCURS INSIDE INHERITED CONDITIONS",
         "freedom appears locally as navigation among constrained possibilities")

def vis_habit_chain(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    xs=[w*.18,w*.34,w*.50,w*.66,w*.82]
    q=ease(u)
    labels=["CUE","REACTION","REWARD","MEMORY","REPEAT"]
    for i,(x,lab) in enumerate(zip(xs,labels)):
        glow_circle(im,x,h*.40,11,[CYAN,CRIMSON,GOLD,VIOLET,GREEN][i],150,8)
        centered(d,(x,h*.67),lab,font(FONT_SANS_BOLD,12),WHITE)
        if i<len(xs)-1:
            arrow(d,(x+14,h*.40),(xs[i+1]-14,h*.40),
                  (*CRIMSON,int(155*q)),2,7)
    arrow(d,(xs[-1],h*.37),(xs[0],h*.37),(*VIOLET,int(130*q)),2,7)
    seal(im,"HABIT IS FREEDOM FORGOTTEN AS AUTOMATION",
         "a chosen pattern begins choosing the organism")

def vis_trauma_lock(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    draw_body(d,cx,cy,.66,WHITE,170)
    for rr in range(45,230,28):
        d.ellipse((cx-rr,cy-rr*.68,cx+rr,cy+rr*.68),
                  outline=(*CRIMSON,int(78*q*(1-rr/260))),width=3)
    for i in range(14):
        a=i*math.tau/14+t*.12
        x=cx+math.cos(a)*170
        y=cy+math.sin(a)*105
        glow_line(im,[(x,y),(cx,cy)],CRIMSON,3,110,8)
    seal(im,"TRAUMA MAKES ONE PAST EVENT GOVERN MANY FUTURES",
         "causal necessity becomes embodied expectation")

def vis_miracle_error(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.30,h*.40)
    right=(w*.70,h*.40)
    q=ease(u)
    # random rupture
    pts=grid_points(w,h,5,5)
    for x,y in pts:
        xx=left[0]+(x-w*.50)*.45
        yy=left[1]+(y-h*.40)*.70
        glow_circle(im,xx,yy,5,CYAN,90,5)
    glow_line(im,[(left[0]-90,left[1]+80),(left[0]+95,left[1]-85)],
              CRIMSON,6,int(180*q),12)
    # lawful transformation
    for rr in range(35,150,25):
        d.ellipse((right[0]-rr,right[1]-rr*.62,right[0]+rr,right[1]+rr*.62),
                  outline=(*GOLD,int(75*q*(1-rr/170))),width=3)
    centered(d,(left[0],h*.68),"RANDOM VIOLATION",font(FONT_SERIF_BOLD,20),CRIMSON)
    centered(d,(right[0],h*.68),"DEEPER ORDER",font(FONT_SERIF_BOLD,20),GOLD)
    seal(im,"FREEDOM IS NOT A MIRACLE PUNCTURING LAW",
         "it is the deeper power by which lawful fields arise and transform")

def vis_novelty(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    q=ease(u)
    base=[]
    for i in range(220):
        x=w*.10+i*w*.80/219
        y=h*.40+math.sin(i*.12)*35
        base.append((x,y))
    glow_line(im,partial(base,q),CYAN,4,180,10)
    branch=[base[120],(w*.66,h*.22),(w*.84,h*.18)]
    glow_line(im,partial(branch,smoothstep(.45,1,u)),GOLD,5,205,13)
    seal(im,"NOVELTY IS A NEW PATH INSIDE A STABLE FIELD",
         "freedom transforms order without requiring chaos")

def vis_creativity(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    fragments=[
        (w*.23,h*.24,CRIMSON),
        (w*.77,h*.24,CYAN),
        (w*.23,h*.58,GREEN),
        (w*.77,h*.58,VIOLET),
    ]
    for x,y,col in fragments:
        glow_circle(im,x,y,12,col,150,8)
        glow_line(im,partial([(x,y),(cx,cy)],q),col,4,145,9)
    glow_circle(im,cx,cy,lerp(12,40,q),GOLD,195,13)
    if q>.65:
        for ray,col in zip(
            [[(cx,cy),(cx+math.cos(a)*180,cy+math.sin(a)*110)]
             for a in np.linspace(0,math.tau,16,endpoint=False)],
            [CRIMSON,VIOLET,CYAN,GREEN,ORANGE,MAGENTA,GOLD,VENOM]*2
        ):
            glow_line(im,partial(ray,(q-.65)/.35),col,3,130,8)
    seal(im,"CREATIVITY RECOMBINES CONSTRAINTS INTO A NEW NECESSITY",
         "the work becomes lawful only after freedom discovers its form")

def vis_ethics(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    centers=[
        (w*.25,h*.30,CYAN),
        (w*.75,h*.30,VIOLET),
        (w*.25,h*.56,GREEN),
        (w*.75,h*.56,CRIMSON),
    ]
    for x,y,col in centers:
        glow_circle(im,x,y,14,col,160,9)
        glow_line(im,partial([(x,y),(cx,cy)],q),col,4,145,9)
    glow_circle(im,cx,cy,16,GOLD,185,12)
    seal(im,"FREEDOM BECOMES ETHICAL WHEN IT RECOGNIZES OTHER CENTERS",
         "power without recognition contracts into domination")

def vis_recognition_break(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    pts=grid_points(w,h,12,6)
    q=ease(u)
    for i,(x,y) in enumerate(pts):
        glow_circle(im,x,y,5,CYAN,90,5)
        if i%12!=11:
            d.line((x,y,pts[i+1][0],pts[i+1][1]),fill=(*CYAN,55),width=2)
        if i+12<len(pts):
            d.line((x,y,pts[i+12][0],pts[i+12][1]),fill=(*CYAN,40),width=2)
    cx,cy=w*.50,h*.40
    glow_circle(im,cx,cy,18,GOLD,200,14)
    for i in range(18):
        a=i*math.tau/18
        ray=[(cx,cy),(cx+math.cos(a)*lerp(20,260,q),
                      cy+math.sin(a)*lerp(12,165,q))]
        glow_line(im,ray,[CRIMSON,VIOLET,GREEN,GOLD][i%4],4,145,9)
    seal(im,"RECOGNITION BREAKS FATALISM WITHOUT BREAKING THE WORLD",
         "the grid remains, but it is no longer mistaken for the source")

def vis_action_after_recognition(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    origin=(w*.28,h*.42)
    q=ease(u)
    draw_body(d,*origin,.58,WHITE,175)
    paths=[
        [(origin[0]+35,origin[1]),(w*.50,h*.25),(w*.76,h*.22)],
        [(origin[0]+35,origin[1]),(w*.54,h*.42),(w*.82,h*.42)],
        [(origin[0]+35,origin[1]),(w*.50,h*.58),(w*.74,h*.62)],
    ]
    for i,pts in enumerate(paths):
        glow_line(im,partial(pts,q),[GREEN,GOLD,VIOLET][i],4,160,9)
    for rr in range(35,180,25):
        d.ellipse((origin[0]-rr,origin[1]-rr*.62,
                   origin[0]+rr,origin[1]+rr*.62),
                  outline=(*GOLD,int(65*q*(1-rr/205))),width=3)
    seal(im,"LIBERATION DOES NOT ABOLISH ACTION",
         "it restores action as expression rather than compulsion")

def vis_science_bridge(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.30,h*.40)
    right=(w*.70,h*.40)
    q=ease(u)
    # dynamical system
    for rr in range(35,150,25):
        d.ellipse((left[0]-rr,left[1]-rr*.62,left[0]+rr,left[1]+rr*.62),
                  outline=(*CYAN,int(75*q*(1-rr/170))),width=3)
    glow_line(im,spiral(left[0],left[1],125,1.8,140,t*.08),VIOLET,3,145,9)
    # svatantrya field
    glow_circle(im,*right,16,GOLD,185,12)
    for rr in range(35,155,25):
        d.ellipse((right[0]-rr,right[1]-rr*.62,
                   right[0]+rr,right[1]+rr*.62),
                  outline=(*GOLD,int(75*q*(1-rr/175))),width=3)
    centered(d,(left[0],h*.68),"DYNAMICAL NOVELTY",font(FONT_SANS_BOLD,13),CYAN)
    centered(d,(right[0],h*.68),"ONTOLOGICAL FREEDOM",font(FONT_SANS_BOLD,13),GOLD)
    glow_line(im,partial([left,(w*.50,h*.20),right],q),VIOLET,4,170,11)
    seal(im,"SCIENCE CAN MODEL EMERGENCE AND NOVELTY",
         "ABHINAVA ASKS WHAT MAKES ANY FIELD OF POSSIBILITY POSSIBLE")

def vis_caution(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    rows=[
        ("PHYSICAL REGULARITIES ARE REAL","SUPPORTED",GREEN),
        ("PERSONAL DESIRE OVERRIDES PHYSICS","FALSE",CRIMSON),
        ("FINITE CHOICE IS CONDITIONED","SUPPORTED",CYAN),
        ("SVĀTANTRYA IS RANDOMNESS","FALSE",CRIMSON),
    ]
    q=ease(u)
    for i,(claim,status,col) in enumerate(rows):
        local=clamp(q*len(rows)-i)
        y=h*(.23+i*.13)
        d.rounded_rectangle((w*.12,y-28,w*.88,y+28),
                            radius=14,
                            fill=(*mix(BLACK,col,.12),int(220*local)),
                            outline=(*col,int(180*local)),width=2)
        centered(d,(w*.39,y),claim,font(FONT_SANS_BOLD,14),WHITE)
        centered(d,(w*.75,y),status,font(FONT_SANS_BOLD,14),col)
    seal(im,"DO NOT CONFUSE ABSOLUTE FREEDOM WITH EGOIC OMNIPOTENCE",
         "the finite person remains embodied, relational, and conditioned")

def vis_final(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    pts=grid_points(w,h,12,6)
    q=ease(u)
    for i,(x,y) in enumerate(pts):
        glow_circle(im,x,y,5,CYAN,85,5)
        if i%12!=11:
            d.line((x,y,pts[i+1][0],pts[i+1][1]),fill=(*CYAN,50),width=2)
        if i+12<len(pts):
            d.line((x,y,pts[i+12][0],pts[i+12][1]),fill=(*CYAN,35),width=2)
    cx,cy=w*.50,h*.40
    glow_circle(im,cx,cy,18,GOLD,205,14)
    colors=[CRIMSON,VIOLET,CYAN,GREEN,ORANGE,MAGENTA,GOLD,VENOM]
    for i,col in enumerate(colors):
        a=i*math.tau/len(colors)+t*.06
        ray=[(cx,cy),(cx+math.cos(a)*lerp(20,260,q),
                      cy+math.sin(a)*lerp(12,165,q))]
        glow_line(im,ray,col,4,145,9)
    if q>.72:
        centered(d,(cx,h*.68),"SVĀTANTRYA",font(FONT_SERIF_BOLD,30),GOLD)
    seal(im,"FREEDOM COMES BEFORE CAUSALITY",
         "law is freedom holding a pattern; liberation is seeing the pattern without mistaking it for the source",GOLD)


VISUALS: dict[str,Callable] = {
    "machine":vis_law_machine,
    "chain":vis_chain,
    "missing":vis_missing_source,
    "freedom":vis_svatantrya,
    "spanda":vis_spanda,
    "choice":vis_pattern_choice,
    "repeat":vis_repetition_law,
    "grid":vis_grid_crystal,
    "niyati":vis_kanchuka_niyati,
    "finite":vis_finite_choice,
    "habit":vis_habit_chain,
    "trauma":vis_trauma_lock,
    "miracle":vis_miracle_error,
    "novelty":vis_novelty,
    "creativity":vis_creativity,
    "ethics":vis_ethics,
    "break":vis_recognition_break,
    "action":vis_action_after_recognition,
    "bridge":vis_science_bridge,
    "caution":vis_caution,
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
    Scene("Machine universe",
          "Modern thought often begins with a machine.",
          7.0,"machine",{}),
    Scene("Law first",
          "Laws determine how one physical state becomes the next.",
          8.0,"machine",{}),
    Scene("Choice last",
          "Organisms appear later, and freedom becomes either a useful illusion or a rare exception.",
          9.5,"machine",{}),

    Scene("Causal chain",
          "Cause becomes effect. Effect becomes cause.",
          7.5,"chain",{}),
    Scene("Complete appearance",
          "The chain seems complete because every event points to an earlier event.",
          8.5,"chain",{}),
    Scene("Hidden question",
          "But the chain does not explain why there is an appearing order in which causes can be known.",
          10.0,"missing",{}),

    Scene("Reversal",
          "Abhinavagupta reverses the order.",
          7.0,"freedom",{}),
    Scene("Freedom first",
          "Freedom comes before causality.",
          6.5,"freedom",{}),
    Scene("Svatantrya",
          "He calls this primordial power svātantrya: consciousness determining its own manifestation.",
          9.5,"freedom",{}),

    Scene("Not randomness",
          "Svātantrya is not randomness.",
          7.0,"freedom",{}),
    Scene("Not indecision",
          "It is not hesitation among options.",
          6.5,"freedom",{}),
    Scene("Power to appear",
          "It is the power to manifest, conceal, differentiate, stabilize, and transform an entire field.",
          10.0,"freedom",{}),

    Scene("Spanda",
          "The first image is pulse.",
          6.5,"spanda",{}),
    Scene("Still movement",
          "Consciousness remains itself while moving into expression.",
          8.5,"spanda",{}),
    Scene("Spanda power",
          "Spanda is not motion through space. It is the living tension between undivided awareness and articulated appearance.",
          10.0,"spanda",{}),

    Scene("Possibility",
          "Before law, imagine a field of possible pattern.",
          8.0,"choice",{}),
    Scene("Selection",
          "One configuration is taken up.",
          6.5,"choice",{}),
    Scene("Self-determination",
          "The pattern does not need an external chooser standing outside consciousness.",
          8.5,"choice",{}),

    Scene("Repetition",
          "The chosen pattern repeats.",
          6.5,"repeat",{}),
    Scene("Stability",
          "Repetition becomes stability.",
          6.5,"repeat",{}),
    Scene("Law",
          "Stability becomes law.",
          6.0,"repeat",{}),
    Scene("Frozen rhythm",
          "Law is frozen rhythm: freedom holding one form consistently.",
          8.5,"grid",{}),

    Scene("Causal world",
          "Once the pattern stabilizes, events become predictable.",
          8.0,"grid",{}),
    Scene("Reliable world",
          "Bodies can evolve, memory can work, and action can learn because the field is reliable.",
          9.5,"grid",{}),
    Scene("Gift of law",
          "Causality is therefore not only confinement. It is also the gift of a world that can be inhabited.",
          10.0,"grid",{}),

    Scene("Niyati",
          "The finite subject experiences this order through niyati.",
          8.0,"niyati",{}),
    Scene("Necessity",
          "This body, this place, this history, this capacity, this consequence.",
          8.5,"niyati",{}),
    Scene("Local necessity",
          "Absolute freedom appears locally as inherited necessity.",
          8.0,"niyati",{}),

    Scene("Finite choice",
          "Human choice occurs inside these conditions.",
          8.0,"finite",{}),
    Scene("Not unlimited",
          "We do not choose our birth, body, language, past, or every available option.",
          9.5,"finite",{}),
    Scene("Navigation",
          "Finite freedom is navigation among constrained possibilities.",
          8.0,"finite",{}),

    Scene("Habit",
          "A chosen pattern can become a habit.",
          7.5,"habit",{}),
    Scene("Automation",
          "Cue, reaction, reward, memory, repetition.",
          8.0,"habit",{}),
    Scene("Forgotten freedom",
          "Habit is freedom forgotten as automation.",
          8.0,"habit",{}),
    Scene("Pattern chooses",
          "The pattern begins choosing the organism.",
          7.5,"habit",{}),

    Scene("Trauma",
          "Trauma reveals a harsher form of causal contraction.",
          8.5,"trauma",{}),
    Scene("Past governs future",
          "One past event becomes a rule for many possible futures.",
          8.5,"trauma",{}),
    Scene("Embodied necessity",
          "Expectation becomes bodily necessity before reflection can intervene.",
          9.0,"trauma",{}),

    Scene("Wrong miracle",
          "Freedom is often imagined as a miracle that punctures law.",
          8.0,"miracle",{}),
    Scene("Random violation",
          "Something impossible suddenly violates the system.",
          7.5,"miracle",{}),
    Scene("Deeper order",
          "Abhinavagupta's claim is deeper: freedom is the power by which lawful systems arise at all.",
          10.0,"miracle",{}),

    Scene("Novelty",
          "Novelty therefore need not mean chaos.",
          7.5,"novelty",{}),
    Scene("New path",
          "A new path can emerge inside a stable field.",
          8.0,"novelty",{}),
    Scene("Transform lawfully",
          "Freedom transforms order without destroying intelligibility.",
          8.0,"novelty",{}),

    Scene("Creativity",
          "Creativity offers an everyday analogy.",
          7.5,"creativity",{}),
    Scene("Fragments",
          "Memory, sensation, technique, constraint, and accident converge.",
          8.5,"creativity",{}),
    Scene("New necessity",
          "A new form appears, and once it appears, its parts suddenly seem necessary.",
          9.0,"creativity",{}),
    Scene("Discovered law",
          "The work becomes lawful after freedom discovers its pattern.",
          8.0,"creativity",{}),

    Scene("Ethics",
          "Absolute freedom is not ethical merely because it is powerful.",
          8.5,"ethics",{}),
    Scene("Other centers",
          "Ethics begins when one center recognizes other centers as expressions of the same field.",
          9.5,"ethics",{}),
    Scene("Domination",
          "Power without recognition contracts into domination.",
          8.0,"ethics",{}),

    Scene("Recognition",
          "Recognition breaks fatalism without breaking the world.",
          8.5,"break",{}),
    Scene("Grid remains",
          "The causal grid remains.",
          6.5,"break",{}),
    Scene("Source revealed",
          "What changes is the belief that the grid is the ultimate source of appearing.",
          9.0,"break",{}),

    Scene("Liberated action",
          "Liberation does not abolish action.",
          7.5,"action",{}),
    Scene("No passivity",
          "It does not reduce the practitioner to passive witnessing.",
          8.0,"action",{}),
    Scene("Expression",
          "Action becomes expression rather than compulsion.",
          7.5,"action",{}),
    Scene("Play within law",
          "The finite agent acts inside conditions while recognizing the deeper field of freedom.",
          9.5,"action",{}),

    Scene("Science",
          "Modern science can model emergence, self-organization, stochasticity, and dynamical novelty.",
          9.5,"bridge",{}),
    Scene("Mechanism",
          "These explain how new patterns arise within physical systems.",
          8.0,"bridge",{}),
    Scene("Prior question",
          "Abhinavagupta asks what makes any field of possibility, law, or intelligibility possible in the first place.",
          10.0,"bridge",{}),

    Scene("Discipline",
          "The comparison must remain disciplined.",
          7.0,"caution",{}),
    Scene("No omnipotence",
          "The personal ego does not override physics by wishing.",
          8.0,"caution",{}),
    Scene("No randomness",
          "Svātantrya is not random noise.",
          7.0,"caution",{}),
    Scene("Conditioned person",
          "The finite person remains embodied, relational, and conditioned.",
          8.5,"caution",{}),

    Scene("Return",
          "Return to the causal grid.",
          6.5,"final",{}),
    Scene("Gold pulse",
          "A gold pulse appears inside it.",
          6.5,"final",{}),
    Scene("Grid not destroyed",
          "The grid does not shatter.",
          6.0,"final",{}),
    Scene("Reinterpretation",
          "It becomes visible as one stabilized expression of a deeper power.",
          8.5,"final",{}),
    Scene("Closing",
          "Freedom comes before causality: law is freedom holding a pattern, and liberation is seeing the pattern without mistaking it for the source.",
          10.0,"final",{}),
]


def render_frame(scene,frame_index,frame_count,width,height,seed):
    u=frame_index/max(1,frame_count-1)
    t=u*scene.duration
    light=.12*smoothstep(.45,1.0,u) if scene.visual in {"break","action","final"} else 0.0
    im=dark_field(width,height,seed,light)
    VISUALS[scene.visual](im,u,t,scene.params)
    border(im)
    return im.convert("RGB")

def ffmpeg_path():
    exe=shutil.which("ffmpeg")
    if not exe:
        raise RuntimeError("ffmpeg is required but was not found on PATH")
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
    txt.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in paths),
        encoding="utf-8"
    )
    output=OUTPUT/"freedom_before_causality.mp4"
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
        "title":"freedom comes before causality",
        "subtitle":"Abhinavagupta on svatantrya, spanda, and the birth of law",
        "scene_count":len(SCENES),
        "runtime_seconds":round(cursor,3),
        "shot_duration_range":[5,10],
        "continuity_object":"gold pulse crystallizing into cyan causal grid",
        "palette":"black, electric cyan, ultraviolet, crimson, acid green, molten gold",
        "visual_arc":[
            "law","chain","missing source","svatantrya","spanda",
            "pattern","repetition","causality","conditioning",
            "recognition","freedom within law"
        ],
        "scenes":records,
    },indent=2,ensure_ascii=False),encoding="utf-8")
    return path

def make_contact_sheet(width,height):
    tw=320
    th=int(tw*height/width)
    cols=4
    rows=math.ceil(len(SCENES)/cols)
    cell_h=th+48
    sheet=Image.new("RGB",(cols*tw,rows*cell_h),BLACK)
    d=ImageDraw.Draw(sheet)
    lf=font(FONT_SANS_BOLD,14)

    for index,scene in enumerate(SCENES,1):
        count=max(2,round(scene.duration*DEFAULT_FPS))
        image=render_frame(
            scene,int(count*.72),count,width,height,index*10000+72
        )
        image.thumbnail((tw,th))
        slot=index-1
        x=(slot%cols)*tw
        y=(slot//cols)*cell_h
        sheet.paste(image,(x,y))
        d.text((x+8,y+th+7),
               f"{index:02d}  {scene.title}",
               font=lf,fill=WHITE)

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
    print(f"Runtime: {sum(scene.duration for scene in SCENES)/60:.2f} minutes")

    if args.scene:
        if not 1<=args.scene<=len(SCENES):
            raise ValueError("scene out of range")
        print(render_scene(
            args.scene,
            SCENES[args.scene-1],
            args.fps,
            args.width,
            args.height,
            args.preview,
        ))
        return

    rendered=[]
    for index,scene in enumerate(SCENES,1):
        print(f"[{index:02d}/{len(SCENES):02d}] {scene.title} ({scene.duration:.1f}s)")
        result=render_scene(
            index,
            scene,
            args.fps,
            args.width,
            args.height,
            args.preview,
        )
        if not args.preview:
            rendered.append(result)

    if not args.no_contact_sheet:
        print(f"Contact sheet: {make_contact_sheet(args.width,args.height)}")

    if not args.preview:
        print(f"Final video: {concatenate(rendered)}")


if __name__=="__main__":
    main()
