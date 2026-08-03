#!/usr/bin/env python3
"""
THE MIRROR AND THE OVERFLOW
Plotinus and Abhinavagupta on Why the One Becomes Many

An original Platinum-house procedural visual essay.

CENTRAL QUESTION
----------------
How can an ultimate unity appear as a world of finite, changing things?

Plotinus and Abhinavagupta offer two of the most sophisticated nondual answers:

PLOTINUS
• The One is beyond being and thought.
• Intellect proceeds from the One and contains the Forms.
• Soul proceeds from Intellect and unfolds intelligible order into time and life.
• Multiplicity is real as dependent image, but ontologically diminished.
• Liberation is inward ascent toward the undivided source.

ABHINAVAGUPTA
• Śiva is self-luminous consciousness: prakāśa.
• Consciousness is inseparable from reflexive self-apprehension: vimarśa.
• Śakti is the freedom by which consciousness manifests difference within itself.
• The world is a real ābhāsa—an appearance of consciousness, not a fall outside it.
• Bondage is contracted recognition; liberation is pratyabhijñā, recognition of
  finite experience as Śiva's own activity.

FILM THESIS
-----------
Plotinus imagines the world through overflow:
the source remains transcendent while reality proceeds in descending articulation.

Abhinavagupta imagines the world through a mirror:
consciousness freely presents itself as subject, object, and act of knowing.

Both deny that the Absolute is one object among others.
Both explain plurality without crude creation from external material.
Both treat liberation as return to what was always most fundamental.

Their decisive disagreement concerns manifestation:

Is multiplicity an increasingly faint image of the source?
Or is multiplicity the source's own free self-display?

The film does not force a final verdict.
It lets the two visual systems test one another.

HOUSE RULES
-----------
• Every shot lasts 5–10 seconds.
• Every shot performs a visible transformation.
• Clean ivory gallery/scientific field.
• No slideshow compositions.
• Sparse labels only.
• Mature frame near u=0.72.
• Plotinus motif: gold overflow descending through violet, cyan, and green.
• Abhinava motif: gold mirror-field folding into subject/object while remaining whole.
• Final synthesis motif: vertical procession crossed by horizontal recognition.

OUTPUT
------
output_mirror_overflow/
  frames/
  scenes/
  mirror_and_overflow.mp4
  narration_timeline.json
  contact_sheet.jpg
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
OUTPUT = ROOT / "output_mirror_overflow"
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
    halo=np.exp(-(((xx-w*.5)/(w*.37))**2+((yy-h*.40)/(h*.31))**2)*2)
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

def radial_points(cx,cy,r,count=160,turns=1.8,phase=0):
    pts=[]
    for i in range(count):
        q=i/(count-1)
        a=q*math.tau*turns+phase
        rr=r*(.15+.85*q)
        pts.append((cx+math.cos(a)*rr,cy+math.sin(a)*rr*.62))
    return pts

def draw_world(d,cx,cy,r,color=CYAN,alpha=200):
    d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(*color,alpha),width=4)
    d.arc((cx-r*.75,cy-r,cx+r*.75,cy+r),90,270,fill=(*color,alpha),width=2)
    d.arc((cx-r*.75,cy-r,cx+r*.75,cy+r),-90,90,fill=(*color,alpha),width=2)
    d.line((cx-r,cy,cx+r,cy),fill=(*color,alpha),width=2)

def vis_question(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    glow_circle(im,cx,cy,18,GOLD,190,12)
    for i in range(32):
        a=i*math.tau/32
        r=lerp(20,240,q)
        x=cx+math.cos(a)*r; y=cy+math.sin(a)*r*.62
        glow_circle(im,x,y,5,[VIOLET,CYAN,GREEN][i%3],110,5)
    seal(im,"HOW CAN THE ONE APPEAR AS MANY?",
         "without dividing into pieces or meeting external material",GOLD)

def vis_plotinus_one(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    glow_circle(im,cx,cy,17,GOLD,190,13)
    for rr in range(35,290,32):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(88*q*(1-rr/320))),width=3)
    centered(d,(cx,h*.68),"BEYOND BEING · BEYOND THOUGHT",
             font(FONT_SERIF_BOLD,24),GOLD)
    seal(im,"PLOTINUS BEGINS ABOVE INTELLIGIBILITY",
         "the first principle cannot itself be a complex act of thinking")

def vis_abhinava_light(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    light=smoothstep(.05,.46,u)
    reflect=smoothstep(.36,.90,u)
    for rr in range(35,250,32):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(88*light*(1-rr/280))),width=3)
    glow_line(im,partial(radial_points(cx,cy,w*.22,160,1.7,t*.2),reflect),
              CYAN,5,int(120+95*reflect),13)
    centered(d,(w*.28,h*.69),"PRAKĀŚA",font(FONT_SERIF_BOLD,26),GOLD)
    centered(d,(w*.72,h*.69),"VIMARŚA",font(FONT_SERIF_BOLD,26),CYAN)
    seal(im,"ABHINAVAGUPTA BEGINS WITH SELF-LUMINOUS CONSCIOUSNESS",
         "light inseparable from its power to apprehend itself")

def vis_plotinus_procession(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx=w*.50; q=ease(u)
    levels=[
        ("ONE",h*.16,GOLD,18),
        ("INTELLECT",h*.31,VIOLET,48),
        ("SOUL",h*.48,CYAN,78),
        ("NATURE",h*.66,GREEN,110),
    ]
    for i,(lab,y,col,r) in enumerate(levels):
        local=clamp(q*len(levels)-i)
        d.ellipse((cx-r*local,y-r*.35*local,cx+r*local,y+r*.35*local),
                  outline=(*col,int(190*local)),width=4)
        if local>.5:
            centered(d,(cx,y),lab,font(FONT_SANS_BOLD,14),col)
        if i<len(levels)-1:
            arrow(d,(cx,y+r*.36),(cx,levels[i+1][1]-levels[i+1][3]*.36),
                  (*SILVER,int(145*local)),3,8)
    seal(im,"PROCESSION DESCENDS THROUGH ARTICULATED LEVELS",
         "each effect expresses its source with greater multiplicity")

def vis_abhinava_manifestation(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    glow_circle(im,cx,cy,16,GOLD,185,12)
    labels=[
        ("SUBJECT",CYAN,-190,-70),
        ("OBJECT",VIOLET,190,-70),
        ("KNOWING",GREEN,0,145),
    ]
    for i,(lab,col,ox,oy) in enumerate(labels):
        local=clamp(q*len(labels)-i)
        x=lerp(cx,cx+ox,local); y=lerp(cy,cy+oy,local)
        glow_circle(im,x,y,13,col,160,10)
        centered(d,(x,y+30),lab,font(FONT_SANS_BOLD,14),col)
        glow_line(im,[(cx,cy),(x,y)],GOLD,3,int(145*local),9)
    seal(im,"CONSCIOUSNESS POLARIZES WITHIN ITSELF",
         "knower, known, and knowing remain one luminous event")

def vis_overflow(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    source=(w*.28,h*.40); q=ease(u)
    glow_circle(im,*source,20,GOLD,190,13)
    streams=[]
    for k,col in enumerate([VIOLET,CYAN,GREEN]):
        pts=[]
        for i in range(120):
            x=lerp(source[0],w*.84,i/119)
            y=source[1]+math.sin(i*.08+k*1.7+t*.2)*(25+22*k)
            pts.append((x,y))
        streams.append((pts,col))
    for pts,col in streams:
        glow_line(im,partial(pts,q),col,4,175,11)
    seal(im,"PLOTINIAN CAUSATION IS OVERFLOW",
         "the source remains while a derived activity proceeds from it")

def vis_mirror(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    d.ellipse((cx-200,cy-225,cx+200,cy+225),
              fill=(*PALE_SILVER,90),outline=(*CYAN,180),width=5)
    objects=[(cx-105,cy-65,GOLD),(cx+95,cy-55,VIOLET),(cx,cy+105,GREEN)]
    for i,(x,y,col) in enumerate(objects):
        local=clamp(q*3-i)
        glow_circle(im,x,y,18,col,int(150+50*local),11)
        d.line((x,y,cx,cy),fill=(*col,int(80*local)),width=2)
    for rr in range(40,200,30):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(55*q*(1-rr/225))),width=2)
    seal(im,"ŚAIVA MANIFESTATION IS A SELF-DISPLAYING MIRROR",
         "the images are not outside the consciousness that presents them")

def vis_diminution(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    ys=[h*.18,h*.33,h*.49,h*.65]
    cols=[GOLD,VIOLET,CYAN,SILVER]
    rs=[22,45,75,105]
    for i,(y,col,r) in enumerate(zip(ys,cols,rs)):
        alpha=int(220*(1-i*.18))
        d.ellipse((w*.50-r,y-r*.30,w*.50+r,y+r*.30),
                  outline=(*col,alpha),width=4)
        if i<len(ys)-1:
            arrow(d,(w*.50,y+r*.32),(w*.50,ys[i+1]-rs[i+1]*.32),
                  (*SILVER,130),3,8)
    gl=layer(im.size)
    ImageDraw.Draw(gl).rectangle((w*.16,h*.15,w*.84,h*.70),
                                 fill=(*CRIMSON,int(32*q)))
    im.alpha_composite(gl)
    seal(im,"FOR PLOTINUS, PROCESSION MEANS DIMINISHED UNITY",
         "the sensible world is beautiful, real, and ontologically dependent")

def vis_freedom(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    glow_circle(im,cx,cy,16,GOLD,185,12)
    petals=[]
    for i in range(12):
        a=i*math.tau/12
        r=lerp(20,190,q)
        x=cx+math.cos(a)*r; y=cy+math.sin(a)*r*.62
        petals.append((x,y))
        d.ellipse((x-28,y-18,x+28,y+18),
                  outline=(*[CYAN,VIOLET,GREEN][i%3],int(175*q)),width=3)
    for p0 in petals:
        d.line((cx,cy,*p0),fill=(*GOLD,int(95*q)),width=2)
    seal(im,"FOR ABHINAVAGUPTA, MANIFESTATION IS FREEDOM",
         "difference is consciousness exercising svātantrya")

def vis_world_status(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.30,h*.40); right=(w*.70,h*.40); q=ease(u)
    draw_world(d,*left,95,VIOLET,190)
    draw_world(d,*right,95,GOLD,190)
    centered(d,(left[0],h*.67),"DEPENDENT IMAGE",font(FONT_SERIF_BOLD,22),VIOLET)
    centered(d,(right[0],h*.67),"REAL ĀBHĀSA",font(FONT_SERIF_BOLD,22),GOLD)
    glow_line(im,partial([left,(w*.50,h*.20),right],q),CYAN,4,175,11)
    seal(im,"BOTH AFFIRM THE WORLD · THEY VALUE ITS STATUS DIFFERENTLY",
         "image of intelligible order versus free appearance of consciousness")

def vis_matter(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx=w*.50; q=ease(u)
    # form drains toward indeterminacy
    for i in range(7):
        y=h*.18+i*h*.075
        width=lerp(90,270,i/6)
        col=mix(GOLD,INK,i/6)
        d.ellipse((cx-width,y-24,cx+width,y+24),
                  outline=(*col,int(190-15*i)),width=3)
    if q>.55:
        gl=layer(im.size)
        ImageDraw.Draw(gl).rectangle((w*.12,h*.59,w*.88,h*.70),
                                     fill=(*INK,int(70*q)))
        im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(12)))
    seal(im,"PLOTINIAN MATTER MARKS THE LIMIT OF FORM",
         "maximum indeterminacy at the edge of intelligibility")

def vis_contraction(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    draw_world(d,cx,cy,lerp(220,95,q),CYAN,190)
    labels=["TIME","SPACE","CAUSALITY","LIMITED KNOWING"]
    for i,lab in enumerate(labels):
        a=i*math.tau/4-math.pi/2
        r=lerp(235,120,q)
        x=cx+math.cos(a)*r; y=cy+math.sin(a)*r*.62
        centered(d,(x,y),lab,font(FONT_SANS_BOLD,13),CRIMSON)
    glow_circle(im,cx,cy,14,GOLD,170,10)
    seal(im,"ŚAIVA BONDAGE IS CONTRACTION, NOT EXILE FROM CONSCIOUSNESS",
         "the infinite subject adopts a finite standpoint")

def vis_desire_compare(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.40); right=(w*.72,h*.40); q=ease(u)
    glow_circle(im,*left,15,VIOLET,170,10)
    glow_circle(im,*right,15,CYAN,170,10)
    targets=[(w*.50,h*.20,GOLD),(w*.50,h*.58,CRIMSON)]
    for target in targets:
        glow_circle(im,*target[:2],12,target[2],150,9)
        glow_line(im,partial([left,target[:2],right],q),
                  target[2],3,145,9)
    centered(d,(left[0],h*.68),"SOUL SEEKS ABSENT GOOD",
             font(FONT_SANS_BOLD,14),VIOLET)
    centered(d,(right[0],h*.68),"CONTRACTED WILL SEEKS COMPLETION",
             font(FONT_SANS_BOLD,14),CYAN)
    seal(im,"DESIRE REVEALS FINITUDE IN BOTH SYSTEMS",
         "a limited center is governed by what is not presently possessed")

def vis_ascent(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    x=w*.50; q=ease(u)
    levels=[
        (h*.68,"SENSE",GREEN,105),
        (h*.51,"SOUL",CYAN,78),
        (h*.34,"INTELLECT",VIOLET,48),
        (h*.17,"ONE",GOLD,20),
    ]
    for i,(y,lab,col,r) in enumerate(levels):
        d.ellipse((x-r,y-r*.32,x+r,y+r*.32),outline=(*col,180),width=4)
        centered(d,(x,y),lab,font(FONT_SANS_BOLD,14),col)
        if i<len(levels)-1:
            arrow(d,(x,y-r*.34),(x,levels[i+1][0]+levels[i+1][3]*.34),
                  (*GOLD,int(170*q)),3,8)
    seal(im,"PLOTINIAN LIBERATION IS ASCENT",
         "turn inward, recover Intellect, and pass beyond thought toward the One")

def vis_recognition(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.40); right=(w*.72,h*.40); q=ease(u)
    glow_circle(im,*left,15,CYAN,170,10)
    glow_circle(im,*right,15,VIOLET,170,10)
    glow_line(im,partial([left,(w*.50,h*.22),right],q),GOLD,5,205,13)
    if q>.58:
        for rr in range(35,220,30):
            d.ellipse((w*.50-rr,h*.40-rr*.62,w*.50+rr,h*.40+rr*.62),
                      outline=(*GOLD,int(70*q*(1-rr/245))),width=3)
    centered(d,(w*.50,h*.68),"PRATYABHIJÑĀ",
             font(FONT_SERIF_BOLD,27),GOLD)
    seal(im,"ŚAIVA LIBERATION IS RECOGNITION",
         "the finite knower recognizes its present activity as Śiva")

def vis_return_difference(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.30,h*.40); right=(w*.70,h*.40); q=ease(u)
    # ascent arrow
    arrow(d,(left[0],h*.62),(left[0],h*.20),(*VIOLET,int(190*q)),5,11)
    # recognition circle
    for rr in range(35,150,25):
        d.ellipse((right[0]-rr,right[1]-rr*.62,right[0]+rr,right[1]+rr*.62),
                  outline=(*GOLD,int(80*q*(1-rr/175))),width=3)
    glow_circle(im,*right,14,GOLD,175,10)
    centered(d,(left[0],h*.69),"RETURN UPWARD",font(FONT_SERIF_BOLD,22),VIOLET)
    centered(d,(right[0],h*.69),"RECOGNIZE HERE",font(FONT_SERIF_BOLD,22),GOLD)
    seal(im,"RETURN HAS TWO GEOMETRIES",
         "transcend the lower or see the Absolute within its present appearance")

def vis_body_compare(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.30,h*.40); right=(w*.70,h*.40); q=ease(u)
    # body outlines
    for center,col in [(left,VIOLET),(right,GOLD)]:
        x,y=center
        d.ellipse((x-24,y-115,x+24,y-67),outline=(*col,180),width=4)
        d.line((x,y-67,x,y+55),fill=(*col,180),width=5)
        d.line((x-60,y-35,x+60,y-35),fill=(*col,180),width=4)
        d.line((x,y+55,x-45,y+135),fill=(*col,180),width=4)
        d.line((x,y+55,x+45,y+135),fill=(*col,180),width=4)
    # left upward separation, right body field
    arrow(d,(left[0],left[1]-120),(left[0],h*.17),(*VIOLET,int(180*q)),4,9)
    for rr in range(35,150,25):
        d.ellipse((right[0]-rr,right[1]-rr*.62,right[0]+rr,right[1]+rr*.62),
                  outline=(*GOLD,int(70*q*(1-rr/170))),width=3)
    seal(im,"THE BODY OCCUPIES A DIFFERENT SOTERIOLOGICAL PLACE",
         "vehicle to transcend versus contracted form to divinize")

def vis_aesthetic_bridge(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    # stage -> shared field
    d.rounded_rectangle((w*.18,h*.20,w*.82,h*.61),radius=18,
                        fill=(*PALE_SILVER,100),outline=(*INK,110),width=3)
    figures=[(w*.32,CRIMSON),(w*.50,GOLD),(w*.68,CYAN)]
    for x,col in figures:
        glow_circle(im,x,h*.40,18,col,150,10)
    if q>.4:
        for rr in range(40,240,32):
            d.ellipse((cx-rr,h*.40-rr*.55,cx+rr,h*.40+rr*.55),
                      outline=(*GOLD,int(65*q*(1-rr/270))),width=2)
    seal(im,"BEAUTY TEMPORARILY LOOSENS PRIVATE CONCERN",
         "Plotinian contemplation and Abhinava's rasa both widen the self")

def vis_identity_difference(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    labels=[
        ("IDENTITY",GOLD,-165,-75),
        ("DIFFERENCE",VIOLET,165,-75),
        ("RELATION",CYAN,0,145),
    ]
    for i,(lab,col,ox,oy) in enumerate(labels):
        local=clamp(q*3-i)
        x=cx+ox*local; y=cy+oy*local
        glow_circle(im,x,y,14,col,160,10)
        centered(d,(x,y+30),lab,font(FONT_SANS_BOLD,14),col)
        glow_line(im,[(cx,cy),(x,y)],GOLD,3,int(120*local),8)
    glow_circle(im,cx,cy,15,GOLD,180,11)
    seal(im,"NONDUALITY MUST EXPLAIN BOTH IDENTITY AND DIFFERENCE",
         "erase either pole and experience becomes unintelligible")

def vis_two_maps(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.31,h*.40); right=(w*.69,h*.40); q=ease(u)
    # vertical tree
    ys=[h*.20,h*.33,h*.47,h*.61]
    cols=[GOLD,VIOLET,CYAN,GREEN]
    for i,(y,col) in enumerate(zip(ys,cols)):
        d.ellipse((left[0]-35-i*12,y-14,left[0]+35+i*12,y+14),
                  outline=(*col,180),width=3)
        if i<len(ys)-1:
            d.line((left[0],y+15,left[0],ys[i+1]-15),
                   fill=(*SILVER,130),width=3)
    # horizontal mirror
    glow_circle(im,*right,14,GOLD,180,11)
    for i,col in enumerate([CYAN,VIOLET,GREEN]):
        a=i*math.tau/3-math.pi/2
        x=right[0]+math.cos(a)*110*q
        y=right[1]+math.sin(a)*75*q
        glow_circle(im,x,y,13,col,150,9)
        d.line((*right,x,y),fill=(*GOLD,100),width=2)
    centered(d,(left[0],h*.69),"PROCESSION",font(FONT_SERIF_BOLD,22),VIOLET)
    centered(d,(right[0],h*.69),"SELF-MANIFESTATION",font(FONT_SERIF_BOLD,22),GOLD)
    seal(im,"TWO MAPS OF THE SAME IMPOSSIBLE PROBLEM",
         "how unity can sustain a real world of difference")

def vis_caution(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    rows=[
        ("THE ONE = ŚIVA","TOO SIMPLE",CRIMSON),
        ("INTELLECT = ŚAKTI","PARTIAL ANALOGY",CYAN),
        ("BOTH ARE NONDUAL SYSTEMS","SUPPORTED",GREEN),
        ("THEIR WORLD-VALUATIONS ARE IDENTICAL","FALSE",CRIMSON),
    ]
    q=ease(u)
    for i,(claim,status,col) in enumerate(rows):
        local=clamp(q*len(rows)-i); y=h*(.23+i*.13)
        d.rounded_rectangle((w*.14,y-28,w*.86,y+28),radius=14,
                            fill=(*mix(WHITE,col,.10),int(220*local)),
                            outline=(*col,int(180*local)),width=2)
        centered(d,(w*.39,y),claim,font(FONT_SANS_BOLD,14),INK)
        centered(d,(w*.74,y),status,font(FONT_SANS_BOLD,14),col)
    seal(im,"PARALLEL DOES NOT MEAN IDENTITY",
         "the disagreement is precisely what makes the comparison useful")

def vis_synthesis_cross(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    # vertical procession
    glow_line(im,partial([(cx,h*.15),(cx,h*.68)],q),VIOLET,5,190,12)
    # horizontal manifestation
    glow_line(im,partial([(w*.20,cy),(w*.80,cy)],q),GOLD,5,200,13)
    glow_circle(im,cx,cy,18,GOLD,190,12)
    labels=[
        ("TRANSCENDENCE",cx,h*.14,VIOLET),
        ("EMBODIMENT",cx,h*.70,GREEN),
        ("SUBJECT",w*.18,cy,CYAN),
        ("OBJECT",w*.82,cy,VIOLET),
    ]
    for lab,x,y,col in labels:
        centered(d,(x,y),lab,font(FONT_SANS_BOLD,13),col)
    seal(im,"THE CROSSING QUESTION",
         "can the Absolute remain beyond all things while fully present as each thing?")

def vis_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    # overflow descends
    vertical=[(cx,h*.15),(cx,h*.66)]
    glow_line(im,partial(vertical,q),VIOLET,5,185,12)
    # mirror opens
    for rr in range(35,250,30):
        d.ellipse((cx-rr*q,cy-rr*.62*q,cx+rr*q,cy+rr*.62*q),
                  outline=(*GOLD,int(80*q*(1-rr/280))),width=3)
    glow_circle(im,cx,cy,17,GOLD,190,12)
    if q>.72:
        centered(d,(cx,h*.69),"OVERFLOW · MIRROR · RECOGNITION",
                 font(FONT_SERIF_BOLD,24),GOLD)
    seal(im,"THE MIRROR AND THE OVERFLOW",
         "the One becomes many either as dependent procession or as consciousness freely appearing to itself",GOLD)


VISUALS: dict[str,Callable] = {
    "question":vis_question,
    "plotinus_one":vis_plotinus_one,
    "abhinava_light":vis_abhinava_light,
    "procession":vis_plotinus_procession,
    "manifest":vis_abhinava_manifestation,
    "overflow":vis_overflow,
    "mirror":vis_mirror,
    "diminish":vis_diminution,
    "freedom":vis_freedom,
    "world":vis_world_status,
    "matter":vis_matter,
    "contract":vis_contraction,
    "desire":vis_desire_compare,
    "ascent":vis_ascent,
    "recognition":vis_recognition,
    "return":vis_return_difference,
    "body":vis_body_compare,
    "aesthetic":vis_aesthetic_bridge,
    "identity":vis_identity_difference,
    "maps":vis_two_maps,
    "caution":vis_caution,
    "cross":vis_synthesis_cross,
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
    Scene("Impossible question",
          "How can the One appear as many without breaking into pieces?",
          8.0,"question",{}),
    Scene("Two answers",
          "Plotinus and Abhinavagupta construct two of philosophy's most powerful answers.",
          9.0,"question",{}),

    Scene("Plotinus begins",
          "Plotinus begins by refusing to make the first principle a mind.",
          8.0,"plotinus_one",{}),
    Scene("Beyond thought",
          "Thinking contains thinker, object, and the relation between them. The first principle must be simpler than this multiplicity.",
          10.0,"plotinus_one",{}),
    Scene("The One",
          "He calls it the One or the Good: beyond being, beyond thought, beyond every determinate form.",
          9.0,"plotinus_one",{}),

    Scene("Abhinava begins",
          "Abhinavagupta begins elsewhere.",
          6.5,"abhinava_light",{}),
    Scene("Prakāśa",
          "The ultimate is prakāśa: the power by which anything appears.",
          8.0,"abhinava_light",{}),
    Scene("Vimarśa",
          "But light without self-apprehension would be inert. Consciousness is also vimarśa: awareness of its own appearing.",
          10.0,"abhinava_light",{}),

    Scene("Plotinian architecture",
          "From the One proceeds Intellect.",
          7.0,"procession",{}),
    Scene("Intellect",
          "Intellect contains the Forms as a living unity of thinker and thought.",
          8.5,"procession",{}),
    Scene("Soul",
          "From Intellect proceeds Soul, which unfolds intelligible order into discursive life, desire, movement, and time.",
          10.0,"procession",{}),
    Scene("Nature",
          "Soul's outward activity becomes Nature, the formative order of embodied things.",
          9.0,"procession",{}),

    Scene("Śaiva architecture",
          "Abhinavagupta does not place manifestation outside consciousness.",
          8.5,"manifest",{}),
    Scene("Polarization",
          "Consciousness polarizes within itself as subject, object, and act of knowing.",
          9.0,"manifest",{}),
    Scene("One event",
          "The three are distinguishable without becoming three independent substances.",
          9.0,"manifest",{}),

    Scene("Overflow",
          "Plotinian causation is often imagined as overflow.",
          7.0,"overflow",{}),
    Scene("Source remains",
          "The source remains what it is while an external activity proceeds from it.",
          8.5,"overflow",{}),
    Scene("No decision",
          "The One does not deliberate and choose to manufacture a universe.",
          8.0,"overflow",{}),
    Scene("Necessary fecundity",
          "Its perfection is fecund: what is fullest gives rise to dependent activity.",
          8.5,"overflow",{}),

    Scene("Mirror",
          "Abhinavagupta's better image is the mirror.",
          7.0,"mirror",{}),
    Scene("Images",
          "Countless images appear, yet none leaves the mirror or divides its reflective capacity.",
          9.0,"mirror",{}),
    Scene("Self-display",
          "The world is consciousness presenting its own powers as form.",
          8.5,"mirror",{}),

    Scene("Diminution",
          "Here the systems begin to separate.",
          7.0,"diminish",{}),
    Scene("Plotinian distance",
          "For Plotinus, procession produces increasingly divided and dependent modes of unity.",
          9.0,"diminish",{}),
    Scene("Sensible image",
          "The sensible world is beautiful and real, but it is an image of intelligible order rather than equal to its source.",
          10.0,"diminish",{}),

    Scene("Śaiva freedom",
          "For Abhinavagupta, manifestation expresses svātantrya: absolute freedom.",
          8.5,"freedom",{}),
    Scene("Not compulsion",
          "The world does not spill out because consciousness lacks control.",
          8.0,"freedom",{}),
    Scene("Play",
          "Difference is consciousness freely displaying what it can be.",
          8.0,"freedom",{}),

    Scene("World status",
          "Both philosophers reject the world as independent material standing outside the Absolute.",
          9.5,"world",{}),
    Scene("Plotinian world",
          "For Plotinus, the world is a dependent image ordered by Soul and intelligible Form.",
          9.0,"world",{}),
    Scene("Śaiva world",
          "For Abhinavagupta, the world is a real ābhāsa: a manifestation whose substance is consciousness itself.",
          10.0,"world",{}),

    Scene("Matter",
          "Plotinus places matter at the limit of intelligibility.",
          8.0,"matter",{}),
    Scene("Indeterminacy",
          "Matter is not an equal principle opposed to the One. It is maximal indeterminacy, the faintest terminus of procession.",
          10.0,"matter",{}),

    Scene("Contraction",
          "Abhinavagupta explains finitude through contraction.",
          8.0,"contract",{}),
    Scene("Kañcukas",
          "The unlimited subject adopts limitation through time, space, causality, restricted agency, and restricted knowledge.",
          10.0,"contract",{}),
    Scene("Still consciousness",
          "The finite subject never becomes something other than consciousness. It forgets the scale of its own activity.",
          9.5,"contract",{}),

    Scene("Desire",
          "Both systems understand desire as a mark of finitude.",
          8.0,"desire",{}),
    Scene("Plotinian desire",
          "Plotinian Soul seeks goods not presently possessed: food, knowledge, sleep, reproduction, return.",
          9.5,"desire",{}),
    Scene("Śaiva desire",
          "Śaiva desire is contracted will seeking externally the completeness that remains implicit within consciousness.",
          10.0,"desire",{}),

    Scene("Plotinian liberation",
          "Plotinian liberation has a vertical geometry.",
          7.5,"ascent",{}),
    Scene("Turn inward",
          "Turn away from dispersed identification, recover the undivided activity of Intellect, and rise toward the One.",
          10.0,"ascent",{}),
    Scene("Beyond thought",
          "The final union passes beyond discursive thought and even intellective multiplicity.",
          9.0,"ascent",{}),

    Scene("Śaiva liberation",
          "Śaiva liberation has a geometry of recognition.",
          7.5,"recognition",{}),
    Scene("Not elsewhere",
          "The practitioner need not leave manifestation to find Śiva.",
          8.0,"recognition",{}),
    Scene("Recognition",
          "Pratyabhijñā recognizes the present knower, known object, and act of knowing as Śiva's own activity.",
          10.0,"recognition",{}),

    Scene("Two returns",
          "Return therefore means something different in each system.",
          8.0,"return",{}),
    Scene("Plotinian return",
          "Plotinus returns upward from image to intelligible source.",
          8.0,"return",{}),
    Scene("Śaiva return",
          "Abhinavagupta returns by seeing the source within the image's present appearing.",
          9.0,"return",{}),

    Scene("The body",
          "The difference becomes sharpest in the body.",
          7.0,"body",{}),
    Scene("Plotinian body",
          "Plotinus values embodied cosmic order, yet the highest self remains above the compound living organism.",
          9.5,"body",{}),
    Scene("Tantric body",
          "Abhinavagupta turns body, sensation, breath, desire, ritual, and aesthetic intensity into possible sites of recognition.",
          10.0,"body",{}),

    Scene("Beauty",
          "Yet beauty brings them unexpectedly close.",
          7.0,"aesthetic",{}),
    Scene("Plotinian beauty",
          "For Plotinus, beauty awakens memory of intelligible form and draws the soul upward.",
          9.0,"aesthetic",{}),
    Scene("Rasa",
          "For Abhinavagupta, aesthetic rasa loosens private limitation and reveals a universalized mode of feeling.",
          9.5,"aesthetic",{}),
    Scene("Expanded self",
          "In both, beauty interrupts the small self by revealing a wider order of participation.",
          9.0,"aesthetic",{}),

    Scene("Identity and difference",
          "Every nondual philosophy must solve two problems at once.",
          8.0,"identity",{}),
    Scene("Identity",
          "Explain how everything belongs to one ultimate reality.",
          7.0,"identity",{}),
    Scene("Difference",
          "And explain why differences remain real enough for knowledge, desire, ethics, and liberation.",
          9.0,"identity",{}),
    Scene("Balance",
          "Erase identity and nonduality fails. Erase difference and experience becomes unintelligible.",
          9.0,"identity",{}),

    Scene("Plotinus strength",
          "Plotinus protects transcendence.",
          7.0,"maps",{}),
    Scene("Absolute beyond capture",
          "The source cannot be reduced to any appearance, concept, experience, or cosmic process.",
          9.0,"maps",{}),
    Scene("Abhinava strength",
          "Abhinavagupta protects immanence.",
          7.0,"maps",{}),
    Scene("Nothing outside",
          "No finite experience can fall outside consciousness or become metaphysically alien to it.",
          9.0,"maps",{}),

    Scene("Danger of Plotinus",
          "Plotinus risks making embodiment appear spiritually secondary.",
          8.0,"caution",{}),
    Scene("Danger of Abhinava",
          "Abhinavagupta risks making the language of divine freedom sound as though suffering requires no further explanation.",
          9.0,"caution",{}),
    Scene("Mutual correction",
          "Each system exposes the temptation hidden inside the other.",
          8.0,"caution",{}),

    Scene("No simple equation",
          "The One is not simply Śiva.",
          7.0,"caution",{}),
    Scene("No simple mapping",
          "Intellect is not simply Śakti, and Soul is not simply the tattva system.",
          8.0,"caution",{}),
    Scene("Useful comparison",
          "The comparison is useful because the systems disagree from within a shared demand for nondual explanation.",
          10.0,"caution",{}),

    Scene("Crossing",
          "The deepest synthesis is a question, not a merger.",
          8.0,"cross",{}),
    Scene("Transcendence and presence",
          "Can the Absolute remain beyond every determinate thing while being fully present as the appearing of each thing?",
          10.0,"cross",{}),
    Scene("Two protections",
          "Plotinus says: do not imprison the source within manifestation.",
          8.0,"cross",{}),
    Scene("Second protection",
          "Abhinavagupta says: do not exile manifestation from the source.",
          8.0,"cross",{}),

    Scene("Final map",
          "One gives us the overflow.",
          6.5,"final",{}),
    Scene("Final mirror",
          "The other gives us the mirror.",
          6.5,"final",{}),
    Scene("Closing",
          "Between them stands the central mystery of nonduality: how the Absolute can exceed the world completely while appearing as nothing but this world, this body, this thought, and this act of recognition.",
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
        "-c:v","libx264","-preset","medium","-crf","18",
        "-pix_fmt","yuv420p","-movflags","+faststart",str(output),
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
    output=OUTPUT/"mirror_and_overflow.mp4"
    subprocess.run([
        ffmpeg_path(),"-y","-f","concat","-safe","0",
        "-i",str(txt),"-c","copy","-movflags","+faststart",str(output),
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return output

def export_timeline():
    cursor=0.0; records=[]
    for index,scene in enumerate(SCENES,1):
        rec=asdict(scene)
        rec["scene_id"]=f"scene_{index:03d}"
        rec["start_seconds"]=round(cursor,3)
        cursor+=scene.duration
        rec["end_seconds"]=round(cursor,3)
        records.append(rec)
    path=OUTPUT/"narration_timeline.json"
    path.write_text(json.dumps({
        "title":"the mirror and the overflow",
        "subtitle":"Plotinus and Abhinavagupta on why the One becomes many",
        "scene_count":len(SCENES),
        "runtime_seconds":round(cursor,3),
        "shot_duration_range":[5,10],
        "continuity_objects":{
            "plotinus":"gold overflow descending through articulated levels",
            "abhinavagupta":"gold mirror-field differentiating within itself",
            "synthesis":"vertical procession crossed by horizontal recognition"
        },
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
