#!/usr/bin/env python3
"""
A TEMPLE TEACHES SPACE HOW TO BECOME A BODY
An original Imaginarium visual essay and Platinum-house procedural renderer.

ORIGINAL THESIS
---------------
A temple is not merely a building that contains a sacred object.
It reorganizes distance, direction, rhythm, sound, darkness, and bodily movement
until space begins to behave like a living body with a center.

This essay joins:
• Vāstu-puruṣa, maṇḍala, axis, threshold, and garbhagṛha
• Tantric body-temple correspondences
• Kashmir Śaiva ābhāsa, spanda, and recognition
• Iamblichean and Proclean sacred architecture
• Corbinian imaginal geography
• embodied cognition, affordances, and predictive perception
• the ethical distinction between sacred orientation and monumental domination

DESIGN CONTRACT
---------------
• Every shot lasts 5–10 seconds.
• Every shot visibly performs the narrated operation.
• Clean white architectural field; deep indigo only for sanctum and imaginal depth.
• No static slide layouts and no decorative loops.
• Graphite = ordinary geometry / material architecture
• Gold = axis, center, consecrated orientation
• Cyan = movement, breath, sensory flow, circumambulation
• Violet = imaginal depth, hidden interior, sacred night
• Crimson = blocked access, domination, false centrality
• Green = integration, return, ethical inhabitation
• Silver = inherited measure, memory, proportion
• Continuity object: an empty square becomes a living sacred body.
• Geometry must grow from architectural operation, not decorative ornament.
• The sanctum must feel dense through absence, not overloaded spectacle.
• The final image must return sacred orientation to ordinary lived space.

OUTPUT
------
output_temple_body/
  frames/scene_001/*.jpg
  scenes/scene_001.mp4
  a_temple_teaches_space_how_to_become_a_body.mp4
  narration_timeline.json
  original_essay.md
  contact_sheet.jpg

REQUIREMENTS
------------
pip install pillow numpy
ffmpeg must be on PATH.

USAGE
-----
python a_temple_teaches_space_how_to_become_a_body_platinum.py
python a_temple_teaches_space_how_to_become_a_body_platinum.py --preview
python a_temple_teaches_space_how_to_become_a_body_platinum.py --scene 12
python a_temple_teaches_space_how_to_become_a_body_platinum.py --fps 12 --width 1920 --height 1080
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
OUTPUT = ROOT / "output_temple_body"
FRAMES = OUTPUT / "frames"
SCENES_DIR = OUTPUT / "scenes"

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 10

WHITE = (248,247,243)
INK = (28,31,35)
SOFT = (84,88,94)
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

FS = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FSB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FSS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FSSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


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

def font(path,size):
    for p in (path,FS,FSS):
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

def ctext(d,xy,text,f,fill=INK):
    d.text(xy,text,font=f,fill=fill,anchor="mm")

def seal(im,title,subtitle="",color=INK,dark=False):
    w,h=im.size
    d=ImageDraw.Draw(im)
    ctext(d,(w/2,h*.875),title,font(FSB,max(22,int(h*.042))),WHITE if dark else color)
    if subtitle:
        ctext(d,(w/2,h*.925),subtitle,font(FSS,max(13,int(h*.020))),PALE_SILVER if dark else SOFT)

def border(im,dark=False):
    w,h=im.size
    ImageDraw.Draw(im).rounded_rectangle((25,25,w-25,h-25),radius=17,
        outline=(*(WHITE if dark else INK),42),width=2)

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
    ImageDraw.Draw(im).ellipse((x-r*.38,y-r*.38,x+r*.38,y+r*.38),
                               fill=(*mix(col,WHITE,.3),230))

def partial(points,p):
    p=clamp(p)
    if len(points)<2:return points
    lens=[math.dist(a,b) for a,b in zip(points[:-1],points[1:])]
    total=sum(lens); target=total*p
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

def square_body(d,cx,cy,size,col=INK,alpha=200,width=4):
    d.rectangle((cx-size/2,cy-size/2,cx+size/2,cy+size/2),
                outline=(*col,alpha),width=width)

def temple_plan(d,cx,cy,size,progress=1.0):
    q=clamp(progress)
    square_body(d,cx,cy,size,INK,int(180*q),4)
    for frac,col in [(.76,SILVER),(.52,GOLD),(.26,VIOLET)]:
        s=size*frac*q
        square_body(d,cx,cy,s,col,int(150*q),3)
    # cardinal gates
    gate=size*.14*q
    d.line((cx-gate/2,cy-size/2,cx+gate/2,cy-size/2),fill=(*WHITE,255),width=8)
    d.line((cx-gate/2,cy+size/2,cx+gate/2,cy+size/2),fill=(*WHITE,255),width=8)
    d.line((cx-size/2,cy-gate/2,cx-size/2,cy+gate/2),fill=(*WHITE,255),width=8)
    d.line((cx+size/2,cy-gate/2,cx+size/2,cy+gate/2),fill=(*WHITE,255),width=8)

def axis(d,cx,cy,length,col=GOLD,alpha=190):
    d.line((cx,cy-length/2,cx,cy+length/2),fill=(*col,alpha),width=5)
    d.line((cx-length/2,cy,cx+length/2,cy),fill=(*col,alpha),width=5)

def person(d,cx,cy,scale=1.0,col=INK,alpha=200):
    d.ellipse((cx-14*scale,cy-56*scale,cx+14*scale,cy-28*scale),
              outline=(*col,alpha),width=3)
    d.line((cx,cy-28*scale,cx,cy+30*scale),fill=(*col,alpha),width=4)
    d.line((cx,cy-5*scale,cx-30*scale,cy+20*scale),fill=(*col,alpha),width=4)
    d.line((cx,cy-5*scale,cx+30*scale,cy+20*scale),fill=(*col,alpha),width=4)
    d.line((cx,cy+30*scale,cx-20*scale,cy+70*scale),fill=(*col,alpha),width=4)
    d.line((cx,cy+30*scale,cx+20*scale,cy+70*scale),fill=(*col,alpha),width=4)

def spiral_path(cx,cy,r0,r1,turns,points=220):
    pts=[]
    for i in range(points):
        q=i/(points-1)
        a=q*math.tau*turns-math.pi/2
        r=lerp(r0,r1,q)
        pts.append((cx+math.cos(a)*r,cy+math.sin(a)*r*.62))
    return pts

def star_field(d,w,h,seed=5,alpha=100):
    rng=random.Random(seed)
    for _ in range(90):
        x=rng.uniform(w*.08,w*.92); y=rng.uniform(h*.08,h*.72)
        r=rng.choice([1,1,1,2])
        d.ellipse((x-r,y-r,x+r,y+r),fill=(*PALE_GOLD,alpha))

def breath_curve(w,h,phase=0,y=.42):
    pts=[]
    for i in range(180):
        q=i/179
        x=lerp(w*.08,w*.92,q)
        yy=h*y+math.sin(q*math.tau*2+phase)*h*.035+math.sin(q*math.tau*7-phase)*h*.010
        pts.append((x,yy))
    return pts


@dataclass
class Scene:
    title:str
    narration:str
    duration:float
    visual:str
    params:dict


def v_empty_square(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    square_body(d,w*.5,h*.42,lerp(70,w*.34,q),mix(SILVER,INK,q),200,4)
    seal(im,"AT FIRST SPACE IS UNDIFFERENTIATED","every direction is equivalent")

def v_axis_birth(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    square_body(d,cx,cy,w*.32,SILVER,160,3)
    axis(d,cx,cy,w*.30*q,GOLD,int(190*q))
    glow_circle(im,cx,cy,14+18*q,GOLD,150,12)
    seal(im,"THE FIRST SACRED ACT IS ORIENTATION","a center appears because directions are no longer equal")

def v_vastu_purusha(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    temple_plan(d,cx,cy,w*.36,q)
    # diagonal body
    person(d,cx,cy,1.45,VIOLET,int(150*q))
    d.line((cx-w*.16,cy+h*.16,cx+w*.16,cy-h*.16),fill=(*GOLD,int(130*q)),width=4)
    seal(im,"VĀSTU-PURUṢA","space is treated as a body before a building occupies it")

def v_cardinal_directions(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    temple_plan(d,cx,cy,w*.32,q)
    dirs=[("EAST",GOLD,0,-1),("SOUTH",CRIMSON,1,0),("WEST",VIOLET,0,1),("NORTH",CYAN,-1,0)]
    for i,(txt,col,dx,dy) in enumerate(dirs):
        x=cx+dx*w*.27; y=cy+dy*h*.28
        glow_line(im,partial([(cx,cy),(x,y)],smoothstep(i*.10,.82,u)),col,4,11,160)
        if q>.7:ctext(d,(x,y),txt,font(FSSB,int(h*.014)),col)
    seal(im,"DIRECTION BECOMES QUALITATIVE","east is not merely elsewhere; it is arrival")

def v_threshold(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.25,h*.42); right=(w*.75,h*.42)
    square_body(d,left[0],left[1],130,SILVER,170,4)
    temple_plan(d,right[0],right[1],180,ease(u))
    q=ease(u)
    glow_line(im,partial([(left[0]+65,left[1]),(w*.5,h*.31),(right[0]-90,right[1])],q),GOLD,5,13,200)
    d.rectangle((w*.48,h*.23,w*.52,h*.60),fill=(*CRIMSON,80),outline=(*CRIMSON,150))
    seal(im,"A THRESHOLD DOES NOT MERELY SEPARATE","it changes the mode of movement")

def v_procession(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.72,h*.42
    temple_plan(d,cx,cy,w*.26,1)
    path=[(w*.08,h*.62),(w*.25,h*.55),(w*.38,h*.46),(w*.52,h*.42),(cx-w*.13,cy)]
    q=ease(u)
    glow_line(im,partial(path,q),CYAN,6,14,210)
    idx=min(len(path)-1,int(q*(len(path)-1)))
    person(d,*path[idx],.65,GREEN,200)
    seal(im,"PROCESSION WRITES MEANING INTO DISTANCE","approach becomes part of knowledge")

def v_circumambulation(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    temple_plan(d,cx,cy,w*.24,1)
    path=spiral_path(cx,cy,w*.28,w*.15,1.8)
    q=ease(u)
    glow_line(im,partial(path,q),CYAN,5,13,200)
    idx=min(len(path)-1,int(q*(len(path)-1)))
    person(d,*path[idx],.55,GREEN,190)
    seal(im,"CIRCUMAMBULATION TEACHES THE CENTER INDIRECTLY","the body learns by orbiting what it cannot yet enter")

def v_garbhagriha(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    # nested dark chambers
    for i,col in enumerate((SILVER,INK,VIOLET)):
        s=w*(.32-i*.08)
        d.rectangle((cx-s/2,cy-s*.42,cx+s/2,cy+s*.42),outline=(*col,int(160*q)),width=4)
    inner=w*.10
    d.rectangle((cx-inner/2,cy-inner*.42,cx+inner/2,cy+inner*.42),
                fill=(*VOID,int(240*q)),outline=(*GOLD,int(180*q)),width=4)
    glow_circle(im,cx,cy,12+14*q,GOLD,120,11)
    seal(im,"GARBHAGṚHA","the womb-chamber gathers the building into hidden density",dark=True)

def v_light_measure(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    d.rectangle((w*.18,h*.22,w*.82,h*.62),outline=(*INK,160),width=4)
    q=ease(u)
    # thin light blade
    x=lerp(w*.18,w*.82,q)
    d.polygon([(x-25,h*.22),(x+25,h*.22),(cx+35,h*.62),(cx-35,h*.62)],fill=(*PALE_GOLD,100))
    glow_circle(im,cx,h*.53,16,GOLD,150,10)
    seal(im,"LIGHT BECOMES A MEASURE OF TIME","architecture teaches the sun where to speak")

def v_sound_architecture(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    temple_plan(d,cx,cy,w*.30,1)
    q=ease(u)
    for i in range(9):
        r=(45+i*25)*q
        d.arc((cx-r,cy-r*.62,cx+r,cy+r*.62),20,340,fill=(*mix(CYAN,GOLD,i/8),120),width=3)
    seal(im,"CHANT MAKES THE WALLS AUDIBLE","sound reveals architecture as a resonant body")

def v_body_temple(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.42); right=(w*.72,h*.42)
    person(d,*left,1.2,INK,190)
    temple_plan(d,*right,w*.25,ease(u))
    q=ease(u)
    correspond=[((left[0],h*.20),(right[0],h*.29),GOLD),
                ((left[0],h*.34),(right[0],h*.38),CYAN),
                ((left[0],h*.47),(right[0],h*.47),VIOLET),
                ((left[0],h*.60),(right[0],h*.56),GREEN)]
    for i,(a,b,col) in enumerate(correspond):
        glow_line(im,partial([a,b],smoothstep(i*.10,.88,u)),col,3,9,130)
    seal(im,"THE BODY BECOMES TEMPLE · THE TEMPLE BECOMES BODY","correspondence is enacted through movement")

def v_spanda_architecture(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=pulse(t,.65)
    size=lerp(w*.20,w*.34,q)
    temple_plan(d,cx,cy,size,1)
    glow_circle(im,cx,cy,18+16*q,GOLD,140,12)
    seal(im,"SPANDA IN STONE","expansion and contraction become traversable")

def v_predictive_affordance(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.18,h*.42); center=(w*.50,h*.42); right=(w*.82,h*.42)
    person(d,*left,.75,INK,190)
    d.rounded_rectangle((center[0]-85,center[1]-65,center[0]+85,center[1]+65),
                        radius=18,fill=(*PALE_CYAN,215),outline=(*CYAN,180),width=3)
    ctext(d,center,"MODEL",font(FSSB,int(h*.020)),CYAN)
    temple_plan(d,*right,w*.18,ease(u))
    q=ease(u)
    glow_line(im,partial([left,center,right],q),CYAN,4,11,170)
    glow_line(im,partial([right,(w*.64,h*.56),center,(w*.35,h*.56),left],smoothstep(.35,.95,u)),GOLD,4,11,160)
    seal(im,"ARCHITECTURE CHANGES WHAT THE BODY EXPECTS TO DO","doors, stairs, darkness, and scale become predictions")

def v_imaginal_geography(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    star_field(d,w,h,13,90)
    cx,cy=w*.5,h*.42
    q=ease(u)
    temple_plan(d,cx,cy,w*.27,q)
    for r,col in [(110,VIOLET),(155,GOLD),(210,CYAN)]:
        d.ellipse((cx-r*q,cy-r*.62*q,cx+r*q,cy+r*.62*q),
                  outline=(*col,int(110*q)),width=3)
    seal(im,"IMAGINAL GEOGRAPHY","a place can remain physical and open into more than physical depth",dark=True)

def v_presence_center(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    temple_plan(d,cx,cy,w*.30,1)
    q=ease(u)
    glow_circle(im,cx,cy,16+28*q,GOLD,150,13)
    # surrounding relations
    for i,col in enumerate((CYAN,VIOLET,GREEN,SILVER)):
        a=i*math.tau/4
        x=cx+math.cos(a)*w*.26; y=cy+math.sin(a)*h*.23
        glow_line(im,partial([(x,y),(cx,cy)],smoothstep(i*.10,.88,u)),col,3,9,130)
    seal(im,"THE CENTER IS NOT AN OBJECT AMONG OBJECTS","it is the relation that orders every approach")

def v_power_failure(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.42); right=(w*.72,h*.42)
    # domination
    temple_plan(d,*left,w*.22,1)
    d.rectangle((left[0]-120,left[1]-120,left[0]+120,left[1]+120),
                outline=(*CRIMSON,190),width=6)
    arrow(d,(left[0],h*.16),(left[0],h*.31),CRIMSON,5,14)
    ctext(d,(left[0],h*.68),"MONUMENTAL POWER",font(FSSB,int(h*.014)),CRIMSON)
    # orientation
    temple_plan(d,*right,w*.22,ease(u))
    glow_circle(im,right[0],right[1],20,GREEN,130,11)
    ctext(d,(right[0],h*.68),"SACRED ORIENTATION",font(FSSB,int(h*.014)),GREEN)
    seal(im,"NOT EVERY CENTER IS SACRED","some architecture teaches submission rather than recognition")

def v_exclusion_failure(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    temple_plan(d,cx,cy,w*.30,1)
    # gates close
    q=ease(u)
    for a,b in [((cx-30,cy-w*.15),(cx+30,cy-w*.15)),
                ((cx-30,cy+w*.15),(cx+30,cy+w*.15)),
                ((cx-w*.15,cy-30),(cx-w*.15,cy+30)),
                ((cx+w*.15,cy-30),(cx+w*.15,cy+30))]:
        d.line((*a,*b),fill=(*CRIMSON,int(210*q)),width=8)
    seal(im,"A TEMPLE CAN FORGET THE WORLD IT CLAIMS TO CENTER","sacred space becomes false when relation becomes exclusion")

def v_abhasa_space(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    temple_plan(d,cx,cy,w*.22,q)
    for i in range(18):
        a=i*math.tau/18
        rr=lerp(25,210,q)*(0.7+0.3*((i%4)/3))
        x=cx+math.cos(a+t*.08)*rr; y=cy+math.sin(a+t*.08)*rr*.62
        col=mix(CYAN,VIOLET,i/17)
        glow_circle(im,x,y,5+3*(i%3),col,90,7)
        glow_line(im,[(cx,cy),(x,y)],col,2,7,70)
    seal(im,"ĀBHĀSA","space is consciousness appearing as relation and distance")

def v_recognition_center(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.22,h*.42); right=(w*.75,h*.42)
    person(d,*left,.8,INK,190)
    temple_plan(d,*right,w*.23,ease(u))
    q=ease(u)
    glow_line(im,partial([left,(w*.5,h*.30),right],q),CYAN,4,11,170)
    glow_line(im,partial([right,(w*.5,h*.56),left],smoothstep(.30,.95,u)),GOLD,5,13,200)
    seal(im,"RECOGNITION RETURNS THE CENTER TO THE KNOWER","the sanctum reveals a capacity already present in awareness")

def v_city_return(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    # city grid
    for i in range(9):
        x=w*(.10+i*.10)
        d.line((x,h*.18,x,h*.68),fill=(*SILVER,70),width=2)
    for j in range(7):
        y=h*(.18+j*.08)
        d.line((w*.08,y,w*.92,y),fill=(*SILVER,70),width=2)
    temple_plan(d,w*.22,h*.42,w*.14,1)
    q=ease(u)
    path=[(w*.29,h*.42),(w*.45,h*.34),(w*.62,h*.49),(w*.84,h*.40)]
    glow_line(im,partial(path,q),GREEN,6,14,210)
    seal(im,"THE TEMPLE MUST TEACH THE CITY HOW TO HAVE A CENTER","not one building's privilege, but a way of inhabiting space")

def v_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    temple_plan(d,cx,cy,lerp(80,w*.34,q),q)
    axis(d,cx,cy,w*.30*q,GOLD,int(180*q))
    glow_circle(im,cx,cy,18+20*q,GOLD,150,13)
    # breath and movement
    glow_line(im,partial(breath_curve(w,h,t*.35,.42),q),CYAN,4,12,160)
    path=spiral_path(cx,cy,w*.25,w*.10,1.4)
    glow_line(im,partial(path,q),GREEN,4,11,160)
    seal(im,"A TEMPLE TEACHES SPACE HOW TO BECOME A BODY",
         "direction becomes relation · center becomes responsibility",color=GREEN)


VISUALS:dict[str,Callable]={
    "empty":v_empty_square,
    "axis":v_axis_birth,
    "vastu":v_vastu_purusha,
    "directions":v_cardinal_directions,
    "threshold":v_threshold,
    "procession":v_procession,
    "circumambulation":v_circumambulation,
    "sanctum":v_garbhagriha,
    "light":v_light_measure,
    "sound":v_sound_architecture,
    "body":v_body_temple,
    "spanda":v_spanda_architecture,
    "predict":v_predictive_affordance,
    "imaginal":v_imaginal_geography,
    "presence":v_presence_center,
    "power":v_power_failure,
    "exclusion":v_exclusion_failure,
    "abhasa":v_abhasa_space,
    "recognition":v_recognition_center,
    "return":v_city_return,
    "final":v_final,
}


SCENES:list[Scene]=[
    Scene("Empty square","At first there is only an empty square.",6.0,"empty",{}),
    Scene("Equivalent directions","Every direction is equivalent.",5.5,"empty",{}),
    Scene("No sacred center","Nothing yet distinguishes center from edge.",6.5,"empty",{}),
    Scene("Orientation begins","Then an axis is drawn.",5.5,"axis",{}),
    Scene("Directions unequal","East, west, north, and south cease to be interchangeable.",8.0,"directions",{}),
    Scene("Center appears","A center appears because movement has been given meaning.",8.0,"axis",{}),
    Scene("Temple thesis","A temple teaches space how to become a body.",8.0,"final",{}),

    Scene("Building not container","A temple is not merely a building containing a sacred object.",8.0,"empty",{}),
    Scene("Reorganizes relations","It reorganizes distance, direction, rhythm, sound, light, and bodily movement.",9.5,"final",{}),
    Scene("Space behaves","Space begins to behave like a living body.",7.0,"body",{}),
    Scene("Edges limbs","Edges become limbs.",5.5,"body",{}),
    Scene("Thresholds senses","Thresholds become senses.",5.5,"threshold",{}),
    Scene("Sanctum heart","The sanctum becomes heart.",5.5,"sanctum",{}),
    Scene("Axis spine","The axis becomes spine.",5.5,"axis",{}),

    Scene("Vastu purusha","The vāstu-puruṣa maṇḍala makes this explicit.",8.0,"vastu",{}),
    Scene("Body beneath plan","A cosmic body is imagined beneath the architectural plan.",8.0,"vastu",{}),
    Scene("Not decorative myth","This is not merely decorative myth.",7.0,"vastu",{}),
    Scene("Space treated alive","It trains builders to treat space as already differentiated and alive.",9.0,"vastu",{}),
    Scene("Building negotiation","Construction becomes negotiation with a body rather than occupation of emptiness.",9.0,"vastu",{}),

    Scene("Orientation first","The first sacred act is orientation.",6.0,"axis",{}),
    Scene("East arrival","East becomes arrival.",5.5,"directions",{}),
    Scene("West withdrawal","West becomes withdrawal.",5.5,"directions",{}),
    Scene("North ascent","North becomes ascent.",5.5,"directions",{}),
    Scene("South descent","South becomes descent.",5.5,"directions",{}),
    Scene("Qualitative direction","Direction becomes qualitative.",6.5,"directions",{}),
    Scene("World no longer neutral","The world is no longer geometrically neutral.",7.5,"directions",{}),

    Scene("Threshold","A threshold is more than a gap in a wall.",7.0,"threshold",{}),
    Scene("Crossing mode","Crossing changes the mode of movement.",6.5,"threshold",{}),
    Scene("Shoes removed","Shoes are removed.",5.5,"threshold",{}),
    Scene("Voice changes","The voice changes.",5.5,"threshold",{}),
    Scene("Speed changes","Speed changes.",5.5,"threshold",{}),
    Scene("Attention changes","Attention changes.",5.5,"threshold",{}),
    Scene("Body knows first","The body knows before the doctrine is explained.",8.0,"threshold",{}),

    Scene("Procession","A procession writes meaning into distance.",7.0,"procession",{}),
    Scene("Approach matters","The way one approaches becomes part of what is known.",8.0,"procession",{}),
    Scene("No instant access","The center is not instantly available.",6.5,"procession",{}),
    Scene("Distance ripens","Distance ripens attention.",6.5,"procession",{}),
    Scene("Movement prepares","Movement prepares perception.",6.5,"procession",{}),
    Scene("Arrival transformed","By arrival, the one who arrives has changed.",8.0,"procession",{}),

    Scene("Circumambulation","Circumambulation teaches the center indirectly.",7.5,"circumambulation",{}),
    Scene("Orbit before entry","The body orbits what it cannot yet enter.",7.5,"circumambulation",{}),
    Scene("Center inferred","The center is inferred through repeated relation.",8.0,"circumambulation",{}),
    Scene("No possession","One does not seize the sacred center.",6.5,"circumambulation",{}),
    Scene("Learn gravity","One learns its gravity.",6.5,"circumambulation",{}),

    Scene("Garbhagriha","The garbhagṛha is the womb-chamber.",7.0,"sanctum",{}),
    Scene("Small dark dense","It is often small, dark, and dense.",7.0,"sanctum",{}),
    Scene("Outer complexity inward","The complexity of the outer building contracts inward.",8.0,"sanctum",{}),
    Scene("Maximum meaning minimum space","Maximum meaning occupies minimum space.",8.0,"sanctum",{}),
    Scene("Hidden center","The center becomes powerful through concealment rather than display.",8.5,"sanctum",{}),
    Scene("Absence density","Absence produces density.",6.0,"sanctum",{}),

    Scene("Light","Light is made architectural.",6.0,"light",{}),
    Scene("Not generic brightness","Not every surface is equally illuminated.",7.0,"light",{}),
    Scene("Sunbeam timed","A beam arrives at a particular hour.",6.5,"light",{}),
    Scene("Stone receives time","Stone receives time.",5.5,"light",{}),
    Scene("Sun speaks","Architecture teaches the sun where to speak.",7.0,"light",{}),
    Scene("Time embodied","Time becomes visible as an event in space.",8.0,"light",{}),

    Scene("Sound","Sound reveals the temple as a resonant body.",7.0,"sound",{}),
    Scene("Chant walls","A chant enters walls, corridors, domes, and chambers.",8.0,"sound",{}),
    Scene("Echo returns altered","The voice returns altered by the building.",8.0,"sound",{}),
    Scene("Architecture answers","Architecture answers the chant.",7.0,"sound",{}),
    Scene("No mute container","The building is no longer a mute container.",7.0,"sound",{}),
    Scene("Audible body","It becomes an audible body.",6.5,"sound",{}),

    Scene("Body temple","Tantric traditions turn this correspondence inward.",8.0,"body",{}),
    Scene("Body as temple","The body becomes temple.",6.0,"body",{}),
    Scene("Temple as body","The temple becomes body.",6.0,"body",{}),
    Scene("Heart sanctum","Heart corresponds to sanctum.",6.0,"body",{}),
    Scene("Breath procession","Breath corresponds to procession.",6.0,"body",{}),
    Scene("Channels corridors","Channels correspond to corridors.",6.0,"body",{}),
    Scene("Crown spire","The crown corresponds to spire.",6.0,"body",{}),
    Scene("Correspondence enacted","The correspondence is enacted through posture, breath, sound, and attention.",9.5,"body",{}),

    Scene("Spanda architecture","Spanda can be read architecturally.",7.0,"spanda",{}),
    Scene("Expansion courtyard","Expansion becomes courtyard.",6.0,"spanda",{}),
    Scene("Contraction chamber","Contraction becomes chamber.",6.0,"spanda",{}),
    Scene("Opening gate","Opening becomes gate.",5.5,"spanda",{}),
    Scene("Closure sanctum","Closure becomes sanctum.",5.5,"spanda",{}),
    Scene("Pulse traversable","The pulse becomes traversable in stone.",7.5,"spanda",{}),
    Scene("Building breathes","The building appears to breathe through movement.",7.5,"spanda",{}),

    Scene("Embodied cognition","Embodied cognition explains one layer of temple power.",8.0,"predict",{}),
    Scene("Architecture affords","Architecture offers actions before concepts.",7.0,"predict",{}),
    Scene("Door invites crossing","A door invites crossing.",5.5,"predict",{}),
    Scene("Stair invites ascent","A stair invites ascent.",5.5,"predict",{}),
    Scene("Darkness slows","Darkness slows the body.",5.5,"predict",{}),
    Scene("Height lowers voice","Height lowers the voice into awe.",6.5,"predict",{}),
    Scene("Body predicts ritual","The body learns to predict what kind of attention belongs here.",8.5,"predict",{}),

    Scene("Predictive perception","Repeated ritual reshapes expectation and salience.",8.0,"predict",{}),
    Scene("Same stone different world","The same stone can later be encountered as a different world.",8.0,"imaginal",{}),
    Scene("No reduction","This does not reduce sacred architecture to psychology.",7.0,"predict",{}),
    Scene("Embodied route","It identifies one embodied route by which sacred meaning becomes stable.",9.0,"predict",{}),

    Scene("Imaginal geography","A temple can become imaginal geography.",7.0,"imaginal",{}),
    Scene("Physical location remains","It remains a physical location.",6.5,"imaginal",{}),
    Scene("More than coordinates","Yet it opens into more than coordinates.",7.0,"imaginal",{}),
    Scene("Mountain axis","A mountain can become axis.",5.5,"imaginal",{}),
    Scene("River boundary","A river can become boundary.",5.5,"imaginal",{}),
    Scene("Cave womb","A cave can become womb.",5.5,"imaginal",{}),
    Scene("City cosmos","A city can become cosmos.",5.5,"imaginal",{}),
    Scene("Depth without disappearance","Imaginal depth does not erase geography; it intensifies it.",8.5,"imaginal",{}),

    Scene("Center question","What becomes present at the center?",7.0,"presence",{}),
    Scene("Not object only","Not merely an object among objects.",7.0,"presence",{}),
    Scene("Ordering relation","The center is the relation ordering every approach.",8.0,"presence",{}),
    Scene("Every edge refers","Every edge refers to it.",6.5,"presence",{}),
    Scene("Every path bends","Every path bends around it.",6.5,"presence",{}),
    Scene("Every ritual converges","Every ritual converges upon it.",6.5,"presence",{}),
    Scene("Center distributed","The center is therefore distributed through the whole building.",8.0,"presence",{}),

    Scene("Power danger","But not every center is sacred.",7.0,"power",{}),
    Scene("Monumental domination","Architecture can magnify domination.",7.5,"power",{}),
    Scene("Scale can crush","Scale can crush the visitor.",6.5,"power",{}),
    Scene("Axis can enthrone ruler","An axis can enthrone a ruler rather than orient a cosmos.",8.0,"power",{}),
    Scene("Awe can suppress","Awe can suppress judgment.",6.5,"power",{}),
    Scene("Sacred orientation test","Sacred orientation must be distinguished from monumental power.",8.5,"power",{}),

    Scene("Exclusion danger","A temple can also forget the world it claims to center.",8.0,"exclusion",{}),
    Scene("Gates close","Gates close.",5.0,"exclusion",{}),
    Scene("Purity becomes hierarchy","Purity becomes hierarchy.",6.5,"exclusion",{}),
    Scene("Center becomes privilege","The center becomes private privilege.",7.0,"exclusion",{}),
    Scene("Relation becomes exclusion","Relation becomes exclusion.",6.0,"exclusion",{}),
    Scene("False sacred space","Sacred space becomes false when it cannot return value to the world outside.",9.0,"exclusion",{}),

    Scene("Abhasa","Kashmir Śaivism offers another language.",6.5,"abhasa",{}),
    Scene("Space as appearance","Space is an ābhāsa, an appearance of consciousness.",8.0,"abhasa",{}),
    Scene("Distance manifested","Distance is not outside awareness; it is awareness appearing as separation.",9.0,"abhasa",{}),
    Scene("Center manifested","Center is awareness appearing as orientation.",8.0,"abhasa",{}),
    Scene("Temple intensifies","The temple does not create consciousness inside dead space.",8.0,"abhasa",{}),
    Scene("Recognition training","It trains recognition of consciousness already appearing as relation and distance.",9.0,"recognition",{}),

    Scene("Recognition","Recognition changes the final meaning of the sanctum.",7.0,"recognition",{}),
    Scene("Not monopoly","The sanctum does not monopolize the center.",7.0,"recognition",{}),
    Scene("Reveals capacity","It reveals the capacity for centered awareness already present in the knower.",9.0,"recognition",{}),
    Scene("Return center","The center is returned to the one who approached it.",8.0,"recognition",{}),
    Scene("Temple fulfilled","The temple is fulfilled when the visitor can leave without losing orientation.",9.0,"recognition",{}),

    Scene("Return city","The temple must teach the city how to have a center.",8.0,"return",{}),
    Scene("Not one building privilege","Not one building's privilege.",6.5,"return",{}),
    Scene("Way of inhabiting","A way of inhabiting roads, rooms, bodies, and decisions.",8.0,"return",{}),
    Scene("Doorways matter","Doorways matter.",5.5,"return",{}),
    Scene("Distances matter","Distances matter.",5.5,"return",{}),
    Scene("Centers matter","Centers matter.",5.5,"return",{}),
    Scene("Ordinary space deepens","Ordinary space becomes morally and imaginatively articulate.",8.5,"return",{}),

    Scene("Final square","At first there is only an empty square.",6.0,"empty",{}),
    Scene("Axis drawn","Then an axis is drawn.",5.5,"axis",{}),
    Scene("Body moves","A body crosses a threshold, circles, descends, listens, and enters.",9.0,"final",{}),
    Scene("Space remembers","Space remembers each action.",6.5,"final",{}),
    Scene("Building breathes","The building begins to breathe.",6.5,"spanda",{}),
    Scene("Center answers","The center begins to answer.",6.5,"presence",{}),
    Scene("Temple thesis final","A temple teaches space how to become a body.",8.0,"final",{}),
    Scene("Responsibility final","And teaches the body that every center is a responsibility.",9.0,"final",{}),
]


def export_original_essay():
    paragraphs=["# a temple teaches space how to become a body",""]
    for scene in SCENES:
        paragraphs.append(scene.narration)
        paragraphs.append("")
    path=OUTPUT/"original_essay.md"
    path.write_text("\n".join(paragraphs),encoding="utf-8")
    return path

def render_frame(scene,fi,fc,w,h,seed):
    u=fi/max(1,fc-1)
    t=u*scene.duration
    dark=scene.visual in {"sanctum","imaginal"}
    im=background(w,h,seed,dark)
    VISUALS[scene.visual](im,u,t,scene.params)
    border(im,dark)
    return im.convert("RGB")

def require_ffmpeg():
    exe=shutil.which("ffmpeg")
    if not exe: raise RuntimeError("ffmpeg is required but was not found on PATH")
    return exe

def encode_scene(i,fps):
    fd=FRAMES/f"scene_{i:03d}"
    out=SCENES_DIR/f"scene_{i:03d}.mp4"
    subprocess.run([
        require_ffmpeg(),"-y",
        "-framerate",str(fps),
        "-i",str(fd/"%05d.jpg"),
        "-c:v","libx264",
        "-preset","medium",
        "-crf","18",
        "-pix_fmt","yuv420p",
        "-movflags","+faststart",
        str(out)
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return out

def render_scene(i,scene,fps,w,h,preview):
    fd=FRAMES/f"scene_{i:03d}"
    fd.mkdir(parents=True,exist_ok=True)
    SCENES_DIR.mkdir(parents=True,exist_ok=True)
    fc=max(2,round(scene.duration*fps))
    if preview:
        for oi,fi in enumerate([0,int(fc*.35),int(fc*.72),fc-1]):
            render_frame(scene,fi,fc,w,h,i*1000+fi).save(fd/f"preview_{oi:02d}.jpg",quality=95)
        return fd
    for fi in range(fc):
        p=fd/f"{fi:05d}.jpg"
        if p.exists(): continue
        render_frame(scene,fi,fc,w,h,i*1000+fi).save(p,quality=95,subsampling=0)
    return encode_scene(i,fps)

def concatenate(paths):
    concat=OUTPUT/"concat.txt"
    concat.write_text("\n".join(f"file '{p.resolve()}'" for p in paths),encoding="utf-8")
    out=OUTPUT/"a_temple_teaches_space_how_to_become_a_body.mp4"
    subprocess.run([
        require_ffmpeg(),"-y","-f","concat","-safe","0","-i",str(concat),
        "-c","copy","-movflags","+faststart",str(out)
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return out

def export_timeline():
    cur=0.0
    payload=[]
    for i,scene in enumerate(SCENES,1):
        rec=asdict(scene)
        rec["scene_id"]=f"scene_{i:03d}"
        rec["start_seconds"]=round(cur,3)
        cur+=scene.duration
        rec["end_seconds"]=round(cur,3)
        payload.append(rec)
    path=OUTPUT/"narration_timeline.json"
    path.write_text(json.dumps({
        "title":"a temple teaches space how to become a body",
        "runtime_seconds":round(cur,3),
        "scene_count":len(SCENES),
        "original_essay":True,
        "style":{
            "continuity_object":"empty square becoming a living sacred body",
            "shot_duration_range_seconds":[5,10],
            "palette_roles":{
                "graphite":"ordinary geometry and material architecture",
                "gold":"axis and consecrated center",
                "cyan":"movement, breath, sensory flow",
                "violet":"imaginal depth and sacred night",
                "crimson":"domination and exclusion",
                "green":"integration and ethical return",
                "silver":"inherited measure and proportion"
            }
        },
        "scenes":payload
    },indent=2,ensure_ascii=False),encoding="utf-8")
    return path

def make_contact_sheet(w,h):
    tw=320
    th=int(tw*h/w)
    thumbs=[]
    for i,scene in enumerate(SCENES,1):
        fc=max(2,round(scene.duration*DEFAULT_FPS))
        im=render_frame(scene,int(fc*.72),fc,w,h,i*1000+72)
        im.thumbnail((tw,th))
        thumbs.append((i,scene.title,im.copy()))
    cols=4
    rows=math.ceil(len(thumbs)/cols)
    sheet=Image.new("RGB",(cols*tw,rows*(th+52)),WHITE)
    d=ImageDraw.Draw(sheet)
    f=font(FSSB,15)
    for i,title,im in thumbs:
        k=i-1
        x=(k%cols)*tw
        y=(k//cols)*(th+52)
        sheet.paste(im,(x,y))
        d.text((x+10,y+th+8),f"{i:03d}  {title}",font=f,fill=INK)
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

    print(f"Essay: {export_original_essay()}")
    print(f"Timeline: {export_timeline()}")
    print(f"Scenes: {len(SCENES)}")
    print(f"Runtime: {sum(s.duration for s in SCENES)/60:.2f} minutes")

    if args.scene:
        if not 1<=args.scene<=len(SCENES):
            raise ValueError("scene out of range")
        print(render_scene(args.scene,SCENES[args.scene-1],args.fps,args.width,args.height,args.preview))
        return

    rendered=[]
    for i,scene in enumerate(SCENES,1):
        print(f"[{i:03d}/{len(SCENES):03d}] {scene.title} ({scene.duration:.1f}s)")
        r=render_scene(i,scene,args.fps,args.width,args.height,args.preview)
        if not args.preview:
            rendered.append(r)

    if not args.no_contact_sheet:
        print(f"Contact sheet: {make_contact_sheet(args.width,args.height)}")
    if not args.preview:
        print(f"Final video: {concatenate(rendered)}")

if __name__=="__main__":
    main()
