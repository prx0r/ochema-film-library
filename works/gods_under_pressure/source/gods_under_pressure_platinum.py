#!/usr/bin/env python3
"""
THE GODS ARE WHAT CONSCIOUSNESS LOOKS LIKE UNDER PRESSURE
Abhinavagupta on Terror, Desire, Possession, and the Birth of Divine Forms

An original dark-spectrum Platinum-house procedural visual essay.

CENTRAL CLAIM
-------------
Abhinavagupta does not treat consciousness as a blank, peaceful witness.

Consciousness has powers.
Under contraction, those powers appear as fear, desire, rage, fixation,
memory, identity, compulsion, ecstasy, and divine form.

A deity is not merely a supernatural person added to the universe.
In the Tantric imagination, a deity is a precise configuration of consciousness:
a patterned relation among awareness, affect, body, attention, action, and world.

The terrifying forms matter because recognition must include what ordinary
spirituality excludes.

FILM THESIS
-----------
The dark deity is not the opposite of consciousness.

It is consciousness appearing through:
• extreme contraction;
• concentrated affect;
• broken identity;
• intensified attention;
• symbolic embodiment;
• and the reversal of fear into recognition.

The visual arc is:

luminous field
→ contraction
→ pressure
→ fracture
→ projection
→ mask
→ deity
→ possession
→ terror
→ recognition
→ reintegration

HOUSE RULES
-----------
• Every shot lasts 5–10 seconds.
• Every shot visibly transforms.
• Dark scenes may use black, ultraviolet, crimson, venom-green, and molten gold.
• White/ivory appears only as the return of recognition.
• No static slideshow compositions.
• Mature frame near u=0.72.
• Continuity object: a gold bindu crushed into a black-red mask,
  then reopened as a many-colored mandala.

OUTPUT
------
output_gods_under_pressure/
  frames/
  scenes/
  gods_under_pressure.mp4
  narration_timeline.json
  contact_sheet.jpg

USAGE
-----
python gods_under_pressure_platinum.py
python gods_under_pressure_platinum.py --preview
python gods_under_pressure_platinum.py --scene 12
python gods_under_pressure_platinum.py --fps 12 --width 1920 --height 1080
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
OUTPUT = ROOT / "output_gods_under_pressure"
FRAMES = OUTPUT / "frames"
SCENES_DIR = OUTPUT / "scenes"

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 10

BLACK=(7,5,12)
DEEP_BLACK=(2,1,5)
IVORY=(247,244,235)
WHITE=(255,253,246)
INK=(24,22,30)
SILVER=(150,153,170)
GOLD=(225,168,57)
PALE_GOLD=(246,217,137)
CRIMSON=(198,34,61)
BLOOD=(109,9,25)
VIOLET=(121,54,202)
ULTRAVIOLET=(72,25,142)
CYAN=(35,190,219)
GREEN=(78,210,120)
VENOM=(135,220,69)
ORANGE=(236,93,37)
BLUE=(44,84,190)
MAGENTA=(224,42,156)

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
    arr+=rng.normal(0,1.8,(h,w,1))
    yy,xx=np.mgrid[0:h,0:w]
    halo=np.exp(-(((xx-w*.5)/(w*.40))**2+((yy-h*.40)/(h*.34))**2)*2.3)
    arr[...,0]+=halo*(12+30*light)
    arr[...,1]+=halo*(3+24*light)
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
    ImageDraw.Draw(fg).line(pts,fill=(*color,min(255,alpha+20)),width=width,joint="curve")
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

def draw_mask(d,cx,cy,scale=1.0,color=CRIMSON,alpha=220,horns=False):
    pts=[
        (cx,cy-95*scale),
        (cx-65*scale,cy-50*scale),
        (cx-52*scale,cy+42*scale),
        (cx,cy+95*scale),
        (cx+52*scale,cy+42*scale),
        (cx+65*scale,cy-50*scale),
        (cx,cy-95*scale),
    ]
    d.line(pts,fill=(*color,alpha),width=max(2,int(5*scale)))
    d.ellipse((cx-34*scale,cy-27*scale,cx-11*scale,cy-5*scale),
              outline=(*color,alpha),width=3)
    d.ellipse((cx+11*scale,cy-27*scale,cx+34*scale,cy-5*scale),
              outline=(*color,alpha),width=3)
    d.arc((cx-28*scale,cy+10*scale,cx+28*scale,cy+48*scale),
          180,360,fill=(*color,alpha),width=3)
    if horns:
        d.line((cx-42*scale,cy-72*scale,cx-86*scale,cy-130*scale),
               fill=(*color,alpha),width=4)
        d.line((cx+42*scale,cy-72*scale,cx+86*scale,cy-130*scale),
               fill=(*color,alpha),width=4)

def mandala_rays(cx,cy,r,count=24,phase=0):
    rays=[]
    for i in range(count):
        a=i*math.tau/count+phase
        rays.append([(cx,cy),(cx+math.cos(a)*r,cy+math.sin(a)*r)])
    return rays

def particles(w,h,count,seed):
    rng=random.Random(seed)
    return [(rng.uniform(w*.1,w*.9),rng.uniform(h*.12,h*.70),rng.uniform(1,5)) for _ in range(count)]


# =============================================================================
# VISUALS
# =============================================================================

def vis_light_pressure(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    glow_circle(im,cx,cy,22,GOLD,210,18)
    r=lerp(280,70,q)
    for rr in range(45,int(r)+1,32):
        d.ellipse((cx-rr,cy-rr*.62,cx+rr,cy+rr*.62),
                  outline=(*GOLD,int(75*(1-rr/max(r,1)))),width=3)
    for a in np.linspace(0,math.tau,12,endpoint=False):
        p0=(cx+math.cos(a)*r,cy+math.sin(a)*r*.62)
        glow_line(im,[p0,(cx,cy)],CRIMSON,3,int(70+120*q),9)
    seal(im,"CONSCIOUSNESS UNDER PRESSURE",
         "the unlimited field contracts around one center",GOLD)

def vis_fracture(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    glow_circle(im,cx,cy,18,GOLD,190,14)
    rng=random.Random(12)
    for i in range(18):
        a=i*math.tau/18+rng.uniform(-.1,.1)
        length=lerp(15,rng.uniform(120,250),q)
        p1=(cx+math.cos(a)*length,cy+math.sin(a)*length*.72)
        glow_line(im,[(cx,cy),p1],[CRIMSON,VIOLET,CYAN][i%3],3,150,9)
    seal(im,"CONTRACTION FRACTURES THE FIELD INTO POWERS",
         "fear, rage, desire, memory, and identity separate from their source")

def vis_projection(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    origin=(w*.28,h*.42); q=ease(u)
    draw_mask(d,*origin,.50,CRIMSON,190)
    targets=[(w*.62,h*.22),(w*.76,h*.42),(w*.66,h*.62)]
    for i,(x,y) in enumerate(targets):
        draw_mask(d,x,y,.34,[VIOLET,CRIMSON,GREEN][i],int(110+90*q),horns=i==1)
        glow_line(im,partial([origin,(x,y)],q),[VIOLET,CRIMSON,GREEN][i],3,130,8)
    seal(im,"WHAT CANNOT BE OWNED RETURNS AS AN OUTSIDE POWER",
         "projection turns internal force into demon, enemy, fate, or god")

def vis_mask_birth(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    for i in range(6):
        a=i*math.tau/6+t*.12
        x=cx+math.cos(a)*165
        y=cy+math.sin(a)*95
        draw_mask(d,x,y,.34,[CRIMSON,VIOLET,GREEN,CYAN,ORANGE,MAGENTA][i],
                  int(180*q),horns=i%2==0)
    draw_mask(d,cx,cy,lerp(.15,.85,q),GOLD,int(220*q),horns=True)
    seal(im,"A DEITY IS A STABILIZED CONFIGURATION OF FORCE",
         "affect, attention, body, image, and action lock into one form")

def vis_possession(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.42; q=ease(u)
    draw_mask(d,cx,cy,.72,CRIMSON,180,horns=True)
    r=lerp(230,90,q)
    d.ellipse((cx-r,cy-r*.75,cx+r,cy+r*.75),outline=(*VIOLET,210),width=5)
    for i in range(9):
        a=i*math.tau/9+t*.2
        x=cx+math.cos(a)*r
        y=cy+math.sin(a)*r*.75
        glow_circle(im,x,y,7,[CRIMSON,VIOLET,MAGENTA][i%3],130,7)
    seal(im,"POSSESSION IS THE COLLAPSE OF MULTIPLE POWERS INTO ONE",
         "one affective pattern seizes the entire field")

def vis_wrath(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    draw_mask(d,cx,cy,.90,CRIMSON,220,horns=True)
    for ray,col in zip(mandala_rays(cx,cy,250,32,t*.15),
                       ([CRIMSON,ORANGE,MAGENTA,VIOLET]*8)):
        glow_line(im,partial(ray,q),col,4,150,10)
    for x,y,r in particles(w,h,80,31):
        yy=y+math.sin(t*.8+x*.01)*12
        glow_circle(im,x,yy,r,ORANGE,80,5)
    seal(im,"WRATH IS ATTENTION WITH NO ESCAPE ROUTE",
         "the entire world is reorganized around violation",CRIMSON)

def vis_fear_mandala(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    draw_mask(d,cx,cy,.72,VIOLET,210,horns=True)
    for rr in range(45,260,28):
        d.ellipse((cx-rr,cy-rr*.68,cx+rr,cy+rr*.68),
                  outline=(*CRIMSON,int(75*q*(1-rr/290))),width=3)
    for i in range(12):
        a=i*math.tau/12+t*.12
        x=cx+math.cos(a)*205
        y=cy+math.sin(a)*130
        draw_mask(d,x,y,.18,CRIMSON,120,horns=True)
    seal(im,"FEAR MULTIPLIES ONE THREAT INTO AN ENTIRE COSMOS",
         "every direction begins to wear the same face")

def vis_desire_web(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    glow_circle(im,cx,cy,15,GOLD,180,12)
    targets=[
        (w*.22,h*.24,MAGENTA),
        (w*.78,h*.24,CYAN),
        (w*.22,h*.59,GREEN),
        (w*.78,h*.59,ORANGE),
    ]
    for i,(x,y,col) in enumerate(targets):
        glow_circle(im,x,y,14,col,160,9)
        pts=[(cx,cy),(lerp(cx,x,.45),lerp(cy,y,.45)+math.sin(i)*45),(x,y)]
        glow_line(im,partial(pts,q),col,4,175,10)
    r=lerp(40,150,q)
    d.ellipse((cx-r,cy-r*.62,cx+r,cy+r*.62),outline=(*CRIMSON,190),width=4)
    seal(im,"DESIRE CREATES A WORLD OF ABSENT COMPLETION",
         "the center becomes defined by what it does not possess")

def vis_corpse_ground(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    horizon=h*.55
    d.line((w*.08,horizon,w*.92,horizon),fill=(*SILVER,100),width=2)
    rng=random.Random(44)
    for i in range(12):
        x=w*.12+i*w*.065
        y=horizon+rng.uniform(-18,25)
        r=lerp(0,16,q)
        d.ellipse((x-r,y-r*.55,x+r,y+r*.55),outline=(*IVORY,130),width=2)
    glow_circle(im,w*.50,h*.32,18,GOLD,180,12)
    for x,y,r in particles(w,h,55,45):
        glow_circle(im,x,y,r,[VIOLET,GREEN,CRIMSON][int(x+y)%3],70,5)
    seal(im,"THE CREMATION GROUND REMOVES THE SOCIAL MASK",
         "beauty, status, identity, and control are forced into impermanence")

def vis_bhairava_gate(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    draw_mask(d,cx,cy,1.05,CRIMSON,230,horns=True)
    for rr,col in zip(range(55,300,35),
                      [CRIMSON,VIOLET,CYAN,GREEN,ORANGE,MAGENTA,GOLD]):
        d.ellipse((cx-rr*q,cy-rr*.68*q,cx+rr*q,cy+rr*.68*q),
                  outline=(*col,int(170*q*(1-rr/330))),width=4)
    glow_circle(im,cx,cy,16,GOLD,190,13)
    seal(im,"BHAIRAVA IS THE FORM TAKEN BY FEAR WHEN IT IS ENTERED",
         "terror becomes a gate instead of a boundary",CRIMSON)

def vis_reverse_fear(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.40); right=(w*.72,h*.40); q=ease(u)
    draw_mask(d,*left,.70,CRIMSON,200,horns=True)
    draw_mask(d,*right,.70,GOLD,200,horns=True)
    glow_line(im,partial([left,(w*.50,h*.18),right],q),GOLD,5,200,13)
    centered(d,(left[0],h*.68),"AVOID",font(FONT_SERIF_BOLD,24),CRIMSON)
    centered(d,(right[0],h*.68),"ENTER",font(FONT_SERIF_BOLD,24),GOLD)
    seal(im,"TANTRA REVERSES THE VECTOR",
         "what ordinary consciousness flees becomes material for recognition")

def vis_kali_time(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    for i in range(12):
        a=i*math.tau/12+t*.1
        r=175
        x=cx+math.cos(a)*r
        y=cy+math.sin(a)*105
        draw_mask(d,x,y,.22,[CRIMSON,VIOLET,MAGENTA][i%3],150,horns=i%2==0)
    draw_mask(d,cx,cy,.82,BLACK,220,horns=True)
    glow_circle(im,cx,cy,14,GOLD,180,11)
    for rr in range(45,250,28):
        d.arc((cx-rr,cy-rr,cx+rr,cy+rr),0,360,
              fill=(*CRIMSON,int(55*q*(1-rr/275))),width=3)
    seal(im,"KĀLĪ IS TIME EXPERIENCED AS DEVOURING POWER",
         "every form is born already moving toward dissolution")

def vis_mantra_weapon(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    syllables=["HRĪṂ","KRĪṂ","HŪṂ","PHAṬ"]
    for i,s in enumerate(syllables):
        a=i*math.tau/4-math.pi/2+t*.18
        r=175
        x=cx+math.cos(a)*r
        y=cy+math.sin(a)*105
        centered(d,(x,y),s,font(FONT_SERIF_BOLD,26),
                 [MAGENTA,CRIMSON,CYAN,GOLD][i])
        glow_line(im,partial([(x,y),(cx,cy)],q),
                  [MAGENTA,CRIMSON,CYAN,GOLD][i],4,170,10)
    glow_circle(im,cx,cy,18,GOLD,190,13)
    seal(im,"MANTRA CONDENSES A GOD INTO REPEATABLE ATTENTION",
         "sound becomes a precision instrument for reorganizing consciousness")

def vis_deity_body(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    # central spine
    glow_line(im,partial([(cx,h*.15),(cx,h*.66)],q),GOLD,6,210,14)
    chakras=[
        (h*.20,VIOLET),
        (h*.30,CYAN),
        (h*.40,GREEN),
        (h*.50,ORANGE),
        (h*.60,CRIMSON),
    ]
    for y,col in chakras:
        glow_circle(im,cx,y,18,col,170,11)
    for i,(y,col) in enumerate(chakras):
        for a in (-1,1):
            x=cx+a*lerp(0,130,q)
            draw_mask(d,x,y,.16,col,int(150*q),horns=i%2==0)
    seal(im,"THE DEITY IS INSTALLED AS A BODY OF POWERS",
         "ritual maps cosmic functions onto breath, sound, limb, and attention")

def vis_sacrifice_identity(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    labels=[
        ("NAME",CYAN,-175,-90),
        ("STATUS",VIOLET,175,-90),
        ("MEMORY",GREEN,-175,105),
        ("CONTROL",CRIMSON,175,105),
    ]
    for lab,col,ox,oy in labels:
        x=lerp(cx+ox,cx,q)
        y=lerp(cy+oy,cy,q)
        centered(d,(x,y),lab,font(FONT_SERIF_BOLD,21),
                 (*col,int(220*(1-q*.75))))
        glow_line(im,partial([(x,y),(cx,cy)],q),col,3,130,8)
    glow_circle(im,cx,cy,lerp(15,55,q),GOLD,190,13)
    seal(im,"THE OFFERING IS THE CLAIM OF PRIVATE OWNERSHIP",
         "identity is fed back into the power from which it formed")

def vis_dark_recognition(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    draw_mask(d,cx,cy,.90,CRIMSON,int(220*(1-q*.25)),horns=True)
    for rr,col in zip(range(45,290,30),
                      [GOLD,CRIMSON,VIOLET,CYAN,GREEN,ORANGE,MAGENTA,GOLD]):
        d.ellipse((cx-rr*q,cy-rr*.68*q,cx+rr*q,cy+rr*.68*q),
                  outline=(*col,int(165*q*(1-rr/320))),width=3)
    glow_circle(im,cx,cy,16,GOLD,200,14)
    seal(im,"RECOGNITION DOES NOT REMOVE THE MONSTER",
         "it reveals the monster as a contracted power of consciousness",GOLD)

def vis_reintegration(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    colors=[CRIMSON,VIOLET,CYAN,GREEN,ORANGE,MAGENTA]
    for i,col in enumerate(colors):
        a=i*math.tau/len(colors)+t*.10
        x=lerp(cx+math.cos(a)*210,cx+math.cos(a)*95,q)
        y=lerp(cy+math.sin(a)*135,cy+math.sin(a)*60,q)
        draw_mask(d,x,y,.28,col,170,horns=i%2==0)
        glow_line(im,partial([(x,y),(cx,cy)],q),col,3,140,8)
    glow_circle(im,cx,cy,20,GOLD,200,14)
    seal(im,"THE POWERS RETURN WITHOUT BECOMING BLAND",
         "integration preserves intensity while ending possession")

def vis_many_gods_one_field(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    cols=[CRIMSON,VIOLET,CYAN,GREEN,ORANGE,MAGENTA,GOLD,VENOM]
    for i,col in enumerate(cols):
        a=i*math.tau/len(cols)+t*.08
        r=190
        x=cx+math.cos(a)*r
        y=cy+math.sin(a)*115
        draw_mask(d,x,y,.25,col,165,horns=i%2==0)
        d.line((x,y,cx,cy),fill=(*col,80),width=2)
    for rr in range(45,260,30):
        d.ellipse((cx-rr,cy-rr*.65,cx+rr,cy+rr*.65),
                  outline=(*GOLD,int(65*q*(1-rr/290))),width=3)
    glow_circle(im,cx,cy,17,GOLD,190,12)
    seal(im,"THE MANY GODS ARE MODES OF ONE FIELD",
         "difference is real without becoming metaphysical separation")

def vis_caution(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    rows=[
        ("DEITIES ORGANIZE AFFECT AND ATTENTION","INTERPRETIVE CLAIM",CYAN),
        ("ALL POSSESSION IS SUPERNATURAL","NOT ESTABLISHED",CRIMSON),
        ("TANTRA USES FEAR AS PRACTICE MATERIAL","SUPPORTED",GREEN),
        ("DARK IMAGERY MAKES HARMLESS ACTION SAFE","FALSE",CRIMSON),
    ]
    q=ease(u)
    for i,(claim,status,col) in enumerate(rows):
        local=clamp(q*len(rows)-i); y=h*(.23+i*.13)
        d.rounded_rectangle((w*.12,y-28,w*.88,y+28),radius=14,
                            fill=(*mix(BLACK,col,.12),int(220*local)),
                            outline=(*col,int(180*local)),width=2)
        centered(d,(w*.39,y),claim,font(FONT_SANS_BOLD,14),WHITE)
        centered(d,(w*.75,y),status,font(FONT_SANS_BOLD,14),col)
    seal(im,"SYMBOLIC DARKNESS IS NOT LICENSE FOR PHYSICAL DANGER",
         "the film studies consciousness, not harmful ritual imitation")

def vis_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40; q=ease(u)
    cols=[CRIMSON,VIOLET,CYAN,GREEN,ORANGE,MAGENTA,GOLD,VENOM]
    for i,col in enumerate(cols):
        a=i*math.tau/len(cols)+t*.07
        r=lerp(240,135,q)
        x=cx+math.cos(a)*r
        y=cy+math.sin(a)*r*.62
        draw_mask(d,x,y,.25,col,170,horns=i%2==0)
        glow_line(im,partial([(x,y),(cx,cy)],q),col,3,130,8)
    for rr in range(45,310,30):
        d.ellipse((cx-rr*q,cy-rr*.66*q,cx+rr*q,cy+rr*.66*q),
                  outline=(*GOLD,int(75*q*(1-rr/340))),width=3)
    glow_circle(im,cx,cy,18,GOLD,205,14)
    if q>.72:
        centered(d,(cx,h*.68),"BHAIRAVA",font(FONT_SERIF_BOLD,30),GOLD)
    seal(im,"THE GODS ARE WHAT CONSCIOUSNESS LOOKS LIKE UNDER PRESSURE",
         "terror, desire, rage, and ecstasy become divine when recognized as powers of the field",GOLD)


VISUALS: dict[str,Callable] = {
    "pressure":vis_light_pressure,
    "fracture":vis_fracture,
    "projection":vis_projection,
    "mask":vis_mask_birth,
    "possession":vis_possession,
    "wrath":vis_wrath,
    "fear":vis_fear_mandala,
    "desire":vis_desire_web,
    "cremation":vis_corpse_ground,
    "bhairava":vis_bhairava_gate,
    "reverse":vis_reverse_fear,
    "kali":vis_kali_time,
    "mantra":vis_mantra_weapon,
    "body":vis_deity_body,
    "sacrifice":vis_sacrifice_identity,
    "recognition":vis_dark_recognition,
    "reintegrate":vis_reintegration,
    "many":vis_many_gods_one_field,
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
    Scene("Peaceful mistake",
          "Modern spirituality often imagines consciousness as a calm, empty witness.",
          8.0,"pressure",{}),
    Scene("Abhinava's field",
          "Abhinavagupta's consciousness is not empty. It is charged with powers.",
          8.5,"pressure",{}),
    Scene("Pressure",
          "When the field contracts around one finite center, those powers come under pressure.",
          9.0,"pressure",{}),

    Scene("Fracture",
          "Fear, rage, desire, memory, identity, and control begin to separate from their common source.",
          9.5,"fracture",{}),
    Scene("Autonomy",
          "Each power starts to behave as though it were the whole.",
          8.0,"fracture",{}),
    Scene("Fragment gods",
          "A fragment of consciousness becomes a miniature god.",
          7.5,"fracture",{}),

    Scene("Projection",
          "What the finite self cannot own returns as an outside force.",
          8.5,"projection",{}),
    Scene("Demon",
          "Rage becomes an enemy. Desire becomes fate. Fear becomes a demon.",
          9.0,"projection",{}),
    Scene("God",
          "A power becomes divine when it acquires image, name, body, memory, and ritual relation.",
          9.5,"mask",{}),

    Scene("Deity theory",
          "A deity is not merely a supernatural person added to the universe.",
          8.5,"mask",{}),
    Scene("Configuration",
          "It is a stabilized configuration of consciousness.",
          7.5,"mask",{}),
    Scene("Components",
          "Affect, attention, posture, sound, expectation, symbol, and action lock into one form.",
          10.0,"mask",{}),

    Scene("Possession",
          "Possession is what happens when one pattern captures the whole field.",
          8.5,"possession",{}),
    Scene("Narrow world",
          "Every perception is interpreted through the same affective logic.",
          8.5,"possession",{}),
    Scene("One god",
          "One god temporarily becomes the entire cosmos.",
          7.5,"possession",{}),

    Scene("Wrath",
          "Wrath is attention with no escape route.",
          7.5,"wrath",{}),
    Scene("Violation",
          "The world contracts around violation, obstacle, insult, or betrayal.",
          9.0,"wrath",{}),
    Scene("Flame world",
          "Everything begins to burn with the same meaning.",
          7.5,"wrath",{}),

    Scene("Fear",
          "Fear performs a different totalization.",
          7.5,"fear",{}),
    Scene("Threat faces",
          "One threat multiplies until every direction wears the same face.",
          8.5,"fear",{}),
    Scene("Cosmic paranoia",
          "A local danger becomes a cosmology.",
          7.0,"fear",{}),

    Scene("Desire",
          "Desire creates a world of absent completion.",
          8.0,"desire",{}),
    Scene("Missing center",
          "The self defines itself through what it does not possess.",
          8.5,"desire",{}),
    Scene("Web",
          "Every object becomes a possible route toward imagined wholeness.",
          9.0,"desire",{}),

    Scene("Cremation ground",
          "Tantric religion deliberately enters places where ordinary identity fails.",
          9.0,"cremation",{}),
    Scene("Masks removed",
          "The cremation ground strips status, beauty, control, and biography from the body.",
          9.5,"cremation",{}),
    Scene("No social refuge",
          "There is nowhere for the social self to hide.",
          7.5,"cremation",{}),

    Scene("Bhairava",
          "Bhairava is not simply a frightening god.",
          7.5,"bhairava",{}),
    Scene("Fear entered",
          "He is the form taken by fear when fear is entered rather than avoided.",
          9.0,"bhairava",{}),
    Scene("Gate",
          "Terror becomes a gate instead of a boundary.",
          7.5,"bhairava",{}),

    Scene("Reverse vector",
          "Tantra reverses the ordinary vector.",
          7.5,"reverse",{}),
    Scene("Avoidance",
          "Ordinary consciousness flees what threatens identity.",
          8.0,"reverse",{}),
    Scene("Entry",
          "Tantric consciousness enters the image, sound, sensation, and force.",
          9.0,"reverse",{}),

    Scene("Kali",
          "Kālī makes time visible as devouring power.",
          8.0,"kali",{}),
    Scene("Dissolution",
          "Every form appears already moving toward dissolution.",
          8.5,"kali",{}),
    Scene("No outside time",
          "The goddess is not inside time. Time is one of her gestures.",
          8.5,"kali",{}),

    Scene("Mantra",
          "Mantra condenses a divine configuration into repeatable attention.",
          9.0,"mantra",{}),
    Scene("Sound weapon",
          "Sound becomes a precision instrument.",
          7.5,"mantra",{}),
    Scene("Repatterning",
          "Breath, rhythm, image, and expectation are reorganized around one seed.",
          9.0,"mantra",{}),

    Scene("Installation",
          "Ritual does not merely worship the deity as external.",
          8.0,"body",{}),
    Scene("Body of powers",
          "The deity is installed as a body of powers.",
          7.5,"body",{}),
    Scene("Nyasa logic",
          "Sound, limb, breath, direction, and attention are mapped onto one another.",
          9.5,"body",{}),
    Scene("Become form",
          "The practitioner becomes the form through which the form can appear.",
          8.5,"body",{}),

    Scene("Sacrifice",
          "The deepest offering is not an object.",
          7.5,"sacrifice",{}),
    Scene("Ownership",
          "It is the claim of private ownership.",
          7.0,"sacrifice",{}),
    Scene("Feed identity back",
          "Name, status, memory, and control are fed back into the power from which they formed.",
          9.5,"sacrifice",{}),

    Scene("Recognition",
          "Recognition does not make the dark deity disappear.",
          8.0,"recognition",{}),
    Scene("Power seen",
          "It reveals the deity as a contracted power of consciousness.",
          8.0,"recognition",{}),
    Scene("No exile",
          "Nothing has to be exiled from the field.",
          7.5,"recognition",{}),

    Scene("Reintegration",
          "The powers return without becoming bland.",
          7.5,"reintegrate",{}),
    Scene("Intensity remains",
          "Rage can remain energy. Fear can remain sensitivity. Desire can remain movement.",
          9.5,"reintegrate",{}),
    Scene("Possession ends",
          "What ends is possession: the claim that one power is the whole.",
          9.0,"reintegrate",{}),

    Scene("Many gods",
          "This is why a nondual system can contain many gods.",
          8.0,"many",{}),
    Scene("Real differences",
          "The powers are genuinely different.",
          7.0,"many",{}),
    Scene("One field",
          "Their difference unfolds within one field of consciousness.",
          8.0,"many",{}),

    Scene("Modern reading",
          "A modern interpretation can describe these forms as affective-cognitive configurations.",
          9.0,"caution",{}),
    Scene("Not reduction",
          "But psychology does not exhaust their ritual, historical, or metaphysical meaning.",
          9.0,"caution",{}),
    Scene("Discipline",
          "Symbolic darkness must also never become an excuse for dangerous imitation.",
          9.0,"caution",{}),

    Scene("Return",
          "Return to the first golden point.",
          6.5,"final",{}),
    Scene("All masks",
          "Every mask now surrounds it.",
          7.0,"final",{}),
    Scene("Recognition",
          "None is outside the light. None is the whole light.",
          8.0,"final",{}),
    Scene("Closing",
          "The gods are what consciousness looks like under pressure: terror, desire, rage, ecstasy, and time becoming divine when they are recognized as powers of the field rather than prisons of the self.",
          10.0,"final",{}),
]


def render_frame(scene,frame_index,frame_count,width,height,seed):
    u=frame_index/max(1,frame_count-1)
    t=u*scene.duration
    # final and recognition scenes brighten slightly
    light = .16*smoothstep(.35,1.0,u) if scene.visual in {"recognition","reintegrate","many","final"} else 0.0
    im=dark_field(width,height,seed,light)
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
    output=OUTPUT/"gods_under_pressure.mp4"
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
        "title":"the gods are what consciousness looks like under pressure",
        "subtitle":"Abhinavagupta on terror, desire, possession, and divine form",
        "scene_count":len(SCENES),
        "runtime_seconds":round(cursor,3),
        "shot_duration_range":[5,10],
        "continuity_object":"gold bindu crushed into black-red mask, reopened as mandala",
        "palette":"black, crimson, ultraviolet, venom green, cyan, molten gold",
        "scenes":records,
    },indent=2,ensure_ascii=False),encoding="utf-8")
    return path

def make_contact_sheet(width,height):
    tw=320; th=int(tw*height/width); cols=4
    rows=math.ceil(len(SCENES)/cols); cell_h=th+48
    sheet=Image.new("RGB",(cols*tw,rows*cell_h),BLACK)
    d=ImageDraw.Draw(sheet); lf=font(FONT_SANS_BOLD,14)
    for index,scene in enumerate(SCENES,1):
        count=max(2,round(scene.duration*DEFAULT_FPS))
        image=render_frame(scene,int(count*.72),count,width,height,index*10000+72)
        image.thumbnail((tw,th))
        slot=index-1; x=(slot%cols)*tw; y=(slot//cols)*cell_h
        sheet.paste(image,(x,y))
        d.text((x+8,y+th+7),f"{index:02d}  {scene.title}",font=lf,fill=WHITE)
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
