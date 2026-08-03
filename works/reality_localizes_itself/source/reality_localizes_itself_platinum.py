#!/usr/bin/env python3
"""
REALITY LOCALIZES ITSELF
Abhinavagupta, Predictive Processing, and the Construction of a Viewpoint

An original Platinum-house procedural visual essay.

CENTRAL CLAIM
-------------
The individual does not first exist and then observe reality.

Reality localizes itself as:
• a body;
• a point of view;
• a field of relevance;
• a remembered history;
• a practical self;
• and a world appearing from here.

Abhinavagupta's radical claim is not that a human ego creates the cosmos.
It is that consciousness freely contracts into finite subjectivity, producing
the correlated poles of knower and known within one luminous field.

Modern cognitive science often explains perception through predictive models,
body maps, attention, action policies, and self-models. These are mechanisms
by which a local perspective is stabilized.

Abhinavagupta asks a prior question:
what does it mean for body, model, brain, location, and world to appear at all?

FILM THESIS
-----------
The modern picture is often:

world → senses → brain model → conscious observer

The Śaiva picture reverses the explanatory order:

conscious manifestation
→ contraction
→ localized body
→ subject/object polarity
→ practical world
→ recognition

The film does not claim neuroscience proves Kashmir Śaivism.
It stages a confrontation between two explanatory starting points.

HOUSE RULES
-----------
• Every shot lasts 5–10 seconds.
• Every shot performs a visible transformation.
• Clean ivory scientific/gallery field.
• No slideshow compositions.
• Sparse labels only.
• Mature frame near u=0.72.
• Continuity object: a gold field contracting into a cyan viewpoint cone.
• Final reveal: the viewpoint appears inside the field it seemed to observe.

OUTPUT
------
output_reality_localizes/
  frames/
  scenes/
  reality_localizes_itself.mp4
  narration_timeline.json
  contact_sheet.jpg

USAGE
-----
python reality_localizes_itself_platinum.py
python reality_localizes_itself_platinum.py --preview
python reality_localizes_itself_platinum.py --scene 12
python reality_localizes_itself_platinum.py --fps 12 --width 1920 --height 1080
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
OUTPUT = ROOT / "output_reality_localizes"
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

def arrow(d,a,b,color=INK,width=3,head=10):
    d.line((*a,*b),fill=color,width=width)
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for s in (-1,1):
        p=(b[0]-math.cos(ang+s*.52)*head,b[1]-math.sin(ang+s*.52)*head)
        d.line((*b,*p),fill=color,width=width)

def draw_body(d,cx,cy,scale=1.0,color=INK,alpha=210):
    d.ellipse((cx-27*scale,cy-145*scale,cx+27*scale,cy-91*scale),
              outline=(*color,alpha),width=max(2,int(4*scale)))
    d.line((cx,cy-91*scale,cx,cy+55*scale),
           fill=(*color,alpha),width=max(3,int(6*scale)))
    d.line((cx-68*scale,cy-54*scale,cx+68*scale,cy-54*scale),
           fill=(*color,alpha),width=max(3,int(5*scale)))
    d.line((cx-68*scale,cy-54*scale,cx-140*scale,cy+18*scale),
           fill=(*color,alpha),width=max(3,int(5*scale)))
    d.line((cx+68*scale,cy-54*scale,cx+140*scale,cy+18*scale),
           fill=(*color,alpha),width=max(3,int(5*scale)))
    d.line((cx,cy+55*scale,cx-52*scale,cy+160*scale),
           fill=(*color,alpha),width=max(3,int(5*scale)))
    d.line((cx,cy+55*scale,cx+52*scale,cy+160*scale),
           fill=(*color,alpha),width=max(3,int(5*scale)))

def draw_eye(d,cx,cy,scale=1.0,color=INK,alpha=210):
    d.arc((cx-90*scale,cy-45*scale,cx+90*scale,cy+45*scale),
          0,180,fill=(*color,alpha),width=max(2,int(4*scale)))
    d.arc((cx-90*scale,cy-45*scale,cx+90*scale,cy+45*scale),
          180,360,fill=(*color,alpha),width=max(2,int(4*scale)))
    d.ellipse((cx-22*scale,cy-22*scale,cx+22*scale,cy+22*scale),
              fill=(*color,alpha))

def world_points(w,h,count=45,seed=0):
    rng=random.Random(seed)
    pts=[]
    for _ in range(count):
        pts.append((rng.uniform(w*.14,w*.86),rng.uniform(h*.20,h*.62)))
    return pts


# =============================================================================
# VISUALS
# =============================================================================

def vis_naive_observer(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.26,h*.40)
    right=(w*.72,h*.40)
    q=ease(u)
    draw_body(d,*left,.72,INK,180)
    draw_eye(d,left[0],left[1]-60,.42,CYAN,180)
    for i,(x,y) in enumerate(world_points(w,h,25,10)):
        if x<right[0]-120:
            continue
        glow_circle(im,x,y,8,[VIOLET,GREEN,GOLD][i%3],120,6)
    cone=layer(im.size)
    cd=ImageDraw.Draw(cone)
    cd.polygon([
        (left[0]+30,left[1]-60),
        (w*.88,h*.20),
        (w*.88,h*.62),
    ],fill=(*CYAN,int(45*q)))
    im.alpha_composite(cone)
    seal(im,"THE PERSON LOOKS OUT AT A READY-MADE WORLD",
         "the default picture places observer and reality on opposite sides")

def vis_coemergence(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    glow_circle(im,cx,cy,16,GOLD,180,11)
    subject=(lerp(cx,w*.27,q),cy)
    obj=(lerp(cx,w*.73,q),cy)
    glow_circle(im,*subject,15,CYAN,170,10)
    glow_circle(im,*obj,15,VIOLET,170,10)
    glow_line(im,[(cx,cy),subject],GOLD,3,int(150*q),9)
    glow_line(im,[(cx,cy),obj],GOLD,3,int(150*q),9)
    centered(d,(subject[0],h*.68),"SUBJECT",font(FONT_SERIF_BOLD,22),CYAN)
    centered(d,(obj[0],h*.68),"OBJECT",font(FONT_SERIF_BOLD,22),VIOLET)
    seal(im,"SUBJECT AND OBJECT CO-EMERGE",
         "neither pole appears independently of the act that relates them")

def vis_field_localizes(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    for rr in range(40,300,30):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(80*(1-q*.25)*(1-rr/330))),width=3)
    r=lerp(260,85,q)
    d.ellipse((cx-r,cy-r*.62,cx+r,cy+r*.62),
              outline=(*CYAN,210),width=5)
    glow_circle(im,cx,cy,15,GOLD,180,11)
    seal(im,"THE FIELD ACCEPTS A CENTER",
         "localization begins when unlimited appearance becomes here")

def vis_body_localization(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    for rr in range(40,230,30):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(70*q*(1-rr/260))),width=3)
    draw_body(d,cx,cy,.78,INK,int(220*q))
    d.ellipse((cx-145,cy-175,cx+145,cy+175),
              outline=(*CYAN,int(190*q)),width=5)
    seal(im,"A BODY IS A STABILIZED HERE",
         "location becomes posture, boundary, sensation, and possible action")

def vis_viewpoint_cone(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    origin=(w*.28,h*.43)
    q=ease(u)
    draw_eye(d,*origin,.55,CYAN,190)
    cone=layer(im.size)
    cd=ImageDraw.Draw(cone)
    cd.polygon([
        (origin[0]+35,origin[1]),
        (w*.88,h*.18),
        (w*.88,h*.65),
    ],fill=(*CYAN,int(55*q)))
    im.alpha_composite(cone)
    pts=world_points(w,h,35,20)
    for i,(x,y) in enumerate(pts):
        if x<origin[0]+60:
            continue
        glow_circle(im,x,y,7,[VIOLET,GREEN,GOLD][i%3],120,6)
    seal(im,"A VIEWPOINT IS A FIELD OF POSSIBLE RELEVANCE",
         "what appears is already organized from somewhere")

def vis_attention_contraction(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    pts=world_points(w,h,50,31)
    target=pts[17]
    q=ease(u)
    for i,(x,y) in enumerate(pts):
        dist=math.dist((x,y),target)
        alpha=int(170*(1-q*.82)) if dist>80 else 190
        glow_circle(im,x,y,7,[CYAN,VIOLET,GREEN][i%3],alpha,6)
    for rr in range(35,220,28):
        d.ellipse((target[0]-rr,target[1]-rr,target[0]+rr,target[1]+rr),
                  outline=(*GOLD,int(80*q*(1-rr/245))),width=3)
    seal(im,"ATTENTION DOES NOT ONLY SELECT",
         "it contracts a world of possibilities around one relevance")

def vis_body_model(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    draw_body(d,cx,cy,.78,INK,180)
    nodes=[
        ("VISION",cx,cy-150,CYAN),
        ("INTEROCEPTION",cx-155,cy,VIOLET),
        ("PROPRIOCEPTION",cx+155,cy,GREEN),
        ("ACTION",cx,cy+155,GOLD),
    ]
    for i,(lab,x,y,col) in enumerate(nodes):
        local=clamp(q*len(nodes)-i)
        glow_circle(im,x,y,11,col,150,8)
        centered(d,(x,y+28),lab,font(FONT_SANS_BOLD,12),col)
        glow_line(im,[(x,y),(cx,cy)],col,3,int(125*local),8)
    d.ellipse((cx-170,cy-195,cx+170,cy+195),
              outline=(*CYAN,int(170*q)),width=4)
    seal(im,"THE BODY-MODEL BINDS MANY SIGNALS INTO ONE PRACTICAL CENTER",
         "this is the body from which action seems to begin")

def vis_world_model(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    origin=(w*.28,h*.43)
    q=ease(u)
    draw_body(d,*origin,.56,INK,175)
    items=[
        ("PATH",w*.62,h*.54,GREEN),
        ("THREAT",w*.74,h*.30,CRIMSON),
        ("OBJECT",w*.58,h*.28,VIOLET),
        ("SHELTER",w*.82,h*.55,GOLD),
    ]
    for i,(lab,x,y,col) in enumerate(items):
        glow_circle(im,x,y,11,col,150,8)
        centered(d,(x,y+28),lab,font(FONT_SANS_BOLD,12),col)
        arrow(d,(origin[0]+45,origin[1]),(x-15,y),(*col,int(150*q)),2,7)
    seal(im,"A WORLD-MODEL IS A MAP OF ACTIONABLE DIFFERENCE",
         "objects appear as what can be approached, avoided, used, or remembered")

def vis_prediction_loop(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    labels=[
        ("MODEL",VIOLET,w*.18,h*.40),
        ("PREDICT",GOLD,w*.36,h*.24),
        ("SENSE",CYAN,w*.58,h*.24),
        ("ERROR",CRIMSON,w*.78,h*.40),
        ("UPDATE",GREEN,w*.58,h*.58),
        ("ACT",INK,w*.36,h*.58),
    ]
    q=ease(u)
    for i,(lab,col,x,y) in enumerate(labels):
        glow_circle(im,x,y,11,col,150,8)
        centered(d,(x,y+27),lab,font(FONT_SANS_BOLD,12),col)
        if i>0:
            px,py=labels[i-1][2],labels[i-1][3]
            arrow(d,(px,py),(x,y),(*col,int(150*q)),2,7)
    arrow(d,(labels[-1][2],labels[-1][3]),
          (labels[0][2],labels[0][3]),(*VIOLET,int(150*q)),2,7)
    seal(im,"THE LOCAL SELF IS STABILIZED BY A PREDICTION-ACTION LOOP",
         "model and world continually correct one another")

def vis_memory_thread(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    y=h*.40
    xs=[w*.18,w*.34,w*.50,w*.66,w*.82]
    q=ease(u)
    cols=[CYAN,VIOLET,GREEN,CRIMSON,GOLD]
    for x,col in zip(xs,cols):
        glow_circle(im,x,y,13,col,150,9)
    glow_line(im,partial([(x,y) for x in xs],q),GOLD,5,200,12)
    if q>.6:
        centered(d,(w*.50,h*.68),"ONE HISTORY",font(FONT_SERIF_BOLD,25),GOLD)
    seal(im,"MEMORY TURNS VIEWPOINT INTO BIOGRAPHY",
         "moments become the past of this center")

def vis_self_model(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    draw_body(d,cx,cy,.70,INK,175)
    labels=[
        ("MY BODY",CYAN,-160,-95),
        ("MY STORY",VIOLET,160,-95),
        ("MY GOALS",GREEN,-160,110),
        ("MY THREAT",CRIMSON,160,110),
    ]
    for lab,col,ox,oy in labels:
        x=cx+ox; y=cy+oy
        glow_circle(im,x,y,10,col,145,8)
        centered(d,(x,y+27),lab,font(FONT_SANS_BOLD,12),col)
        glow_line(im,[(x,y),(cx,cy)],col,3,int(110*q),8)
    r=lerp(220,135,q)
    d.ellipse((cx-r,cy-r*.68,cx+r,cy+r*.68),
              outline=(*CRIMSON,190),width=5)
    seal(im,"THE SELF-MODEL BECOMES A DEFENDED CENTER",
         "localization hardens into identity")

def vis_kanchukas(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    labels=[
        ("TIME",GOLD,-185,-95),
        ("SPACE",CYAN,185,-95),
        ("CAUSALITY",VIOLET,-185,110),
        ("LIMITED POWER",CRIMSON,185,110),
        ("LIMITED KNOWING",GREEN,0,170),
    ]
    for lab,col,ox,oy in labels:
        x=lerp(cx+ox,cx+ox*.68,q)
        y=lerp(cy+oy,cy+oy*.68,q)
        centered(d,(x,y),lab,font(FONT_SANS_BOLD,12),col)
    r=lerp(250,95,q)
    d.ellipse((cx-r,cy-r*.68,cx+r,cy+r*.68),
              outline=(*CYAN,205),width=5)
    glow_circle(im,cx,cy,14,GOLD,175,10)
    seal(im,"THE KAÑCUKAS ARE CONDITIONS OF LOCAL PERSPECTIVE",
         "infinity appears as limited time, place, power, causality, and knowledge")

def vis_subject_object_world(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    subject=(w*.26,cy)
    obj=(w*.74,cy)
    world=(cx,h*.22)
    glow_circle(im,*subject,15,CYAN,170,10)
    glow_circle(im,*obj,15,VIOLET,170,10)
    glow_circle(im,*world,15,GREEN,170,10)
    for p0 in (subject,obj,world):
        glow_line(im,[(cx,cy),p0],GOLD,3,int(145*q),9)
    glow_circle(im,cx,cy,16,GOLD,180,11)
    seal(im,"SUBJECT, OBJECT, AND WORLD ARE ONE DIFFERENTIATED EVENT",
         "the relations are real without becoming separate substances")

def vis_location_inside_awareness(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    # map appears inside field
    for rr in range(45,290,32):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(75*q*(1-rr/320))),width=3)
    d.line((w*.23,h*.25,w*.77,h*.25,w*.77,h*.58,w*.23,h*.58,w*.23,h*.25),
           fill=(*CYAN,int(180*q)),width=4)
    glow_circle(im,w*.41,h*.42,13,CRIMSON,170,10)
    centered(d,(w*.41,h*.48),"HERE",font(FONT_SERIF_BOLD,22),CRIMSON)
    seal(im,"LOCATION ITSELF APPEARS",
         "here and there are contents within the luminous field")

def vis_brain_on_screen(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    # screen
    d.rounded_rectangle((w*.18,h*.17,w*.82,h*.64),
                        radius=20,fill=(*PALE_SILVER,80),
                        outline=(*CYAN,175),width=4)
    # brain-like network
    rng=random.Random(61)
    pts=[(rng.uniform(w*.30,w*.70),rng.uniform(h*.25,h*.55)) for _ in range(38)]
    for i,(x,y) in enumerate(pts):
        glow_circle(im,x,y,5,VIOLET,105,5)
        if i:
            d.line((*pts[i-1],x,y),fill=(*SILVER,70),width=2)
    if q>.5:
        for rr in range(35,260,30):
            d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                      outline=(*GOLD,int(65*q*(1-rr/290))),width=3)
    seal(im,"THE BRAIN ALSO APPEARS WITHIN EXPERIENCE",
         "explaining correlations does not remove the question of manifestation")

def vis_camera_error(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.30,h*.40)
    right=(w*.70,h*.40)
    q=ease(u)
    # camera model
    d.rectangle((left[0]-75,left[1]-55,left[0]+75,left[1]+55),
                outline=(*INK,170),width=4)
    d.ellipse((left[0]+40,left[1]-28,left[0]+96,left[1]+28),
              outline=(*CYAN,180),width=4)
    # field model
    for rr in range(35,155,28):
        d.ellipse((right[0]-rr,right[1]-rr*.62,right[0]+rr,right[1]+rr*.62),
                  outline=(*GOLD,int(80*q*(1-rr/180))),width=3)
    glow_circle(im,*right,14,GOLD,175,10)
    centered(d,(left[0],h*.68),"CAMERA IN WORLD",font(FONT_SERIF_BOLD,21),INK)
    centered(d,(right[0],h*.68),"WORLD IN APPEARING",font(FONT_SERIF_BOLD,21),GOLD)
    seal(im,"CONSCIOUSNESS IS NOT A CAMERA INSIDE THE HEAD",
         "the camera, head, and world already belong to what appears")

def vis_no_homunculus(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    d.ellipse((cx-175,cy-210,cx+175,cy+210),
              outline=(*INK,170),width=4)
    alpha=int(210*(1-q))
    draw_body(d,cx,cy,.26,CRIMSON,alpha)
    if q>.35:
        for rr in range(35,215,28):
            d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                      outline=(*GOLD,int(75*q*(1-rr/245))),width=3)
    seal(im,"NO TINY OBSERVER IS NEEDED",
         "knowing is present without becoming another object to be known")

def vis_action_localizes(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    origin=(w*.28,h*.42)
    q=ease(u)
    draw_body(d,*origin,.58,INK,175)
    targets=[
        (w*.70,h*.26,GREEN),
        (w*.78,h*.48,CRIMSON),
        (w*.62,h*.60,GOLD),
    ]
    for x,y,col in targets:
        glow_circle(im,x,y,12,col,150,8)
    path=[(origin[0]+45,origin[1]),(w*.48,h*.48),(w*.62,h*.60)]
    glow_line(im,partial(path,q),GOLD,5,195,12)
    seal(im,"ACTION MAKES THE VIEWPOINT CONCRETE",
         "a perspective is stabilized by what it can successfully do")

def vis_emotion_world(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    origin=(w*.32,h*.42)
    q=ease(u)
    draw_body(d,*origin,.58,INK,170)
    threats=[(w*.66,h*.24),(w*.78,h*.40),(w*.68,h*.60)]
    for x,y in threats:
        glow_circle(im,x,y,11,CRIMSON,150,8)
        glow_line(im,[(origin[0]+35,origin[1]),(x,y)],
                  CRIMSON,3,int(145*q),8)
    cone=layer(im.size)
    ImageDraw.Draw(cone).polygon([
        (origin[0]+30,origin[1]),
        (w*.88,h*.15),
        (w*.88,h*.68),
    ],fill=(*CRIMSON,int(35*q)))
    im.alpha_composite(cone)
    seal(im,"EMOTION REORGANIZES THE LOCAL WORLD",
         "fear changes distance, salience, memory, and available action")

def vis_language_nouns(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    processes=[
        ("GROWING",GREEN,-180,-80),
        ("FLOWING",CYAN,180,-80),
        ("REMEMBERING",VIOLET,-180,105),
        ("DEFENDING",CRIMSON,180,105),
    ]
    for lab,col,ox,oy in processes:
        x=lerp(cx+ox,cx,q*.62)
        y=lerp(cy+oy,cy,q*.62)
        centered(d,(x,y),lab,font(FONT_SERIF_BOLD,20),
                 (*col,int(210*(1-q*.55))))
    if q>.52:
        centered(d,(cx,cy),"SELF",font(FONT_SERIF_BOLD,33),INK)
    seal(im,"LANGUAGE FREEZES ACTIVITY INTO A THING",
         "a moving coordination becomes the noun self")

def vis_object_frozen_action(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    # dynamic tree
    branches=[
        [(cx,cy+150),(cx,cy+30),(cx-55,cy-55),(cx-105,cy-110)],
        [(cx,cy+30),(cx+55,cy-45),(cx+110,cy-95)],
        [(cx,cy-10),(cx-20,cy-95),(cx-60,cy-145)],
        [(cx,cy-20),(cx+25,cy-110),(cx+55,cy-150)],
    ]
    for pts in branches:
        glow_line(im,partial(pts,q),GREEN,5,175,11)
    if q>.65:
        centered(d,(cx,h*.68),"TREE",font(FONT_SERIF_BOLD,30),INK)
    seal(im,"OBJECTS ARE STABILIZED ACTIONS",
         "verbs become nouns when a process changes slowly enough for a viewpoint")

def vis_other_minds(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.32,h*.40)
    right=(w*.68,h*.40)
    q=ease(u)
    draw_body(d,*left,.62,INK,170)
    draw_body(d,*right,.62,INK,170)
    for rr in range(35,145,25):
        d.ellipse((left[0]-rr,left[1]-rr*.62,left[0]+rr,left[1]+rr*.62),
                  outline=(*CYAN,int(65*q*(1-rr/165))),width=3)
        d.ellipse((right[0]-rr,right[1]-rr*.62,right[0]+rr,right[1]+rr*.62),
                  outline=(*VIOLET,int(65*q*(1-rr/165))),width=3)
    glow_line(im,partial([left,(w*.50,h*.22),right],q),GOLD,4,175,11)
    seal(im,"REALITY LOCALIZES AS MANY CENTERS",
         "nonduality does not require one empirical viewpoint")

def vis_shared_world(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    centers=[(w*.26,h*.48,CYAN),(w*.50,h*.30,GOLD),(w*.74,h*.48,VIOLET)]
    q=ease(u)
    for x,y,col in centers:
        glow_circle(im,x,y,14,col,160,9)
    for rr in range(45,270,32):
        d.ellipse((w*.50-rr,h*.40-rr*.58,w*.50+rr,h*.40+rr*.58),
                  outline=(*GOLD,int(70*q*(1-rr/300))),width=3)
    seal(im,"MANY VIEWPOINTS PARTICIPATE IN ONE FIELD",
         "difference is not outside unity; it is how unity becomes relational")

def vis_recognition(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    draw_body(d,cx,cy,.72,INK,170)
    d.ellipse((cx-130,cy-160,cx+130,cy+160),
              outline=(*CYAN,185),width=4)
    for rr in range(45,285,30):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(75*q*(1-rr/315))),width=3)
    glow_circle(im,cx,cy,15,GOLD,180,11)
    if q>.6:
        centered(d,(cx,h*.68),"PRATYABHIJÑĀ",font(FONT_SERIF_BOLD,28),GOLD)
    seal(im,"RECOGNITION DOES NOT DESTROY THE VIEWPOINT",
         "the local center recognizes the field whose contraction it is")

def vis_science_bridge(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.30,h*.40)
    right=(w*.70,h*.40)
    q=ease(u)
    # predictive loop
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
              (*nodes[(i+1)%len(nodes)][2],150),2,7)
    # luminous field
    for rr in range(35,155,28):
        d.ellipse((right[0]-rr,right[1]-rr*.62,
                   right[0]+rr,right[1]+rr*.62),
                  outline=(*GOLD,int(80*q*(1-rr/180))),width=3)
    centered(d,(left[0],h*.68),"HOW VIEWPOINT IS STABILIZED",
             font(FONT_SANS_BOLD,13),CYAN)
    centered(d,(right[0],h*.68),"WHAT APPEARING IS",
             font(FONT_SANS_BOLD,13),GOLD)
    glow_line(im,partial([left,(w*.50,h*.20),right],q),VIOLET,4,175,11)
    seal(im,"SCIENCE AND ABHINAVA BEGIN AT DIFFERENT LEVELS",
         "mechanism of localization versus ontology of manifestation")

def vis_caution(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    rows=[
        ("BRAINS STABILIZE LOCAL PERSPECTIVES","SUPPORTED",GREEN),
        ("THE EGO CREATES THE PHYSICAL UNIVERSE","FALSE",CRIMSON),
        ("SUBJECT AND OBJECT ARE CORRELATED","PHILOSOPHICAL CLAIM",CYAN),
        ("NEUROSCIENCE PROVES ŚAIVISM","NOT ESTABLISHED",CRIMSON),
    ]
    q=ease(u)
    for i,(claim,status,col) in enumerate(rows):
        local=clamp(q*len(rows)-i)
        y=h*(.23+i*.13)
        d.rounded_rectangle((w*.14,y-28,w*.86,y+28),
                            radius=14,
                            fill=(*mix(WHITE,col,.10),int(220*local)),
                            outline=(*col,int(180*local)),width=2)
        centered(d,(w*.39,y),claim,font(FONT_SANS_BOLD,14),INK)
        centered(d,(w*.74,y),status,font(FONT_SANS_BOLD,14),col)
    seal(im,"DO NOT CONFUSE COSMIC CONSCIOUSNESS WITH THE PERSONAL EGO",
         "localization is not private omnipotence")

def vis_final(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    # field
    for rr in range(45,300,30):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(75*q*(1-rr/330))),width=3)
    # local viewpoint
    origin=(cx-95,cy+35)
    draw_eye(d,*origin,.55,CYAN,int(210*q))
    cone=layer(im.size)
    ImageDraw.Draw(cone).polygon([
        (origin[0]+35,origin[1]),
        (w*.82,h*.22),
        (w*.82,h*.59),
    ],fill=(*CYAN,int(45*q)))
    im.alpha_composite(cone)
    glow_circle(im,cx,cy,17,GOLD,185,12)
    if q>.72:
        centered(d,(cx,h*.68),"CITTA LOCALIZES · ŚIVA REMAINS",
                 font(FONT_SERIF_BOLD,24),GOLD)
    seal(im,"REALITY LOCALIZES ITSELF",
         "the observer is not outside the field; it is one way the field becomes here",GOLD)


VISUALS: dict[str,Callable] = {
    "naive":vis_naive_observer,
    "coemerge":vis_coemergence,
    "localize":vis_field_localizes,
    "body":vis_body_localization,
    "viewpoint":vis_viewpoint_cone,
    "attention":vis_attention_contraction,
    "bodymodel":vis_body_model,
    "worldmodel":vis_world_model,
    "predict":vis_prediction_loop,
    "memory":vis_memory_thread,
    "selfmodel":vis_self_model,
    "kanchukas":vis_kanchukas,
    "triad":vis_subject_object_world,
    "location":vis_location_inside_awareness,
    "brain":vis_brain_on_screen,
    "camera":vis_camera_error,
    "homunculus":vis_no_homunculus,
    "action":vis_action_localizes,
    "emotion":vis_emotion_world,
    "language":vis_language_nouns,
    "object":vis_object_frozen_action,
    "others":vis_other_minds,
    "shared":vis_shared_world,
    "recognition":vis_recognition,
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
    Scene("Default picture",
          "The ordinary picture is simple.",
          6.0,"naive",{}),
    Scene("Person and world",
          "A person exists here. A world exists there. The person looks out and receives information.",
          9.5,"naive",{}),
    Scene("Observer",
          "Consciousness appears to belong to the observer, like a light inside the head.",
          9.0,"naive",{}),

    Scene("Abhinava's reversal",
          "Abhinavagupta reverses the explanatory order.",
          8.0,"coemerge",{}),
    Scene("No preexisting observer",
          "There is not first an observer and then an observed world.",
          8.0,"coemerge",{}),
    Scene("Co-emergence",
          "Subject and object arise together within one act of manifestation.",
          8.5,"coemerge",{}),

    Scene("Field",
          "Begin with no privileged location.",
          6.5,"localize",{}),
    Scene("No here",
          "No here, no there, no center from which the rest appears distant.",
          8.5,"localize",{}),
    Scene("Contraction",
          "Localization begins when the field accepts a center.",
          8.0,"localize",{}),

    Scene("Body",
          "That center becomes a body.",
          6.5,"body",{}),
    Scene("Stable here",
          "A body is a stabilized here: a boundary, a posture, a sensorium, and a range of possible action.",
          10.0,"body",{}),
    Scene("Embodied location",
          "Location is no longer only geometric. It becomes lived.",
          8.0,"body",{}),

    Scene("Viewpoint",
          "A body opens a viewpoint.",
          6.5,"viewpoint",{}),
    Scene("Partial field",
          "Some things are visible. Others are hidden. Some are near enough to affect action. Others fall outside concern.",
          10.0,"viewpoint",{}),
    Scene("Relevance",
          "A viewpoint is not only an angle. It is a field of relevance.",
          8.0,"viewpoint",{}),

    Scene("Attention",
          "Attention further contracts this field.",
          7.0,"attention",{}),
    Scene("Not only filter",
          "It does not merely select one item from a complete world already given.",
          9.0,"attention",{}),
    Scene("World formation",
          "It organizes what becomes figure, background, urgency, and possibility.",
          9.0,"attention",{}),

    Scene("Body model",
          "Modern cognitive science describes part of this through a body-model.",
          8.5,"bodymodel",{}),
    Scene("Binding",
          "Vision, proprioception, interoception, touch, and action are bound into one practical center.",
          10.0,"bodymodel",{}),
    Scene("From here",
          "The organism acts as though these signals belong to one body acting from here.",
          9.0,"bodymodel",{}),

    Scene("World model",
          "The same system constructs a world-model.",
          8.0,"worldmodel",{}),
    Scene("Actionable differences",
          "Objects appear as paths, obstacles, tools, shelters, threats, and opportunities.",
          9.5,"worldmodel",{}),
    Scene("World for action",
          "The perceived world is already structured by possible action.",
          8.0,"worldmodel",{}),

    Scene("Prediction",
          "Predictive processing describes a continuous loop.",
          8.0,"predict",{}),
    Scene("Model predicts",
          "The model predicts incoming sensation.",
          7.0,"predict",{}),
    Scene("Error updates",
          "Prediction error updates the model.",
          7.0,"predict",{}),
    Scene("Action changes input",
          "Action changes the sensory stream so the world and model remain coupled.",
          9.0,"predict",{}),
    Scene("Stabilized self",
          "A stable viewpoint emerges from this circular correction.",
          8.0,"predict",{}),

    Scene("Memory",
          "Memory turns a viewpoint into a history.",
          8.0,"memory",{}),
    Scene("Past of this body",
          "These events happened to this body, in this place, under this name.",
          9.0,"memory",{}),
    Scene("One biography",
          "Separate moments become one biography.",
          7.5,"memory",{}),

    Scene("Self model",
          "The self-model then becomes a defended center.",
          8.0,"selfmodel",{}),
    Scene("Mine",
          "My body. My story. My goals. My threat.",
          7.5,"selfmodel",{}),
    Scene("Useful construction",
          "This construction is useful. It coordinates survival across time.",
          8.5,"selfmodel",{}),
    Scene("Forgotten construction",
          "But the model forgets that it is a model.",
          7.5,"selfmodel",{}),

    Scene("Kanchukas",
          "Abhinavagupta describes localization through the kañcukas, the coverings of finite subjectivity.",
          9.5,"kanchukas",{}),
    Scene("Time and space",
          "Unlimited presence appears as this time and this place.",
          8.0,"kanchukas",{}),
    Scene("Power and knowing",
          "Unlimited agency and knowing appear as limited capacity and partial information.",
          9.0,"kanchukas",{}),
    Scene("Causality",
          "Freedom appears as a chain of causes the finite subject must negotiate.",
          8.5,"kanchukas",{}),

    Scene("No fall outside",
          "The localized subject does not fall outside consciousness.",
          8.0,"triad",{}),
    Scene("Three poles",
          "Consciousness differentiates as knower, known, and knowing.",
          8.5,"triad",{}),
    Scene("One event",
          "The three are real distinctions within one luminous event.",
          8.5,"triad",{}),

    Scene("Location appears",
          "Now ask a stranger question.",
          6.5,"location",{}),
    Scene("Where is here",
          "Where does here appear?",
          6.0,"location",{}),
    Scene("Map in awareness",
          "The map, the body, the room, and the relation between them all appear within experience.",
          9.5,"location",{}),
    Scene("Location content",
          "Location is not outside awareness waiting to contain it. Location itself is one of the things awareness presents.",
          10.0,"location",{}),

    Scene("Brain",
          "The brain also appears.",
          6.5,"brain",{}),
    Scene("Scientific object",
          "It appears as an image, measurement, model, sensation, surgery, scan, or concept.",
          9.0,"brain",{}),
    Scene("Correlation",
          "Neuroscience can discover precise correlations between brain activity and conscious states.",
          9.5,"brain",{}),
    Scene("Prior question",
          "But correlation does not erase the prior question: what does it mean for brain and measurement to appear at all?",
          10.0,"brain",{}),

    Scene("Camera metaphor",
          "Consciousness is often imagined as a camera inside the head.",
          8.0,"camera",{}),
    Scene("Already on screen",
          "But the camera, the head, and the external world are already present on the screen of appearing.",
          9.5,"camera",{}),
    Scene("Wrong direction",
          "Looking for the screen inside the movie reverses the relation.",
          8.0,"camera",{}),

    Scene("Homunculus",
          "A tiny observer inside the brain would solve nothing.",
          8.0,"homunculus",{}),
    Scene("Regress",
          "Something would still need to know the tiny observer's experience.",
          8.0,"homunculus",{}),
    Scene("Self-luminosity",
          "The regress ends only when knowing is present without becoming another object.",
          9.0,"homunculus",{}),

    Scene("Action",
          "A viewpoint is stabilized through action.",
          7.5,"action",{}),
    Scene("Reach",
          "The organism reaches, avoids, eats, speaks, and navigates from one practical origin.",
          9.0,"action",{}),
    Scene("Successful localization",
          "Repeatedly successful action makes the localized center feel self-evident.",
          8.5,"action",{}),

    Scene("Emotion",
          "Emotion deepens localization.",
          7.0,"emotion",{}),
    Scene("Fear world",
          "Fear does not merely add a feeling to a neutral map.",
          8.0,"emotion",{}),
    Scene("Geometry changes",
          "It changes distance, salience, memory, posture, and available action.",
          9.0,"emotion",{}),
    Scene("World from here",
          "The world becomes the world as it matters from here.",
          8.0,"emotion",{}),

    Scene("Language",
          "Language then freezes the coordination into a noun.",
          8.0,"language",{}),
    Scene("Processes",
          "Growing, sensing, predicting, remembering, and defending become the thing called self.",
          9.5,"language",{}),
    Scene("Noun illusion",
          "A stable name hides a moving process.",
          7.5,"language",{}),

    Scene("Objects",
          "The same may be true of objects.",
          7.0,"object",{}),
    Scene("Frozen actions",
          "A tree is growing, exchanging, repairing, bending, sensing, and reproducing.",
          9.0,"object",{}),
    Scene("Tree",
          "We call the stabilized activity a tree.",
          7.5,"object",{}),
    Scene("Verbs and nouns",
          "Reality may be verbs appearing as nouns to a finite viewpoint.",
          8.5,"object",{}),

    Scene("Other centers",
          "Nonduality does not imply that only one empirical viewpoint exists.",
          9.0,"others",{}),
    Scene("Many localizations",
          "Reality localizes as many bodies, histories, and centers of concern.",
          8.5,"others",{}),
    Scene("Irreducible difference",
          "Each perspective remains irreducible at its own scale.",
          8.0,"others",{}),

    Scene("Shared world",
          "Many viewpoints nevertheless participate in one field.",
          8.0,"shared",{}),
    Scene("Relation",
          "They touch, communicate, conflict, cooperate, and transform one another.",
          9.0,"shared",{}),
    Scene("Unity relational",
          "Unity is not sameness. It is the field within which difference becomes relation.",
          9.0,"shared",{}),

    Scene("Recognition",
          "Liberation is not the destruction of localization.",
          8.0,"recognition",{}),
    Scene("Viewpoint remains",
          "The body remains here. The world still appears from somewhere.",
          8.5,"recognition",{}),
    Scene("Scale recognized",
          "What changes is the scale at which the localized subject understands itself.",
          9.0,"recognition",{}),
    Scene("Pratyabhijna",
          "Pratyabhijñā recognizes this center as a contraction of the consciousness that presents the entire field.",
          10.0,"recognition",{}),

    Scene("Science bridge",
          "Modern science can explain how a local perspective is stabilized.",
          8.5,"bridge",{}),
    Scene("Mechanisms",
          "Body maps, attention, prediction, memory, affect, and action are part of the mechanism.",
          9.5,"bridge",{}),
    Scene("Abhinava question",
          "Abhinavagupta asks what appearing, location, and subject-object correlation are in the first place.",
          9.5,"bridge",{}),
    Scene("Different levels",
          "One describes the architecture of a viewpoint. The other describes the ontological field in which viewpoints appear.",
          10.0,"bridge",{}),

    Scene("Discipline",
          "The synthesis must remain disciplined.",
          7.0,"caution",{}),
    Scene("No ego cosmology",
          "The personal ego does not manufacture the universe.",
          7.5,"caution",{}),
    Scene("No scientific proof",
          "Predictive processing does not prove Kashmir Śaivism.",
          7.5,"caution",{}),
    Scene("Real confrontation",
          "The real confrontation concerns explanatory order: does consciousness arise inside the world, or does worldhood arise within manifestation?",
          10.0,"caution",{}),

    Scene("Return",
          "Return to the person looking out at reality.",
          7.5,"final",{}),
    Scene("Reveal",
          "The body, the view, the objects, the distance, and the act of looking all appear together.",
          9.5,"final",{}),
    Scene("Not outside",
          "The observer was never outside the field.",
          7.5,"final",{}),
    Scene("Closing",
          "Reality localizes itself: the field becomes a body, a viewpoint, a world, and finally the recognition that this here was one way the whole learned to appear.",
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
        for oi,fi in enumerate(samples):
            render_frame(
                scene,fi,count,width,height,index*10000+fi
            ).save(frame_dir/f"preview_{oi:02d}.jpg",quality=95)
        return frame_dir

    for fi in range(count):
        p=frame_dir/f"{fi:05d}.jpg"
        if not p.exists():
            render_frame(
                scene,fi,count,width,height,index*10000+fi
            ).save(p,quality=95,subsampling=0)
    return encode_scene(index,fps)

def concatenate(paths):
    txt=OUTPUT/"concat.txt"
    txt.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in paths),
        encoding="utf-8"
    )
    output=OUTPUT/"reality_localizes_itself.mp4"
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
        "title":"reality localizes itself",
        "subtitle":"Abhinavagupta, predictive processing, and the construction of a viewpoint",
        "scene_count":len(SCENES),
        "runtime_seconds":round(cursor,3),
        "shot_duration_range":[5,10],
        "continuity_object":"gold field contracting into cyan viewpoint cone",
        "visual_arc":[
            "field",
            "contraction",
            "body",
            "viewpoint",
            "body-model",
            "world-model",
            "self-model",
            "recognition"
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
        d.text((x+8,y+th+7),
               f"{index:02d}  {scene.title}",
               font=lf,fill=INK)

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
