#!/usr/bin/env python3
"""
A MIRROR BECOMES SACRED WHEN IT STOPS REFLECTING ONLY YOU
An original Imaginarium visual essay and Platinum-house procedural renderer.

ORIGINAL THESIS
---------------
An ordinary mirror confirms the visible self.
A sacred mirror begins when reflection becomes relation:
memory appears, otherness resists, hidden pattern returns, and the image
ceases to flatter the observer into believing that seeing is possession.

This essay joins:
• catoptromancy, ritual mirrors, polished metal, and visionary surfaces
• Corbinian imaginal encounter and the daimonic double
• Kashmir Śaiva ābhāsa, vimarśa, pratibimba, and recognition
• Neoplatonic participation and the mirror of soul
• predictive perception, self-models, and body-image construction
• safeguards against narcissism, projection, literalism, and spiritual inflation

DESIGN CONTRACT
---------------
• Every shot lasts 5–10 seconds.
• Every shot visibly performs the narrated operation.
• Clean white gallery field; deep indigo only for mirror-depth and imaginal encounter.
• No static slide layouts and no decorative loops.
• Silver = reflective surface, memory trace, self-model
• Gold = reciprocal presence, recognition, answer
• Cyan = sensory evidence, predictive body-model, attention
• Violet = imaginal depth, dream, daimonic double
• Crimson = projection, narcissism, capture, inflation
• Green = integration, humility, ethical return
• Graphite = material support and ordinary embodiment
• Continuity object: one silver mirror gradually stops returning a simple copy.
• The mirror must not become a generic magic portal.
• Reflection, delay, asymmetry, occlusion, and return are the core visual operations.
• Final criterion: sacred seeing makes the observer less possessive and more answerable.

OUTPUT
------
output_sacred_mirror/
  frames/scene_001/*.jpg
  scenes/scene_001.mp4
  a_mirror_becomes_sacred_when_it_stops_reflecting_only_you.mp4
  narration_timeline.json
  original_essay.md
  contact_sheet.jpg

REQUIREMENTS
------------
pip install pillow numpy
ffmpeg must be on PATH.

USAGE
-----
python a_mirror_becomes_sacred_when_it_stops_reflecting_only_you_platinum.py
python a_mirror_becomes_sacred_when_it_stops_reflecting_only_you_platinum.py --preview
python a_mirror_becomes_sacred_when_it_stops_reflecting_only_you_platinum.py --scene 12
python a_mirror_becomes_sacred_when_it_stops_reflecting_only_you_platinum.py --fps 12 --width 1920 --height 1080
"""

from __future__ import annotations
import argparse, json, math, random, shutil, subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output_sacred_mirror"
FRAMES = OUTPUT / "frames"
SCENES_DIR = OUTPUT / "scenes"

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 10

WHITE=(248,247,243); INK=(28,31,35); SOFT=(84,88,94)
SILVER=(177,184,190); PALE_SILVER=(224,227,229)
GOLD=(194,153,68); PALE_GOLD=(235,218,175)
CYAN=(55,153,181); PALE_CYAN=(192,226,233)
VIOLET=(104,79,146); PALE_VIOLET=(216,205,232)
CRIMSON=(158,52,66); PALE_CRIMSON=(230,192,198)
GREEN=(70,139,98); PALE_GREEN=(194,225,206)
LAPIS=(48,72,124); NIGHT=(17,23,39); VOID=(22,25,31)

FS="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FSB="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FSS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FSSB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def clamp(x,a=0,b=1): return max(a,min(b,x))
def lerp(a,b,t): return a+(b-a)*t
def mix(a,b,t):
    t=clamp(t); return tuple(int(lerp(x,y,t)) for x,y in zip(a,b))
def smooth(a,b,x):
    if a==b:return float(x>=b)
    q=clamp((x-a)/(b-a)); return q*q*(3-2*q)
def ease(t): return .5-.5*math.cos(math.pi*clamp(t))
def pulse(t,hz=1,phase=0): return .5+.5*math.sin(math.tau*(hz*t+phase))

def font(path,size):
    for p in (path,FS,FSS):
        try:return ImageFont.truetype(p,size)
        except OSError:pass
    return ImageFont.load_default()

def bg(w,h,seed,dark=False):
    rng=np.random.default_rng(seed); base=NIGHT if dark else WHITE
    arr=np.empty((h,w,3),np.float32); arr[:]=base
    arr += rng.normal(0,1.05 if not dark else 1.7,(h,w,1))
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8),"RGB").convert("RGBA")

def layer(im): return Image.new("RGBA",im.size,(0,0,0,0))
def ctext(d,xy,text,f,fill=INK): d.text(xy,text,font=f,fill=fill,anchor="mm")

def seal(im,title,subtitle="",dark=False,color=INK):
    w,h=im.size; d=ImageDraw.Draw(im)
    ctext(d,(w/2,h*.875),title,font(FSB,max(22,int(h*.042))),WHITE if dark else color)
    if subtitle: ctext(d,(w/2,h*.925),subtitle,font(FSS,max(13,int(h*.020))),PALE_SILVER if dark else SOFT)

