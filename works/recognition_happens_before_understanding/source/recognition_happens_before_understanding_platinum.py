#!/usr/bin/env python3
"""
RECOGNITION HAPPENS BEFORE UNDERSTANDING
How Meaning Arrives Before Explanation

An original Imaginarium visual essay and Platinum-house procedural renderer.

THESIS
------
Recognition is not the conclusion of an explanation.

A face, danger, melody, place, mood, or truth can be known before the knower
can state the features, reasons, or rules by which it was known. Explanation
comes later. It decomposes an already meaningful whole into parts that can be
communicated, tested, remembered, and revised.

Recognition is therefore not irrational.
It is pre-discursive intelligence.

Yet recognition is not infallible. Habit, projection, fear, and expectation
can counterfeit familiarity. Mature understanding must return analysis to the
living whole and test whether the recognition survives correction.

SOURCE CONSTELLATION
--------------------
• Kashmir Śaiva pratyabhijñā: recognition
• pratibhā: immediate flash of meaning
• vimarśa: reflexive awareness
• sphoṭa and the whole-before-parts problem in language
• rasa: immediate recognition of affective form
• phenomenology and pre-reflective awareness
• Gestalt perception and global precedence
• predictive processing and rapid pattern completion
• expertise and tacit knowledge
• memory, familiarity, and false recognition
• machine classification as analogy, not equivalence

DESIGN CONTRACT
---------------
• Every shot lasts 5–10 seconds.
• Every shot visibly performs the narrated operation.
• Clean white field; dark fields only when recognition occurs without stable detail.
• No static explanatory slides.
• Silver = incomplete evidence and latent familiarity
• Gold = immediate recognition and meaningful fit
• Cyan = sensory evidence and analytical inspection
• Violet = whole-form, mood, and pre-verbal meaning
• Crimson = projection, false familiarity, and premature certainty
• Green = corrected understanding and reintegration
• Graphite = explicit concepts, verbal explanation, and measurable features
• Continuity object: one blurred figure recognized before its details stabilize.
• Analysis should physically dissect the figure.
• The whole must appear before its parts.
• Final understanding must restore the whole without erasing the corrections.
• Scientific comparisons do not prove Śaiva metaphysics.

OUTPUT
------
output_recognition_before_understanding/
  frames/scene_001/*.jpg
  scenes/scene_001.mp4
  recognition_happens_before_understanding.mp4
  narration_timeline.json
  original_essay.md
  contact_sheet.jpg

REQUIREMENTS
------------
pip install pillow numpy
ffmpeg must be on PATH.

USAGE
-----
python recognition_happens_before_understanding_platinum.py
python recognition_happens_before_understanding_platinum.py --preview
python recognition_happens_before_understanding_platinum.py --scene 12
python recognition_happens_before_understanding_platinum.py --fps 12 --width 1920 --height 1080
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
OUTPUT = ROOT / "output_recognition_before_understanding"
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
VOID=(22,25,31); NIGHT=(17,23,39)

FS="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FSB="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FSS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FSSB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def clamp(x,a=0,b=1): return max(a,min(b,x))
def lerp(a,b,t): return a+(b-a)*t
def mix(a,b,t):
    t=clamp(t)
    return tuple(int(lerp(x,y,t)) for x,y in zip(a,b))
def smooth(a,b,x):
    if a==b: return float(x>=b)
    q=clamp((x-a)/(b-a))
    return q*q*(3-2*q)
def ease(t): return .5-.5*math.cos(math.pi*clamp(t))
def pulse(t,hz=1,phase=0): return .5+.5*math.sin(math.tau*(hz*t+phase))

def font(path,size):
    for p in (path,FS,FSS):
        try: return ImageFont.truetype(p,size)
        except OSError: pass
    return ImageFont.load_default()

def bg(w,h,seed,dark=False):
    rng=np.random.default_rng(seed)
    base=NIGHT if dark else WHITE
    arr=np.empty((h,w,3),np.float32)
    arr[:]=base
    arr += rng.normal(0,1.0 if not dark else 1.7,(h,w,1))
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8),"RGB").convert("RGBA")

def layer(im): return Image.new("RGBA",im.size,(0,0,0,0))
def ctext(d,xy,text,f,fill=INK): d.text(xy,text,font=f,fill=fill,anchor="mm")

def seal(im,title,subtitle="",dark=False,color=INK):
    w,h=im.size
    d=ImageDraw.Draw(im)
    ctext(d,(w/2,h*.875),title,font(FSB,max(22,int(h*.042))),WHITE if dark else color)
    if subtitle:
        ctext(d,(w/2,h*.925),subtitle,font(FSS,max(13,int(h*.020))),
              PALE_SILVER if dark else SOFT)

def border(im,dark=False):
    w,h=im.size
    ImageDraw.Draw(im).rounded_rectangle(
        (25,25,w-25,h-25),radius=17,
        outline=(*(WHITE if dark else INK),40),width=2
    )

def glow_line(im,pts,col,width=4,blur=14,alpha=220):
    if len(pts)<2: return
    ov=layer(im); d=ImageDraw.Draw(ov)
    d.line(pts,fill=(*col,alpha),width=width,joint="curve")
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(blur)))
    im.alpha_composite(ov)

def glow_circle(im,x,y,r,col,alpha=180,blur=16):
    ov=layer(im); d=ImageDraw.Draw(ov)
    d.ellipse((x-r,y-r,x+r,y+r),fill=(*col,alpha))
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(im).ellipse(
        (x-r*.35,y-r*.35,x+r*.35,y+r*.35),
        fill=(*mix(col,WHITE,.3),230)
    )

def partial(points,p):
    p=clamp(p)
    if len(points)<2: return points
    lengths=[math.dist(a,b) for a,b in zip(points[:-1],points[1:])]
    total=sum(lengths); target=total*p
    out=[points[0]]; walked=0
    for i,L in enumerate(lengths):
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

def organic_outline(cx,cy,rx,ry,phase=0,points=150):
    pts=[]
    for i in range(points):
        a=math.tau*i/points
        rr=1+.06*math.sin(a*3+phase)+.035*math.sin(a*7-phase*.4)
        pts.append((cx+math.cos(a)*rx*rr,cy+math.sin(a)*ry*rr))
    return pts

def blurred_form(im,cx,cy,rx,ry,clarity=0.0,col=VIOLET,phase=0):
    pts=organic_outline(cx,cy,rx,ry,phase)
    ov=layer(im)
    d=ImageDraw.Draw(ov)
    d.polygon(pts,fill=(*mix(PALE_SILVER,col,.35),120))
    blur=lerp(28,2,clarity)
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(blur)))
    if clarity>.35:
        ImageDraw.Draw(im).line(pts+[pts[0]],fill=(*col,int(190*clarity)),width=4,joint="curve")

def face(d,cx,cy,scale=1,col=INK,alpha=190,detail=1.0):
    d.ellipse((cx-54*scale,cy-72*scale,cx+54*scale,cy+72*scale),
              outline=(*col,int(alpha*detail)),width=max(2,int(4*scale)))
    if detail>.35:
        for sx in (-20,20):
            d.ellipse((cx+sx*scale-5,cy-16*scale-4,cx+sx*scale+5,cy-16*scale+4),
                      fill=(*col,int(alpha*detail)))
    if detail>.65:
        d.arc((cx-22*scale,cy+6*scale,cx+22*scale,cy+32*scale),
              10,170,fill=(*col,int(alpha*detail)),width=max(2,int(3*scale)))

def feature_nodes(d,cx,cy,scale=1,alpha=180):
    nodes=[
        ("EYES",cx,cy-18*scale,CYAN),
        ("MOUTH",cx,cy+25*scale,GOLD),
        ("CONTOUR",cx-65*scale,cy,VIOLET),
        ("POSTURE",cx+70*scale,cy+20*scale,GREEN),
    ]
    for txt,x,y,col in nodes:
        d.ellipse((x-18,y-18,x+18,y+18),fill=(*mix(WHITE,col,.15),alpha),outline=(*col,alpha),width=3)
        ctext(d,(x,y+36),txt,font(FSSB,12),col)

def whole_to_parts(im,cx,cy,q):
    d=ImageDraw.Draw(im)
    blurred_form(im,cx,cy,105,135,1-q*.55,VIOLET,0)
    points=[
        (cx-155,cy-85,CYAN),
        (cx+155,cy-85,GOLD),
        (cx-155,cy+90,VIOLET),
        (cx+155,cy+90,GREEN),
    ]
    for i,(x,y,col) in enumerate(points):
        qq=smooth(i*.08,.80,u if 'u' in globals() else q)
        glow_line(im,partial([(cx,cy),(x,y)],q),col,3,9,130)
        d.ellipse((x-24*q,y-24*q,x+24*q,y+24*q),
                  fill=(*mix(WHITE,col,.15),int(200*q)),outline=(*col,int(180*q)),width=3)

def gestalt_nodes(d,w,h,progress):
    configs=[
        [(w*.40,h*.33),(w*.47,h*.33),(w*.54,h*.33),(w*.61,h*.33)],
        [(w*.42,h*.50),(w*.49,h*.44),(w*.56,h*.50),(w*.49,h*.56)],
    ]
    for config in configs:
        for x,y in config:
            r=8+5*progress
            d.ellipse((x-r,y-r,x+r,y+r),fill=(*SILVER,170))
    if progress>.55:
        d.rounded_rectangle((w*.37,h*.28,w*.64,h*.38),radius=22,
                            outline=(*GOLD,int(180*progress)),width=4)
        d.ellipse((w*.39,h*.40,w*.59,h*.60),outline=(*VIOLET,int(170*progress)),width=4)

def word_box(d,cx,cy,text,col=INK,alpha=210,scale=1):
    f=font(FSB,max(18,int(30*scale)))
    box=d.textbbox((0,0),text,font=f)
    tw,th=box[2]-box[0],box[3]-box[1]
    pad=18*scale
    d.rounded_rectangle((cx-tw/2-pad,cy-th/2-pad*.7,cx+tw/2+pad,cy+th/2+pad*.7),
                        radius=int(14*scale),fill=(*mix(WHITE,col,.09),alpha),
                        outline=(*col,alpha),width=max(2,int(3*scale)))
    ctext(d,(cx,cy),text,f,col)

def graph_field(d,cx,cy,radius,count=26,seed=8):
    rng=random.Random(seed)
    nodes=[]
    for _ in range(count):
        a=rng.random()*math.tau
        r=radius*math.sqrt(rng.random())
        nodes.append((cx+math.cos(a)*r,cy+math.sin(a)*r*.65))
    for i,a in enumerate(nodes):
        for step in (3,7):
            b=nodes[(i+step)%len(nodes)]
            d.line((*a,*b),fill=(*SILVER,45),width=2)
    for x,y in nodes:
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*SILVER,130))
    return nodes

@dataclass
class Scene:
    title:str
    narration:str
    duration:float
    visual:str
    params:dict


def v_blur_known(im,u,t,p):
    w,h=im.size
    q=ease(u)
    blurred_form(im,w*.55,h*.41,110,140,q*.18,VIOLET,t*.05)
    glow_circle(im,w*.55,h*.41,8+18*q,GOLD,125,13)
    seal(im,"YOU KNOW BEFORE YOU CAN SAY HOW","the whole arrives ahead of its explanation")

def v_face_flash(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    blurred_form(im,w*.55,h*.41,105,135,q*.25,VIOLET,t*.05)
    face(d,w*.55,h*.41,.95,GOLD,int(70+120*q),smooth(.28,.75,u))
    glow_circle(im,w*.55,h*.41,14+22*pulse(t,.55)*q,GOLD,130,15)
    seal(im,"A FACE IS RECOGNIZED IN A FLASH","features become explicit afterward")

def v_global_precedence(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    gestalt_nodes(d,w,h,q)
    glow_circle(im,w*.50,h*.43,8+12*q,GOLD,95,10)
    seal(im,"THE WHOLE ORGANIZES THE PARTS","not every perception is assembled piece by piece")

def v_part_analysis(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.41
    q=ease(u)
    blurred_form(im,cx,cy,105,135,1-q*.45,VIOLET,0)
    features=[
        ("CURVE",w*.20,h*.25,CYAN),
        ("ANGLE",w*.80,h*.25,GOLD),
        ("RATIO",w*.20,h*.58,VIOLET),
        ("CONTRAST",w*.80,h*.58,GREEN),
    ]
    for i,(txt,x,y,col) in enumerate(features):
        qq=smooth(i*.10,.70+i*.05,u)
        glow_line(im,partial([(cx,cy),(x,y)],qq),col,3,9,130)
        if qq>.68:
            word_box(d,x,y,txt,col,190,.55)
    seal(im,"EXPLANATION DISSECTS AN ALREADY MEANINGFUL WHOLE","analysis follows recognition")

def v_pratibha(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.41
    q=ease(u)
    blurred_form(im,cx,cy,120,145,.55,VIOLET,t*.04)
    glow_circle(im,cx,cy,lerp(10,60,pulse(t,.55)*q),GOLD,155,20)
    for i in range(16):
        a=i*math.tau/16
        r=lerp(30,190,q)
        x=cx+math.cos(a)*r; y=cy+math.sin(a)*r*.62
        d.line((cx,cy,x,y),fill=(*GOLD,60),width=2)
    seal(im,"PRATIBHĀ","meaning flashes before reasons")

def v_pratyabhijna(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.26,h*.42); right=(w*.74,h*.42)
    q=ease(u)
    blurred_form(im,*right,100,130,.72,VIOLET,0)
    glow_circle(im,*left,18,GOLD,130,11)
    glow_line(im,partial([left,(w*.50,h*.28),right],q),CYAN,4,11,170)
    glow_line(im,partial([right,(w*.50,h*.57),left],smooth(.30,.95,u)),GOLD,5,13,200)
    seal(im,"PRATYABHIJÑĀ","this is that—identity recovered before deduction")

def v_melody(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    points=[]
    for i in range(18):
        x=lerp(w*.12,w*.88,i/17)
        y=h*.42+math.sin(i*.72)*h*.11+math.sin(i*.29)*h*.035
        points.append((x,y))
        d.ellipse((x-5,y-5,x+5,y+5),fill=(*SILVER,150))
    glow_line(im,partial(points,q),GOLD,5,13,200)
    if q>.62:
        d.rounded_rectangle((w*.15,h*.25,w*.85,h*.60),radius=35,
                            outline=(*VIOLET,int(150*q)),width=4)
    seal(im,"THE MELODY IS KNOWN BEFORE ITS INTERVALS","temporal form is grasped as a whole")

def v_rasa(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.41
    q=ease(u)
    for i,col in enumerate((VIOLET,GOLD,CYAN,GREEN,CRIMSON)):
        r=lerp(25,175,q)*(1-i*.08)
        d.arc((cx-r,cy-r*.62,cx+r,cy+r*.62),
              i*25,300+i*12,fill=(*col,90),width=4)
    glow_circle(im,cx,cy,18+20*q,GOLD,120,13)
    seal(im,"RASA IS RECOGNIZED AS A FIELD OF FEELING","mood is known before it is named")

def v_expertise(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    nodes=graph_field(d,cx,cy,210,34,11)
    chosen=[nodes[3],nodes[12],nodes[22],nodes[29]]
    glow_line(im,partial(chosen,q),GOLD,6,15,210)
    for x,y in chosen:
        glow_circle(im,x,y,10,GOLD,110,8)
    seal(im,"EXPERTISE RECOGNIZES CONFIGURATIONS","the rules are often reconstructed after the judgment")

def v_predictive_completion(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.41
    q=ease(u)
    # partial contour completed by prediction
    pts=organic_outline(cx,cy,120,145,0,160)
    visible=pts[:45]+pts[95:125]
    d.line(visible[:45],fill=(*CYAN,180),width=4)
    d.line(visible[45:],fill=(*CYAN,180),width=4)
    predicted=pts[44:96]+pts[124:]+pts[:1]
    glow_line(im,partial(predicted,q),GOLD,4,12,180)
    seal(im,"PREDICTION COMPLETES WHAT EVIDENCE LEAVES OPEN","recognition is active pattern completion")

def v_false_familiarity(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.42); right=(w*.72,h*.42)
    q=ease(u)
    blurred_form(im,*left,90,120,.35,VIOLET,0)
    blurred_form(im,*right,90,120,.35,VIOLET,1.2)
    glow_circle(im,*left,16,CRIMSON,130,12)
    glow_circle(im,*right,16,GOLD,130,12)
    word_box(d,left[0],h*.67,"FAMILIAR",CRIMSON,190,.55)
    word_box(d,right[0],h*.67,"RECOGNIZED",GOLD,190,.55)
    d.line((w*.49,h*.22,w*.51,h*.61),fill=(*CRIMSON,int(190*q)),width=5)
    seal(im,"FAMILIARITY CAN COUNTERFEIT RECOGNITION","felt fit is evidence, not proof")

def v_projection(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.41
    q=ease(u)
    blurred_form(im,cx,cy,110,140,.30,VIOLET,t*.04)
    for i in range(8):
        a=i*math.tau/8
        x=cx+math.cos(a)*170; y=cy+math.sin(a)*105
        arrow(d,(x,y),(cx,cy),CRIMSON,3,10)
    word_box(d,cx,cy,"WHAT I EXPECTED",CRIMSON,205,.75)
    seal(im,"PROJECTION FORCES THE WHOLE TO MATCH A PRIOR NEED","recognition becomes capture")

def v_correction(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.41
    q=ease(u)
    blurred_form(im,cx,cy,110,140,lerp(.3,1,q),mix(VIOLET,GREEN,q),0)
    # red prior withdraws; cyan evidence enters
    for i in range(6):
        a=i*math.tau/6
        x=cx+math.cos(a)*190; y=cy+math.sin(a)*115
        glow_line(im,partial([(x,y),(cx,cy)],q),CYAN,3,9,135)
    d.arc((cx-150,cy-100,cx+150,cy+100),20,int(320*(1-q)),
          fill=(*CRIMSON,150),width=5)
    glow_circle(im,cx,cy,18,GREEN,130,12)
    seal(im,"UNDERSTANDING CORRECTS RECOGNITION WITHOUT DESTROYING IT","the whole survives better evidence")

def v_language_lag(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.30,h*.41); right=(w*.73,h*.41)
    q=ease(u)
    blurred_form(im,*left,95,125,.72,VIOLET,0)
    glow_circle(im,*left,16,GOLD,130,11)
    words=["FACE","OLD","TIRED","FAMILIAR"]
    for i,txt in enumerate(words):
        qq=smooth(i*.12,.64+i*.06,u)
        if qq>.65:
            word_box(d,right[0],h*(.25+i*.12),txt,mix(CYAN,INK,i/3),190,.5)
    glow_line(im,partial([(left[0]+95,left[1]),(right[0]-90,right[1])],q),GOLD,4,11,160)
    seal(im,"LANGUAGE CATCHES UP IN FRAGMENTS","the original whole exceeds each description")

def v_sphota(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.41
    q=ease(u)
    syllables=["THE","BIRD","HAS","FLOWN"]
    xs=[w*(.18+i*.21) for i in range(4)]
    for i,(txt,x) in enumerate(zip(syllables,xs)):
        qq=smooth(i*.10,.60+i*.07,u)
        if qq>.5: word_box(d,x,h*.52,txt,SILVER,int(180*qq),.55)
    if q>.72:
        glow_circle(im,cx,h*.30,38,GOLD,150,15)
        ctext(d,(cx,h*.30),"MEANING",font(FSB,int(h*.030)),GOLD)
    seal(im,"SPHOṬA","successive sounds disclose one indivisible meaning")

def v_analysis_destroys(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.40
    q=ease(u)
    blurred_form(im,cx,cy,110,140,1-q,VIOLET,0)
    pieces=[
        (w*.19,h*.25,"FEATURE 1",CYAN),
        (w*.81,h*.25,"FEATURE 2",GOLD),
        (w*.19,h*.57,"FEATURE 3",VIOLET),
        (w*.81,h*.57,"FEATURE 4",GREEN),
    ]
    for i,(x,y,txt,col) in enumerate(pieces):
        qq=smooth(i*.08,.75,u)
        glow_line(im,partial([(cx,cy),(x,y)],qq),col,3,9,120)
        if qq>.67: word_box(d,x,y,txt,col,190,.45)
    seal(im,"ANALYSIS CAN DESTROY THE PHENOMENON IT EXPLAINS","the parts remain while the living whole disappears")

def v_reintegration(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.41
    q=ease(u)
    points=[
        (w*.19,h*.25,CYAN),
        (w*.81,h*.25,GOLD),
        (w*.19,h*.57,VIOLET),
        (w*.81,h*.57,GREEN),
    ]
    for i,(x,y,col) in enumerate(points):
        glow_line(im,partial([(x,y),(cx,cy)],smooth(i*.08,.90,u)),col,3,9,130)
    blurred_form(im,cx,cy,110,140,q,mix(VIOLET,GREEN,q),0)
    glow_circle(im,cx,cy,18+10*q,GOLD,125,12)
    seal(im,"MATURE UNDERSTANDING RETURNS THE PARTS TO THE WHOLE","explanation becomes transparent to recognition")

def v_machine_boundary(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.42); right=(w*.72,h*.42)
    graph_field(d,left[0],left[1],120,28,17)
    word_box(d,left[0],left[1],"CLASSIFIED",CYAN,195,.60)
    blurred_form(im,*right,100,130,.75,VIOLET,0)
    glow_circle(im,*right,16,GOLD,130,11)
    q=smooth(.35,.9,u)
    d.line((w*.49,h*.22,w*.51,h*.61),fill=(*CRIMSON,int(210*q)),width=6)
    seal(im,"CLASSIFICATION IS NOT YET RECOGNITION IN THE FULL PHILOSOPHICAL SENSE","functional analogy does not settle consciousness")

def v_practice(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.41
    q=pulse(t,.35)
    blurred_form(im,cx,cy,110,140,.45+.35*q,VIOLET,t*.02)
    for r,col in ((55,CYAN),(105,GOLD),(165,GREEN)):
        d.arc((cx-r,cy-r*.62,cx+r,cy+r*.62),20,340,
              fill=(*col,int(70+65*q)),width=3)
    seal(im,"PRACTICE HOLDS RECOGNITION OPEN","long enough for evidence, language, and correction to meet")

def v_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.55,h*.41
    q=ease(u)
    blurred_form(im,cx,cy,lerp(45,115,q),lerp(60,145,q),lerp(.15,.82,q),mix(SILVER,VIOLET,q),t*.03)
    glow_circle(im,cx,cy,8+20*q,GOLD,135,14)
    for i,col in enumerate((CYAN,GOLD,VIOLET,GREEN)):
        a=i*math.tau/4
        x=cx+math.cos(a)*185*q; y=cy+math.sin(a)*115*q
        glow_line(im,partial([(x,y),(cx,cy)],q),col,3,9,110)
    seal(im,"RECOGNITION HAPPENS BEFORE UNDERSTANDING",
         "understanding becomes complete when explanation returns to the whole",color=GREEN)


VISUALS:dict[str,Callable]={
    "blur":v_blur_known,
    "face":v_face_flash,
    "gestalt":v_global_precedence,
    "parts":v_part_analysis,
    "pratibha":v_pratibha,
    "pratyabhijna":v_pratyabhijna,
    "melody":v_melody,
    "rasa":v_rasa,
    "expertise":v_expertise,
    "completion":v_predictive_completion,
    "false":v_false_familiarity,
    "projection":v_projection,
    "correction":v_correction,
    "language":v_language_lag,
    "sphota":v_sphota,
    "destroy":v_analysis_destroys,
    "reintegrate":v_reintegration,
    "machine":v_machine_boundary,
    "practice":v_practice,
    "final":v_final,
}


SCENES:list[Scene]=[
    Scene("Known before clear","You know what it is before you can see it clearly.",7.0,"blur",{}),
    Scene("Whole before parts","The whole arrives before its parts.",6.5,"gestalt",{}),
    Scene("Language late","Language arrives later.",6.0,"language",{}),
    Scene("Explanation later","Explanation arrives later still.",6.5,"parts",{}),
    Scene("Thesis","Recognition happens before understanding.",8.0,"final",{}),

    Scene("Face flash","A face is recognized in a fraction of a second.",8.0,"face",{}),
    Scene("No feature list","You do not first list eyes, nose, mouth, ratios, and contour.",9.0,"parts",{}),
    Scene("Person first","The person appears first.",6.5,"face",{}),
    Scene("Features available later","The features become available for analysis afterward.",8.0,"parts",{}),
    Scene("Already meaningful","Perception begins with an already meaningful whole.",8.0,"gestalt",{}),

    Scene("Melody","A melody works the same way.",6.0,"melody",{}),
    Scene("Intervals later","The intervals can be measured later.",6.5,"melody",{}),
    Scene("Phrase first","But the phrase is heard as one temporal gesture.",8.0,"melody",{}),
    Scene("Whole across time","A whole is recognized across time before its units are calculated.",9.0,"melody",{}),

    Scene("Mood","A room has a mood before you identify its causes.",8.0,"rasa",{}),
    Scene("Light posture silence","Light, posture, silence, distance, and memory combine.",8.5,"rasa",{}),
    Scene("Atmosphere first","Atmosphere is recognized first.",6.5,"rasa",{}),
    Scene("Causes later","Causes are reconstructed later.",6.5,"parts",{}),
    Scene("Rasa","Rasa names this immediate recognition of affective form.",8.5,"rasa",{}),

    Scene("Pratibha","Kashmir Śaivism calls the flash pratibhā.",8.0,"pratibha",{}),
    Scene("Meaning at once","Meaning appears all at once.",6.5,"pratibha",{}),
    Scene("No chain yet","No chain of reasons is yet present.",7.0,"pratibha",{}),
    Scene("Not irrational","This does not make the event irrational.",7.0,"pratibha",{}),
    Scene("Pre-discursive intelligence","It reveals intelligence operating before discourse.",8.5,"pratibha",{}),

    Scene("Pratyabhijna","Pratyabhijñā means recognition.",6.0,"pratyabhijna",{}),
    Scene("This is that","This is that.",5.0,"pratyabhijna",{}),
    Scene("Identity recovered","An identity is recovered rather than derived.",7.5,"pratyabhijna",{}),
    Scene("Prior capacity","The present pattern activates a prior capacity to know it.",8.5,"pratyabhijna",{}),
    Scene("Recognition relation","Recognition is a relation between appearance and latent intelligibility.",9.0,"pratyabhijna",{}),

    Scene("Not memory copy","Recognition is not simply matching a stored photograph.",8.0,"completion",{}),
    Scene("Partial evidence","Partial evidence is completed by expectation and learned structure.",9.0,"completion",{}),
    Scene("Active event","Recognition is active.",6.0,"completion",{}),
    Scene("World and knower","World and knower contribute to one event of fit.",8.5,"completion",{}),
    Scene("Pattern completion","The missing contour is supplied before conscious inference reports itself.",9.0,"completion",{}),

    Scene("Gestalt","Gestalt psychology discovered related effects.",7.0,"gestalt",{}),
    Scene("Grouping","Elements group by proximity, similarity, closure, and continuation.",8.5,"gestalt",{}),
    Scene("Configuration","The configuration changes what each element is perceived to be.",9.0,"gestalt",{}),
    Scene("Parts depend whole","The parts depend on the whole that they supposedly construct.",8.5,"gestalt",{}),
    Scene("Circular perception","Perception is circular rather than simply additive.",7.5,"gestalt",{}),

    Scene("Expertise","Expertise makes the priority of recognition obvious.",8.0,"expertise",{}),
    Scene("Chess position","A chess master sees a position.",6.5,"expertise",{}),
    Scene("Doctor pattern","A doctor sees a clinical pattern.",6.5,"expertise",{}),
    Scene("Musician tension","A musician hears a harmonic tension.",6.5,"expertise",{}),
    Scene("Craftsperson material","A craftsperson feels what the material will permit.",7.5,"expertise",{}),
    Scene("Rules reconstructed","Rules are often reconstructed after the judgment.",8.5,"expertise",{}),

    Scene("Tacit knowledge","Much knowledge is tacit.",6.5,"expertise",{}),
    Scene("Can do not say","One can do more than one can explain.",7.0,"expertise",{}),
    Scene("Body knows","The body knows timing, balance, and proportion.",7.0,"rasa",{}),
    Scene("Explanation partial","Explanation captures only part of the intelligence involved.",8.0,"parts",{}),
    Scene("No mystification","Tacit knowledge should not be mystified.",7.0,"expertise",{}),
    Scene("Trainable sensitivity","It is often trained sensitivity to high-dimensional structure.",9.0,"expertise",{}),

    Scene("Language lag","Language catches up in fragments.",7.0,"language",{}),
    Scene("Old face tired","Old. Familiar. Tired. Guarded.",6.5,"language",{}),
    Scene("Each true partial","Each description may be true and partial.",8.0,"language",{}),
    Scene("Whole exceeds words","The recognized whole exceeds every one of them.",8.0,"language",{}),
    Scene("No final sentence","No final sentence exhausts the face.",7.0,"language",{}),

    Scene("Sphota","The Indian theory of sphoṭa frames a related problem.",8.0,"sphota",{}),
    Scene("Sounds successive","Speech sounds arrive successively.",7.0,"sphota",{}),
    Scene("Meaning whole","Meaning can appear as one whole.",6.5,"sphota",{}),
    Scene("Sentence disclosed","The sentence is not understood by preserving four isolated sound objects.",9.0,"sphota",{}),
    Scene("Burst","Successive marks disclose an indivisible burst of sense.",8.0,"sphota",{}),

    Scene("Understanding dissects","Understanding then dissects the recognized whole.",8.0,"parts",{}),
    Scene("Features","It identifies features.",5.5,"parts",{}),
    Scene("Relations","Relations.",5.0,"parts",{}),
    Scene("Causes","Causes.",5.0,"parts",{}),
    Scene("Rules","Rules.",5.0,"parts",{}),
    Scene("Communication","The whole becomes communicable and testable.",8.0,"parts",{}),

    Scene("Analysis gain","Analysis is not the enemy.",6.0,"parts",{}),
    Scene("Errors exposed","It exposes errors.",6.0,"correction",{}),
    Scene("Comparisons possible","It permits comparison.",6.0,"parts",{}),
    Scene("Knowledge transmitted","It transmits knowledge beyond the original recognizer.",8.0,"language",{}),
    Scene("Recognition revised","It allows recognition to be revised.",7.5,"correction",{}),

    Scene("False familiarity","Because recognition can be false.",6.5,"false",{}),
    Scene("Familiar not same","Familiarity is not identity.",6.0,"false",{}),
    Scene("Expectation fit","Expectation can produce a feeling of fit.",7.0,"false",{}),
    Scene("Déjà vu","A scene may feel remembered without being remembered.",7.0,"false",{}),
    Scene("Confidence no proof","Confidence is not proof.",6.0,"false",{}),

    Scene("Projection","Projection is counterfeit recognition.",7.0,"projection",{}),
    Scene("Need imposed","A prior need is imposed on ambiguous evidence.",8.0,"projection",{}),
    Scene("Desired person","The desired person becomes the person actually present.",8.0,"projection",{}),
    Scene("Feared pattern","The feared pattern becomes the pattern actually occurring.",8.0,"projection",{}),
    Scene("Whole forced","The whole is forced to fit before it can answer.",8.0,"projection",{}),

    Scene("Recognition test","Recognition must therefore survive correction.",8.0,"correction",{}),
    Scene("More evidence enters","More evidence enters.",6.0,"correction",{}),
    Scene("Whole changes","The whole may change.",6.0,"correction",{}),
    Scene("Not destroyed","True recognition is not destroyed by detail.",7.0,"correction",{}),
    Scene("Becomes precise","It becomes more precise.",6.5,"correction",{}),

    Scene("Analysis danger","But analysis has its own danger.",6.5,"destroy",{}),
    Scene("Living face fragments","The living face becomes measurements.",7.0,"destroy",{}),
    Scene("Melody becomes intervals","The melody becomes intervals.",6.5,"destroy",{}),
    Scene("Rasa becomes causes","The mood becomes causes.",6.5,"destroy",{}),
    Scene("Phenomenon disappears","The phenomenon disappears inside its explanation.",8.5,"destroy",{}),

    Scene("Reduction","Reduction mistakes components for the experienced whole.",8.0,"destroy",{}),
    Scene("Inventory not encounter","An inventory is not an encounter.",7.0,"destroy",{}),
    Scene("Mechanism not meaning","A mechanism is not yet meaning.",7.0,"destroy",{}),
    Scene("Explanation no replacement","Explanation should not replace what it explains.",8.0,"destroy",{}),
    Scene("Return required","It must return to the whole.",6.5,"reintegrate",{}),

    Scene("Reintegration","Mature understanding reintegrates.",6.5,"reintegrate",{}),
    Scene("Parts return","The parts return to the living configuration.",7.0,"reintegrate",{}),
    Scene("Corrections retained","Corrections are retained.",6.5,"reintegrate",{}),
    Scene("Whole transformed","The whole is transformed rather than restored unchanged.",8.0,"reintegrate",{}),
    Scene("Understanding complete","Understanding becomes complete when analysis becomes transparent to recognition.",9.5,"reintegrate",{}),

    Scene("Vimarsa","Śaiva vimarśa names reflexive awareness.",7.0,"pratyabhijna",{}),
    Scene("Knowing knows","Knowing does not merely occur; it knows itself occurring.",8.0,"pratyabhijna",{}),
    Scene("Recognition reflects","Recognition can become aware of its own operation.",8.0,"practice",{}),
    Scene("Flash held open","The flash is held open long enough to examine.",8.0,"practice",{}),
    Scene("Intuition disciplined","Intuition becomes disciplined without being extinguished.",8.5,"practice",{}),

    Scene("Predictive comparison","Predictive processing provides a useful comparison.",8.0,"completion",{}),
    Scene("Hypothesis fit","A hypothesis fits partial sensory evidence.",7.0,"completion",{}),
    Scene("Rapid stabilization","The percept stabilizes before explicit reasoning.",8.0,"completion",{}),
    Scene("Top down bottom up","Top-down expectation and bottom-up correction interact.",8.5,"correction",{}),
    Scene("No metaphysical proof","This does not prove the metaphysics of recognition.",7.0,"machine",{}),
    Scene("Shared operation","It clarifies the operation of whole-form completion.",8.0,"completion",{}),

    Scene("Machine analogy","Machine classification introduces a sharper boundary.",8.0,"machine",{}),
    Scene("System classifies","A system can classify a pattern before producing an explanation.",8.0,"machine",{}),
    Scene("Post hoc explanation","Its explanation may be post hoc or incomplete.",8.0,"machine",{}),
    Scene("Functional similarity","This creates a functional similarity.",7.0,"machine",{}),
    Scene("No settled equivalence","It does not establish equivalence with conscious recognition.",9.0,"machine",{}),

    Scene("Practice","Practice can train the interval between recognition and judgment.",8.0,"practice",{}),
    Scene("Let whole appear","Let the whole appear.",6.0,"practice",{}),
    Scene("Do not freeze","Do not freeze it immediately into a conclusion.",7.0,"practice",{}),
    Scene("Invite detail","Invite detail.",5.5,"practice",{}),
    Scene("Permit correction","Permit correction.",5.5,"practice",{}),
    Scene("Return whole","Return to the whole.",6.0,"reintegrate",{}),

    Scene("Final blur","At first there is only a blurred form.",7.0,"blur",{}),
    Scene("Known flash","It is known in a flash.",6.0,"pratibha",{}),
    Scene("Identity returns","Identity returns before reasons.",7.0,"pratyabhijna",{}),
    Scene("Words gather","Words gather afterward.",6.0,"language",{}),
    Scene("Analysis divides","Analysis divides the whole.",6.0,"parts",{}),
    Scene("Correction refines","Correction refines it.",6.0,"correction",{}),
    Scene("Reintegration restores","Reintegration restores living meaning.",7.0,"reintegrate",{}),
    Scene("Final thesis","Recognition happens before understanding.",8.0,"final",{}),
    Scene("Final completion","Understanding is complete when it can explain the parts without losing the whole.",9.5,"final",{}),
]


def export_original_essay():
    lines=[
        "# recognition happens before understanding",
        "",
        "## how meaning arrives before explanation",
        "",
    ]
    for scene in SCENES:
        lines += [scene.narration,""]
    path=OUTPUT/"original_essay.md"
    path.write_text("\n".join(lines),encoding="utf-8")
    return path

def render_frame(scene,fi,fc,w,h,seed):
    u=fi/max(1,fc-1)
    t=u*scene.duration
    dark=False
    im=bg(w,h,seed,dark)
    VISUALS[scene.visual](im,u,t,scene.params)
    border(im,dark)
    return im.convert("RGB")

def require_ffmpeg():
    exe=shutil.which("ffmpeg")
    if not exe:
        raise RuntimeError("ffmpeg is required but was not found on PATH")
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
        str(out),
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return out

def render_scene(i,scene,fps,w,h,preview):
    fd=FRAMES/f"scene_{i:03d}"
    fd.mkdir(parents=True,exist_ok=True)
    SCENES_DIR.mkdir(parents=True,exist_ok=True)
    fc=max(2,round(scene.duration*fps))

    if preview:
        for oi,fi in enumerate([0,int(fc*.35),int(fc*.72),fc-1]):
            render_frame(scene,fi,fc,w,h,i*1000+fi).save(
                fd/f"preview_{oi:02d}.jpg",quality=95
            )
        return fd

    for fi in range(fc):
        path=fd/f"{fi:05d}.jpg"
        if path.exists():
            continue
        render_frame(scene,fi,fc,w,h,i*1000+fi).save(
            path,quality=95,subsampling=0
        )
    return encode_scene(i,fps)

def concatenate(paths):
    concat=OUTPUT/"concat.txt"
    concat.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in paths),
        encoding="utf-8"
    )
    out=OUTPUT/"recognition_happens_before_understanding.mp4"
    subprocess.run([
        require_ffmpeg(),"-y",
        "-f","concat",
        "-safe","0",
        "-i",str(concat),
        "-c","copy",
        "-movflags","+faststart",
        str(out),
    ],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return out

def export_timeline():
    cursor=0.0
    payload=[]
    for i,scene in enumerate(SCENES,1):
        record=asdict(scene)
        record["scene_id"]=f"scene_{i:03d}"
        record["start_seconds"]=round(cursor,3)
        cursor+=scene.duration
        record["end_seconds"]=round(cursor,3)
        payload.append(record)

    path=OUTPUT/"narration_timeline.json"
    path.write_text(json.dumps({
        "title":"recognition happens before understanding",
        "subtitle":"how meaning arrives before explanation",
        "runtime_seconds":round(cursor,3),
        "scene_count":len(SCENES),
        "original_essay":True,
        "style":{
            "continuity_object":"blurred whole recognized before its details stabilize",
            "shot_duration_range_seconds":[5,10],
            "palette_roles":{
                "silver":"incomplete evidence and familiarity",
                "gold":"recognition and meaningful fit",
                "cyan":"sensory evidence and analysis",
                "violet":"whole-form and pre-verbal meaning",
                "crimson":"projection and false certainty",
                "green":"correction and reintegration",
                "graphite":"explicit concepts and explanation",
            },
        },
        "scenes":payload,
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

    print(f"Essay: {export_original_essay()}")
    print(f"Timeline: {export_timeline()}")
    print(f"Scenes: {len(SCENES)}")
    print(f"Runtime: {sum(s.duration for s in SCENES)/60:.2f} minutes")

    if args.scene:
        if not 1<=args.scene<=len(SCENES):
            raise ValueError("scene out of range")
        print(render_scene(args.scene,SCENES[args.scene-1],
                           args.fps,args.width,args.height,args.preview))
        return

    rendered=[]
    for i,scene in enumerate(SCENES,1):
        print(f"[{i:03d}/{len(SCENES):03d}] {scene.title} ({scene.duration:.1f}s)")
        result=render_scene(i,scene,args.fps,args.width,args.height,args.preview)
        if not args.preview:
            rendered.append(result)

    if not args.no_contact_sheet:
        print(f"Contact sheet: {make_contact_sheet(args.width,args.height)}")
    if not args.preview:
        print(f"Final video: {concatenate(rendered)}")

if __name__=="__main__":
    main()
