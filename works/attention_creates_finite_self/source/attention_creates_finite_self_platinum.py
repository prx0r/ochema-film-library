#!/usr/bin/env python3
"""
ATTENTION CREATES THE FINITE SELF
Abhinavagupta on Avadhāna, Contraction, Salience, and the Birth of "Me"

An original dark-spectrum Platinum-house procedural visual essay.

CENTRAL CLAIM
-------------
Modern cognitive science often describes attention as selection:

    many signals
      ↓
    competition
      ↓
    selected information
      ↓
    improved processing

Abhinavagupta pushes the question deeper.

Selection does not merely choose an object.
It helps produce the finite subject for whom that object matters.

Attention contracts an open field into:
• figure and background;
• here and elsewhere;
• urgent and irrelevant;
• mine and not-mine;
• possible and impossible;
• self and world.

The finite self is therefore not a thing that later uses attention.
It is continuously stabilized by repeated acts of attentional contraction.

FILM THESIS
-----------
Attention is the cutting edge of finitude.

The film follows:

open luminosity
→ salience
→ exclusion
→ fixation
→ practical world
→ defended identity
→ obsession
→ attentional capture
→ contemplative suspension
→ panoramic awareness
→ precise attention without contraction

The conclusion is not that attention should disappear.
Liberation is attention becoming transparent to the field from which it selects.

HOUSE RULES
-----------
• Every scene lasts 5–10 seconds.
• Every scene visibly transforms.
• Dark prismatic palette: black, ultraviolet, cyan, acid green,
  crimson, magenta, molten gold, and brief ivory revelation.
• No static slide layouts.
• Mature frame near u=0.72.
• Continuity object: a gold omnidirectional field compressed into a cyan beam,
  hardened into a crimson tunnel, then reopened as a many-colored mandala.
• Every scene must animate the exact claim being spoken.

OUTPUT
------
output_attention_finite_self/
  frames/
  scenes/
  attention_creates_finite_self.mp4
  narration_timeline.json
  contact_sheet.jpg

USAGE
-----
python attention_creates_finite_self_platinum.py
python attention_creates_finite_self_platinum.py --preview
python attention_creates_finite_self_platinum.py --scene 12
python attention_creates_finite_self_platinum.py --fps 12 --width 1920 --height 1080
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
OUTPUT = ROOT / "output_attention_finite_self"
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
    q=clamp((x-a)/(b-a))
    return q*q*(3-2*q)
def ease(t):
    t=clamp(t)
    return .5-.5*math.cos(math.pi*t)
def pulse(t,speed=1.0,phase=0.0):
    return .5+.5*math.sin(math.tau*(speed*t+phase))

def font(path,size):
    for candidate in (path,FONT_SERIF,FONT_SANS):
        try:
            return ImageFont.truetype(candidate,size)
        except OSError:
            pass
    return ImageFont.load_default()

def layer(size):
    return Image.new("RGBA",size,(0,0,0,0))

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
    if len(pts)<2:
        return
    gl=layer(im.size)
    gd=ImageDraw.Draw(gl)
    gd.line(pts,fill=(*color,alpha),width=width*3,joint="curve")
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).line(
        pts,fill=(*color,min(255,alpha+20)),width=width,joint="curve"
    )
    im.alpha_composite(fg)

def partial(pts,a):
    if not pts:
        return []
    a=clamp(a)
    if a>=1:
        return pts
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

def draw_eye(d,cx,cy,scale=1.0,color=CYAN,alpha=210):
    d.arc((cx-90*scale,cy-45*scale,cx+90*scale,cy+45*scale),
          0,180,fill=(*color,alpha),width=max(2,int(4*scale)))
    d.arc((cx-90*scale,cy-45*scale,cx+90*scale,cy+45*scale),
          180,360,fill=(*color,alpha),width=max(2,int(4*scale)))
    d.ellipse((cx-22*scale,cy-22*scale,cx+22*scale,cy+22*scale),
              fill=(*color,alpha))

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

def radial_points(cx,cy,r,count=160,turns=1.5,phase=0.0):
    pts=[]
    for i in range(count):
        q=i/(count-1)
        a=q*math.tau*turns+phase
        rr=r*(.12+.88*q)
        pts.append((cx+math.cos(a)*rr,cy+math.sin(a)*rr*.62))
    return pts

def cloud(w,h,count,seed):
    rng=random.Random(seed)
    return [(rng.uniform(w*.10,w*.90),
             rng.uniform(h*.15,h*.68),
             rng.uniform(2,7)) for _ in range(count)]


# =============================================================================
# VISUALS
# =============================================================================

def vis_open_field(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    colors=[GOLD,CYAN,VIOLET,GREEN,MAGENTA,ORANGE]
    for i,(x,y,r) in enumerate(cloud(w,h,90,2)):
        glow_circle(im,x,y,r,colors[i%len(colors)],95,6)
    for rr in range(50,300,32):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(65*q*(1-rr/330))),width=3)
    seal(im,"BEFORE ATTENTION, THE FIELD HAS NO PRIVILEGED CENTER",
         "many possibilities coexist without one becoming the world")

def vis_salience_birth(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    pts=cloud(w,h,70,4)
    target=pts[31]
    q=ease(u)
    for i,(x,y,r) in enumerate(pts):
        dist=math.dist((x,y),target)
        alpha=190 if dist<80 else int(100*(1-q))
        glow_circle(im,x,y,r,[CYAN,VIOLET,GREEN,MAGENTA][i%4],alpha,6)
    for rr in range(35,230,28):
        d.ellipse((target[0]-rr,target[1]-rr,
                   target[0]+rr,target[1]+rr),
                  outline=(*GOLD,int(80*q*(1-rr/255))),width=3)
    seal(im,"SALIENCE IS THE BIRTH OF IMPORTANCE",
         "one difference begins to reorganize the field around itself")

def vis_beam(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    origin=(w*.24,h*.42)
    q=ease(u)
    draw_eye(d,*origin,.58,CYAN,190)
    width=lerp(h*.46,h*.08,q)
    cone=layer(im.size)
    cd=ImageDraw.Draw(cone)
    cd.polygon([
        (origin[0]+35,origin[1]),
        (w*.88,origin[1]-width/2),
        (w*.88,origin[1]+width/2),
    ],fill=(*CYAN,int(45+35*q)))
    im.alpha_composite(cone)
    glow_circle(im,w*.76,h*.42,15,GOLD,185,11)
    seal(im,"ATTENTION COMPRESSES POSSIBILITY INTO A BEAM",
         "precision increases as the rest of the field disappears")

def vis_figure_ground(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    pts=cloud(w,h,70,7)
    target=(w*.58,h*.38)
    q=ease(u)
    for i,(x,y,r) in enumerate(pts):
        fg=math.dist((x,y),target)<105
        col=GOLD if fg else SILVER
        alpha=185 if fg else int(120*(1-q*.82))
        glow_circle(im,x,y,r,col,alpha,6)
    d.ellipse((target[0]-115,target[1]-80,target[0]+115,target[1]+80),
              outline=(*GOLD,int(200*q)),width=5)
    seal(im,"FIGURE AND GROUND ARE CO-PRODUCED",
         "the selected object and the excluded background arise together")

def vis_here_there(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    glow_circle(im,cx,cy,15,GOLD,185,11)
    r=lerp(260,90,q)
    d.ellipse((cx-r,cy-r*.62,cx+r,cy+r*.62),outline=(*CYAN,205),width=5)
    centered(d,(cx,h*.68),"HERE",font(FONT_SERIF_BOLD,27),GOLD)
    for i,label in enumerate(["THERE","ELSEWHERE","OUTSIDE"]):
        a=i*math.tau/3-math.pi/2
        x=cx+math.cos(a)*230
        y=cy+math.sin(a)*135
        centered(d,(x,y),label,font(FONT_SANS_BOLD,13),VIOLET)
    seal(im,"A CENTER CREATES HERE AND THERE",
         "attention localizes the subject while spatializing the world")

def vis_relevance_world(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    origin=(w*.28,h*.43)
    q=ease(u)
    draw_body(d,*origin,.58,WHITE,175)
    items=[
        ("FOOD",w*.62,h*.26,GREEN),
        ("THREAT",w*.78,h*.40,CRIMSON),
        ("PATH",w*.62,h*.58,CYAN),
        ("ALLY",w*.82,h*.58,GOLD),
    ]
    for lab,x,y,col in items:
        glow_circle(im,x,y,12,col,155,9)
        centered(d,(x,y+28),lab,font(FONT_SANS_BOLD,12),col)
        glow_line(im,partial([(origin[0]+35,origin[1]),(x,y)],q),
                  col,3,135,8)
    seal(im,"ATTENTION BUILDS A WORLD OF RELEVANCE",
         "things appear as what can be used, feared, desired, or ignored")

def vis_mine_notmine(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    objects=[
        (w*.25,h*.28,CYAN),
        (w*.75,h*.28,VIOLET),
        (w*.25,h*.56,GREEN),
        (w*.75,h*.56,CRIMSON),
    ]
    for i,(x,y,col) in enumerate(objects):
        glow_circle(im,x,y,13,col,150,9)
        if i%2==0:
            glow_line(im,partial([(x,y),(cx,cy)],q),GOLD,4,155,9)
    d.ellipse((cx-125,cy-90,cx+125,cy+90),outline=(*GOLD,190),width=5)
    centered(d,(cx,h*.68),"MINE",font(FONT_SERIF_BOLD,28),GOLD)
    seal(im,"REPEATED ATTENTION DRAWS THE BORDER OF MINE",
         "ownership is salience stabilized across time")

def vis_identity_tunnel(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    draw_body(d,cx,cy,.64,WHITE,170)
    words=["BODY","NAME","ROLE","STORY","GOAL"]
    for i,word in enumerate(words):
        rr=lerp(260,95+i*10,q)
        d.ellipse((cx-rr,cy-rr*.66,cx+rr,cy+rr*.66),
                  outline=(*[CYAN,VIOLET,GREEN,CRIMSON,GOLD][i],170),width=4)
        if q>.45:
            centered(d,(cx,cy-rr*.66-14),word,font(FONT_SANS_BOLD,12),
                     [CYAN,VIOLET,GREEN,CRIMSON,GOLD][i])
    seal(im,"THE SELF IS AN ATTENTIONAL TUNNEL",
         "what is repeatedly selected begins to define the selector")

def vis_threat_capture(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    origin=(w*.30,h*.42)
    q=ease(u)
    draw_body(d,*origin,.58,WHITE,170)
    threats=[(w*.62,h*.22),(w*.80,h*.40),(w*.66,h*.62)]
    for x,y in threats:
        glow_circle(im,x,y,13,CRIMSON,170,10)
        glow_line(im,partial([(origin[0]+35,origin[1]),(x,y)],q),
                  CRIMSON,4,160,9)
    cone=layer(im.size)
    ImageDraw.Draw(cone).polygon([
        (origin[0]+25,origin[1]),
        (w*.92,h*.12),
        (w*.92,h*.70),
    ],fill=(*CRIMSON,int(42*q)))
    im.alpha_composite(cone)
    seal(im,"THREAT CAPTURES THE ENTIRE ATTENTIONAL FIELD",
         "one danger becomes the organizing principle of reality")

def vis_desire_capture(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    glow_circle(im,cx,cy,14,GOLD,180,11)
    targets=[
        (w*.20,h*.23,MAGENTA),
        (w*.80,h*.23,CYAN),
        (w*.20,h*.59,GREEN),
        (w*.80,h*.59,ORANGE),
    ]
    for i,(x,y,col) in enumerate(targets):
        glow_circle(im,x,y,13,col,155,9)
        mid=(lerp(cx,x,.52),lerp(cy,y,.52)+math.sin(i)*35)
        glow_line(im,partial([(cx,cy),mid,(x,y)],q),col,4,155,9)
    r=lerp(40,145,q)
    d.ellipse((cx-r,cy-r*.62,cx+r,cy+r*.62),outline=(*CRIMSON,190),width=5)
    seal(im,"DESIRE MAKES ABSENCE MORE VISIBLE THAN PRESENCE",
         "attention is pulled toward what the self imagines will complete it")

def vis_obsession(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    target=(cx,cy)
    glow_circle(im,*target,18,CRIMSON,195,13)
    for i in range(18):
        a=i*math.tau/18+t*.18
        r=lerp(250,90,q)
        x=cx+math.cos(a)*r
        y=cy+math.sin(a)*r*.62
        glow_circle(im,x,y,7,[VIOLET,CYAN,MAGENTA][i%3],110,6)
        glow_line(im,[(x,y),target],CRIMSON,2,95,7)
    seal(im,"OBSESSION IS ATTENTION THAT CAN NO LONGER RELEASE",
         "the selected object occupies the place of the whole field")

def vis_algorithm_capture(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    q=ease(u)
    cards=[]
    for j in range(3):
        for i in range(5):
            cards.append((w*.16+i*w*.17,h*.22+j*h*.15))
    for idx,(x,y) in enumerate(cards):
        col=[CRIMSON,MAGENTA,CYAN,VIOLET,GREEN][idx%5]
        d.rounded_rectangle((x-55,y-38,x+55,y+38),radius=10,
                            outline=(*col,150),width=3)
    beam_x=lerp(w*.14,w*.86,q)
    gl=layer(im.size)
    ImageDraw.Draw(gl).rectangle((beam_x-32,h*.16,beam_x+32,h*.66),
                                 fill=(*GOLD,45))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(16)))
    seal(im,"ATTENTION CAN BE INDUSTRIALLY CAPTURED",
         "prediction systems learn which differences keep the self contracted")

def vis_notification_fracture(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    draw_body(d,cx,cy,.62,WHITE,170)
    icons=[
        (w*.24,h*.23,CRIMSON),
        (w*.76,h*.23,CYAN),
        (w*.22,h*.58,MAGENTA),
        (w*.78,h*.58,GREEN),
        (w*.50,h*.18,GOLD),
    ]
    for i,(x,y,col) in enumerate(icons):
        glow_circle(im,x,y,13,col,160,9)
        glow_line(im,partial([(cx,cy),(x,y)],q),col,4,145,9)
    for i in range(14):
        a=i*math.tau/14
        p0=(cx,cy)
        p1=(cx+math.cos(a)*lerp(20,190,q),cy+math.sin(a)*lerp(12,120,q))
        glow_line(im,[p0,p1],[CRIMSON,VIOLET,CYAN][i%3],2,105,7)
    seal(im,"FRAGMENTED ATTENTION PRODUCES A FRAGMENTED SELF",
         "every interruption briefly installs a new world")

def vis_task_switch(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    tasks=[
        ("WRITE",w*.18,CYAN),
        ("MESSAGE",w*.34,MAGENTA),
        ("SEARCH",w*.50,GOLD),
        ("VIDEO",w*.66,CRIMSON),
        ("RETURN",w*.82,GREEN),
    ]
    q=ease(u)
    for i,(lab,x,col) in enumerate(tasks):
        glow_circle(im,x,h*.40,12,col,150,8)
        centered(d,(x,h*.67),lab,font(FONT_SANS_BOLD,12),col)
        if i<len(tasks)-1:
            arrow(d,(x+15,h*.40),(tasks[i+1][1]-15,h*.40),
                  (*tasks[i+1][2],int(155*q)),2,7)
    seal(im,"TASK SWITCHING REBUILDS THE SELF AGAIN AND AGAIN",
         "each task installs a different field of goals, memory, and relevance")

def vis_pain_zoom(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    draw_body(d,cx,cy,.64,WHITE,165)
    target=(cx+45,cy+70)
    glow_circle(im,*target,14,CRIMSON,190,12)
    r=lerp(240,45,q)
    d.ellipse((target[0]-r,target[1]-r,target[0]+r,target[1]+r),
              outline=(*CRIMSON,200),width=5)
    seal(im,"PAIN COLLAPSES THE BODY INTO ONE LOCATION",
         "the whole organism becomes the place that hurts")

def vis_rasa_release(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    colors=[CRIMSON,VIOLET,CYAN,GREEN,ORANGE,MAGENTA,GOLD]
    glow_circle(im,cx,cy,16,CRIMSON,180,12)
    for i,col in enumerate(colors):
        a=i*math.tau/len(colors)+t*.08
        r=lerp(30,205,q)
        x=cx+math.cos(a)*r
        y=cy+math.sin(a)*r*.62
        glow_circle(im,x,y,13,col,145,9)
        glow_line(im,partial([(cx,cy),(x,y)],q),col,3,120,8)
    seal(im,"RASA RELEASES ATTENTION FROM PRIVATE CONSEQUENCE",
         "emotion expands when it is no longer trapped inside mine")

def vis_meditation_release(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    draw_body(d,cx,cy,.64,WHITE,170)
    beam=[(cx,h*.17),(cx,h*.66)]
    glow_line(im,partial(beam,q),CYAN,5,180,11)
    for rr in range(45,280,30):
        d.ellipse((cx-rr*q,cy-rr*.62*q,cx+rr*q,cy+rr*.62*q),
                  outline=(*GOLD,int(72*q*(1-rr/310))),width=3)
    seal(im,"MEDITATION DOES NOT DESTROY ATTENTION",
         "it reveals the field surrounding the beam")

def vis_panorama(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    colors=[GOLD,CYAN,VIOLET,GREEN,MAGENTA,ORANGE]
    for i,(x,y,r) in enumerate(cloud(w,h,85,32)):
        glow_circle(im,x,y,r,colors[i%len(colors)],100,6)
    for rr in range(45,300,30):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(65*q*(1-rr/330))),width=3)
    glow_circle(im,cx,cy,14,GOLD,180,11)
    seal(im,"PANORAMIC AWARENESS HOLDS FIGURE WITHOUT ERASING FIELD",
         "precision and openness no longer oppose one another")

def vis_open_focus(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    origin=(w*.25,h*.42)
    q=ease(u)
    draw_eye(d,*origin,.58,CYAN,190)
    cone=layer(im.size)
    cd=ImageDraw.Draw(cone)
    cd.polygon([
        (origin[0]+35,origin[1]),
        (w*.88,h*.17),
        (w*.88,h*.67),
    ],fill=(*CYAN,38))
    im.alpha_composite(cone)
    for rr in range(45,250,30):
        d.ellipse((w*.60-rr,w*0+h*.40-rr*.62,
                   w*.60+rr,h*.40+rr*.62),
                  outline=(*GOLD,int(65*q*(1-rr/280))),width=3)
    glow_circle(im,w*.70,h*.40,15,GOLD,180,11)
    seal(im,"LIBERATED ATTENTION IS OPEN AND PRECISE",
         "the object is vivid without becoming the whole universe")

def vis_aham_idam(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.30,h*.40)
    right=(w*.70,h*.40)
    q=ease(u)
    glow_circle(im,*left,16,GOLD,185,11)
    glow_circle(im,*right,16,VIOLET,175,10)
    centered(d,(left[0],h*.68),"AHAM",font(FONT_SERIF_BOLD,27),GOLD)
    centered(d,(right[0],h*.68),"IDAM",font(FONT_SERIF_BOLD,27),VIOLET)
    glow_line(im,partial([left,(w*.50,h*.20),right],q),CYAN,5,190,12)
    for rr in range(45,260,30):
        d.ellipse((w*.50-rr,w*0+h*.40-rr*.62,
                   w*.50+rr,h*.40+rr*.62),
                  outline=(*GOLD,int(62*q*(1-rr/290))),width=3)
    seal(im,"AHAM AND IDAM ARE POLES WITHIN ONE ACT",
         "I and this arise together through directed awareness")

def vis_ritual_attention(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    centers=[
        ("SOUND",cx,h*.20,MAGENTA),
        ("IMAGE",w*.72,cy,CYAN),
        ("BREATH",cx,h*.60,GREEN),
        ("BODY",w*.28,cy,CRIMSON),
    ]
    for lab,x,y,col in centers:
        glow_circle(im,x,y,13,col,155,9)
        centered(d,(x,y+28),lab,font(FONT_SANS_BOLD,12),col)
        glow_line(im,partial([(x,y),(cx,cy)],q),col,4,145,9)
    glow_circle(im,cx,cy,18,GOLD,195,13)
    seal(im,"RITUAL COORDINATES MULTIPLE STREAMS INTO ONE ATTENTIONAL BODY",
         "sound, image, breath, and gesture become a single field")

def vis_mantra_focus(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    syllables=["A","HA","M"]
    for i,s in enumerate(syllables):
        a=i*math.tau/3-math.pi/2+t*.12
        r=175
        x=cx+math.cos(a)*r
        y=cy+math.sin(a)*105
        centered(d,(x,y),s,font(FONT_SERIF_BOLD,36),
                 [MAGENTA,CYAN,GOLD][i])
        glow_line(im,partial([(x,y),(cx,cy)],q),
                  [MAGENTA,CYAN,GOLD][i],5,175,11)
    glow_circle(im,cx,cy,18,GOLD,195,13)
    seal(im,"MANTRA REWRITES THE ATTRACTOR OF ATTENTION",
         "repetition stabilizes a new center of recognition")

def vis_ethical_attention(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    centers=[
        (w*.25,h*.30,CYAN),
        (w*.75,h*.30,VIOLET),
        (w*.25,h*.56,GREEN),
        (w*.75,h*.56,CRIMSON),
    ]
    q=ease(u)
    for x,y,col in centers:
        glow_circle(im,x,y,14,col,160,9)
    for i,(x,y,col) in enumerate(centers):
        for j,(x2,y2,col2) in enumerate(centers):
            if j>i:
                glow_line(im,partial([(x,y),(x2,y2)],q),
                          mix(col,col2,.5),2,95,7)
    seal(im,"WHAT RECEIVES ATTENTION ENTERS THE FIELD OF VALUE",
         "neglect is not neutral when another center depends on being seen")

def vis_science_bridge(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.30,h*.40)
    right=(w*.70,h*.40)
    q=ease(u)
    # competition model
    nodes=[
        (left[0],left[1]-85,VIOLET),
        (left[0]+95,left[1],CRIMSON),
        (left[0],left[1]+85,GREEN),
        (left[0]-95,left[1],CYAN),
    ]
    for x,y,col in nodes:
        glow_circle(im,x,y,10,col,145,8)
        glow_line(im,[(x,y),left],col,3,110,8)
    glow_circle(im,*left,14,GOLD,175,10)
    # consciousness field
    for rr in range(35,155,25):
        d.ellipse((right[0]-rr,right[1]-rr*.62,
                   right[0]+rr,right[1]+rr*.62),
                  outline=(*GOLD,int(75*q*(1-rr/175))),width=3)
    glow_circle(im,*right,14,GOLD,180,11)
    centered(d,(left[0],h*.68),"SELECTION MECHANISMS",
             font(FONT_SANS_BOLD,13),CYAN)
    centered(d,(right[0],h*.68),"PRODUCTION OF FINITUDE",
             font(FONT_SANS_BOLD,13),GOLD)
    glow_line(im,partial([left,(w*.50,h*.18),right],q),VIOLET,4,165,10)
    seal(im,"SCIENCE ASKS WHAT ATTENTION SELECTS",
         "ABHINAVA ASKS WHAT KIND OF SUBJECT SELECTION CREATES")

def vis_caution(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    rows=[
        ("ATTENTION MODULATES PERCEPTION","SUPPORTED",GREEN),
        ("ALL FINITUDE IS ONLY ATTENTIONAL","TOO SIMPLE",CRIMSON),
        ("REPEATED SALIENCE SHAPES IDENTITY","SUPPORTED",CYAN),
        ("MEDITATION MAKES ATTENTION UNLIMITED","NOT ESTABLISHED",CRIMSON),
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
    seal(im,"ATTENTION IS ONE MECHANISM OF CONTRACTION, NOT THE WHOLE METAPHYSICS",
         "body, memory, affect, language, and action also stabilize the finite self")

def vis_final(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    colors=[GOLD,CYAN,VIOLET,GREEN,MAGENTA,ORANGE,CRIMSON,VENOM]
    for i,col in enumerate(colors):
        a=i*math.tau/len(colors)+t*.06
        r=lerp(260,145,q)
        x=cx+math.cos(a)*r
        y=cy+math.sin(a)*r*.62
        glow_circle(im,x,y,12,col,145,9)
        glow_line(im,partial([(x,y),(cx,cy)],q),col,3,125,8)
    # beam remains but field also visible
    glow_line(im,[(w*.20,cy),(w*.80,cy)],CYAN,5,175,11)
    for rr in range(45,310,30):
        d.ellipse((cx-rr*q,cy-rr*.62*q,cx+rr*q,cy+rr*.62*q),
                  outline=(*GOLD,int(72*q*(1-rr/340))),width=3)
    glow_circle(im,cx,cy,18,GOLD,205,14)
    if q>.72:
        centered(d,(cx,h*.68),"AVADHĀNA WITHOUT BANDHA",
                 font(FONT_SERIF_BOLD,25),GOLD)
    seal(im,"ATTENTION CREATES THE FINITE SELF",
         "liberation is not losing focus, but seeing the field that every act of focus temporarily conceals",GOLD)


VISUALS: dict[str,Callable] = {
    "open":vis_open_field,
    "salience":vis_salience_birth,
    "beam":vis_beam,
    "figure":vis_figure_ground,
    "here":vis_here_there,
    "relevance":vis_relevance_world,
    "mine":vis_mine_notmine,
    "identity":vis_identity_tunnel,
    "threat":vis_threat_capture,
    "desire":vis_desire_capture,
    "obsession":vis_obsession,
    "algorithm":vis_algorithm_capture,
    "notifications":vis_notification_fracture,
    "switch":vis_task_switch,
    "pain":vis_pain_zoom,
    "rasa":vis_rasa_release,
    "meditation":vis_meditation_release,
    "panorama":vis_panorama,
    "openfocus":vis_open_focus,
    "ahamidam":vis_aham_idam,
    "ritual":vis_ritual_attention,
    "mantra":vis_mantra_focus,
    "ethics":vis_ethical_attention,
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
    Scene("Open field",
          "Imagine awareness before anything has become important.",
          7.5,"open",{}),
    Scene("No privileged center",
          "Color, sound, memory, sensation, and possibility coexist without one becoming the center.",
          9.5,"open",{}),
    Scene("Potential",
          "The field is not empty. It is uncommitted.",
          7.5,"open",{}),

    Scene("Salience",
          "Then one difference begins to matter.",
          7.0,"salience",{}),
    Scene("Importance",
          "A movement, sound, face, pain, desire, or threat brightens against the rest.",
          9.0,"salience",{}),
    Scene("First contraction",
          "Salience is the first contraction of the field.",
          8.0,"salience",{}),

    Scene("Beam",
          "Attention compresses possibility into a beam.",
          8.0,"beam",{}),
    Scene("Precision",
          "The selected object becomes clearer.",
          7.0,"beam",{}),
    Scene("Loss",
          "But precision is purchased by the disappearance of alternatives.",
          8.5,"beam",{}),

    Scene("Figure ground",
          "Attention does not merely discover a figure.",
          7.5,"figure",{}),
    Scene("Co-production",
          "It co-produces figure and background.",
          7.5,"figure",{}),
    Scene("World split",
          "The object and the excluded field arise together.",
          8.0,"figure",{}),

    Scene("Here",
          "A finite center begins to form.",
          7.0,"here",{}),
    Scene("There",
          "Here appears with there.",
          6.5,"here",{}),
    Scene("Spatial self",
          "Attention localizes the subject while spatializing the world.",
          8.5,"here",{}),

    Scene("Relevance",
          "The world now appears through relevance.",
          8.0,"relevance",{}),
    Scene("Action map",
          "Food, threat, path, ally, shelter, obstacle.",
          8.0,"relevance",{}),
    Scene("Not neutral objects",
          "Things appear as what can be used, feared, desired, or ignored.",
          9.0,"relevance",{}),

    Scene("Mine",
          "Repeated attention draws the border of mine.",
          8.0,"mine",{}),
    Scene("Investment",
          "What is continually monitored becomes invested with ownership.",
          8.5,"mine",{}),
    Scene("Not mine",
          "The rest becomes background, environment, or not-my-problem.",
          8.5,"mine",{}),

    Scene("Identity tunnel",
          "The self is not one object hidden behind experience.",
          8.0,"identity",{}),
    Scene("Repeated selection",
          "It is a tunnel stabilized by repeated selection.",
          8.0,"identity",{}),
    Scene("Self contents",
          "Body, name, role, story, injury, goal.",
          8.0,"identity",{}),
    Scene("Selector defined",
          "What is repeatedly selected begins to define the selector.",
          8.5,"identity",{}),

    Scene("Threat capture",
          "Fear demonstrates the process with brutal clarity.",
          8.0,"threat",{}),
    Scene("One danger",
          "One danger captures the attentional field.",
          7.5,"threat",{}),
    Scene("Threat world",
          "Distance, memory, posture, and possibility reorganize around threat.",
          9.0,"threat",{}),
    Scene("Whole reality",
          "A local danger becomes the organizing principle of reality.",
          8.5,"threat",{}),

    Scene("Desire capture",
          "Desire captures attention through absence.",
          8.0,"desire",{}),
    Scene("Missing completion",
          "What is missing becomes more vivid than what is present.",
          8.5,"desire",{}),
    Scene("Routes",
          "The world becomes a map of routes toward imagined completion.",
          8.5,"desire",{}),

    Scene("Obsession",
          "Obsession is attention that can no longer release.",
          8.0,"obsession",{}),
    Scene("Object as whole",
          "The selected object occupies the place of the whole field.",
          8.0,"obsession",{}),
    Scene("Compulsion",
          "Attention ceases to be a capacity and becomes a compulsion.",
          8.5,"obsession",{}),

    Scene("Industrial capture",
          "Modern systems learn to capture this mechanism.",
          8.0,"algorithm",{}),
    Scene("Prediction",
          "They predict which image, outrage, desire, or uncertainty will hold the beam.",
          9.5,"algorithm",{}),
    Scene("Contracted user",
          "The commodity is not information. It is the repeatedly contracted user.",
          9.5,"algorithm",{}),

    Scene("Notification",
          "Every interruption briefly installs a new world.",
          8.0,"notifications",{}),
    Scene("Fragment",
          "Message, headline, alert, memory, task.",
          8.0,"notifications",{}),
    Scene("Fragmented self",
          "Fragmented attention produces a fragmented self.",
          8.0,"notifications",{}),

    Scene("Task switching",
          "Task switching is not merely moving between windows.",
          8.0,"switch",{}),
    Scene("Rebuild",
          "Each task rebuilds goals, memory, relevance, and identity.",
          8.5,"switch",{}),
    Scene("Many selves",
          "The finite self is reconstructed many times each minute.",
          8.5,"switch",{}),

    Scene("Pain",
          "Pain can collapse the entire body into one location.",
          8.0,"pain",{}),
    Scene("Body becomes wound",
          "The organism becomes the place that hurts.",
          8.0,"pain",{}),
    Scene("Attention and suffering",
          "Suffering grows when attention cannot rediscover the wider body.",
          9.0,"pain",{}),

    Scene("Abhinava",
          "Abhinavagupta gives this contraction a metaphysical scale.",
          8.5,"ahamidam",{}),
    Scene("Aham idam",
          "Aham, I, and idam, this, are poles within one act of awareness.",
          9.0,"ahamidam",{}),
    Scene("Directed awareness",
          "Directed awareness differentiates knower and known without producing two independent substances.",
          10.0,"ahamidam",{}),

    Scene("Attention and bondage",
          "Bondage begins when the selected pole forgets the field.",
          8.0,"identity",{}),
    Scene("Object fixation",
          "The object appears independent.",
          7.0,"figure",{}),
    Scene("Subject fixation",
          "The subject appears sealed inside itself.",
          7.0,"identity",{}),
    Scene("Mutual imprisonment",
          "The finite self and its world imprison one another.",
          8.5,"identity",{}),

    Scene("Rasa",
          "Rasa loosens attention from private consequence.",
          8.0,"rasa",{}),
    Scene("Emotion expands",
          "Emotion remains vivid while ownership falls away.",
          8.5,"rasa",{}),
    Scene("Field returns",
          "The field returns around the selected feeling.",
          8.0,"rasa",{}),

    Scene("Meditation",
          "Meditation performs a related reversal.",
          8.0,"meditation",{}),
    Scene("Beam visible",
          "The beam of attention becomes visible as a movement within awareness.",
          8.5,"meditation",{}),
    Scene("Not whole",
          "What had seemed to be the whole mind is recognized as one operation.",
          9.0,"meditation",{}),

    Scene("Panorama",
          "Panoramic awareness does not blur the object.",
          8.0,"panorama",{}),
    Scene("Figure with field",
          "It holds figure without erasing field.",
          8.0,"panorama",{}),
    Scene("Precision openness",
          "Precision and openness no longer oppose one another.",
          8.5,"panorama",{}),

    Scene("Open focus",
          "Liberated attention can remain precise.",
          8.0,"openfocus",{}),
    Scene("No capture",
          "The object is vivid without becoming the whole universe.",
          8.0,"openfocus",{}),
    Scene("Transparent selection",
          "Selection becomes transparent to the field from which it selects.",
          9.0,"openfocus",{}),

    Scene("Ritual",
          "Tantric ritual engineers this attentional transformation.",
          8.5,"ritual",{}),
    Scene("Coordination",
          "Sound, image, breath, posture, direction, and memory are coordinated.",
          9.0,"ritual",{}),
    Scene("Attentional body",
          "Many streams become one attentional body.",
          8.0,"ritual",{}),

    Scene("Mantra",
          "Mantra rewrites the attractor of attention.",
          8.0,"mantra",{}),
    Scene("Repetition",
          "Repetition stabilizes one luminous pattern against distraction.",
          8.5,"mantra",{}),
    Scene("New center",
          "The finite self is reorganized around a new center of recognition.",
          9.0,"mantra",{}),

    Scene("Ethics",
          "Attention is also ethical.",
          7.0,"ethics",{}),
    Scene("Value",
          "What receives attention enters the field of value.",
          8.0,"ethics",{}),
    Scene("Neglect",
          "Neglect is not neutral when another center depends on being seen.",
          9.0,"ethics",{}),

    Scene("Science",
          "Modern science explains competition, salience, working memory, and attentional control.",
          9.5,"bridge",{}),
    Scene("Selection question",
          "It asks what gets selected and how selection improves processing.",
          8.5,"bridge",{}),
    Scene("Abhinava question",
          "Abhinavagupta asks what kind of finite subject selection continually creates.",
          9.5,"bridge",{}),

    Scene("Discipline",
          "The comparison must remain disciplined.",
          7.0,"caution",{}),
    Scene("Not everything",
          "Attention is not the only mechanism of finitude.",
          7.5,"caution",{}),
    Scene("Other structures",
          "Body, affect, language, memory, action, and social relation also stabilize the self.",
          9.5,"caution",{}),
    Scene("No infinity claim",
          "Meditation does not make a human nervous system literally unlimited.",
          8.5,"caution",{}),

    Scene("Return",
          "Return to the original field.",
          6.5,"final",{}),
    Scene("Beam remains",
          "The beam remains.",
          6.0,"final",{}),
    Scene("Field remains",
          "But the field is no longer forgotten.",
          7.0,"final",{}),
    Scene("Closing",
          "Attention creates the finite self: liberation is not losing focus, but seeing the luminous field that every act of focus temporarily conceals.",
          10.0,"final",{}),
]


def render_frame(scene,frame_index,frame_count,width,height,seed):
    u=frame_index/max(1,frame_count-1)
    t=u*scene.duration
    light=.15*smoothstep(.42,1.0,u) if scene.visual in {
        "rasa","meditation","panorama","openfocus","final"
    } else 0.0
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
    output=OUTPUT/"attention_creates_finite_self.mp4"
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
        "title":"attention creates the finite self",
        "subtitle":"Abhinavagupta on contraction, salience, and the birth of me",
        "scene_count":len(SCENES),
        "runtime_seconds":round(cursor,3),
        "shot_duration_range":[5,10],
        "continuity_object":"gold field compressed into cyan beam, hardened into crimson tunnel",
        "palette":"black, ultraviolet, cyan, acid green, crimson, magenta, molten gold",
        "visual_arc":[
            "open field","salience","beam","figure-ground","relevance",
            "ownership","identity tunnel","capture","fragmentation",
            "panoramic awareness","open precision"
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
