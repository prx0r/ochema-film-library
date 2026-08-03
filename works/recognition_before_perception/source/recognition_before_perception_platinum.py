#!/usr/bin/env python3
"""
RECOGNITION COMES BEFORE PERCEPTION
Abhinavagupta on Pratyabhijñā, Familiarity, and Why Nothing Appears Raw

An original dark-spectrum Platinum-house procedural visual essay.

CENTRAL CLAIM
-------------
Modern theories often imagine perception as:

    raw sensation
      ↓
    feature extraction
      ↓
    object recognition
      ↓
    meaning
      ↓
    self-reference

The Pratyabhijñā tradition challenges this order.

An experience is never first a meaningless sensory atom.
For anything to appear at all, consciousness must already:

• illuminate it;
• distinguish it;
• relate it to a field;
• register its presence;
• and implicitly apprehend itself as the knower.

Recognition is therefore not merely a later comparison with stored memory.
It is the deeper structure by which an appearing is grasped as this.

FILM THESIS
-----------
Perception without recognition would not be mysterious perception.
It would be no experience at all.

The film moves through:

undifferentiated stimulation
→ selective differentiation
→ implicit familiarity
→ objecthood
→ naming
→ self-reference
→ breakdown
→ ambiguity
→ re-recognition
→ pratyabhijñā

It distinguishes:
• perceptual recognition;
• conceptual classification;
• autobiographical familiarity;
• and metaphysical recognition.

The final claim is not that every object has been previously encountered.
It is that every experience already arrives within the form of intelligibility.

HOUSE RULES
-----------
• Every scene lasts 5–10 seconds.
• Every scene visibly transforms.
• Dark prismatic palette: black, ultraviolet, cyan, acid green,
  crimson, magenta, and molten gold.
• Recognition sequences brighten toward ivory without flattening color.
• No static slide layouts.
• Mature frame near u=0.72.
• Continuity object: a broken gold glyph that repeatedly disintegrates
  and reassembles at higher levels of recognition.

OUTPUT
------
output_recognition_before_perception/
  frames/
  scenes/
  recognition_before_perception.mp4
  narration_timeline.json
  contact_sheet.jpg

USAGE
-----
python recognition_before_perception_platinum.py
python recognition_before_perception_platinum.py --preview
python recognition_before_perception_platinum.py --scene 12
python recognition_before_perception_platinum.py --fps 12 --width 1920 --height 1080
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
OUTPUT = ROOT / "output_recognition_before_perception"
FRAMES = OUTPUT / "frames"
SCENES_DIR = OUTPUT / "scenes"

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 10

BLACK=(5,4,10)
DEEP_BLACK=(1,1,4)
WHITE=(255,253,246)
IVORY=(247,244,235)
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
INK=(24,22,30)

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

def dark_field(w,h,seed,light=0.0):
    rng=np.random.default_rng(seed)
    base=np.array(mix(BLACK,IVORY,light),dtype=np.float32)
    arr=np.empty((h,w,3),dtype=np.float32); arr[:]=base
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
    w,h=im.size; d=ImageDraw.Draw(im)
    centered(d,(w/2,h*.875),title,font(FONT_SERIF_BOLD,max(22,int(h*.04))),color)
    if subtitle:
        centered(d,(w/2,h*.923),subtitle,font(FONT_SANS,max(13,int(h*.019))),mix(color,SILVER,.55))

def border(im):
    w,h=im.size; d=ImageDraw.Draw(im)
    d.rounded_rectangle((26,26,w-26,h-26),radius=18,outline=(*GOLD,55),width=2)

def glow_circle(im,x,y,r,color,alpha=180,blur=16):
    gl=layer(im.size); gd=ImageDraw.Draw(gl)
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
    gl=layer(im.size); gd=ImageDraw.Draw(gl)
    gd.line(pts,fill=(*color,alpha),width=width*3,joint="curve")
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).line(
        pts,fill=(*color,min(255,alpha+20)),width=width,joint="curve"
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

def arrow(d,a,b,color=WHITE,width=3,head=10):
    d.line((*a,*b),fill=color,width=width)
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for s in (-1,1):
        p=(b[0]-math.cos(ang+s*.52)*head,b[1]-math.sin(ang+s*.52)*head)
        d.line((*b,*p),fill=color,width=width)

def draw_eye(d,cx,cy,scale=1.0,color=CYAN,alpha=210):
    d.arc((cx-90*scale,cy-45*scale,cx+90*scale,cy+45*scale),
          0,180,fill=(*color,alpha),width=max(2,int(4*scale)))
    d.arc((cx-90*scale,cy-45*scale,cx+90*scale,cy+45*scale),
          180,360,fill=(*color,alpha),width=max(2,int(4*scale)))
    d.ellipse((cx-22*scale,cy-22*scale,cx+22*scale,cy+22*scale),
              fill=(*color,alpha))

def draw_glyph(d,cx,cy,scale=1.0,color=GOLD,alpha=220):
    # abstract recognition glyph: eye + split diamond
    draw_eye(d,cx,cy-15,scale*.52,color,alpha)
    pts=[
        (cx,cy-90*scale),
        (cx+75*scale,cy),
        (cx,cy+90*scale),
        (cx-75*scale,cy),
        (cx,cy-90*scale),
    ]
    d.line(pts,fill=(*color,alpha),width=max(2,int(4*scale)))
    d.line((cx-75*scale,cy,cx+75*scale,cy),
           fill=(*color,alpha),width=max(2,int(3*scale)))

def fragments(cx,cy,count,seed,radius):
    rng=random.Random(seed)
    pts=[]
    for _ in range(count):
        a=rng.random()*math.tau
        r=rng.uniform(radius*.25,radius)
        pts.append((cx+math.cos(a)*r,cy+math.sin(a)*r*.65))
    return pts

def noisy_contour(cx,cy,r,t,count=180):
    pts=[]
    for i in range(count):
        a=i*math.tau/count
        rr=r*(1+.13*math.sin(a*5+t)+.07*math.sin(a*11-t*.7))
        pts.append((cx+math.cos(a)*rr,cy+math.sin(a)*rr*.72))
    pts.append(pts[0])
    return pts


# =============================================================================
# VISUALS
# =============================================================================

def vis_raw_noise(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    rng=random.Random(5)
    for i in range(150):
        x=rng.uniform(w*.10,w*.90)
        y=rng.uniform(h*.15,h*.68)
        r=rng.uniform(1,6)
        col=[CYAN,VIOLET,GREEN,CRIMSON,MAGENTA][i%5]
        glow_circle(im,x,y,r,col,70,5)
    seal(im,"IMAGINE EXPERIENCE BEFORE RECOGNITION",
         "no object, no feature, no here, no this")

def vis_differentiation(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    rng=random.Random(6)
    pts=[(rng.uniform(w*.10,w*.90),rng.uniform(h*.15,h*.68)) for _ in range(100)]
    q=ease(u); target=(w*.58,h*.38)
    for i,(x,y) in enumerate(pts):
        dist=math.dist((x,y),target)
        alpha=180 if dist<90 else int(90*(1-q))
        glow_circle(im,x,y,4,[CYAN,VIOLET,GREEN][i%3],alpha,5)
    contour=noisy_contour(*target,lerp(15,95,q),t)
    glow_line(im,contour,GOLD,4,190,11)
    seal(im,"TO APPEAR IS ALREADY TO BE DIFFERENTIATED",
         "this emerges only against what it is not")

def vis_thisness(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    contour=noisy_contour(cx,cy,lerp(30,130,q),t)
    glow_line(im,contour,CYAN,5,200,12)
    glow_circle(im,cx,cy,15,GOLD,185,12)
    if q>.55:
        centered(d,(cx,h*.68),"THIS",font(FONT_SERIF_BOLD,30),GOLD)
    seal(im,"PERCEPTION ALREADY CONTAINS THISNESS",
         "an appearing is grasped as a unit before it is named")

def vis_familiarity(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    draw_glyph(d,cx,cy,lerp(.25,.95,q),GOLD,int(120+100*q))
    for rr in range(45,255,30):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*VIOLET,int(70*q*(1-rr/285))),width=3)
    seal(im,"FAMILIARITY PRECEDES EXPLICIT MEMORY",
         "the field already knows how to receive what appears")

def vis_object_birth(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    pts=fragments(cx,cy,60,15,230)
    for i,(x,y) in enumerate(pts):
        tx=cx+(x-cx)*.45
        ty=cy+(y-cy)*.45
        xx=lerp(x,tx,q); yy=lerp(y,ty,q)
        glow_circle(im,xx,yy,4,[CYAN,VIOLET,GREEN][i%3],100,5)
    contour=noisy_contour(cx,cy,120,t)
    glow_line(im,partial(contour,q),GOLD,5,195,12)
    seal(im,"OBJECTHOOD IS A STABILIZED ACT OF RECOGNITION",
         "many changing signals become one persisting thing")

def vis_name(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    contour=noisy_contour(cx,cy,110,t)
    glow_line(im,contour,CYAN,4,180,10)
    letters=list("TREE")
    for i,ch in enumerate(letters):
        a=i*math.tau/len(letters)-math.pi/2
        x=lerp(cx+math.cos(a)*180,cx-45+i*30,q)
        y=lerp(cy+math.sin(a)*110,cy,q)
        centered(d,(x,y),ch,font(FONT_SERIF_BOLD,28),
                 [GREEN,GOLD,CYAN,VIOLET][i])
    seal(im,"NAMING COMPRESSES RECOGNITION INTO A SYMBOL",
         "the word stabilizes a pattern across changing encounters")

def vis_category(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    examples=[
        (w*.20,h*.28,70,55),
        (w*.42,h*.50,55,90),
        (w*.65,h*.27,85,45),
        (w*.78,h*.52,65,65),
    ]
    q=ease(u)
    for i,(x,y,rx,ry) in enumerate(examples):
        d.ellipse((x-rx,y-ry,x+rx,y+ry),
                  outline=(*[GREEN,CYAN,VIOLET,GOLD][i],170),width=4)
        glow_line(im,partial([(x,y),(w*.50,h*.40)],q),
                  [GREEN,CYAN,VIOLET,GOLD][i],3,135,8)
    centered(d,(w*.50,h*.40),"TREE",font(FONT_SERIF_BOLD,30),GOLD)
    seal(im,"A CATEGORY RECOGNIZES IDENTITY THROUGH DIFFERENCE",
         "no two examples match, yet one form is apprehended")

def vis_self_reference(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.40); right=(w*.72,h*.40); q=ease(u)
    draw_eye(d,*left,.62,CYAN,190)
    contour=noisy_contour(*right,95,t)
    glow_line(im,contour,VIOLET,4,180,10)
    glow_line(im,partial([left,(w*.50,h*.20),right],q),GOLD,5,195,12)
    glow_circle(im,w*.50,h*.20,14,GOLD,175,10)
    seal(im,"EVERY PERCEPTION IMPLICITLY CONTAINS A KNOWER",
         "the object appears together with the tacit sense that it is known")

def vis_vimarsa(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    draw_glyph(d,cx,cy,.85,GOLD,210)
    copies=[
        (w*.28,h*.25,CYAN),
        (w*.72,h*.25,VIOLET),
        (w*.28,h*.57,GREEN),
        (w*.72,h*.57,CRIMSON),
    ]
    for x,y,col in copies:
        draw_glyph(d,x,y,.25,col,int(160*q))
        glow_line(im,partial([(x,y),(cx,cy)],q),col,3,125,8)
    seal(im,"VIMARŚA IS AWARENESS APPREHENDING ITS OWN ACTIVITY",
         "illumination is never entirely blind to itself")

def vis_unknown_object(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    contour=noisy_contour(cx,cy,130,t*1.4)
    glow_line(im,contour,MAGENTA,5,190,12)
    labels=["ANIMAL?","MASK?","TOOL?","SHADOW?"]
    for i,lab in enumerate(labels):
        a=i*math.tau/4-math.pi/2
        x=cx+math.cos(a)*210
        y=cy+math.sin(a)*130
        centered(d,(x,y),lab,font(FONT_SERIF_BOLD,17),
                 [CYAN,VIOLET,GREEN,CRIMSON][i])
        glow_line(im,partial([(x,y),(cx,cy)],q),
                  [CYAN,VIOLET,GREEN,CRIMSON][i],2,110,7)
    seal(im,"THE UNKNOWN IS STILL RECOGNIZED AS UNKNOWN",
         "uncertainty is already an intelligible mode of appearance")

def vis_illusion(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.30,h*.40); right=(w*.70,h*.40); q=ease(u)
    # rope
    glow_line(im,[(left[0]-110,left[1]+45),(left[0]-20,left[1]-35),
                  (left[0]+110,left[1]+35)],GOLD,6,190,12)
    # snake
    pts=[]
    for i in range(160):
        x=right[0]-120+i*240/159
        y=right[1]+math.sin(i*.12+t)*35
        pts.append((x,y))
    glow_line(im,pts,VENOM,6,190,12)
    glow_line(im,partial([left,(w*.50,h*.20),right],q),CRIMSON,4,165,10)
    seal(im,"ERROR IS MISRECOGNITION, NOT RAW SENSATION",
         "something appears as what it is not")

def vis_face_failure(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    rng=random.Random(27); q=ease(u)
    faces=[]
    for j in range(3):
        for i in range(5):
            x=w*.18+i*w*.16
            y=h*.24+j*h*.16
            faces.append((x,y))
    for i,(x,y) in enumerate(faces):
        d.ellipse((x-35,y-45,x+35,y+45),outline=(*SILVER,130),width=3)
        d.ellipse((x-15,y-10,x-8,y-3),fill=(*CYAN,130))
        d.ellipse((x+8,y-10,x+15,y-3),fill=(*CYAN,130))
        if i==7:
            d.rectangle((x-42,y-52,x+42,y+52),outline=(*CRIMSON,int(210*q)),width=4)
    seal(im,"WHEN RECOGNITION FAILS, THE WORLD CHANGES STRUCTURE",
         "features may remain while personhood no longer arrives")

def vis_agnosia(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    objects=[
        (w*.24,h*.30,"CUP",CYAN),
        (w*.50,h*.30,"KEY",GOLD),
        (w*.76,h*.30,"FACE",VIOLET),
        (w*.36,h*.55,"TREE",GREEN),
        (w*.64,h*.55,"HAND",CRIMSON),
    ]
    q=ease(u)
    for x,y,lab,col in objects:
        contour=noisy_contour(x,y,45,t+x*.001)
        glow_line(im,contour,col,3,130,8)
        alpha=int(210*(1-q))
        centered(d,(x,y+70),lab,font(FONT_SANS_BOLD,13),(*col,alpha))
    seal(im,"AGNOSIA SEPARATES SEEING FROM KNOWING WHAT IS SEEN",
         "perception is not one indivisible operation")

def vis_memory_recall(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    shards=fragments(cx,cy,28,44,220)
    for i,(x,y) in enumerate(shards):
        tx=cx+((i%7)-3)*24
        ty=cy+((i//7)-1.5)*28
        xx=lerp(x,tx,q); yy=lerp(y,ty,q)
        glow_circle(im,xx,yy,6,[VIOLET,CYAN,GREEN,GOLD][i%4],125,6)
    if q>.55:
        draw_glyph(d,cx,cy,.70,GOLD,int(210*q))
    seal(im,"MEMORY IS RECOGNITION RECONSTRUCTING A PRIOR FORM",
         "the past returns by becoming intelligible again")

def vis_prediction(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    labels=[
        ("PRIOR",VIOLET,w*.18,h*.40),
        ("PREDICT",GOLD,w*.36,h*.24),
        ("SENSE",CYAN,w*.58,h*.24),
        ("ERROR",CRIMSON,w*.78,h*.40),
        ("UPDATE",GREEN,w*.58,h*.58),
        ("RECOGNIZE",MAGENTA,w*.36,h*.58),
    ]
    q=ease(u)
    for i,(lab,col,x,y) in enumerate(labels):
        glow_circle(im,x,y,10,col,145,8)
        centered(d,(x,y+26),lab,font(FONT_SANS_BOLD,11),col)
        if i:
            arrow(d,labels[i-1][2:4],(x,y),(*col,int(145*q)),2,7)
    arrow(d,labels[-1][2:4],labels[0][2:4],(*VIOLET,int(145*q)),2,7)
    seal(im,"PREDICTION MAKES RECOGNITION DYNAMIC",
         "the system continually tests what kind of world is appearing")

def vis_attention(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    pts=fragments(w*.50,h*.40,70,58,280)
    target=pts[22]; q=ease(u)
    for i,(x,y) in enumerate(pts):
        dist=math.dist((x,y),target)
        alpha=180 if dist<75 else int(100*(1-q))
        glow_circle(im,x,y,5,[CYAN,VIOLET,GREEN][i%3],alpha,5)
    for rr in range(35,220,28):
        d.ellipse((target[0]-rr,target[1]-rr,
                   target[0]+rr,target[1]+rr),
                  outline=(*GOLD,int(75*q*(1-rr/245))),width=3)
    seal(im,"ATTENTION PREPARES WHAT CAN BE RECOGNIZED",
         "salience is the doorway through which a form becomes this")

def vis_language_prison(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    words=["ENEMY","FAILURE","MINE","IMPOSSIBLE","THREAT"]
    for i,word in enumerate(words):
        a=i*math.tau/len(words)-math.pi/2
        r=lerp(230,120,q)
        x=cx+math.cos(a)*r
        y=cy+math.sin(a)*r*.62
        centered(d,(x,y),word,font(FONT_SERIF_BOLD,17),
                 [CRIMSON,VIOLET,MAGENTA,ORANGE,CYAN][i])
    d.ellipse((cx-130,cy-90,cx+130,cy+90),outline=(*CRIMSON,200),width=5)
    seal(im,"A NAME CAN BECOME A PRISON OF RECOGNITION",
         "the label starts deciding what every new appearance means")

def vis_rasa_recognition(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    colors=[CRIMSON,VIOLET,CYAN,GREEN,ORANGE,MAGENTA,GOLD]
    for i,col in enumerate(colors):
        a=i*math.tau/len(colors)+t*.08
        r=190
        x=cx+math.cos(a)*r
        y=cy+math.sin(a)*115
        glow_circle(im,x,y,14,col,145,9)
        glow_line(im,partial([(x,y),(cx,cy)],q),col,3,125,8)
    glow_circle(im,cx,cy,17,GOLD,190,12)
    seal(im,"RASA RECOGNIZES EMOTION WITHOUT PRIVATE CAPTURE",
         "feeling becomes intelligible as a universal mode")

def vis_self_misrecognition(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    draw_glyph(d,cx,cy,.30,CRIMSON,190)
    labels=[
        ("BODY",CYAN,-170,-95),
        ("STORY",VIOLET,170,-95),
        ("ROLE",GREEN,-170,110),
        ("MEMORY",MAGENTA,170,110),
    ]
    for lab,col,ox,oy in labels:
        x=lerp(cx+ox,cx+ox*.58,q)
        y=lerp(cy+oy,cy+oy*.58,q)
        centered(d,(x,y),lab,font(FONT_SERIF_BOLD,18),col)
        glow_line(im,[(x,y),(cx,cy)],col,3,105,8)
    d.ellipse((cx-120,cy-85,cx+120,cy+85),outline=(*CRIMSON,195),width=5)
    seal(im,"BONDAGE IS RECOGNITION CONTRACTED AROUND THE WRONG SCALE",
         "a local form is taken as the whole knower")

def vis_pratyabhijna(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    shards=fragments(cx,cy,34,66,250)
    for i,(x,y) in enumerate(shards):
        tx=cx+math.cos(i*math.tau/34)*75
        ty=cy+math.sin(i*math.tau/34)*50
        xx=lerp(x,tx,q); yy=lerp(y,ty,q)
        glow_circle(im,xx,yy,6,
                    [CRIMSON,VIOLET,CYAN,GREEN,ORANGE,MAGENTA][i%6],
                    125,6)
    draw_glyph(d,cx,cy,lerp(.20,1.0,q),GOLD,int(120+100*q))
    for rr in range(45,285,30):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(70*q*(1-rr/315))),width=3)
    centered(d,(cx,h*.68),"PRATYABHIJÑĀ",font(FONT_SERIF_BOLD,28),GOLD)
    seal(im,"LIBERATION IS THE RECOGNITION OF THE KNOWER",
         "the finite center recognizes the awareness in which center and world appear")

def vis_not_memory(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.30,h*.40); right=(w*.70,h*.40); q=ease(u)
    # memory archive
    for i in range(5):
        d.rectangle((left[0]-90+i*12,left[1]-70+i*10,
                     left[0]+90+i*12,left[1]+70+i*10),
                    outline=(*VIOLET,130),width=3)
    # self-luminous recognition
    draw_glyph(d,*right,.78,GOLD,210)
    glow_line(im,partial([left,(w*.50,h*.18),right],q),CYAN,4,165,10)
    centered(d,(left[0],h*.68),"RETRIEVAL",font(FONT_SERIF_BOLD,21),VIOLET)
    centered(d,(right[0],h*.68),"SELF-RECOGNITION",font(FONT_SERIF_BOLD,21),GOLD)
    seal(im,"PRATYABHIJÑĀ IS NOT ORDINARY MEMORY",
         "it is the recovery of an identity never actually lost")

def vis_science_bridge(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.30,h*.40); right=(w*.70,h*.40); q=ease(u)
    # recognition network
    nodes=[
        (left[0],left[1]-80,VIOLET),
        (left[0]+90,left[1],CRIMSON),
        (left[0],left[1]+80,GREEN),
        (left[0]-90,left[1],CYAN),
    ]
    for x,y,col in nodes:
        glow_circle(im,x,y,10,col,145,8)
    for i in range(len(nodes)):
        arrow(d,nodes[i][:2],nodes[(i+1)%len(nodes)][:2],
              (*nodes[(i+1)%len(nodes)][2],145),2,7)
    draw_glyph(d,*right,.68,GOLD,200)
    centered(d,(left[0],h*.68),"RECOGNITION MECHANISMS",
             font(FONT_SANS_BOLD,13),CYAN)
    centered(d,(right[0],h*.68),"CONDITION OF APPEARING",
             font(FONT_SANS_BOLD,13),GOLD)
    glow_line(im,partial([left,(w*.50,h*.18),right],q),VIOLET,4,165,10)
    seal(im,"SCIENCE MODELS HOW SYSTEMS IDENTIFY PATTERNS",
         "ABHINAVA ASKS HOW ANY PATTERN BECOMES PRESENT AS THIS")

def vis_caution(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    rows=[
        ("PERCEPTION USES PRIOR STRUCTURE","SUPPORTED",GREEN),
        ("EVERY OBJECT HAS BEEN SEEN BEFORE","FALSE",CRIMSON),
        ("RECOGNITION HAS MULTIPLE LEVELS","SUPPORTED",CYAN),
        ("NEUROSCIENCE PROVES PRATYABHIJÑĀ","NOT ESTABLISHED",CRIMSON),
    ]
    q=ease(u)
    for i,(claim,status,col) in enumerate(rows):
        local=clamp(q*len(rows)-i); y=h*(.23+i*.13)
        d.rounded_rectangle((w*.12,y-28,w*.88,y+28),radius=14,
                            fill=(*mix(BLACK,col,.12),int(220*local)),
                            outline=(*col,int(180*local)),width=2)
        centered(d,(w*.39,y),claim,font(FONT_SANS_BOLD,14),WHITE)
        centered(d,(w*.75,y),status,font(FONT_SANS_BOLD,14),col)
    seal(im,"DO NOT REDUCE METAPHYSICAL RECOGNITION TO CLASSIFICATION",
         "identifying an object is not yet recognizing the nature of the knower")

def vis_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    shards=fragments(cx,cy,42,91,280)
    colors=[CRIMSON,VIOLET,CYAN,GREEN,ORANGE,MAGENTA]
    for i,(x,y) in enumerate(shards):
        a=i*math.tau/len(shards)
        tx=cx+math.cos(a)*95
        ty=cy+math.sin(a)*60
        xx=lerp(x,tx,q); yy=lerp(y,ty,q)
        glow_circle(im,xx,yy,6,colors[i%len(colors)],125,6)
    draw_glyph(d,cx,cy,lerp(.15,1.05,q),GOLD,int(110+110*q))
    for rr in range(45,310,30):
        d.ellipse((cx-rr*q,cy-rr*.62*q,cx+rr*q,cy+rr*.62*q),
                  outline=(*GOLD,int(75*q*(1-rr/340))),width=3)
    if q>.72:
        centered(d,(cx,h*.68),"AHAM",font(FONT_SERIF_BOLD,31),GOLD)
    seal(im,"RECOGNITION COMES BEFORE PERCEPTION",
         "nothing appears raw; every experience already arrives within the form of intelligibility",GOLD)


VISUALS: dict[str,Callable] = {
    "noise":vis_raw_noise,
    "differentiate":vis_differentiation,
    "this":vis_thisness,
    "familiar":vis_familiarity,
    "object":vis_object_birth,
    "name":vis_name,
    "category":vis_category,
    "selfref":vis_self_reference,
    "vimarsa":vis_vimarsa,
    "unknown":vis_unknown_object,
    "illusion":vis_illusion,
    "face":vis_face_failure,
    "agnosia":vis_agnosia,
    "memory":vis_memory_recall,
    "predict":vis_prediction,
    "attention":vis_attention,
    "language":vis_language_prison,
    "rasa":vis_rasa_recognition,
    "selferror":vis_self_misrecognition,
    "pratyabhijna":vis_pratyabhijna,
    "notmemory":vis_not_memory,
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
    Scene("Raw experience",
          "Modern theories often begin with raw sensation.",
          7.0,"noise",{}),
    Scene("Meaning later",
          "First color, sound, pressure, and movement. Meaning is added later.",
          8.5,"noise",{}),
    Scene("Impossible field",
          "But what would a completely unrecognized experience actually be?",
          8.5,"noise",{}),

    Scene("Differentiation",
          "For anything to appear, it must already differ from what it is not.",
          9.0,"differentiate",{}),
    Scene("Figure and field",
          "Figure appears against field.",
          6.5,"differentiate",{}),
    Scene("First recognition",
          "This differentiation is already the beginning of recognition.",
          8.0,"differentiate",{}),

    Scene("Thisness",
          "An experience arrives as this.",
          6.5,"this",{}),
    Scene("Unit",
          "Before naming, it is already grasped as a unit.",
          8.0,"this",{}),
    Scene("Not chaos",
          "Perception never presents pure chaos and then politely waits for thought.",
          9.0,"this",{}),

    Scene("Familiarity",
          "The field already knows how to receive what appears.",
          8.5,"familiar",{}),
    Scene("Not memory image",
          "This familiarity need not be a retrieved picture of the same object.",
          8.5,"familiar",{}),
    Scene("Form of reception",
          "It is the prior form through which an appearing becomes intelligible.",
          9.0,"familiar",{}),

    Scene("Object birth",
          "A stable object is constructed across changing signals.",
          8.5,"object",{}),
    Scene("Many views",
          "Angles, shadows, occlusions, and movements vary.",
          8.0,"object",{}),
    Scene("One thing",
          "Recognition binds them as one persisting thing.",
          8.0,"object",{}),

    Scene("Naming",
          "Language condenses recognition into a symbol.",
          8.0,"name",{}),
    Scene("Tree",
          "The word tree stabilizes a pattern across countless different encounters.",
          9.0,"name",{}),
    Scene("Compression",
          "Naming is compression, not the beginning of intelligibility.",
          8.0,"name",{}),

    Scene("Category",
          "A category recognizes identity through difference.",
          8.0,"category",{}),
    Scene("No identical examples",
          "No two trees are identical.",
          6.5,"category",{}),
    Scene("Form across variation",
          "Yet one form is apprehended through their variation.",
          8.0,"category",{}),

    Scene("Knower",
          "Every perception also contains a tacit knower.",
          8.0,"selfref",{}),
    Scene("Known by someone",
          "The object does not merely appear. It appears as known.",
          8.0,"selfref",{}),
    Scene("Implicit self",
          "The sense of I is implicit before it becomes a sentence.",
          8.0,"selfref",{}),

    Scene("Vimarsa",
          "Abhinavagupta calls this reflexive power vimarśa.",
          8.0,"vimarsa",{}),
    Scene("Not blind light",
          "Consciousness is not a blind light illuminating objects.",
          8.0,"vimarsa",{}),
    Scene("Self-apprehension",
          "It apprehends its own activity in the act of illumination.",
          8.5,"vimarsa",{}),

    Scene("Unknown",
          "Even the unknown is recognized.",
          7.0,"unknown",{}),
    Scene("Uncertainty",
          "We recognize uncertainty, ambiguity, strangeness, and incomplete fit.",
          9.0,"unknown",{}),
    Scene("Unknown as mode",
          "Unknown is not absence of intelligibility. It is an intelligible mode.",
          9.0,"unknown",{}),

    Scene("Illusion",
          "Error also depends upon recognition.",
          7.5,"illusion",{}),
    Scene("Rope and snake",
          "A rope is misrecognized as a snake.",
          7.0,"illusion",{}),
    Scene("Positive form",
          "The error is not raw sensation. It is a positive but incorrect form of appearing.",
          9.5,"illusion",{}),

    Scene("Face recognition",
          "Neurology reveals that recognition can fail selectively.",
          8.5,"face",{}),
    Scene("Features remain",
          "A person may see eyes, nose, mouth, and movement.",
          8.0,"face",{}),
    Scene("Person absent",
          "Yet the familiar person does not arrive.",
          7.5,"face",{}),
    Scene("Changed world",
          "The sensory field remains while its human meaning changes structure.",
          9.0,"face",{}),

    Scene("Agnosia",
          "Agnosia separates seeing from knowing what is seen.",
          8.0,"agnosia",{}),
    Scene("Contours without objects",
          "Contours and colors may remain while cup, key, face, or hand fail to appear as such.",
          9.5,"agnosia",{}),
    Scene("Layered perception",
          "Perception is therefore a layered achievement.",
          8.0,"agnosia",{}),

    Scene("Memory",
          "Memory is another form of recognition.",
          7.5,"memory",{}),
    Scene("Reconstruction",
          "Fragments, traces, affect, and context are reconstructed into a prior form.",
          9.0,"memory",{}),
    Scene("Past intelligible again",
          "The past returns by becoming intelligible again.",
          8.0,"memory",{}),

    Scene("Prediction",
          "Predictive processing makes recognition dynamic.",
          8.0,"predict",{}),
    Scene("Prior",
          "The system brings expectations to sensation.",
          7.5,"predict",{}),
    Scene("Error",
          "Mismatch generates error.",
          6.5,"predict",{}),
    Scene("Revision",
          "Recognition is continually revised through contact with the world.",
          8.5,"predict",{}),

    Scene("Attention",
          "Attention prepares what can be recognized.",
          8.0,"attention",{}),
    Scene("Salience",
          "One signal becomes salient while others fall into background.",
          8.5,"attention",{}),
    Scene("Doorway",
          "Salience is the doorway through which a form becomes this.",
          8.5,"attention",{}),

    Scene("Language prison",
          "Recognition can also become rigid.",
          7.5,"language",{}),
    Scene("Enemy",
          "A person is named enemy, failure, threat, possession, or obstacle.",
          9.0,"language",{}),
    Scene("Label decides",
          "The label begins deciding what every new appearance means.",
          8.5,"language",{}),
    Scene("Closed world",
          "Recognition becomes a prison.",
          7.0,"language",{}),

    Scene("Rasa",
          "Rasa shows recognition without private capture.",
          8.0,"rasa",{}),
    Scene("Emotion form",
          "Grief, courage, wonder, and love are recognized as universal forms.",
          9.0,"rasa",{}),
    Scene("No ownership",
          "Feeling becomes intelligible without being reduced to mine.",
          8.0,"rasa",{}),

    Scene("Self error",
          "The deepest error concerns the knower itself.",
          8.0,"selferror",{}),
    Scene("Local form",
          "Body, story, role, and memory are recognized.",
          8.0,"selferror",{}),
    Scene("Wrong scale",
          "But a local configuration is mistaken for the whole knower.",
          8.5,"selferror",{}),
    Scene("Bondage",
          "Bondage is recognition contracted around the wrong scale.",
          8.5,"selferror",{}),

    Scene("Pratyabhijna",
          "Pratyabhijñā means recognition.",
          7.0,"pratyabhijna",{}),
    Scene("Not new object",
          "Liberation does not reveal a new object hidden behind experience.",
          8.5,"pratyabhijna",{}),
    Scene("Recognize knower",
          "It recognizes the nature of the one to whom every object appears.",
          9.0,"pratyabhijna",{}),

    Scene("Not memory",
          "This is not ordinary memory retrieval.",
          7.5,"notmemory",{}),
    Scene("Never lost",
          "It is recovery of an identity never actually lost.",
          8.0,"notmemory",{}),
    Scene("Forgotten mode",
          "The knowledge was concealed as the very mode of finite knowing.",
          8.5,"notmemory",{}),

    Scene("Science bridge",
          "Modern science can model feature binding, categorization, prediction, familiarity, and recall.",
          10.0,"bridge",{}),
    Scene("Mechanisms",
          "These are mechanisms by which organisms identify patterns.",
          8.0,"bridge",{}),
    Scene("Prior question",
          "Abhinavagupta asks the prior question: how does any pattern become present as this?",
          9.5,"bridge",{}),

    Scene("Discipline",
          "The levels must remain distinct.",
          7.0,"caution",{}),
    Scene("No universal memory bank",
          "Recognition does not mean every object has literally been seen before.",
          8.5,"caution",{}),
    Scene("No proof",
          "Neuroscience does not prove Pratyabhijñā metaphysics.",
          8.0,"caution",{}),
    Scene("Real confrontation",
          "The real confrontation concerns whether intelligibility is added to experience or belongs to appearing from the start.",
          10.0,"caution",{}),

    Scene("Return",
          "Return to the original noise.",
          6.5,"final",{}),
    Scene("Fragments gather",
          "The fragments gather into a form.",
          7.0,"final",{}),
    Scene("Glyph",
          "The form becomes a glyph of knowing.",
          7.0,"final",{}),
    Scene("Closing",
          "Recognition comes before perception: nothing appears raw, because every experience already arrives differentiated, related, and implicitly known within the form of intelligibility.",
          10.0,"final",{}),
]


def render_frame(scene,frame_index,frame_count,width,height,seed):
    u=frame_index/max(1,frame_count-1)
    t=u*scene.duration
    light=.16*smoothstep(.45,1.0,u) if scene.visual in {"pratyabhijna","notmemory","final"} else 0.0
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
    output=OUTPUT/"recognition_before_perception.mp4"
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
        "title":"recognition comes before perception",
        "subtitle":"Abhinavagupta on pratyabhijna, familiarity, and why nothing appears raw",
        "scene_count":len(SCENES),
        "runtime_seconds":round(cursor,3),
        "shot_duration_range":[5,10],
        "continuity_object":"broken gold recognition glyph",
        "palette":"black, ultraviolet, cyan, acid green, crimson, magenta, molten gold",
        "visual_arc":[
            "noise","differentiation","thisness","familiarity","objecthood",
            "naming","self-reference","failure","reconstruction","pratyabhijna"
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