def border(im,dark=False):
    w,h=im.size
    ImageDraw.Draw(im).rounded_rectangle((25,25,w-25,h-25),radius=17,
        outline=(*(WHITE if dark else INK),42),width=2)

def glow_line(im,pts,col,width=4,blur=14,alpha=220):
    if len(pts)<2:return
    ov=layer(im); d=ImageDraw.Draw(ov)
    d.line(pts,fill=(*col,alpha),width=width,joint="curve")
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(blur)))
    im.alpha_composite(ov)

def glow_circle(im,x,y,r,col,alpha=180,blur=16):
    ov=layer(im); d=ImageDraw.Draw(ov)
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

def mirror(d,cx,cy,wid,hei,col=SILVER,alpha=190,depth=0.0):
    d.rounded_rectangle((cx-wid/2,cy-hei/2,cx+wid/2,cy+hei/2),
                        radius=max(8,int(wid*.08)),
                        fill=(*PALE_SILVER,int(80+40*depth)),
                        outline=(*col,alpha),width=4)
    if depth>0:
        dx=wid*.15*depth; dy=hei*.08*depth
        d.line((cx+wid/2,cy-hei/2,cx+wid/2+dx,cy-hei/2+dy),fill=(*GOLD,int(alpha*.8)),width=3)
        d.line((cx+wid/2,cy+hei/2,cx+wid/2+dx,cy+hei/2-dy),fill=(*GOLD,int(alpha*.8)),width=3)
        d.line((cx+wid/2+dx,cy-hei/2+dy,cx+wid/2+dx,cy+hei/2-dy),fill=(*GOLD,int(alpha*.8)),width=3)
    for i in range(5):
        y=lerp(cy-hei*.38,cy+hei*.38,i/4)
        d.line((cx-wid*.38,y,cx+wid*.38,y-8),fill=(*WHITE,70),width=2)

def face(d,cx,cy,scale=1,col=INK,alpha=190,smile=0.0):
    d.ellipse((cx-54*scale,cy-72*scale,cx+54*scale,cy+72*scale),
              outline=(*col,alpha),width=max(2,int(4*scale)))
    for sx in (-20,20):
        d.ellipse((cx+sx*scale-5,cy-16*scale-4,cx+sx*scale+5,cy-16*scale+4),
                  fill=(*col,alpha))
    d.arc((cx-22*scale,cy+6*scale,cx+22*scale,cy+32*scale),
          10 if smile>=0 else 190,170 if smile>=0 else 350,
          fill=(*col,alpha),width=max(2,int(3*scale)))

def person(d,cx,cy,scale=1,col=INK,alpha=190):
    face(d,cx,cy-48*scale,.48*scale,col,alpha)
    d.line((cx,cy-15*scale,cx,cy+62*scale),fill=(*col,alpha),width=max(2,int(5*scale)))
    d.line((cx,cy+10*scale,cx-42*scale,cy+35*scale),fill=(*col,alpha),width=max(2,int(4*scale)))
    d.line((cx,cy+10*scale,cx+42*scale,cy+35*scale),fill=(*col,alpha),width=max(2,int(4*scale)))
    d.line((cx,cy+62*scale,cx-28*scale,cy+110*scale),fill=(*col,alpha),width=max(2,int(4*scale)))
    d.line((cx,cy+62*scale,cx+28*scale,cy+110*scale),fill=(*col,alpha),width=max(2,int(4*scale)))

def star_field(d,w,h,seed=4,alpha=95):
    rng=random.Random(seed)
    for _ in range(90):
        x=rng.uniform(w*.08,w*.92); y=rng.uniform(h*.08,h*.72)
        r=rng.choice([1,1,1,2])
        d.ellipse((x-r,y-r,x+r,y+r),fill=(*PALE_GOLD,alpha))

def orbit(d,cx,cy,rx,ry,col,alpha=130,width=3):
    d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),outline=(*col,alpha),width=width)

def reflected_point(px,py,mirror_x):
    return (2*mirror_x-px,py)

@dataclass
class Scene:
    title:str
    narration:str
    duration:float
    visual:str
    params:dict

