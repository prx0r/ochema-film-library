#!/usr/bin/env python3
"""
THE BODY IS AN ELECTRICAL SOCIETY
A Michael Levin–themed Platinum-house procedural visual essay.

SCIENTIFIC GROUNDING
--------------------
Built around established themes in developmental bioelectricity:

• all cells maintain transmembrane voltage;
• ion channels and pumps create and modify resting-potential states;
• gap junctions couple cells into multicellular electrical networks;
• slow non-neural bioelectric states can regulate proliferation, migration,
  differentiation, gene expression, polarity, regeneration, and cancer;
• tissue-wide voltage patterns can store instructive, non-genetic information;
• bioelectric circuits can display attractors, robustness, plasticity, and memory;
• morphogenesis translates physiological state into transcription and mechanics.

The film treats "electrical society" as a systems metaphor:
cells retain local autonomy while participating in a distributed physiological
network whose states help coordinate large-scale anatomical outcomes.

It does not claim that voltage alone explains development, nor that tissue
electricity is identical to human thought or phenomenal consciousness.

FILM THESIS
-----------
A body is not assembled only by genes issuing molecular instructions.
It is also coordinated by cells continuously negotiating physiological state.

Each cell maintains a voltage.
Gap junctions make neighboring voltages mutually relevant.
The collective enters tissue-scale electrical states.
Those states alter gene expression and cell behavior.
Anatomy emerges partly from this translation between distributed physiology
and material form.

The body's hidden electrical society is not a second ghostly body.
It is living matter communicating about what the body is becoming.

HOUSE RULES
-----------
• Every shot lasts 5–10 seconds.
• Every shot performs before → operation → after.
• Clean ivory scientific/gallery field.
• No static slide layouts.
• Sparse labels only.
• Mature frame near u=0.72.
• Continuity object: a cyan voltage wave that expands from one membrane into
  a tissue-wide gold pattern.

PALETTE ROLES
-------------
IVORY    open physiological field
CYAN     membrane potential / communication
GOLD     coherent tissue state / anatomical instruction
GREEN    viable integration / repair
CRIMSON  stress / depolarized defection / pattern error
VIOLET   memory / alternative electrical attractor
INK      visible anatomy / fixed material structure

OUTPUT
------
output_electrical_society/
  frames/scene_001/*.jpg
  scenes/scene_001.mp4
  body_electrical_society.mp4
  narration_timeline.json
  contact_sheet.jpg

USAGE
-----
python body_electrical_society_platinum.py
python body_electrical_society_platinum.py --preview
python body_electrical_society_platinum.py --scene 12
python body_electrical_society_platinum.py --fps 12 --width 1920 --height 1080
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


# =============================================================================
# CONFIG
# =============================================================================

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output_electrical_society"
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
DEEP_CYAN=(34,101,129)
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


# =============================================================================
# HELPERS
# =============================================================================

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
    for candidate in (path,FONT_SERIF,FONT_SANS):
        try: return ImageFont.truetype(candidate,size)
        except OSError: pass
    return ImageFont.load_default()

def layer(size): return Image.new("RGBA",size,(0,0,0,0))

def field(w,h,seed):
    rng=np.random.default_rng(seed)
    arr=np.empty((h,w,3),dtype=np.float32)
    arr[:]=IVORY
    arr+=rng.normal(0,.9,(h,w,1))
    yy,xx=np.mgrid[0:h,0:w]
    halo=np.exp(-(((xx-w*.5)/(w*.37))**2+((yy-h*.40)/(h*.31))**2)*2)
    arr[...,1]+=halo*3.4
    arr[...,2]+=halo*5.0
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8),"RGB").convert("RGBA")

def centered(d,xy,text,fnt,fill=INK):
    d.text(xy,text,font=fnt,fill=fill,anchor="mm")

def seal(im,title,subtitle="",color=INK):
    w,h=im.size
    d=ImageDraw.Draw(im)
    centered(d,(w/2,h*.875),title,font(FONT_SERIF_BOLD,max(22,int(h*.04))),color)
    if subtitle:
        centered(d,(w/2,h*.923),subtitle,font(FONT_SANS,max(13,int(h*.019))),SOFT_INK)

def border(im):
    w,h=im.size
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((26,26,w-26,h-26),radius=18,outline=(*INK,45),width=2)

def glow_circle(im,x,y,r,color,alpha=170,blur=14):
    gl=layer(im.size)
    gd=ImageDraw.Draw(gl)
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
    gl=layer(im.size)
    gd=ImageDraw.Draw(gl)
    gd.line(pts,fill=(*color,alpha),width=width*3,joint="curve")
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).line(
        pts,fill=(*mix(color,WHITE,.08),min(255,alpha+25)),
        width=width,joint="curve"
    )
    im.alpha_composite(fg)

def partial(pts,amount):
    if not pts: return []
    amount=clamp(amount)
    if amount>=1: return pts
    target=amount*(len(pts)-1)
    idx=int(target)
    frac=target-idx
    out=list(pts[:idx+1])
    if idx+1<len(pts):
        a,b=pts[idx],pts[idx+1]
        out.append((lerp(a[0],b[0],frac),lerp(a[1],b[1],frac)))
    return out

def arrow(d,a,b,color=INK,width=3,head=10):
    d.line((*a,*b),fill=color,width=width)
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for s in (-1,1):
        p=(b[0]-math.cos(ang+s*.52)*head,b[1]-math.sin(ang+s*.52)*head)
        d.line((*b,*p),fill=color,width=width)

def draw_cell(d,cx,cy,r,color=CYAN,alpha=205,fill_alpha=75):
    d.ellipse((cx-r,cy-r,cx+r,cy+r),
              fill=(*mix(WHITE,color,.14),fill_alpha),
              outline=(*color,alpha),width=3)

def tissue_grid(w,h,cols=11,rows=6,seed=12):
    rng=random.Random(seed)
    nodes=[]
    for j in range(rows):
        for i in range(cols):
            x=w*.13+i*w*.74/(cols-1)+rng.uniform(-7,7)
            y=h*.20+j*h*.42/(rows-1)+rng.uniform(-6,6)
            nodes.append((x,y))
    return nodes

def membrane_channels(d,cx,cy,r,t,alpha=210):
    for i in range(12):
        a=i*math.tau/12
        x1=cx+math.cos(a)*(r-18)
        y1=cy+math.sin(a)*(r-18)
        x2=cx+math.cos(a)*(r+24)
        y2=cy+math.sin(a)*(r+24)
        d.line((x1,y1,x2,y2),fill=(*INK,110),width=4)
        q=(t*.32+i/12)%1
        if i%2: q=1-q
        x=lerp(x1,x2,q); y=lerp(y1,y2,q)
        col=GOLD if i%2==0 else VIOLET
        d.ellipse((x-5,y-5,x+5,y+5),fill=(*col,alpha))

def voltage_wave(cx,cy,length,amp,t,phase=0.0,samples=180):
    pts=[]
    for i in range(samples):
        q=i/(samples-1)
        x=cx-length/2+q*length
        env=math.sin(math.pi*q)**.55
        y=cy+math.sin(q*math.tau*4+t*.65+phase)*amp*env
        pts.append((x,y))
    return pts

def draw_embryo(d,cx,cy,r,stage,color=CYAN,alpha=210):
    if stage<=1:
        draw_cell(d,cx,cy,r,color,alpha)
        return
    rings=max(2,stage)
    for i in range(rings):
        a=i*math.tau/rings
        x=cx+math.cos(a)*r*.55
        y=cy+math.sin(a)*r*.55
        draw_cell(d,x,y,r*.42,color,alpha)

def attractor_curve(left,right,base,centers,depths,widths,samples=260):
    pts=[]
    for i in range(samples):
        q=i/(samples-1)
        y=base
        for c,d,w in zip(centers,depths,widths):
            y-=d*math.exp(-((q-c)/w)**2)
        pts.append((lerp(left,right,q),y))
    return pts


# =============================================================================
# VISUALS
# =============================================================================

def vis_single_membrane(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    r=lerp(55,145,q)
    draw_cell(d,cx,cy,r,CYAN,215,70)
    membrane_channels(d,cx,cy,r,t)
    for rr in range(35,210,28):
        d.arc((cx-rr,cy-rr,cx+rr,cy+rr),210,330,
              fill=(*CYAN,int(70*q*(1-rr/230))),width=3)
    seal(im,"EVERY CELL IS AN ELECTRICAL OBJECT",
         "a membrane separates charge and creates a voltage")

def vis_voltage_not_spike(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    pts=[]
    for i in range(220):
        x=w*.10+i*w*.80/219
        slow=math.sin(i*.045+t*.6)*45
        pts.append((x,cy+slow))
    glow_line(im,partial(pts,q),CYAN,5,205,13)
    for i in range(7):
        x=w*.18+i*w*.64/6
        d.line((x,cy-95,x,cy+95),fill=(*SILVER,65),width=2)
    centered(d,(cx,h*.68),"SLOW STATE · NOT ONLY FAST SPIKE",
             font(FONT_SERIF_BOLD,24),CYAN)
    seal(im,"BIOELECTRICITY IS OLDER AND BROADER THAN NERVES",
         "non-neural tissues also use membrane-potential dynamics")

def vis_channels_write(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    draw_cell(d,cx,cy,145,CYAN,210,65)
    q=ease(u)
    for i in range(14):
        a=i*math.tau/14
        x1=cx+math.cos(a)*120
        y1=cy+math.sin(a)*120
        x2=cx+math.cos(a)*172
        y2=cy+math.sin(a)*172
        openness=(q+i/14)%1
        col=GREEN if openness>.45 else CRIMSON
        width=2+int(openness*5)
        d.line((x1,y1,x2,y2),fill=(*col,180),width=width)
        ion=openness
        x=lerp(x1,x2,ion); y=lerp(y1,y2,ion)
        glow_circle(im,x,y,5,GOLD,120,6)
    seal(im,"ION CHANNELS WRITE PHYSIOLOGICAL STATE",
         "small molecular gates reshape the voltage of the whole cell")

def vis_gap_social(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    nodes=tissue_grid(w,h,11,6,23)
    cols=11; rows=6
    q=ease(u)
    for j in range(rows):
        for i in range(cols):
            idx=j*cols+i
            if i<cols-1:
                a=nodes[idx]; b=nodes[idx+1]
                d.line((*a,*b),fill=(*CYAN,105),width=3)
            if j<rows-1:
                a=nodes[idx]; b=nodes[idx+cols]
                d.line((*a,*b),fill=(*CYAN,70),width=2)
    for x,y in nodes:
        draw_cell(d,x,y,10,CYAN,185,60)
    wave=lerp(w*.10,w*.90,q)
    gl=layer(im.size)
    gd=ImageDraw.Draw(gl)
    gd.rectangle((wave-28,h*.14,wave+28,h*.68),fill=(*GOLD,48))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(18)))
    seal(im,"GAP JUNCTIONS MAKE VOLTAGE SOCIAL",
         "neighboring cells become parts of one physiological conversation")

def vis_consensus(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    nodes=tissue_grid(w,h,10,5,41)
    q=ease(u)
    for i,(x,y) in enumerate(nodes):
        phase=i*.31
        local=math.sin(t*.9+phase)*(1-q)
        col=mix(VIOLET,CYAN,.5+.5*local)
        draw_cell(d,x,y,11,col,180,60)
    if q>.35:
        for i in range(len(nodes)-1):
            if i%10!=9:
                d.line((*nodes[i],*nodes[i+1]),fill=(*GOLD,int(110*q)),width=2)
    if q>.68:
        for x,y in nodes:
            d.ellipse((x-6,y-6,x+6,y+6),fill=(*GOLD,120))
    seal(im,"COUPLING CAN CREATE PHYSIOLOGICAL CONSENSUS",
         "many local voltages settle into a tissue-level state")

def vis_attractor(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left,right=w*.12,w*.88
    base=h*.64
    q=ease(u)
    pts=attractor_curve(left,right,base,[.26,.74],[95,105],[.12,.11])
    d.line(pts,fill=(*INK,190),width=4)
    xq=lerp(.48,.74,q)
    idx=int(xq*(len(pts)-1))
    x,y=pts[idx]
    glow_circle(im,x,y-14,15,VIOLET if xq>.55 else CYAN,180,10)
    centered(d,(w*.28,h*.70),"STATE A",font(FONT_SANS_BOLD,15),CYAN)
    centered(d,(w*.72,h*.70),"STATE B",font(FONT_SANS_BOLD,15),VIOLET)
    seal(im,"BIOELECTRIC NETWORKS CAN HAVE ATTRACTORS",
         "a brief input can move tissue into a persistent alternative state")

def vis_pattern_memory(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    nodes=tissue_grid(w,h,12,5,58)
    q=ease(u)
    switch=smoothstep(.16,.50,u)
    for i,(x,y) in enumerate(nodes):
        band=(i%12)/11
        col=mix(CYAN,VIOLET,switch*(.25+.75*band))
        draw_cell(d,x,y,10,col,180,55)
    pulse_alpha=int(150*(1-smoothstep(.44,.70,u)))
    gl=layer(im.size)
    ImageDraw.Draw(gl).rectangle((w*.44,h*.16,w*.56,h*.66),
                                 fill=(*CRIMSON,pulse_alpha))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(20)))
    if q>.55:
        glow_line(im,voltage_wave(w*.50,h*.41,w*.66,h*.04,t,1.2),
                  VIOLET,5,190,13)
    seal(im,"THE INPUT VANISHES · THE NETWORK REMEMBERS",
         "patterning information can persist outside DNA sequence")

def vis_embryo_prepattern(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    stage=min(8,1+int(q*7))
    draw_embryo(d,cx,cy,120,stage,CYAN,195)
    # invisible axes become visible
    arrow(d,(cx-180,cy),(cx+180,cy),(*GOLD,int(190*q)),4,10)
    arrow(d,(cx,cy+145),(cx,cy-145),(*VIOLET,int(170*q)),4,10)
    centered(d,(cx,h*.69),"AXES BEFORE ORGANS",font(FONT_SERIF_BOLD,25),GOLD)
    seal(im,"ELECTRICAL PREPATTERNS CAN PRECEDE VISIBLE ANATOMY",
         "physiological asymmetry helps organize later form")

def vis_voltage_to_gene(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.22,h*.40); center=(w*.50,h*.40); right=(w*.78,h*.40)
    q=ease(u)
    draw_cell(d,*left,70,CYAN,195,65)
    membrane_channels(d,*left,70,t,170)
    # transcription helix
    for i in range(90):
        yy=lerp(h*.25,h*.56,i/89)
        xx=center[0]+math.sin(i*.28+t)*25
        d.ellipse((xx-3,yy-3,xx+3,yy+3),fill=(*VIOLET,150))
        xx2=center[0]-math.sin(i*.28+t)*25
        d.ellipse((xx2-3,yy-3,xx2+3,yy+3),fill=(*GOLD,150))
    # behavior arrows
    for k,lab in enumerate(("DIVIDE","MIGRATE","DIFFERENTIATE")):
        y=h*(.28+k*.13)
        d.rounded_rectangle((right[0]-90,y-20,right[0]+90,y+20),
                            radius=12,fill=(*PALE_GREEN,160),
                            outline=(*GREEN,170),width=2)
        centered(d,(right[0],y),lab,font(FONT_SANS_BOLD,14),GREEN)
    glow_line(im,partial([left,center,right],q),GOLD,5,205,13)
    seal(im,"VOLTAGE IS TRANSLATED INTO GENE EXPRESSION AND BEHAVIOR",
         "physiology interfaces with transcription and mechanics")

def vis_growth_decisions(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    origins=[(cx-180,cy),(cx,cy),(cx+180,cy)]
    labels=["MIGRATE","DIVIDE","DIFFERENTIATE"]
    colors=[CYAN,GREEN,GOLD]
    for i,(x,y) in enumerate(origins):
        draw_cell(d,x,y,28,colors[i],190,70)
        local=clamp(q*3-i)
        if i==0:
            arrow(d,(x,y),(x+110*local,y-45*local),(*CYAN,180),4,9)
        elif i==1:
            draw_cell(d,x-30*local,y,28,GREEN,int(190*local),70)
            draw_cell(d,x+30*local,y,28,GREEN,int(190*local),70)
        else:
            d.polygon([(x,y-45*local),(x-40*local,y+30*local),
                       (x+40*local,y+30*local)],
                      outline=(*GOLD,int(190*local)))
        centered(d,(x,h*.67),labels[i],font(FONT_SANS_BOLD,15),colors[i])
    seal(im,"CELLULAR DECISIONS BECOME ANATOMY",
         "electrical state biases what each cell does next")

def vis_eye_induction(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    # tissue field
    nodes=tissue_grid(w,h,10,5,66)
    for x,y in nodes:
        draw_cell(d,x,y,10,CYAN,155,45)
    target=(cx,cy)
    for rr in range(35,120,25):
        d.ellipse((target[0]-rr,target[1]-rr,target[0]+rr,target[1]+rr),
                  outline=(*GOLD,int(80*q*(1-rr/140))),width=3)
    if q>.46:
        alpha=int(220*(q-.46)/.54)
        d.ellipse((cx-80,cy-45,cx+80,cy+45),outline=(*INK,alpha),width=5)
        d.ellipse((cx-24,cy-24,cx+24,cy+24),fill=(*VIOLET,alpha))
        d.ellipse((cx-9,cy-9,cx+9,cy+9),fill=(*INK,alpha))
    seal(im,"A LOCAL VOLTAGE STATE CAN INSTRUCT AN ORGAN PROGRAM",
         "bioelectric cues can act upstream of complex morphogenesis")

def vis_polarity(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    # tissue strip
    d.rounded_rectangle((w*.15,h*.31,w*.85,h*.49),radius=35,
                        fill=(*PALE_CYAN,120),outline=(*CYAN,190),width=4)
    for i in range(80):
        x=lerp(w*.17,w*.83,i/79)
        col=mix(GOLD,VIOLET,i/79)
        d.line((x,h*.33,x,h*.47),fill=(*col,int(45+85*q)),width=3)
    arrow(d,(w*.22,h*.58),(w*.78,h*.58),(*INK,180),4,10)
    centered(d,(w*.22,h*.66),"ANTERIOR",font(FONT_SANS_BOLD,14),GOLD)
    centered(d,(w*.78,h*.66),"POSTERIOR",font(FONT_SANS_BOLD,14),VIOLET)
    seal(im,"ELECTRICAL GRADIENTS CAN CARRY POLARITY",
         "the tissue encodes direction before rebuilding structure")

def vis_robustness(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    nodes=tissue_grid(w,h,11,5,74)
    q=ease(u)
    wound_x=lerp(w*.20,w*.55,smoothstep(.05,.35,u))
    for i,(x,y) in enumerate(nodes):
        damaged=abs(x-wound_x)<55 and .20<u<.65
        if damaged:
            continue
        draw_cell(d,x,y,10,CYAN,170,55)
    # signal reroutes
    if q>.32:
        paths=[
            [(w*.18,h*.28),(w*.42,h*.22),(w*.64,h*.28),(w*.82,h*.30)],
            [(w*.18,h*.52),(w*.40,h*.60),(w*.65,h*.53),(w*.82,h*.50)],
        ]
        for pts in paths:
            glow_line(im,partial(pts,(q-.32)/.68),GOLD,4,180,11)
    seal(im,"NETWORKS CAN PRESERVE STATE THROUGH DAMAGE",
         "distributed information is harder to erase than one local signal")

def vis_channelopathy(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.30,h*.40); right=(w*.70,h*.40)
    q=ease(u)
    draw_cell(d,*left,110,CYAN,190,60)
    membrane_channels(d,*left,110,t,160)
    draw_cell(d,*right,110,CRIMSON,190,60)
    # locked channels
    for i in range(12):
        a=i*math.tau/12
        x1=right[0]+math.cos(a)*92
        y1=right[1]+math.sin(a)*92
        x2=right[0]+math.cos(a)*134
        y2=right[1]+math.sin(a)*134
        d.line((x1,y1,x2,y2),fill=(*CRIMSON,170),width=5)
        d.line((x1-5,y1-5,x2+5,y2+5),fill=(*INK,110),width=2)
    centered(d,(left[0],h*.67),"COHERENT STATE",font(FONT_SANS_BOLD,15),CYAN)
    centered(d,(right[0],h*.67),"ALTERED CHANNEL LOGIC",font(FONT_SANS_BOLD,15),CRIMSON)
    seal(im,"CHANNEL DEFECTS CAN BECOME ANATOMICAL DEFECTS",
         "molecular gates participate in body-scale patterning")

def vis_cancer_voltage(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    nodes=tissue_grid(w,h,11,6,82)
    cx,cy=w*.58,h*.42
    q=ease(u)
    for x,y in nodes:
        dist=math.dist((x,y),(cx,cy))
        col=CRIMSON if dist<85*q else CYAN
        draw_cell(d,x,y,10,col,170,55)
    if q>.40:
        for rr in range(30,120,22):
            d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),
                      outline=(*CRIMSON,int(80*q*(1-rr/140))),width=3)
    seal(im,"CANCER CAN INVOLVE LOSS OF ELECTRICAL INTEGRATION",
         "cells defect from the physiological state of the tissue",CRIMSON)

def vis_normalize(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    nodes=tissue_grid(w,h,11,6,82)
    cx,cy=w*.58,h*.42
    q=ease(u)
    for x,y in nodes:
        dist=math.dist((x,y),(cx,cy))
        base=CRIMSON if dist<85 else CYAN
        col=mix(base,CYAN,q)
        draw_cell(d,x,y,10,col,170,55)
    wave=voltage_wave(w*.50,h*.41,w*.70,h*.045,t)
    glow_line(im,partial(wave,q),CYAN,5,205,13)
    seal(im,"RESTORING PHYSIOLOGICAL CONTEXT CAN CHANGE CELL BEHAVIOR",
         "the intervention can target communication, not only destruction",GREEN)

def vis_neural_somatic(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.40); right=(w*.72,h*.40)
    q=ease(u)
    # nerve network
    rng=random.Random(17)
    for center,col in [(left,VIOLET),(right,CYAN)]:
        nodes=[]
        for i in range(22):
            a=rng.random()*math.tau
            r=rng.uniform(20,120)
            nodes.append((center[0]+math.cos(a)*r,center[1]+math.sin(a)*r*.70))
        for i,(x,y) in enumerate(nodes):
            d.ellipse((x-5,y-5,x+5,y+5),fill=(*col,160))
            if i:
                px,py=nodes[i-1]
                d.line((px,py,x,y),fill=(*col,80),width=2)
    centered(d,(left[0],h*.67),"NEURAL ELECTRICITY",font(FONT_SANS_BOLD,15),VIOLET)
    centered(d,(right[0],h*.67),"SOMATIC ELECTRICITY",font(FONT_SANS_BOLD,15),CYAN)
    glow_line(im,partial([left,(w*.50,h*.23),right],q),GOLD,4,180,11)
    seal(im,"BRAIN AND BODY USE RELATED ELECTRICAL LOGIC",
         "one navigates behavior; the other helps navigate anatomical space")

def vis_code_not_map(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.40); right=(w*.72,h*.40)
    q=ease(u)
    # literal image
    d.rounded_rectangle((left[0]-135,left[1]-105,left[0]+135,left[1]+105),
                        radius=18,fill=(*PALE_SILVER,150),
                        outline=(*INK,150),width=3)
    centered(d,(left[0],left[1]),"TINY PICTURE",
             font(FONT_SERIF_BOLD,25),CRIMSON)
    if q>.35:
        d.line((left[0]-95,left[1]-70,left[0]+95,left[1]+70),
               fill=(*CRIMSON,210),width=5)
        d.line((left[0]+95,left[1]-70,left[0]-95,left[1]+70),
               fill=(*CRIMSON,210),width=5)
    # state code
    nodes=tissue_grid(w,h,5,4,93)
    for x,y in nodes:
        xx=right[0]+(x-w*.50)*.52
        yy=right[1]+(y-h*.40)*.72
        draw_cell(d,xx,yy,9,CYAN,170,55)
    glow_line(im,voltage_wave(right[0],right[1],w*.24,h*.035,t),
              GOLD,4,190,11)
    seal(im,"THE BIOELECTRIC CODE IS NOT A MINIATURE ANATOMICAL IMAGE",
         "distributed physiological states constrain what cells build")

def vis_bowtie(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    left_points=[(w*.12,h*(.20+i*.09)) for i in range(6)]
    center=(w*.50,h*.40)
    right_points=[(w*.88,h*(.20+i*.09)) for i in range(6)]
    for i,p0 in enumerate(left_points):
        glow_circle(im,*p0,8,[CYAN,VIOLET,GREEN][i%3],135,7)
        glow_line(im,partial([p0,center],q),CYAN,2,110,7)
    glow_circle(im,*center,18,GOLD,180,11)
    for i,p1 in enumerate(right_points):
        glow_line(im,partial([center,p1],q),GOLD,2,110,7)
        glow_circle(im,*p1,8,[GREEN,CRIMSON,CYAN][i%3],135,7)
    seal(im,"MANY SIGNALS PASS THROUGH SHARED CONTROL BOTTLENECKS",
         "compact physiological states can coordinate diverse downstream actions")

def vis_multiscale_dialogue(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    levels=[
        ("CHANNEL",w*.16,18,CYAN),
        ("CELL",w*.34,31,GREEN),
        ("TISSUE",w*.54,50,GOLD),
        ("ORGAN",w*.75,73,VIOLET),
        ("BODY",w*.91,95,CRIMSON),
    ]
    q=ease(u)
    for i,(lab,x,r,col) in enumerate(levels):
        local=clamp(q*len(levels)-i)
        glow_circle(im,x,h*.40,r*local,col,int(120+90*local),11)
        centered(d,(x,h*.68),lab,font(FONT_SANS_BOLD,13),col)
        if i<len(levels)-1:
            arrow(d,(x+r+6,h*.40),
                  (levels[i+1][1]-levels[i+1][2]-6,h*.40),
                  (*SILVER,int(145*local)),2,7)
    seal(im,"CONTROL FLOWS ACROSS SCALES",
         "molecules alter cells; tissue states constrain molecular choices")

def vis_electroceutical(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.24,h*.40); right=(w*.76,h*.40)
    q=ease(u)
    # malformed field
    nodes=tissue_grid(w,h,5,5,105)
    for x,y in nodes:
        xx=left[0]+(x-w*.50)*.50
        yy=left[1]+(y-h*.40)*.75
        draw_cell(d,xx,yy,8,CRIMSON,160,50)
    # intervention pulse
    path=[left,(w*.50,h*.22),right]
    glow_line(im,partial(path,q),CYAN,5,210,13)
    # normalized field
    for x,y in nodes:
        xx=right[0]+(x-w*.50)*.50
        yy=right[1]+(y-h*.40)*.75
        draw_cell(d,xx,yy,8,mix(CRIMSON,CYAN,q),160,50)
    centered(d,(left[0],h*.67),"PATHOLOGICAL STATE",
             font(FONT_SANS_BOLD,14),CRIMSON)
    centered(d,(right[0],h*.67),"REWRITTEN STATE",
             font(FONT_SANS_BOLD,14),GREEN)
    seal(im,"ELECTROCEUTICALS AIM TO EDIT CONTROL STATE",
         "change the patterning conversation rather than place every cell")

def vis_anatomy_from_field(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    nodes=tissue_grid(w,h,12,5,116)
    for x,y in nodes:
        draw_cell(d,x,y,8,CYAN,135,45)
    glow_line(im,voltage_wave(cx,cy,w*.66,h*.045,t),
              CYAN,5,190,13)
    if q>.42:
        # organ contour emerges
        alpha=int(210*(q-.42)/.58)
        d.ellipse((cx-190,cy-105,cx+190,cy+105),
                  outline=(*GOLD,alpha),width=5)
        d.line((cx-70,cy-20,cx,cy+45,cx+85,cy-25),
               fill=(*GREEN,alpha),width=5)
    seal(im,"PHYSIOLOGICAL ORDER BECOMES MATERIAL FORM",
         "distributed state is translated into anatomy")

def vis_caution(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    claims=[
        ("VOLTAGE PATTERNS INSTRUCT MORPHOGENESIS","SUPPORTED",GREEN),
        ("BIOELECTRICITY ACTS ALONE","FALSE",CRIMSON),
        ("NETWORK STATES CAN STORE INFORMATION","SUPPORTED",CYAN),
        ("TISSUE VOLTAGE = HUMAN THOUGHT","NOT ESTABLISHED",CRIMSON),
    ]
    q=ease(u)
    for i,(claim,status,col) in enumerate(claims):
        local=clamp(q*len(claims)-i)
        y=h*(.23+i*.13)
        d.rounded_rectangle((w*.14,y-28,w*.86,y+28),
                            radius=14,
                            fill=(*mix(WHITE,col,.10),int(220*local)),
                            outline=(*col,int(180*local)),width=2)
        centered(d,(w*.39,y),claim,font(FONT_SANS_BOLD,14),INK)
        centered(d,(w*.74,y),status,font(FONT_SANS_BOLD,14),col)
    seal(im,"KEEP THE ELECTRIC BODY INSIDE BIOLOGY",
         "voltage interacts with genes, chemicals, forces, and environment")

def vis_tantric_bridge(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.30,h*.40); right=(w*.70,h*.40)
    q=ease(u)
    nodes=tissue_grid(w,h,5,4,123)
    for x,y in nodes:
        xx=left[0]+(x-w*.50)*.50
        yy=left[1]+(y-h*.40)*.72
        draw_cell(d,xx,yy,8,CYAN,155,45)
    glow_line(im,voltage_wave(left[0],left[1],w*.22,h*.03,t),
              CYAN,4,180,11)
    for rr in range(35,155,28):
        d.ellipse((right[0]-rr,right[1]-rr*.60,
                   right[0]+rr,right[1]+rr*.60),
                  outline=(*GOLD,int(85*q*(1-rr/180))),width=3)
    centered(d,(left[0],h*.67),"DISTRIBUTED PHYSIOLOGICAL STATE",
             font(FONT_SANS_BOLD,14),CYAN)
    centered(d,(right[0],h*.67),"LUMINOUS MANIFESTATION",
             font(FONT_SANS_BOLD,14),GOLD)
    glow_line(im,partial([left,(w*.50,h*.20),right],q),
              VIOLET,4,180,11)
    seal(im,"BIOELECTRICITY EXPLAINS COORDINATION, NOT CONSCIOUSNESS ITSELF",
         "the scientific and Tantric questions remain distinct")

def vis_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    nodes=tissue_grid(w,h,12,6,140)
    for x,y in nodes:
        draw_cell(d,x,y,8,CYAN,145,45)
    wave=voltage_wave(cx,cy,w*.72,h*.05,t)
    glow_line(im,partial(wave,q),CYAN,5,210,14)
    if q>.45:
        alpha=int(210*(q-.45)/.55)
        d.ellipse((cx-230,cy-135,cx+230,cy+135),
                  outline=(*GOLD,alpha),width=5)
    if q>.72:
        centered(d,(cx,h*.69),"V_MEM → FORM",
                 font(FONT_SERIF_BOLD,29),GOLD)
    seal(im,"THE BODY IS AN ELECTRICAL SOCIETY",
         "cells negotiate physiological state until distributed signals become anatomy",GOLD)


VISUALS: dict[str,Callable] = {
    "membrane":vis_single_membrane,
    "slow":vis_voltage_not_spike,
    "channels":vis_channels_write,
    "junctions":vis_gap_social,
    "consensus":vis_consensus,
    "attractor":vis_attractor,
    "memory":vis_pattern_memory,
    "embryo":vis_embryo_prepattern,
    "translate":vis_voltage_to_gene,
    "decisions":vis_growth_decisions,
    "eye":vis_eye_induction,
    "polarity":vis_polarity,
    "robust":vis_robustness,
    "channelopathy":vis_channelopathy,
    "cancer":vis_cancer_voltage,
    "normalize":vis_normalize,
    "neural":vis_neural_somatic,
    "code":vis_code_not_map,
    "bowtie":vis_bowtie,
    "scales":vis_multiscale_dialogue,
    "electro":vis_electroceutical,
    "anatomy":vis_anatomy_from_field,
    "caution":vis_caution,
    "bridge":vis_tantric_bridge,
    "final":vis_final,
}


# =============================================================================
# FILM-FIRST ESSAY
# =============================================================================

@dataclass
class Scene:
    title:str
    narration:str
    duration:float
    visual:str
    params:dict


SCENES = [
    Scene("First voltage",
          "The moment life enclosed itself in a membrane, electricity became unavoidable.",
          8.5,"membrane",{}),
    Scene("Separated charge",
          "Inside and outside no longer contained the same ions in the same proportions.",
          8.5,"membrane",{}),
    Scene("Cellular voltage",
          "Every living cell became a tiny electrical object.",
          7.0,"membrane",{}),

    Scene("Beyond nerves",
          "We usually notice electricity only when nerves fire or muscles contract.",
          8.5,"slow",{}),
    Scene("Older current",
          "But membrane potential is far older than brains.",
          7.0,"slow",{}),
    Scene("Slow states",
          "Non-neural cells use slower electrical states to regulate growth, identity, polarity, and repair.",
          9.5,"slow",{}),

    Scene("Channels",
          "Ion channels are molecular gates in the membrane.",
          7.0,"channels",{}),
    Scene("Open and close",
          "Open one set of channels and charge moves. Close another and the voltage settles somewhere else.",
          9.5,"channels",{}),
    Scene("Write state",
          "A small molecular gate can rewrite the physiological state of an entire cell.",
          9.0,"channels",{}),

    Scene("Pumps",
          "Ion pumps spend energy to maintain differences that diffusion would erase.",
          8.5,"membrane",{}),
    Scene("Living inequality",
          "The cell remains alive by continually recreating electrical inequality.",
          8.5,"membrane",{}),
    Scene("State variable",
          "Voltage becomes a compact state variable integrating many molecular processes at once.",
          9.5,"channels",{}),

    Scene("Gap junction",
          "Then cells open direct channels to one another.",
          7.5,"junctions",{}),
    Scene("Social voltage",
          "Through gap junctions, ions and small signals pass from cell to cell.",
          8.0,"junctions",{}),
    Scene("One network",
          "Neighboring voltages become mutually relevant. Separate cells enter one physiological network.",
          9.5,"junctions",{}),

    Scene("Consensus",
          "Coupled cells can settle into a collective electrical state.",
          8.0,"consensus",{}),
    Scene("Not average",
          "The result is not merely an average of isolated voltages.",
          7.5,"consensus",{}),
    Scene("Network decision",
          "The topology of coupling changes which stable states the tissue can occupy.",
          9.0,"consensus",{}),

    Scene("Attractors",
          "Like neural circuits, non-neural bioelectric networks can have attractors.",
          9.0,"attractor",{}),
    Scene("Brief input",
          "A brief input pushes the tissue across a threshold.",
          7.5,"attractor",{}),
    Scene("Persistent state",
          "The input disappears, but the new network state remains.",
          8.0,"attractor",{}),

    Scene("Memory",
          "This is a minimal form of memory.",
          6.5,"memory",{}),
    Scene("Not recollection",
          "The tissue does not need to recollect an image.",
          7.0,"memory",{}),
    Scene("Future altered",
          "Its past survives as a persistent state that changes what it builds next.",
          8.5,"memory",{}),

    Scene("Embryo",
          "Before an embryo has organs, it already has physiological asymmetries.",
          9.0,"embryo",{}),
    Scene("Axes",
          "Voltage differences can help establish left and right, head and tail, center and edge.",
          9.5,"embryo",{}),
    Scene("Prepattern",
          "An electrical prepattern can precede the anatomy it helps organize.",
          8.0,"embryo",{}),

    Scene("Translation",
          "Voltage does not become anatomy by magic.",
          7.0,"translate",{}),
    Scene("Gene expression",
          "Electrical state changes calcium, neurotransmitter transport, second messengers, chromatin, and gene expression.",
          10.0,"translate",{}),
    Scene("Mechanical action",
          "Genes and signaling pathways alter proliferation, migration, differentiation, adhesion, and force.",
          10.0,"translate",{}),
    Scene("Interface",
          "Bioelectricity is an interface between distributed physiology and material construction.",
          9.0,"translate",{}),

    Scene("Decisions",
          "Every cell must decide what to do next.",
          7.0,"decisions",{}),
    Scene("Move",
          "Move.",
          5.0,"decisions",{}),
    Scene("Divide",
          "Divide.",
          5.0,"decisions",{}),
    Scene("Differentiate",
          "Become another kind of cell.",
          6.0,"decisions",{}),
    Scene("Collective bias",
          "Tissue-scale voltage patterns bias these local decisions toward a larger anatomical result.",
          9.5,"decisions",{}),

    Scene("Organ program",
          "In experimental systems, local bioelectric states can initiate complex organ programs.",
          9.0,"eye",{}),
    Scene("Eye field",
          "A region of tissue can be induced toward eye formation by changing upstream physiological cues.",
          9.5,"eye",{}),
    Scene("Complex downstream",
          "The electrical intervention does not manually position every retinal cell.",
          8.0,"eye",{}),
    Scene("Recruit program",
          "It recruits a deeply competent developmental program.",
          8.0,"eye",{}),

    Scene("Polarity",
          "Regeneration requires direction.",
          6.5,"polarity",{}),
    Scene("Which end",
          "A wound must determine which structures belong at this end of the fragment.",
          8.5,"polarity",{}),
    Scene("Electrical axis",
          "Bioelectric gradients participate in the tissue's representation of anatomical polarity.",
          9.0,"polarity",{}),

    Scene("Robustness",
          "A useful patterning system must survive noise and damage.",
          8.0,"robust",{}),
    Scene("Rerouting",
          "Distributed networks can reroute signals when local connections fail.",
          8.5,"robust",{}),
    Scene("State survives",
          "The collective state can remain legible even when individual cells are replaced.",
          9.0,"robust",{}),

    Scene("Channelopathy",
          "Change an ion channel and the effect may exceed one cell's physiology.",
          8.0,"channelopathy",{}),
    Scene("Anatomical consequence",
          "Because channels alter network state, molecular defects can become organ-level pattern defects.",
          9.5,"channelopathy",{}),
    Scene("Scale bridge",
          "A microscopic gate participates in a macroscopic anatomy.",
          8.0,"channelopathy",{}),

    Scene("Cancer",
          "Cancer reveals what happens when cells leave the electrical society.",
          8.5,"cancer",{}),
    Scene("Isolation",
          "Aberrant cells can become electrically isolated from the tissue around them.",
          8.0,"cancer",{}),
    Scene("Local agenda",
          "They continue solving local survival problems while abandoning the patterning goals of the organ.",
          9.5,"cancer",{}),

    Scene("Normalization",
          "This suggests an alternative to treating every abnormal cell only as an enemy.",
          9.0,"normalize",{}),
    Scene("Restore context",
          "Restore aspects of the physiological context, and behavior may shift toward tissue-level cooperation.",
          9.5,"normalize",{}),
    Scene("Reintegration",
          "The aim can be reintegration, not only destruction.",
          7.5,"normalize",{}),

    Scene("Neural and somatic",
          "Neural and somatic bioelectricity are not identical, but they share deep logic.",
          9.0,"neural",{}),
    Scene("State processing",
          "Both use ion channels, coupling, thresholds, memory, and network dynamics.",
          9.0,"neural",{}),
    Scene("Different spaces",
          "Brains help bodies navigate behavioral space. Somatic networks help cells navigate anatomical space.",
          9.5,"neural",{}),

    Scene("Not a picture",
          "The electrical pattern is not a tiny picture of the future body.",
          8.5,"code",{}),
    Scene("Distributed code",
          "It is a distributed code whose states constrain how cells interpret position and choose action.",
          9.5,"code",{}),
    Scene("Meaning in use",
          "Its meaning lies in what downstream systems do when the network occupies that state.",
          9.0,"code",{}),

    Scene("Bow tie",
          "Many molecular inputs can converge on a smaller number of physiological control states.",
          9.0,"bowtie",{}),
    Scene("Fan out",
          "Those states can then fan out into many transcriptional and mechanical consequences.",
          9.0,"bowtie",{}),
    Scene("Compact interface",
          "This bow-tie architecture makes voltage a powerful control interface.",
          8.5,"bowtie",{}),

    Scene("Across scales",
          "Control moves in both directions across biological scales.",
          8.0,"scales",{}),
    Scene("Bottom up",
          "Channels alter cells. Cells alter tissue.",
          7.0,"scales",{}),
    Scene("Top down",
          "But tissue-level states also constrain which molecular actions remain viable.",
          8.5,"scales",{}),
    Scene("Dialogue",
          "The body is built through dialogue, not one-way command.",
          8.0,"scales",{}),

    Scene("Electroceutical",
          "A future regenerative medicine may communicate with this dialogue.",
          8.5,"electro",{}),
    Scene("Edit state",
          "Instead of placing every cell, an intervention could edit the collective physiological state.",
          9.5,"electro",{}),
    Scene("Recruit repair",
          "The tissue's own competencies would implement the anatomical correction.",
          8.5,"electro",{}),

    Scene("Anatomy emerges",
          "This is the central image.",
          6.0,"anatomy",{}),
    Scene("Field first",
          "A distributed physiological state appears before the finished structure.",
          8.0,"anatomy",{}),
    Scene("Matter follows",
          "Cells read, transform, and act within that state until electrical order becomes material form.",
          10.0,"anatomy",{}),

    Scene("Discipline",
          "But bioelectricity must not become a new mystical fluid.",
          8.0,"caution",{}),
    Scene("One layer",
          "Voltage interacts with genes, chemicals, biomechanics, metabolism, and environment.",
          9.0,"caution",{}),
    Scene("No total theory",
          "It is a powerful control layer, not a complete explanation of life.",
          8.0,"caution",{}),
    Scene("No thought equivalence",
          "And tissue voltage is not automatically equivalent to human thought or experience.",
          8.5,"caution",{}),

    Scene("Tantric bridge",
          "The philosophical comparison begins only after the biology is kept intact.",
          8.5,"bridge",{}),
    Scene("Levin",
          "Levin asks how distributed physiological states coordinate living form.",
          8.0,"bridge",{}),
    Scene("Abhinavagupta",
          "Abhinavagupta asks what it means for state, body, relation, and world to appear within awareness.",
          9.0,"bridge",{}),
    Scene("Different levels",
          "One is a theory of biological coordination. The other is a metaphysics and phenomenology of manifestation.",
          10.0,"bridge",{}),

    Scene("Return",
          "Return to the body.",
          5.5,"final",{}),
    Scene("Not silent matter",
          "It is not silent matter waiting for genes to dictate every move.",
          8.0,"final",{}),
    Scene("Conversation",
          "It is a society of electrically active cells negotiating physiological state.",
          8.5,"final",{}),
    Scene("Form",
          "Those negotiations enter genes, forces, movements, and differentiation until a body takes shape.",
          10.0,"final",{}),
    Scene("Closing",
          "The body is an electrical society: billions of membranes, linked by living currents, continuously deciding what kind of whole they are becoming.",
          10.0,"final",{}),
]


# =============================================================================
# PIPELINE
# =============================================================================

def render_frame(scene,frame_index,frame_count,width,height,seed):
    u=frame_index/max(1,frame_count-1)
    t=u*scene.duration
    im=field(width,height,seed)
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
        samples=[0,int(count*.33),int(count*.72),count-1]
        for output_index,frame_index in enumerate(samples):
            render_frame(
                scene,frame_index,count,width,height,index*10000+frame_index
            ).save(frame_dir/f"preview_{output_index:02d}.jpg",quality=95)
        return frame_dir

    for frame_index in range(count):
        p=frame_dir/f"{frame_index:05d}.jpg"
        if p.exists():
            continue
        render_frame(
            scene,frame_index,count,width,height,index*10000+frame_index
        ).save(p,quality=95,subsampling=0)

    return encode_scene(index,fps)

def concatenate(paths):
    concat_file=OUTPUT/"concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in paths),
        encoding="utf-8"
    )
    output=OUTPUT/"body_electrical_society.mp4"
    subprocess.run([
        ffmpeg_path(),"-y",
        "-f","concat","-safe","0",
        "-i",str(concat_file),
        "-c","copy",
        "-movflags","+faststart",
        str(output),
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return output

def export_timeline():
    cursor=0.0
    records=[]
    for index,scene in enumerate(SCENES,1):
        record=asdict(scene)
        record["scene_id"]=f"scene_{index:03d}"
        record["start_seconds"]=round(cursor,3)
        cursor+=scene.duration
        record["end_seconds"]=round(cursor,3)
        records.append(record)

    path=OUTPUT/"narration_timeline.json"
    path.write_text(json.dumps({
        "title":"the body is an electrical society",
        "scene_count":len(SCENES),
        "runtime_seconds":round(cursor,3),
        "shot_duration_range":[5,10],
        "continuity_object":"cyan voltage wave becoming gold anatomical contour",
        "scientific_scope":"developmental bioelectricity and morphogenesis",
        "scenes":records,
    },indent=2,ensure_ascii=False),encoding="utf-8")
    return path

def make_contact_sheet(width,height):
    tw=320
    th=int(tw*height/width)
    cols=4
    rows=math.ceil(len(SCENES)/cols)
    cell_h=th+48
    sheet=Image.new("RGB",(cols*tw,rows*cell_h),IVORY)
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
        d.text((x+8,y+th+7),f"{index:02d}  {scene.title}",font=lf,fill=INK)

    path=OUTPUT/"contact_sheet.jpg"
    sheet.save(path,quality=94)
    return path

def parse_args():
    parser=argparse.ArgumentParser()
    parser.add_argument("--fps",type=int,default=DEFAULT_FPS)
    parser.add_argument("--width",type=int,default=DEFAULT_WIDTH)
    parser.add_argument("--height",type=int,default=DEFAULT_HEIGHT)
    parser.add_argument("--scene",type=int)
    parser.add_argument("--preview",action="store_true")
    parser.add_argument("--no-contact-sheet",action="store_true")
    return parser.parse_args()

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
            index,scene,args.fps,args.width,args.height,args.preview
        )
        if not args.preview:
            rendered.append(result)

    if not args.no_contact_sheet:
        print(f"Contact sheet: {make_contact_sheet(args.width,args.height)}")

    if not args.preview:
        print(f"Final video: {concatenate(rendered)}")


if __name__=="__main__":
    main()
