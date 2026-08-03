#!/usr/bin/env python3
"""
A RITUAL OBJECT TEACHES MATTER TO REMEMBER HEAVEN
An original Imaginarium visual essay and Platinum-house procedural renderer.

ORIGINAL THESIS
---------------
A ritual object is not powerful because matter secretly contains a trapped god.
It becomes powerful when material form, symbolic intelligence, bodily practice,
memory, attention, and cosmological correspondence are trained into one circuit.

This essay joins:
• Ficino's spiritus and astral medicine
• Iamblichean and Proclean theurgy
• Tantric nyāsa, mantra, yantra, and consecration
• Kashmir Śaiva ābhāsa and recognition
• Corbin's imaginal correspondence
• predictive perception and embodied cognition
• the ethical distinction between ritual transformation and magical inflation

DESIGN CONTRACT
---------------
• Every shot lasts 5–10 seconds.
• Every shot visibly performs the narrated operation.
• Clean white field; deep indigo only when cosmological depth is required.
• No static slide layouts and no decorative loops.
• Graphite = raw matter / ordinary object
• Gold = celestial correspondence / consecrated coherence
• Cyan = breath, attention, sensory coupling
• Violet = imaginal depth / planetary intelligence / symbolic resonance
• Crimson = coercion, inflation, fetishism, domination
• Green = ethical embodiment / healed relation / returned action
• Silver = memory trace / inherited ritual form
• Continuity object: one small dark talisman becomes increasingly articulate.
• The object must never become a generic glowing amulet.
• Its transformation must occur through geometry, sound, touch, rhythm, and relation.
• Final criterion: the ritual object returns the practitioner to the world with more responsibility.

OUTPUT
------
output_ritual_object_heaven/
  frames/scene_001/*.jpg
  scenes/scene_001.mp4
  a_ritual_object_teaches_matter_to_remember_heaven.mp4
  narration_timeline.json
  original_essay.md
  contact_sheet.jpg

REQUIREMENTS
------------
pip install pillow numpy
ffmpeg must be on PATH.

USAGE
-----
python a_ritual_object_teaches_matter_to_remember_heaven_platinum.py
python a_ritual_object_teaches_matter_to_remember_heaven_platinum.py --preview
python a_ritual_object_teaches_matter_to_remember_heaven_platinum.py --scene 12
python a_ritual_object_teaches_matter_to_remember_heaven_platinum.py --fps 12 --width 1920 --height 1080
"""

from __future__ import annotations

import argparse
import json
import math
import random
import shutil
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output_ritual_object_heaven"
FRAMES = OUTPUT / "frames"
SCENES_DIR = OUTPUT / "scenes"

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 10

WHITE = (248,247,243)
PAPER = (242,239,232)
INK = (28,31,35)
SOFT_INK = (84,88,94)
SILVER = (177,184,190)
PALE_SILVER = (224,227,229)
GOLD = (194,153,68)
PALE_GOLD = (235,218,175)
CYAN = (55,153,181)
PALE_CYAN = (192,226,233)
VIOLET = (104,79,146)
PALE_VIOLET = (216,205,232)
CRIMSON = (158,52,66)
PALE_CRIMSON = (230,192,198)
GREEN = (70,139,98)
PALE_GREEN = (194,225,206)
LAPIS = (48,72,124)
VOID = (22,25,31)
NIGHT = (17,23,39)

FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def clamp(x, lo=0.0, hi=1.0): return max(lo, min(hi, x))
def lerp(a,b,t): return a + (b-a)*t
def mix(a,b,t):
    t = clamp(t)
    return tuple(int(lerp(x,y,t)) for x,y in zip(a,b))
def smoothstep(a,b,x):
    if a == b: return 1.0 if x >= b else 0.0
    q = clamp((x-a)/(b-a))
    return q*q*(3-2*q)
def ease(t): return .5 - .5*math.cos(math.pi*clamp(t))
def pulse(t,hz=1.0,phase=0.0): return .5 + .5*math.sin(math.tau*(hz*t+phase))

def load_font(path,size):
    for p in (path,FONT_SERIF,FONT_SANS):
        try: return ImageFont.truetype(p,size)
        except OSError: pass
    return ImageFont.load_default()

def rgba_layer(size): return Image.new("RGBA",size,(0,0,0,0))

def background(w,h,seed,dark=False):
    rng=np.random.default_rng(seed)
    base=NIGHT if dark else WHITE
    arr=np.empty((h,w,3),dtype=np.float32)
    arr[:] = base
    arr += rng.normal(0,1.05 if not dark else 1.7,(h,w,1))
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8),"RGB").convert("RGBA")

def centered_text(d,xy,text,font,fill=INK):
    d.text(xy,text,font=font,fill=fill,anchor="mm")

def seal(im,title,subtitle="",color=INK,dark=False):
    w,h=im.size
    d=ImageDraw.Draw(im)
    centered_text(d,(w/2,h*.875),title,load_font(FONT_SERIF_BOLD,max(22,int(h*.042))),WHITE if dark else color)
    if subtitle:
        centered_text(d,(w/2,h*.925),subtitle,load_font(FONT_SANS,max(13,int(h*.020))),PALE_SILVER if dark else SOFT_INK)

def border(im,dark=False):
    w,h=im.size
    ImageDraw.Draw(im).rounded_rectangle((25,25,w-25,h-25),radius=17,outline=(*(WHITE if dark else INK),42),width=2)

def glow_line(im,pts,col,width=4,glow=14,alpha=220):
    if len(pts)<2:return
    ov=rgba_layer(im.size)
    d=ImageDraw.Draw(ov)
    d.line(pts,fill=(*col,alpha),width=width,joint="curve")
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(glow)))
    im.alpha_composite(ov)