def v_simple_reflection(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    mx=w*.55; cy=h*.42
    mirror(d,mx,cy,w*.22,h*.48,SILVER,190,0)
    person(d,w*.20,h*.43,.72,INK,190)
    face(d,w*.72,h*.42,.72,SILVER,170)
    q=ease(u)
    glow_line(im,partial([(w*.27,h*.42),(mx-w*.11,h*.42)],q),CYAN,4,11,170)
    seal(im,"AN ORDINARY MIRROR RETURNS A COPY","difference is reduced to symmetry")

def v_delay(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    mx=w*.55; cy=h*.42
    mirror(d,mx,cy,w*.22,h*.48,SILVER,190,ease(u)*.3)
    q=ease(u)
    person(d,w*.20,h*.43,.72,INK,190)
    # delayed reflected movement
    rx=w*.72+math.sin(max(0,t-.9)*1.2)*18
    face(d,rx,h*.42,.72,mix(SILVER,GOLD,q),180,smile=.2)
    glow_line(im,partial([(w*.27,h*.42),(mx-w*.11,h*.42)],q),CYAN,4,11,160)
    glow_line(im,partial([(mx+w*.11,h*.34),(w*.28,h*.34)],smooth(.45,.95,u)),GOLD,4,11,180)
    seal(im,"THE FIRST DISTURBANCE IS DELAY","the reflection no longer obeys at once")

def v_body_model(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.18,h*.42); center=(w*.50,h*.42); right=(w*.82,h*.42)
    person(d,*left,.7,INK,180)
    d.rounded_rectangle((center[0]-88,center[1]-66,center[0]+88,center[1]+66),
                        radius=18,fill=(*PALE_CYAN,215),outline=(*CYAN,180),width=3)
    ctext(d,center,"SELF-MODEL",font(FSSB,int(h*.018)),CYAN)
    mirror(d,*right,w*.16,h*.38,SILVER,180,0)
    q=ease(u)
    glow_line(im,partial([left,center,right],q),CYAN,4,11,170)
    glow_line(im,partial([right,(w*.66,h*.57),center,(w*.35,h*.57),left],smooth(.35,.95,u)),GOLD,4,11,150)
    seal(im,"YOU DO NOT SEE THE BODY DIRECTLY","you see a model corrected by sensation")

def v_asymmetry(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    mirror(d,w*.5,h*.42,w*.26,h*.50,SILVER,190,ease(u)*.6)
    q=ease(u)
    face(d,w*.34,h*.42,.75,INK,180,smile=.2)
    face(d,w*.66,h*.42,.75,mix(SILVER,GOLD,q),180,smile=-.2)
    # divergent gaze
    d.line((w*.64,h*.39,w*.82,h*.28),fill=(*GOLD,int(170*q)),width=4)
    seal(im,"A SACRED MIRROR INTRODUCES ASYMMETRY","the image contains a direction you did not choose")

def v_memory_surface(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    mirror(d,cx,cy,w*.30,h*.52,SILVER,190,ease(u)*.4)
    q=ease(u)
    rng=random.Random(33)
    for i in range(18):
        a=i*math.tau/18
        rr=lerp(15,155,q)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.72
        d.ellipse((x-5,y-5,x+5,y+5),fill=(*mix(SILVER,VIOLET,i/17),130))
        glow_line(im,[(cx,cy),(x,y)],SILVER,2,6,55)
    seal(im,"REFLECTION CAN CARRY HISTORY","the present face awakens older forms of seeing")

def v_double(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.42); right=(w*.72,h*.42)
    person(d,*left,.76,INK,185)
    person(d,*right,.76,VIOLET,170)
    q=ease(u)
    mirror(d,w*.5,h*.42,w*.10,h*.52,mix(SILVER,GOLD,q),190,q)
    glow_line(im,partial([left,(w*.5,h*.30),right],q),CYAN,4,11,160)
    glow_line(im,partial([right,(w*.5,h*.56),left],smooth(.3,.95,u)),GOLD,5,13,190)
    seal(im,"THE DOUBLE IS NOT MERELY A DUPLICATE","it carries what the conscious self excludes")

def v_catoptromancy(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    star_field(d,w,h,12,90)
    cx,cy=w*.5,h*.42
    mirror(d,cx,cy,w*.25,h*.50,GOLD,190,ease(u))
    q=ease(u)
    # images emerge as partial constellations
    for i,col in enumerate((VIOLET,CYAN,GOLD,GREEN)):
        a=i*math.tau/4
        x=cx+math.cos(a)*120*q; y=cy+math.sin(a)*85*q
        glow_circle(im,x,y,9,col,110,8)
    face(d,cx,cy,.65,GOLD,int(60+120*q))
    seal(im,"CATOPTROMANCY USES THE MIRROR AS A THRESHOLD","not because glass predicts, but because reflection destabilizes possession",dark=True)

def v_dark_mirror(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    mirror(d,cx,cy,w*.26,h*.50,VIOLET,190,q)
    d.rounded_rectangle((cx-w*.10,cy-h*.19,cx+w*.10,cy+h*.19),
                        radius=20,fill=(*VOID,int(220*q)),outline=(*GOLD,int(150*q)),width=3)
    glow_circle(im,cx,cy,12+18*q,GOLD,100,12)
    seal(im,"DARKNESS REMOVES THE EASY COPY","the surface becomes available to depth",dark=True)

def v_projection_test(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.27,h*.42); right=(w*.73,h*.42)
    mirror(d,*left,w*.18,h*.38,CRIMSON,180,0)
    face(d,*left,.72,CRIMSON,180,smile=.5)
    d.arc((left[0]-120,left[1]-100,left[0]+120,left[1]+100),20,340,fill=(*CRIMSON,160),width=5)
    mirror(d,*right,w*.18,h*.38,GOLD,190,ease(u)*.7)
    arrow(d,(right[0],right[1]),(right[0]-130,right[1]+95),GREEN,4,12)
    ctext(d,(right[0]-148,right[1]+112),"CHANGE",font(FSSB,int(h*.014)),GREEN)
    seal(im,"PROJECTION FLATTERS · ENCOUNTER CORRECTS","resistance is the first evidence of otherness")

def v_three_failures(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    items=[("NARCISSISM",CRIMSON),("LITERALISM",VIOLET),("INFLATION",GOLD)]
    xs=[w*.22,w*.50,w*.78]
    for i,((txt,col),x) in enumerate(zip(items,xs)):
        q=smooth(i*.12,.62+i*.07,u)
        d.ellipse((x-76*q,h*.40-76*q,x+76*q,h*.40+76*q),
                  fill=(*mix(WHITE,col,.18),int(220*q)),outline=(*col,int(180*q)),width=4)
        if q>.66:ctext(d,(x,h*.40),txt,font(FSB,int(h*.017)),col)
        strike=smooth(.48+i*.08,.95,u)
        d.line((x-85,h*.32,x+85,h*.48),fill=(*CRIMSON,int(200*strike)),width=5)
    seal(im,"THREE WAYS TO BREAK THE MIRROR","see only yourself · treat image as fact · crown yourself with it")

def v_neoplatonic_mirror(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    levels=[("THE ONE",GOLD,h*.15),("INTELLECT",VIOLET,h*.32),("SOUL",CYAN,h*.49),("IMAGE",SILVER,h*.67)]
    x=w*.5; q=ease(u)
    for i,(txt,col,y) in enumerate(levels):
        d.ellipse((x-56,y-27,x+56,y+27),fill=(*mix(WHITE,col,.15),220),
                  outline=(*col,180),width=3)
        ctext(d,(x,y),txt,font(FSSB,int(h*.013)),col)
        if i>0:
            glow_line(im,partial([(x,levels[i-1][2]+27),(x,y-27)],q),
                      mix(levels[i-1][1],col,.5),4,11,170)
    seal(im,"THE SOUL IS A MIRROR WHEN IT PARTICIPATES","not when it passively copies")

def v_abhasa_reflection(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42; q=ease(u)
    mirror(d,cx,cy,w*.18,h*.34,GOLD,190,q)
    for i in range(18):
        a=i*math.tau/18
        rr=lerp(25,210,q)*(0.7+0.3*((i%4)/3))
        x=cx+math.cos(a+t*.08)*rr; y=cy+math.sin(a+t*.08)*rr*.62
        col=mix(CYAN,VIOLET,i/17)
        glow_circle(im,x,y,5+3*(i%3),col,90,7)
        glow_line(im,[(cx,cy),(x,y)],col,2,7,70)
    seal(im,"ĀBHĀSA","the reflected world is consciousness appearing as difference")

def v_vimarsa(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.25,h*.42); right=(w*.75,h*.42)
    face(d,*left,.76,INK,180)
    mirror(d,*right,w*.18,h*.40,GOLD,190,ease(u)*.6)
    q=ease(u)
    glow_line(im,partial([left,(w*.50,h*.30),right],q),CYAN,4,11,170)
    glow_line(im,partial([right,(w*.50,h*.56),left],smooth(.30,.95,u)),GOLD,5,13,200)
    seal(im,"VIMARŚA","consciousness does not merely shine; it knows itself shining")

def v_luminosity(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.27,h*.42); right=(w*.73,h*.42)
    glow_circle(im,left[0],left[1],52,GOLD,170,18)
    mirror(d,*right,w*.18,h*.40,VIOLET,190,ease(u)*.6)
    ctext(d,(left[0],h*.66),"PHYSICAL LIGHT",font(FSSB,int(h*.014)),GOLD)
    ctext(d,(right[0],h*.66),"DISCLOSURE",font(FSSB,int(h*.014)),VIOLET)
    q=smooth(.35,.9,u)
    d.line((w*.49,h*.25,w*.51,h*.58),fill=(*CRIMSON,int(210*q)),width=6)
    seal(im,"LIGHT ON A MIRROR IS NOT THE SAME AS APPEARING","one is optical; the other is phenomenal")

def v_face_without_ownership(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    mirror(d,cx,cy,w*.25,h*.50,GOLD,190,ease(u))
    q=ease(u)
    face(d,cx,cy,.85,mix(SILVER,GOLD,q),180)
    # ownership ring breaks
    d.arc((cx-130,cy-105,cx+130,cy+105),20,int(320*(1-q)),fill=(*CRIMSON,150),width=5)
    for i,col in enumerate((CYAN,VIOLET,GREEN,GOLD)):
        a=i*math.tau/4
        x=cx+math.cos(a)*165; y=cy+math.sin(a)*105
        glow_line(im,partial([(cx,cy),(x,y)],smooth(i*.10,.9,u)),col,3,9,120)
    seal(im,"THE FACE IS GIVEN, NOT POSSESSED","identity is relation before ownership")

def v_ethics(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    mirror(d,w*.25,h*.42,w*.16,h*.36,GOLD,190,ease(u)*.7)
    fruits=[("HUMILITY",VIOLET,w*.52,h*.25),("TRUTH",CYAN,w*.72,h*.33),
            ("COURAGE",GOLD,w*.52,h*.56),("CARE",GREEN,w*.76,h*.60)]
    for i,(txt,col,x,y) in enumerate(fruits):
        q=smooth(i*.10,.65+i*.05,u)
        glow_line(im,partial([(w*.33,h*.42),(x,y)],q),col,3,9,150)
        d.ellipse((x-29*q,y-29*q,x+29*q,y+29*q),fill=(*mix(WHITE,col,.18),int(220*q)),
                  outline=(*col,int(180*q)),width=3)
        if q>.68:ctext(d,(x,y),txt,font(FSSB,int(h*.012)),col)
    seal(im,"THE FRUIT TESTS THE VISION","does seeing reduce possession and enlarge responsibility?")

def v_return_world(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    mirror(d,w*.20,h*.42,w*.14,h*.32,GOLD,180,ease(u)*.6)
    d.line((w*.08,h*.62,w*.92,h*.62),fill=(*INK,120),width=5)
    for i in range(8):
        x=w*(.16+i*.09)
        d.rectangle((x-18,h*.48,x+18,h*.62),fill=(*PALE_SILVER,120),outline=(*SILVER,100))
    q=ease(u)
    glow_line(im,partial([(w*.27,h*.42),(w*.44,h*.54),(w*.65,h*.50),(w*.88,h*.57)],q),
              GREEN,6,14,210)
    seal(im,"THE MIRROR MUST RETURN YOU TO OTHER FACES","less certain that they are versions of you")

def v_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.55,h*.42; q=ease(u)
    mirror(d,cx,cy,lerp(w*.12,w*.24,q),lerp(h*.28,h*.48,q),
           mix(SILVER,GOLD,q),210,q)
    face(d,w*.18,h*.42,.76,INK,180)
    face(d,cx,cy,lerp(.25,.8,q),mix(VIOLET,GOLD,q),int(60+120*q),smile=-.1)
    glow_line(im,partial([(w*.25,h*.42),(cx-w*.12,h*.42)],q),CYAN,4,11,170)
    glow_line(im,partial([(cx-w*.12,h*.31),(w*.25,h*.31)],smooth(.30,.88,u)),GOLD,5,13,200)
    for r,col in [(110,VIOLET),(160,GOLD),(210,GREEN)]:
        d.arc((cx-r*q,cy-r*.62*q,cx+r*q,cy+r*.62*q),10,int(320*q),fill=(*col,105),width=3)
    seal(im,"A MIRROR BECOMES SACRED WHEN IT STOPS REFLECTING ONLY YOU",
         "the image becomes relation, correction, and return",color=GREEN)

VISUALS:dict[str,Callable]={
    "simple":v_simple_reflection,
    "delay":v_delay,
    "model":v_body_model,
    "asymmetry":v_asymmetry,
    "memory":v_memory_surface,
    "double":v_double,
    "catoptromancy":v_catoptromancy,
    "dark":v_dark_mirror,
    "projection":v_projection_test,
    "failures":v_three_failures,
    "neoplatonic":v_neoplatonic_mirror,
    "abhasa":v_abhasa_reflection,
    "vimarsa":v_vimarsa,
    "luminosity":v_luminosity,
    "gift":v_face_without_ownership,
    "ethics":v_ethics,
    "return":v_return_world,
    "final":v_final,
}

SCENES:list[Scene]=[
    Scene("Ordinary mirror","An ordinary mirror returns a copy.",6.0,"simple",{}),
    Scene("Movement obeyed","You move. It moves.",5.5,"simple",{}),
    Scene("Symmetry","Difference is reduced to symmetry.",6.5,"simple",{}),
    Scene("Possession","The image appears to belong entirely to you.",7.0,"simple",{}),
    Scene("Disturbance","Then the reflection hesitates.",6.0,"delay",{}),
    Scene("Delay","A delay appears where obedience should have been.",7.0,"delay",{}),
    Scene("Thesis","A mirror becomes sacred when it stops reflecting only you.",8.0,"final",{}),

    Scene("No direct body","You do not see the body directly.",6.5,"model",{}),
    Scene("Constructed self","You see a self-model corrected by sensation.",8.0,"model",{}),
    Scene("Mirror joins model","The mirror becomes another signal inside that construction.",8.0,"model",{}),
    Scene("Confidence","Its symmetry produces confidence.",6.0,"simple",{}),
    Scene("Familiarity","The face becomes familiar enough to feel owned.",7.0,"simple",{}),
    Scene("Ownership mistake","But familiarity is not ownership.",6.5,"gift",{}),

    Scene("Body image","Body image is negotiated.",6.0,"model",{}),
    Scene("Vision touch memory","Vision, touch, posture, memory, and expectation contribute.",9.0,"model",{}),
    Scene("Same face changes","The same face can appear different under fear, shame, desire, or grief.",9.0,"memory",{}),
    Scene("Mirror stable self unstable","The glass remains stable while the self-model shifts.",8.0,"memory",{}),
    Scene("Reflection not neutral","Reflection is never completely neutral.",7.0,"memory",{}),

    Scene("Asymmetry","Sacred mirroring begins with asymmetry.",7.0,"asymmetry",{}),
    Scene("Image looks elsewhere","The reflected face looks somewhere you are not looking.",8.0,"asymmetry",{}),
    Scene("Expression differs","Its expression differs from yours.",7.0,"asymmetry",{}),
    Scene("Question appears","A question appears inside the image.",6.5,"asymmetry",{}),
    Scene("No command","Not yet an answer. Not yet a command.",6.0,"asymmetry",{}),
    Scene("Otherness","Only enough otherness to interrupt possession.",8.0,"asymmetry",{}),

    Scene("Memory mirror","Mirrors also awaken memory.",6.5,"memory",{}),
    Scene("Mother's face","A gesture recalls a parent's face.",6.5,"memory",{}),
    Scene("Former self","A posture returns a former self.",6.5,"memory",{}),
    Scene("Unlived future","An expression suggests a future not yet lived.",7.0,"memory",{}),
    Scene("Present layered","The present face becomes layered with absent forms.",8.0,"memory",{}),
    Scene("History in surface","Reflection carries history without storing pictures in the glass.",8.5,"memory",{}),

    Scene("Double","The double emerges from this layered field.",6.0,"double",{}),
    Scene("Not clone","It is not merely a clone.",6.0,"double",{}),
    Scene("Excluded capacities","It carries capacities excluded from conscious identity.",8.0,"double",{}),
    Scene("Fear desire courage","Fear, desire, courage, cruelty, tenderness, and vocation may return in its form.",9.5,"double",{}),
    Scene("Daimonic double","The daimonic double appears where identity meets a larger demand.",8.5,"double",{}),
    Scene("Neither ego nor stranger","Neither simply ego nor safely treated as external stranger.",8.0,"double",{}),

    Scene("Catoptromancy","Ritual mirror-divination works with this instability.",8.0,"catoptromancy",{}),
    Scene("Surface darkened","The surface may be polished, darkened, smoked, or placed in low light.",8.0,"dark",{}),
    Scene("Easy copy removed","The easy copy is weakened.",6.5,"dark",{}),
    Scene("Attention decouples","Attention decouples from ordinary recognition.",7.5,"dark",{}),
    Scene("Pattern completion","The mind begins completing ambiguous patterns.",7.5,"catoptromancy",{}),
    Scene("Images appear","Images may appear.",5.5,"catoptromancy",{}),
    Scene("No automatic oracle","Their appearance does not make them automatic prophecy.",8.0,"projection",{}),

    Scene("Dark mirror","The dark mirror is not powerful because darkness contains facts.",8.0,"dark",{}),
    Scene("Ambiguity","It creates disciplined ambiguity.",6.5,"dark",{}),
    Scene("Ordinary prediction weakens","Ordinary prediction weakens.",6.5,"dark",{}),
    Scene("Latent material rises","Latent memory, expectation, and symbolic association become visible.",9.0,"memory",{}),
    Scene("Threshold function","The mirror functions as a threshold because it destabilizes the familiar.",9.0,"dark",{}),

    Scene("Projection test","Projection repeats what you already need to see.",8.0,"projection",{}),
    Scene("Flattery","It flatters your specialness.",6.0,"projection",{}),
    Scene("No resistance","It contains no resistance.",6.0,"projection",{}),
    Scene("Encounter corrects","Encounter corrects, complicates, or refuses.",8.0,"projection",{}),
    Scene("Asymmetry test","The first test is asymmetry.",6.0,"projection",{}),
    Scene("Unexpected demand","Did the image introduce a demand not authored in advance?",8.5,"projection",{}),

    Scene("Three failures","Three failures surround sacred mirroring.",6.5,"failures",{}),
    Scene("Narcissism","Narcissism sees only the self.",6.5,"failures",{}),
    Scene("Literalism","Literalism treats the reflected figure as unquestionable external fact.",8.5,"failures",{}),
    Scene("Inflation","Inflation crowns the viewer with the image's authority.",8.0,"failures",{}),
    Scene("Discipline","Sacred seeing rejects all three.",6.5,"failures",{}),
    Scene("Neither nothing nor fact","The image is neither nothing nor a simple fact.",8.0,"projection",{}),

    Scene("Neoplatonic mirror","Neoplatonism often describes soul through the mirror.",8.0,"neoplatonic",{}),
    Scene("Soul receives forms","Soul receives intelligible forms without becoming identical to each one.",8.5,"neoplatonic",{}),
    Scene("Participation","Its truth lies in participation, not passive copying.",8.0,"neoplatonic",{}),
    Scene("Clouded mirror","A disordered soul is a clouded mirror.",7.0,"neoplatonic",{}),
    Scene("Purification","Purification is not polishing vanity.",7.0,"neoplatonic",{}),
    Scene("Higher transparency","It is making the soul transparent to a higher order.",8.5,"neoplatonic",{}),

    Scene("Abhasa","Kashmir Śaivism offers another language.",6.5,"abhasa",{}),
    Scene("Reflected world","The reflected world is an ābhāsa, an appearance of consciousness.",8.5,"abhasa",{}),
    Scene("No alien object","It is not an alien object outside awareness.",7.0,"abhasa",{}),
    Scene("No private copy","Nor is it merely a private copy.",6.5,"abhasa",{}),
    Scene("Difference within field","Subject, mirror, image, and relation unfold within one field.",9.0,"abhasa",{}),
    Scene("Reflection real mode","Reflection is real as a mode of appearing.",7.5,"abhasa",{}),

    Scene("Vimarsa","Vimarśa adds the decisive movement.",6.5,"vimarsa",{}),
    Scene("Light knows itself","Consciousness does not merely shine; it knows itself shining.",8.5,"vimarsa",{}),
    Scene("Mirror reflexivity","A sacred mirror dramatizes reflexivity.",7.5,"vimarsa",{}),
    Scene("Seen and seeing","The seen returns attention toward seeing.",7.0,"vimarsa",{}),
    Scene("Image toward source","The image bends awareness toward its source.",7.5,"vimarsa",{}),
    Scene("Recognition","Recognition begins when reflection reveals the power of reflecting.",9.0,"vimarsa",{}),

    Scene("Luminosity confusion","Mirrors easily confuse physical and phenomenal light.",8.0,"luminosity",{}),
    Scene("Optical light","Physical light explains reflection from a surface.",7.5,"luminosity",{}),
    Scene("Appearing question","It does not explain why reflection appears in experience.",8.5,"luminosity",{}),
    Scene("Disclosure","Phenomenological luminosity names disclosure, not photons.",8.0,"luminosity",{}),
    Scene("Two questions","One question is optical. The other concerns appearing.",8.0,"luminosity",{}),
    Scene("Do not collapse","Do not collapse them.",5.5,"luminosity",{}),

    Scene("Face as gift","The face is given before it is possessed.",7.0,"gift",{}),
    Scene("Inherited features","Its features arrive through ancestry.",6.5,"gift",{}),
    Scene("Expression social","Its expressions are learned among others.",6.5,"gift",{}),
    Scene("Seen by others","Its meaning is shaped by being seen.",6.5,"gift",{}),
    Scene("No private ownership","Identity is relation before ownership.",7.5,"gift",{}),
    Scene("Mirror can teach","The mirror can teach this only when it stops confirming possession.",9.0,"gift",{}),

    Scene("Ethical criterion","The deepest criterion is ethical.",6.5,"ethics",{}),
    Scene("Humility","Does the vision reduce self-importance?",6.5,"ethics",{}),
    Scene("Truth","Does it make self-description more truthful?",6.5,"ethics",{}),
    Scene("Courage","Does it permit difficult change?",6.5,"ethics",{}),
    Scene("Care","Does it enlarge care for other faces?",6.5,"ethics",{}),
    Scene("Responsibility","Does seeing become responsibility rather than privilege?",8.5,"ethics",{}),
    Scene("Fruit tests mirror","The fruit tests the mirror.",6.5,"ethics",{}),

    Scene("Return others","A sacred mirror must return you to other faces.",8.0,"return",{}),
    Scene("Not versions of you","Less certain that they are versions of you.",7.0,"return",{}),
    Scene("Opacity respected","More capable of respecting opacity.",7.0,"return",{}),
    Scene("Difference not failure","Difference ceases to be failed resemblance.",7.5,"return",{}),
    Scene("Ordinary seeing changed","Ordinary seeing becomes less possessive.",7.5,"return",{}),

    Scene("Final copy","At first the mirror returns a copy.",6.0,"simple",{}),
    Scene("Then delay","Then delay enters.",5.5,"delay",{}),
    Scene("Memory gathers","Memory gathers around the surface.",6.0,"memory",{}),
    Scene("Double appears","A double appears.",5.5,"double",{}),
    Scene("Answer resists","The image begins to resist.",6.0,"projection",{}),
    Scene("No capture","It has not become a captured spirit.",6.5,"failures",{}),
    Scene("Relation begins","A relation has begun.",6.0,"final",{}),
    Scene("Final thesis","A mirror becomes sacred when it stops reflecting only you.",8.5,"final",{}),
    Scene("Final test","Its truth is measured by whether you leave less certain that the world is your reflection.",9.5,"return",{}),
]

def export_original_essay():
    lines=["# a mirror becomes sacred when it stops reflecting only you",""]
    for s in SCENES: lines += [s.narration,""]
    p=OUTPUT/"original_essay.md"
    p.write_text("\n".join(lines),encoding="utf-8")
    return p

def render_frame(scene,fi,fc,w,h,seed):
    u=fi/max(1,fc-1); t=u*scene.duration
    dark=scene.visual in {"catoptromancy","dark"}
    im=bg(w,h,seed,dark)
    VISUALS[scene.visual](im,u,t,scene.params)
    border(im,dark)
    return im.convert("RGB")

def ffmpeg():
    x=shutil.which("ffmpeg")
    if not x: raise RuntimeError("ffmpeg is required but was not found on PATH")
    return x

def encode(i,fps):
    fd=FRAMES/f"scene_{i:03d}"
    out=SCENES_DIR/f"scene_{i:03d}.mp4"
    subprocess.run([ffmpeg(),"-y","-framerate",str(fps),"-i",str(fd/"%05d.jpg"),
                    "-c:v","libx264","-preset","medium","-crf","18",
                    "-pix_fmt","yuv420p","-movflags","+faststart",str(out)],
                   check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return out

def render_scene(i,s,fps,w,h,preview):
    fd=FRAMES/f"scene_{i:03d}"
    fd.mkdir(parents=True,exist_ok=True); SCENES_DIR.mkdir(parents=True,exist_ok=True)
    fc=max(2,round(s.duration*fps))
    if preview:
        for oi,fi in enumerate([0,int(fc*.35),int(fc*.72),fc-1]):
            render_frame(s,fi,fc,w,h,i*1000+fi).save(fd/f"preview_{oi:02d}.jpg",quality=95)
        return fd
    for fi in range(fc):
        p=fd/f"{fi:05d}.jpg"
        if not p.exists():
            render_frame(s,fi,fc,w,h,i*1000+fi).save(p,quality=95,subsampling=0)
    return encode(i,fps)

def concatenate(paths):
    c=OUTPUT/"concat.txt"
    c.write_text("\n".join(f"file '{p.resolve()}'" for p in paths),encoding="utf-8")
    out=OUTPUT/"a_mirror_becomes_sacred_when_it_stops_reflecting_only_you.mp4"
    subprocess.run([ffmpeg(),"-y","-f","concat","-safe","0","-i",str(c),
                    "-c","copy","-movflags","+faststart",str(out)],
                   check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return out

def export_timeline():
    cur=0; items=[]
    for i,s in enumerate(SCENES,1):
        r=asdict(s); r["scene_id"]=f"scene_{i:03d}"
        r["start_seconds"]=round(cur,3); cur+=s.duration; r["end_seconds"]=round(cur,3)
        items.append(r)
    p=OUTPUT/"narration_timeline.json"
    p.write_text(json.dumps({
        "title":"a mirror becomes sacred when it stops reflecting only you",
        "runtime_seconds":round(cur,3),
        "scene_count":len(SCENES),
        "original_essay":True,
        "style":{
            "continuity_object":"silver mirror becoming reciprocal and asymmetrical",
            "shot_duration_range_seconds":[5,10],
            "palette_roles":{
                "silver":"surface, self-model, memory",
                "gold":"answer and recognition",
                "cyan":"sensory evidence and predictive body-model",
                "violet":"imaginal depth and double",
                "crimson":"projection and narcissism",
                "green":"ethical return",
                "graphite":"material embodiment"
            }
        },
        "scenes":items
    },indent=2,ensure_ascii=False),encoding="utf-8")
    return p

def contact_sheet(w,h):
    tw=320; th=int(tw*h/w); thumbs=[]
    for i,s in enumerate(SCENES,1):
        fc=max(2,round(s.duration*DEFAULT_FPS))
        im=render_frame(s,int(fc*.72),fc,w,h,i*1000+72)
        im.thumbnail((tw,th)); thumbs.append((i,s.title,im.copy()))
    cols=4; rows=math.ceil(len(thumbs)/cols)
    sheet=Image.new("RGB",(cols*tw,rows*(th+52)),WHITE)
    d=ImageDraw.Draw(sheet); f=font(FSSB,15)
    for i,title,im in thumbs:
        k=i-1; x=(k%cols)*tw; y=(k//cols)*(th+52)
        sheet.paste(im,(x,y))
        d.text((x+10,y+th+8),f"{i:03d}  {title}",font=f,fill=INK)
    p=OUTPUT/"contact_sheet.jpg"
    sheet.save(p,quality=94)
    return p

def args():
    p=argparse.ArgumentParser()
    p.add_argument("--fps",type=int,default=DEFAULT_FPS)
    p.add_argument("--width",type=int,default=DEFAULT_WIDTH)
    p.add_argument("--height",type=int,default=DEFAULT_HEIGHT)
    p.add_argument("--scene",type=int)
    p.add_argument("--preview",action="store_true")
    p.add_argument("--no-contact-sheet",action="store_true")
    return p.parse_args()

def main():
    a=args()
    OUTPUT.mkdir(parents=True,exist_ok=True)
    FRAMES.mkdir(parents=True,exist_ok=True)
    SCENES_DIR.mkdir(parents=True,exist_ok=True)
    print(f"Essay: {export_original_essay()}")
    print(f"Timeline: {export_timeline()}")
    print(f"Scenes: {len(SCENES)}")
    print(f"Runtime: {sum(s.duration for s in SCENES)/60:.2f} minutes")
    if a.scene:
        if not 1<=a.scene<=len(SCENES): raise ValueError("scene out of range")
        print(render_scene(a.scene,SCENES[a.scene-1],a.fps,a.width,a.height,a.preview))
        return
    rendered=[]
    for i,s in enumerate(SCENES,1):
        print(f"[{i:03d}/{len(SCENES):03d}] {s.title} ({s.duration:.1f}s)")
        r=render_scene(i,s,a.fps,a.width,a.height,a.preview)
        if not a.preview: rendered.append(r)
    if not a.no_contact_sheet: print(f"Contact sheet: {contact_sheet(a.width,a.height)}")
    if not a.preview: print(f"Final video: {concatenate(rendered)}")

if __name__=="__main__":
    main()