def glow_circle(im,x,y,r,col,alpha=180,blur=16):
    ov=rgba_layer(im.size)
    d=ImageDraw.Draw(ov)
    d.ellipse((x-r,y-r,x+r,y+r),fill=(*col,alpha))
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(im).ellipse((x-r*.38,y-r*.38,x+r*.38,y+r*.38),fill=(*mix(col,WHITE,.3),230))

def partial_polyline(points,progress):
    progress=clamp(progress)
    if len(points)<2:return points
    lens=[math.dist(a,b) for a,b in zip(points[:-1],points[1:])]
    total=sum(lens); target=total*progress
    out=[points[0]]; walked=0
    for i,L in enumerate(lens):
        if walked+L<=target:
            out.append(points[i+1]); walked+=L
        else:
            q=(target-walked)/L if L else 0
            a,b=points[i],points[i+1]
            out.append((lerp(a[0],b[0],q),lerp(a[1],b[1],q)))
            break
    return out

def arrow(d,a,b,col=INK,width=3,head=11):
    d.line((*a,*b),fill=col,width=width)
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for delta in (2.55,-2.55):
        p=(b[0]+math.cos(ang+delta)*head,b[1]+math.sin(ang+delta)*head)
        d.line((*b,*p),fill=col,width=width)

def organic_blob(d,cx,cy,rx,ry,color,phase=0,points=100,outline=None):
    pts=[]
    for i in range(points):
        a=math.tau*i/points
        wob=1+.06*math.sin(a*3+phase)+.035*math.sin(a*7-phase*.5)
        pts.append((cx+math.cos(a)*rx*wob,cy+math.sin(a)*ry*wob))
    d.polygon(pts,fill=color,outline=outline)
    return pts

def talisman(d,cx,cy,r,fill=INK,outline=SILVER,alpha=220,inscription=0.0):
    pts=[]
    for i in range(6):
        a=-math.pi/2+i*math.tau/6
        pts.append((cx+math.cos(a)*r,cy+math.sin(a)*r))
    d.polygon(pts,fill=(*fill,alpha),outline=(*outline,alpha))
    if inscription>0:
        rr=r*.58
        d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=(*GOLD,int(190*inscription)),width=3)
        for i in range(3):
            a=i*math.tau/3-math.pi/2
            b=a+math.tau/3
            d.line((cx+math.cos(a)*rr,cy+math.sin(a)*rr,cx+math.cos(b)*rr,cy+math.sin(b)*rr),
                   fill=(*GOLD,int(180*inscription)),width=3)

def breath_curve(w,h,phase=0,y=.42):
    pts=[]
    for i in range(180):
        q=i/179
        x=lerp(w*.08,w*.92,q)
        yy=h*y+math.sin(q*math.tau*2+phase)*h*.04+math.sin(q*math.tau*7-phase)*h*.012
        pts.append((x,yy))
    return pts

def hand(d,cx,cy,scale=1.0,col=INK,alpha=180):
    d.ellipse((cx-35*scale,cy-25*scale,cx+35*scale,cy+25*scale),outline=(*col,alpha),width=4)
    for i in range(5):
        x=cx-28*scale+i*14*scale
        d.line((x,cy-10*scale,x-8*scale,cy-80*scale-(i%2)*10*scale),fill=(*col,alpha),width=5)

def star_field(d,w,h,seed=4,alpha=100):
    rng=random.Random(seed)
    for _ in range(100):
        x=rng.uniform(w*.08,w*.92); y=rng.uniform(h*.08,h*.72)
        r=rng.choice([1,1,1,2])
        d.ellipse((x-r,y-r,x+r,y+r),fill=(*PALE_GOLD,alpha))

def orbit(d,cx,cy,rx,ry,col,alpha=150,width=3):
    d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),outline=(*col,alpha),width=width)


@dataclass
class Scene:
    title:str
    narration:str
    duration:float
    visual:str
    params:dict


def visual_raw_object(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    talisman(d,w*.5,h*.42,72,INK,SILVER,220,0)
    hand(d,w*.20,h*.50,1.0,INK,150)
    seal(im,"AT FIRST IT IS ONLY MATTER","stone · metal · pigment · fiber")

def visual_correspondence(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    talisman(d,cx,cy,72,mix(INK,GOLD,q*.35),mix(SILVER,GOLD,q),220,q)
    for i,(col,label) in enumerate([(GOLD,"SUN"),(VIOLET,"SATURN"),(CYAN,"VENUS"),(GREEN,"MERCURY")]):
        a=-math.pi/2+i*math.tau/4
        x=cx+math.cos(a)*w*.28; y=cy+math.sin(a)*h*.25
        orbit(d,cx,cy,abs(x-cx),abs(y-cy)+15,col,int(70+90*q),2)
        glow_circle(im,x,y,12,col,120,9)
        if q>.7:centered_text(d,(x,y-28),label,load_font(FONT_SANS_BOLD,int(h*.013)),col)
    seal(im,"CORRESPONDENCE IS NOT RESEMBLANCE","it is a disciplined relation among levels")

def visual_material_memory(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    talisman(d,cx,cy,74,INK,SILVER,220,q)
    # inherited traces
    for i in range(14):
        a=i*math.tau/14
        rr=lerp(50,200,q)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.62
        glow_line(im,[(cx,cy),(x,y)],SILVER,2,7,90)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*SILVER,130))
    seal(im,"MATERIAL CAN CARRY A HISTORY OF USE","not memory as thought, but memory as patterned readiness")

def visual_breath_consecration(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.66,h*.42
    talisman(d,cx,cy,70,INK,SILVER,220,ease(u))
    q=ease(u)
    path=breath_curve(w,h,t*.5,.42)
    glow_line(im,partial_polyline(path,q),CYAN,5,14,210)
    # mouth / practitioner
    d.arc((w*.10,h*.35,w*.30,h*.50),200,340,fill=(*INK,180),width=4)
    glow_circle(im,cx,cy,18+22*q,GOLD,130,12)
    seal(im,"BREATH MAKES THE BODY PART OF THE CIRCUIT","consecration begins when matter enters a living rhythm")

def visual_mantra_inscription(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    talisman(d,cx,cy,78,INK,mix(SILVER,GOLD,q),220,q)
    # sound rings become geometry
    for i in range(7):
        r=90+i*26*q
        d.arc((cx-r,cy-r*.62,cx+r,cy+r*.62),0,int(310*q),fill=(*mix(CYAN,GOLD,i/6),120),width=3)
    seal(im,"MANTRA DOES NOT DESCRIBE THE OBJECT","it trains vibration, attention, and form into one pattern")

def visual_nyasa_body(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    # body axis
    cx=w*.38
    d.ellipse((cx-28,h*.17,cx+28,h*.25),outline=(*INK,180),width=4)
    d.line((cx,h*.25,cx,h*.61),fill=(*INK,180),width=5)
    d.line((cx,h*.34,cx-85,h*.46),fill=(*INK,180),width=5)
    d.line((cx,h*.34,cx+85,h*.46),fill=(*INK,180),width=5)
    d.line((cx,h*.61,cx-55,h*.72),fill=(*INK,180),width=5)
    d.line((cx,h*.61,cx+55,h*.72),fill=(*INK,180),width=5)
    points=[(cx,h*.20),(cx,h*.31),(cx,h*.42),(cx,h*.54),(cx,h*.64)]
    q=ease(u)
    for i,pnt in enumerate(points):
        glow_circle(im,pnt[0],pnt[1],10+8*smoothstep(i*.12,.8,u),mix(CYAN,GOLD,i/4),140,9)
    talisman(d,w*.72,h*.42,66,INK,GOLD,220,q)
    for i,pnt in enumerate(points):
        glow_line(im,partial_polyline([pnt,(w*.72,h*.42)],smoothstep(i*.10,.88,u)),mix(CYAN,GOLD,i/4),3,9,130)
    seal(im,"NYĀSA PLACES THE COSMOS INTO THE BODY","the object and practitioner are consecrated together")

def visual_yantra_machine(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    # square gate
    size=250*q
    d.rectangle((cx-size/2,cy-size/2,cx+size/2,cy+size/2),outline=(*INK,160),width=4)
    # triangles
    for i in range(5):
        r=(45+i*32)*q
        pts=[(cx,cy-r),(cx-r*.86,cy+r*.5),(cx+r*.86,cy+r*.5)]
        d.line(pts+[pts[0]],fill=(*mix(VIOLET,GOLD,i/4),150),width=3)
    talisman(d,cx,cy,40,INK,GOLD,220,q)
    seal(im,"YANTRA IS GEOMETRY USED AS AN OPERATION","a spatial grammar for concentrating relation")

def visual_spiritus(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    star_field(d,w,h,9,90)
    cx,cy=w*.5,h*.42
    talisman(d,cx,cy,68,INK,GOLD,220,ease(u))
    q=ease(u)
    # descending planetary breath
    for i,col in enumerate((GOLD,VIOLET,CYAN,GREEN)):
        x=w*(.20+i*.20)
        glow_line(im,partial_polyline([(x,h*.08),(cx,cy)],smoothstep(i*.08,.85,u)),col,4,11,150)
    # circulating spiritus
    for r in (95,145,200):
        d.arc((cx-r,cy-r*.62,cx+r,cy+r*.62),20,int(300*q),fill=(*PALE_GOLD,90),width=3)
    seal(im,"FICINO'S SPIRITUS","the subtle medium through which body, soul, and stars become mutually legible",dark=True)

def visual_theurgic_chain(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    levels=[("MATTER",INK,h*.68),("SYMBOL",CYAN,h*.52),("DAIMON",VIOLET,h*.34),("INTELLECT",GOLD,h*.16)]
    x=w*.5
    q=ease(u)
    for i,(txt,col,y) in enumerate(levels):
        d.ellipse((x-42,y-25,x+42,y+25),fill=(*mix(WHITE,col,.16),220),outline=(*col,180),width=3)
        centered_text(d,(x,y),txt,load_font(FONT_SANS_BOLD,int(h*.013)),col)
        if i>0:
            glow_line(im,partial_polyline([(x,levels[i-1][2]-25),(x,y+25)],q),mix(levels[i-1][1],col,.5),4,11,180)
    seal(im,"THEURGY DOES NOT DRAG HEAVEN DOWN","it aligns levels so that each can become transparent to the next")

def visual_presence_not_prison(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.42); right=(w*.72,h*.42)
    # trapped god failure
    talisman(d,*left,68,INK,CRIMSON,220,1)
    d.rectangle((left[0]-95,left[1]-95,left[0]+95,left[1]+95),outline=(*CRIMSON,180),width=5)
    # relational presence
    talisman(d,*right,68,INK,GOLD,220,ease(u))
    for i,col in enumerate((CYAN,GOLD,VIOLET,GREEN)):
        a=i*math.tau/4
        x=right[0]+math.cos(a)*120; y=right[1]+math.sin(a)*85
        glow_line(im,partial_polyline([(right[0],right[1]),(x,y)],ease(u)),col,3,9,130)
    seal(im,"PRESENCE IS NOT IMPRISONMENT","the object becomes a meeting-place, not a container")

def visual_predictive_object(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.20,h*.42); center=(w*.50,h*.42); right=(w*.80,h*.42)
    talisman(d,*right,60,INK,SILVER,220,ease(u))
    # sensory model
    d.rounded_rectangle((center[0]-85,center[1]-65,center[0]+85,center[1]+65),radius=18,
                        fill=(*PALE_CYAN,215),outline=(*CYAN,180),width=3)
    centered_text(d,center,"MODEL",load_font(FONT_SANS_BOLD,int(h*.020)),CYAN)
    # body
    hand(d,*left,1.0,INK,160)
    q=ease(u)
    glow_line(im,partial_polyline([left,center,right],q),CYAN,4,11,170)
    glow_line(im,partial_polyline([right,(w*.63,h*.57),center,(w*.36,h*.57),left],smoothstep(.35,.95,u)),GOLD,4,11,160)
    seal(im,"RITUAL CHANGES WHAT THE OBJECT CAN MEAN","expectation, sensation, posture, and memory converge")

def visual_inherited_attention(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    talisman(d,cx,cy,68,INK,SILVER,220,ease(u))
    q=ease(u)
    # generations of hands
    for i in range(6):
        x=w*(.12+i*.15); y=h*(.26 if i%2==0 else .58)
        hand(d,x,y,.55,mix(SILVER,GOLD,i/5),100+int(70*q))
        glow_line(im,partial_polyline([(x,y),(cx,cy)],smoothstep(i*.08,.88,u)),mix(SILVER,GOLD,i/5),2,7,90)
    seal(im,"TRADITION IS STORED ATTENTION","the object inherits a choreography of ways to be encountered")

def visual_fetishism_failure(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.42); right=(w*.72,h*.42)
    talisman(d,*left,72,INK,CRIMSON,220,1)
    centered_text(d,(left[0],h*.66),"POWER AS PROPERTY",load_font(FONT_SANS_BOLD,int(h*.014)),CRIMSON)
    talisman(d,*right,72,INK,GOLD,220,ease(u))
    centered_text(d,(right[0],h*.66),"POWER AS RELATION",load_font(FONT_SANS_BOLD,int(h*.014)),GREEN)
    q=smoothstep(.35,.9,u)
    d.line((w*.49,h*.25,w*.51,h*.58),fill=(*CRIMSON,int(210*q)),width=6)
    seal(im,"FETISHISM FORGETS THE CIRCUIT","it treats relation as a substance owned by the object")

def visual_coercion_failure(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    talisman(d,w*.5,h*.42,75,INK,CRIMSON,220,1)
    q=ease(u)
    # grasping hooks
    for i in range(8):
        a=i*math.tau/8
        x=w*.5+math.cos(a)*180; y=h*.42+math.sin(a)*110
        arrow(d,(x,y),(w*.5+math.cos(a)*80,h*.42+math.sin(a)*50),CRIMSON,4,12)
    d.ellipse((w*.5-130*q,h*.42-85*q,w*.5+130*q,h*.42+85*q),outline=(*CRIMSON,160),width=5)
    seal(im,"COERCION COLLAPSES RITUAL INTO DOMINATION","the sacred becomes a technology for forcing outcomes")

def visual_abhasa_object(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    talisman(d,cx,cy,62,INK,mix(SILVER,GOLD,q),220,q)
    for i in range(18):
        a=i*math.tau/18
        rr=lerp(25,200,q)*(0.7+0.3*((i%4)/3))
        x=cx+math.cos(a+t*.08)*rr; y=cy+math.sin(a+t*.08)*rr*.62
        col=mix(CYAN,VIOLET,i/17)
        glow_circle(im,x,y,5+3*(i%3),col,90,7)
        glow_line(im,[(cx,cy),(x,y)],col,2,7,70)
    seal(im,"ĀBHĀSA","the object is consciousness appearing as material difference")

def visual_recognition_object(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.25,h*.42); right=(w*.75,h*.42)
    talisman(d,*right,70,INK,GOLD,220,ease(u))
    hand(d,*left,1.0,INK,160)
    q=ease(u)
    glow_line(im,partial_polyline([left,(w*.5,h*.30),right],q),CYAN,4,11,170)
    glow_line(im,partial_polyline([right,(w*.5,h*.56),left],smoothstep(.30,.95,u)),GOLD,5,13,200)
    seal(im,"RECOGNITION RETURNS THE SACRED TO THE KNOWER","the object does not monopolize the presence it reveals")

def visual_imaginal_object(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    talisman(d,w*.5,h*.42,70,INK,GOLD,220,ease(u))
    q=ease(u)
    # object opens depth without ceasing to be material
    for r,col in [(100,SILVER),(145,VIOLET),(200,GOLD)]:
        d.ellipse((w*.5-r*q,h*.42-r*.62*q,w*.5+r*q,h*.42+r*.62*q),outline=(*col,int(120*q)),width=3)
    d.line((w*.5-70,h*.42,w*.5+70,h*.42),fill=(*INK,180),width=4)
    seal(im,"THE OBJECT REMAINS HERE AND OPENS ELSEWHERE","imaginal depth does not erase material location")

def visual_ethics_test(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    talisman(d,w*.25,h*.42,62,INK,GOLD,220,ease(u))
    fruits=[("CLARITY",CYAN,w*.52,h*.25),("HUMILITY",VIOLET,w*.72,h*.33),
            ("COURAGE",GOLD,w*.52,h*.56),("CARE",GREEN,w*.76,h*.60)]
    for i,(txt,col,x,y) in enumerate(fruits):
        q=smoothstep(i*.10,.65+i*.05,u)
        glow_line(im,partial_polyline([(w*.31,h*.42),(x,y)],q),col,3,9,150)
        d.ellipse((x-28*q,y-28*q,x+28*q,y+28*q),fill=(*mix(WHITE,col,.18),int(220*q)),outline=(*col,int(180*q)),width=3)
        if q>.68:centered_text(d,(x,y),txt,load_font(FONT_SANS_BOLD,int(h*.012)),col)
    seal(im,"THE FRUIT TESTS THE CONSECRATION","does the object enlarge responsibility rather than fantasy?")

def visual_return_world(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    talisman(d,w*.20,h*.42,55,INK,GOLD,220,ease(u))
    # ordinary world
    d.line((w*.08,h*.62,w*.92,h*.62),fill=(*INK,120),width=5)
    for i in range(8):
        x=w*(.16+i*.09)
        d.rectangle((x-18,h*.48,x+18,h*.62),fill=(*PALE_SILVER,120),outline=(*SILVER,100))
    q=ease(u)
    glow_line(im,partial_polyline([(w*.26,h*.42),(w*.45,h*.54),(w*.67,h*.50),(w*.88,h*.57)],q),GREEN,6,14,210)
    seal(im,"THE OBJECT MUST RETURN YOU TO THE WORLD","not enchanted away from it, but more answerable within it")

def visual_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    talisman(d,cx,cy,74,mix(INK,GOLD,q*.30),mix(SILVER,GOLD,q),220,q)
    # breath, orbit, relation, ethical path all converge
    glow_line(im,partial_polyline(breath_curve(w,h,t*.4,.42),q),CYAN,4,12,170)
    for r,col in [(110,VIOLET),(155,GOLD),(205,GREEN)]:
        d.arc((cx-r*q,cy-r*.62*q,cx+r*q,cy+r*.62*q),10,int(320*q),fill=(*col,110),width=3)
    glow_circle(im,cx,cy,20+18*q,GOLD,150,13)
    seal(im,"A RITUAL OBJECT TEACHES MATTER TO REMEMBER HEAVEN",
         "not by escaping matter, but by making relation visible",color=GREEN)


VISUALS:dict[str,Callable]={
    "raw":visual_raw_object,
    "correspondence":visual_correspondence,
    "memory":visual_material_memory,
    "breath":visual_breath_consecration,
    "mantra":visual_mantra_inscription,
    "nyasa":visual_nyasa_body,
    "yantra":visual_yantra_machine,
    "spiritus":visual_spiritus,
    "theurgy":visual_theurgic_chain,
    "presence":visual_presence_not_prison,
    "predict":visual_predictive_object,
    "tradition":visual_inherited_attention,
    "fetish":visual_fetishism_failure,
    "coercion":visual_coercion_failure,
    "abhasa":visual_abhasa_object,
    "recognition":visual_recognition_object,
    "imaginal":visual_imaginal_object,
    "ethics":visual_ethics_test,
    "return":visual_return_world,
    "final":visual_final,
}


SCENES:list[Scene]=[
    Scene("Raw matter","At first the object is only matter.",5.5,"raw",{}),
    Scene("Stone metal pigment","Stone. Metal. Pigment. Fiber.",5.5,"raw",{}),
    Scene("No trapped god","No trapped god waits inside it.",6.5,"presence",{}),
    Scene("No automatic power","No automatic power radiates from its shape.",7.0,"raw",{}),
    Scene("Ritual begins","Ritual begins by teaching matter how to participate in a larger relation.",9.0,"final",{}),

    Scene("Object and operation","A ritual object is not merely an object.",6.5,"raw",{}),
    Scene("Condensed operation","It is an operation condensed into material form.",8.0,"yantra",{}),
    Scene("Geometry memory","Its geometry remembers an order.",6.5,"memory",{}),
    Scene("Material touch","Its material remembers touch.",6.0,"memory",{}),
    Scene("Name sound","Its name remembers sound.",6.0,"mantra",{}),
    Scene("Placement cosmos","Its placement remembers a cosmos.",6.5,"correspondence",{}),
    Scene("Repeated use","Its repeated use remembers a way of attending.",8.0,"tradition",{}),

    Scene("Correspondence","The first principle is correspondence.",6.0,"correspondence",{}),
    Scene("Not resemblance","Correspondence is not visual resemblance.",6.5,"correspondence",{}),
    Scene("Gold not sun","Gold does not resemble the sun in any sufficient sense.",7.0,"correspondence",{}),
    Scene("Shared qualities","It shares brightness, incorruptibility, centrality, and value.",8.5,"correspondence",{}),
    Scene("Planet plant organ","A planet, plant, organ, color, tone, and virtue can be linked through a patterned family.",9.5,"correspondence",{}),
    Scene("Relation across levels","The object condenses that family into one site.",8.0,"correspondence",{}),

    Scene("Ficino","Marsilio Ficino called the mediating field spiritus.",7.0,"spiritus",{}),
    Scene("Subtle body","Spiritus was subtle body, breath, imagination, sensation, and astral susceptibility.",9.5,"spiritus",{}),
    Scene("Not crude gas","It was not merely gas and not merely metaphor.",7.0,"spiritus",{}),
    Scene("Mutual legibility","It named the medium through which body, soul, and stars became mutually legible.",9.5,"spiritus",{}),
    Scene("Talisman role","A talisman tuned that medium.",6.5,"spiritus",{}),
    Scene("Not remote control","Not as a remote control for the planets.",7.0,"coercion",{}),
    Scene("Atmosphere of relation","As a carefully constructed atmosphere of relation.",8.0,"spiritus",{}),

    Scene("Breath","Breath brings the practitioner into the circuit.",6.0,"breath",{}),
    Scene("Warm object","The object warms in the hand.",6.0,"breath",{}),
    Scene("Pulse and rhythm","Pulse, breathing, voice, and gaze acquire rhythm.",8.0,"breath",{}),
    Scene("Material living timing","Matter is placed inside living timing.",7.0,"breath",{}),
    Scene("Consecration","Consecration begins when material form is synchronized with embodied attention.",9.0,"breath",{}),

    Scene("Mantra","Mantra adds patterned sound.",5.5,"mantra",{}),
    Scene("Not label","The mantra is not a label attached to the object.",6.5,"mantra",{}),
    Scene("Vibration geometry","Its repetition trains vibration into geometry.",7.5,"mantra",{}),
    Scene("Breath attention memory","Breath, attention, memory, and articulation begin to recur together.",9.0,"mantra",{}),
    Scene("Predictive deepening","The nervous system learns the object's ritual significance through repeated coupling.",9.0,"predict",{}),
    Scene("Not reduction","This does not reduce the rite to neurology.",7.0,"predict",{}),
    Scene("Embodied route","It identifies one embodied route by which significance becomes stable.",8.0,"predict",{}),

    Scene("Nyasa","Tantric nyāsa places mantras, deities, and powers upon the body.",8.0,"nyasa",{}),
    Scene("Body map","The body becomes a map rather than a private container.",7.5,"nyasa",{}),
    Scene("Heart sun","The heart can become sun.",5.5,"nyasa",{}),
    Scene("Breath mantra","Breath can become mantra.",5.5,"nyasa",{}),
    Scene("Limbs directions","Limbs can become directions.",6.0,"nyasa",{}),
    Scene("Practitioner object","The practitioner and object are consecrated together.",7.5,"nyasa",{}),
    Scene("No outside operator","There is no neutral operator standing outside the ritual.",8.0,"nyasa",{}),

    Scene("Yantra","Yantra gives the relation a spatial grammar.",6.5,"yantra",{}),
    Scene("Square threshold","The square establishes a threshold.",6.0,"yantra",{}),
    Scene("Triangle force","The triangle directs force.",5.5,"yantra",{}),
    Scene("Circle continuity","The circle stabilizes continuity.",5.5,"yantra",{}),
    Scene("Bindu concentration","The bindu gathers the field into one point.",6.5,"yantra",{}),
    Scene("Geometry operation","The diagram is not an illustration of a deity.",7.0,"yantra",{}),
    Scene("Spatial operation","It is a spatial operation for concentrating relation.",8.0,"yantra",{}),

    Scene("Theurgy","Iamblichean theurgy begins from a related insight.",7.0,"theurgy",{}),
    Scene("Symbols more than signs","Symbols are not merely signs invented by human agreement.",8.0,"theurgy",{}),
    Scene("Causal signatures","They are causal signatures linking levels of reality.",8.0,"theurgy",{}),
    Scene("Matter participates","Matter can participate in orders beyond itself without ceasing to be matter.",9.0,"theurgy",{}),
    Scene("Alignment","The rite aligns material, psychic, daimonic, and intelligible levels.",8.5,"theurgy",{}),
    Scene("No dragging heaven","It does not drag heaven downward.",6.5,"theurgy",{}),
    Scene("Transparency","It makes each level more transparent to the next.",8.0,"theurgy",{}),

    Scene("Presence question","What then becomes present in the object?",7.0,"presence",{}),
    Scene("Not trapped being","Not a trapped being compressed into metal.",7.5,"presence",{}),
    Scene("Not mere suggestion","Not merely a private suggestion in the practitioner's head.",8.0,"predict",{}),
    Scene("Meeting place","The object becomes a meeting-place.",6.5,"presence",{}),
    Scene("Relations converge","Memory, body, image, name, cosmology, and attention converge there.",9.0,"presence",{}),
    Scene("Presence relational","Presence is relational before it is substantial.",8.0,"presence",{}),

    Scene("Predictive transformation","Predictive perception helps explain one layer of this change.",8.0,"predict",{}),
    Scene("Ordinary object model","At first the object is predicted as ordinary material.",8.0,"predict",{}),
    Scene("Ritual learning","Repeated ritual changes expectation, salience, posture, and sensory weighting.",9.0,"predict",{}),
    Scene("Different perception","The same object can later be perceived as dense with significance.",8.0,"predict",{}),
    Scene("No proof","This does not prove celestial beings inhabit it.",7.0,"predict",{}),
    Scene("No dismissal","It also does not justify dismissing the experience as nothing but suggestion.",8.0,"predict",{}),
    Scene("Circuit visible","It shows that material meaning is enacted through a body-world circuit.",9.0,"predict",{}),

    Scene("Tradition","Tradition strengthens the circuit across generations.",7.0,"tradition",{}),
    Scene("Inherited attention","A ritual object inherits attention.",6.0,"tradition",{}),
    Scene("Gestures remembered","Hands remember how to hold it.",6.0,"tradition",{}),
    Scene("Voices remember","Voices remember how to sound around it.",6.0,"tradition",{}),
    Scene("Rooms remember","Rooms remember where it belongs.",6.0,"tradition",{}),
    Scene("Stories prepare","Stories prepare the field before the object is encountered.",8.0,"tradition",{}),
    Scene("Stored choreography","Tradition is stored choreography.",6.5,"tradition",{}),

    Scene("Fetishism","The first failure is fetishism.",6.0,"fetish",{}),
    Scene("Power property","Fetishism treats power as a property owned by the object.",8.0,"fetish",{}),
    Scene("Circuit forgotten","The practitioner, rite, lineage, ethics, and context disappear.",8.0,"fetish",{}),
    Scene("Commodity magic","The object becomes a magical commodity.",6.5,"fetish",{}),
    Scene("Relation forgotten","Relation is mistaken for substance.",6.5,"fetish",{}),

    Scene("Coercion","The second failure is coercion.",6.0,"coercion",{}),
    Scene("Force outcome","The object becomes a technology for forcing outcomes.",8.0,"coercion",{}),
    Scene("Domination logic","Desire replaces relation with domination.",7.5,"coercion",{}),
    Scene("Sacred shrinks","The sacred shrinks into a servant of appetite.",7.0,"coercion",{}),
    Scene("Instrumental world","The world becomes entirely instrumental.",7.0,"coercion",{}),
    Scene("Ritual collapse","At that point ritual has collapsed into manipulation.",8.0,"coercion",{}),

    Scene("Inflation","The third failure is inflation.",6.0,"fetish",{}),
    Scene("Special owner","The practitioner imagines possessing secret access unavailable to ordinary correction.",9.0,"fetish",{}),
    Scene("Feeling proof","Feeling becomes proof.",5.5,"fetish",{}),
    Scene("Object flatters","The object flatters identity rather than transforming it.",8.0,"fetish",{}),
    Scene("No resistance","Nothing resists the preferred story.",6.0,"fetish",{}),
    Scene("Imaginal discipline","A serious imaginal discipline requires resistance, time, and consequence.",9.0,"imaginal",{}),

    Scene("Abhasa","Kashmir Śaivism offers another language.",6.5,"abhasa",{}),
    Scene("Object appearance","The object is an ābhāsa, an appearance of consciousness.",8.0,"abhasa",{}),
    Scene("Not alien matter","It is not alien matter standing outside awareness.",7.0,"abhasa",{}),
    Scene("Not private fantasy","Nor is it private fantasy.",6.5,"abhasa",{}),
    Scene("Consciousness difference","Consciousness appears as material difference, relation, and recognition.",9.0,"abhasa",{}),
    Scene("Sacred already","Consecration does not make an otherwise dead universe sacred.",9.0,"abhasa",{}),
    Scene("Recognition training","It trains recognition of the sacred already appearing as form.",9.0,"recognition",{}),

    Scene("Recognition","This changes the final direction of ritual.",6.0,"recognition",{}),
    Scene("Not object monopoly","The object does not monopolize divine presence.",7.5,"recognition",{}),
    Scene("Doorway","It functions as a doorway.",5.5,"imaginal",{}),
    Scene("Presence returned","The presence encountered there is returned to the knower and world.",8.0,"recognition",{}),
    Scene("Every object potential","The consecrated object reveals what every object potentially is.",8.5,"recognition",{}),
    Scene("Particular intensifies universal","Particular intensity discloses universal appearing.",8.0,"recognition",{}),

    Scene("Imaginal depth","Corbin's imaginal clarifies why the object can remain material and open elsewhere.",9.0,"imaginal",{}),
    Scene("Here and more","It is here, yet more than here.",6.0,"imaginal",{}),
    Scene("Not portal fantasy","Not a science-fiction portal hidden inside the metal.",8.0,"imaginal",{}),
    Scene("Layered disclosure","A layered disclosure joining sensory form, symbolic intelligence, and encounter.",9.0,"imaginal",{}),
    Scene("Material preserved","The material location is preserved.",6.5,"imaginal",{}),
    Scene("Depth added","Depth is added without erasing the surface.",7.0,"imaginal",{}),

    Scene("Ethical test","The object must finally be tested by its fruit.",7.0,"ethics",{}),
    Scene("Clarity","Does it make perception clearer?",6.0,"ethics",{}),
    Scene("Humility","Does it reduce self-importance?",6.0,"ethics",{}),
    Scene("Courage","Does it enable difficult action?",6.0,"ethics",{}),
    Scene("Care","Does it enlarge care for bodies, promises, places, and other people?",9.0,"ethics",{}),
    Scene("Responsibility","Does the sacred become responsibility rather than privilege?",8.0,"ethics",{}),
    Scene("Fruit validates","The fruit does not prove the metaphysics, but it tests the encounter.",9.0,"ethics",{}),

    Scene("Return","A ritual object must return the practitioner to the ordinary world.",8.0,"return",{}),
    Scene("Not escape","Not enchanted away from matter.",6.0,"return",{}),
    Scene("More answerable","More answerable within matter.",6.5,"return",{}),
    Scene("Stone remains stone","The stone remains stone.",5.5,"return",{}),
    Scene("Relation remembered","But the relation it condensed can now be recognized elsewhere.",8.0,"return",{}),
    Scene("Sun in metal","The sun in metal becomes the sun in courage.",7.0,"return",{}),
    Scene("Venus in fragrance","Venus in fragrance becomes care in speech.",7.0,"return",{}),
    Scene("Saturn in lead","Saturn in lead becomes endurance in time.",7.0,"return",{}),
    Scene("Correspondence embodied","Correspondence becomes embodied character.",8.0,"return",{}),

    Scene("Final return","At first the object is only matter.",5.5,"raw",{}),
    Scene("Then relation","Then geometry, sound, breath, memory, and attention gather around it.",9.0,"final",{}),
    Scene("Circuit forms","A circuit forms between material support and living participation.",8.0,"final",{}),
    Scene("Heaven remembered","Matter begins to remember heaven.",7.0,"final",{}),
    Scene("Not escape upward","Not by escaping upward.",5.5,"final",{}),
    Scene("Relation visible","By making correspondence visible within form.",8.0,"final",{}),
    Scene("Final thesis","A ritual object teaches matter to remember heaven.",8.0,"final",{}),
    Scene("Final criterion","Its success is measured by whether the practitioner learns to remember it too.",9.0,"ethics",{}),
]


def export_original_essay():
    paragraphs=["# a ritual object teaches matter to remember heaven",""]
    for scene in SCENES:
        paragraphs.append(scene.narration)
        paragraphs.append("")
    path=OUTPUT/"original_essay.md"
    path.write_text("\n".join(paragraphs),encoding="utf-8")
    return path


def render_frame(scene,frame_index,frame_count,width,height,seed):
    u=frame_index/max(1,frame_count-1)
    t=u*scene.duration
    dark=scene.visual in {"spiritus"}
    im=background(width,height,seed,dark)
    VISUALS[scene.visual](im,u,t,scene.params)
    border(im,dark)
    return im.convert("RGB")


def require_ffmpeg():
    exe=shutil.which("ffmpeg")
    if not exe: raise RuntimeError("ffmpeg is required but was not found on PATH")
    return exe


def encode_scene(scene_index,fps):
    frame_dir=FRAMES/f"scene_{scene_index:03d}"
    output_path=SCENES_DIR/f"scene_{scene_index:03d}.mp4"
    subprocess.run([
        require_ffmpeg(),"-y",
        "-framerate",str(fps),
        "-i",str(frame_dir/"%05d.jpg"),
        "-c:v","libx264",
        "-preset","medium",
        "-crf","18",
        "-pix_fmt","yuv420p",
        "-movflags","+faststart",
        str(output_path)
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return output_path


def render_scene(scene_index,scene,fps,width,height,preview):
    frame_dir=FRAMES/f"scene_{scene_index:03d}"
    frame_dir.mkdir(parents=True,exist_ok=True)
    SCENES_DIR.mkdir(parents=True,exist_ok=True)
    frame_count=max(2,round(scene.duration*fps))
    if preview:
        for out_index,frame_index in enumerate([0,int(frame_count*.35),int(frame_count*.72),frame_count-1]):
            render_frame(scene,frame_index,frame_count,width,height,scene_index*1000+frame_index).save(
                frame_dir/f"preview_{out_index:02d}.jpg",quality=95
            )
        return frame_dir
    for frame_index in range(frame_count):
        path=frame_dir/f"{frame_index:05d}.jpg"
        if path.exists(): continue
        render_frame(scene,frame_index,frame_count,width,height,scene_index*1000+frame_index).save(
            path,quality=95,subsampling=0
        )
    return encode_scene(scene_index,fps)


def concatenate(scene_paths):
    concat_file=OUTPUT/"concat.txt"
    concat_file.write_text("\n".join(f"file '{p.resolve()}'" for p in scene_paths),encoding="utf-8")
    output_path=OUTPUT/"a_ritual_object_teaches_matter_to_remember_heaven.mp4"
    subprocess.run([
        require_ffmpeg(),"-y","-f","concat","-safe","0","-i",str(concat_file),
        "-c","copy","-movflags","+faststart",str(output_path)
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return output_path


def export_timeline():
    cursor=0.0
    payload=[]
    for index,scene in enumerate(SCENES,start=1):
        record=asdict(scene)
        record["scene_id"]=f"scene_{index:03d}"
        record["start_seconds"]=round(cursor,3)
        cursor+=scene.duration
        record["end_seconds"]=round(cursor,3)
        payload.append(record)
    path=OUTPUT/"narration_timeline.json"
    path.write_text(json.dumps({
        "title":"a ritual object teaches matter to remember heaven",
        "runtime_seconds":round(cursor,3),
        "scene_count":len(SCENES),
        "original_essay":True,
        "style":{
            "continuity_object":"dark talisman becoming a relational circuit",
            "shot_duration_range_seconds":[5,10],
            "palette_roles":{
                "graphite":"raw matter",
                "gold":"celestial correspondence",
                "cyan":"breath and embodied coupling",
                "violet":"imaginal depth",
                "crimson":"coercion and inflation",
                "green":"ethical embodiment",
                "silver":"inherited ritual memory"
            }
        },
        "scenes":payload
    },indent=2,ensure_ascii=False),encoding="utf-8")
    return path


def make_contact_sheet(width,height):
    thumb_w=320
    thumb_h=int(thumb_w*height/width)
    thumbs=[]
    for index,scene in enumerate(SCENES,start=1):
        frame_count=max(2,round(scene.duration*DEFAULT_FPS))
        im=render_frame(scene,int(frame_count*.72),frame_count,width,height,index*1000+72)
        im.thumbnail((thumb_w,thumb_h))
        thumbs.append((index,scene.title,im.copy()))
    columns=4
    rows=math.ceil(len(thumbs)/columns)
    cell_h=thumb_h+52
    sheet=Image.new("RGB",(columns*thumb_w,rows*cell_h),WHITE)
    d=ImageDraw.Draw(sheet)
    label_font=load_font(FONT_SANS_BOLD,15)
    for index,title,im in thumbs:
        slot=index-1
        x=(slot%columns)*thumb_w
        y=(slot//columns)*cell_h
        sheet.paste(im,(x,y))
        d.text((x+10,y+thumb_h+8),f"{index:03d}  {title}",font=label_font,fill=INK)
    path=OUTPUT/"contact_sheet.jpg"
    sheet.save(path,quality=94)
    return path


def parse_args():
    parser=argparse.ArgumentParser()
    parser.add_argument("--fps",type=int,default=DEFAULT_FPS)
    parser.add_argument("--width",type=int,default=DEFAULT_WIDTH)
    parser.add_argument("--height",type=int,default=DEFAULT_HEIGHT)
    parser.add_argument("--scene",type=int,default=None)
    parser.add_argument("--preview",action="store_true")
    parser.add_argument("--no-contact-sheet",action="store_true")
    return parser.parse_args()


def main():
    args=parse_args()
    OUTPUT.mkdir(parents=True,exist_ok=True)
    FRAMES.mkdir(parents=True,exist_ok=True)
    SCENES_DIR.mkdir(parents=True,exist_ok=True)

    print(f"Essay: {export_original_essay()}")
    print(f"Timeline: {export_timeline()}")
    print(f"Scenes: {len(SCENES)}")
    print(f"Runtime: {sum(s.duration for s in SCENES)/60:.2f} minutes")

    if args.scene is not None:
        if not 1<=args.scene<=len(SCENES):
            raise ValueError(f"--scene must be between 1 and {len(SCENES)}")
        print(render_scene(args.scene,SCENES[args.scene-1],args.fps,args.width,args.height,args.preview))
        return

    rendered=[]
    for index,scene in enumerate(SCENES,start=1):
        print(f"[{index:03d}/{len(SCENES):03d}] {scene.title} ({scene.duration:.1f}s)")
        result=render_scene(index,scene,args.fps,args.width,args.height,args.preview)
        if not args.preview:
            rendered.append(result)

    if not args.no_contact_sheet:
        print(f"Contact sheet: {make_contact_sheet(args.width,args.height)}")
    if not args.preview:
        print(f"Final video: {concatenate(rendered)}")


if __name__=="__main__":
    main()
