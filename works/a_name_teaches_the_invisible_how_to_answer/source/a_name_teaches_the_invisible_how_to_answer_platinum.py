#!/usr/bin/env python3
"""
A NAME TEACHES THE INVISIBLE HOW TO ANSWER
An original Imaginarium visual essay and Platinum-house procedural renderer.

ORIGINAL THESIS
---------------
A sacred name is not merely a label attached to an already completed being.
It is a disciplined event in which breath, sound, memory, image, attention,
body, and inherited relation are synchronized until the invisible acquires
a repeatable way of appearing.

This essay joins:
• mantra, nāma-rūpa, japa, bīja, nyāsa, and devatā
• Kashmir Śaiva vāc, mātrikā, ābhāsa, pratibhā, and recognition
• Neoplatonic divine names and theurgy
• Corbinian angelology and imaginal encounter
• predictive perception, auditory imagery, and embodied cognition
• safeguards against projection, literalism, coercion, and spiritual inflation

DESIGN CONTRACT
---------------
• Every shot lasts 5–10 seconds.
• Every shot visibly performs the narrated operation.
• Clean white field; deep indigo only for invisible depth and imaginal presence.
• No static slide layouts and no decorative loops.
• Silver = unspoken name / latent form / inherited trace
• Cyan = breath, articulation, attention, auditory prediction
• Gold = answer, presence, recognition, divine intelligibility
• Violet = imaginal depth, deity-form, dream, subtle interior
• Crimson = projection, coercion, false certainty, naming as domination
• Green = integration, ethical fruit, returned embodiment
• Graphite = ordinary language, material support, social reality
• Continuity object: one unspoken glyph becomes breath, sound, form, face, and relation.
• The name must never become a generic glowing word.
• Typography must remain sparse and function as ritual seals.
• Final criterion: the name makes the practitioner more truthful and more answerable.

OUTPUT
------
output_name_invisible/
  frames/scene_001/*.jpg
  scenes/scene_001.mp4
  a_name_teaches_the_invisible_how_to_answer.mp4
  narration_timeline.json
  original_essay.md
  contact_sheet.jpg

REQUIREMENTS
------------
pip install pillow numpy
ffmpeg must be on PATH.

USAGE
-----
python a_name_teaches_the_invisible_how_to_answer_platinum.py
python a_name_teaches_the_invisible_how_to_answer_platinum.py --preview
python a_name_teaches_the_invisible_how_to_answer_platinum.py --scene 12
python a_name_teaches_the_invisible_how_to_answer_platinum.py --fps 12 --width 1920 --height 1080
"""

from __future__ import annotations
import argparse, json, math, random, shutil, subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output_name_invisible"
FRAMES = OUTPUT / "frames"
SCENES_DIR = OUTPUT / "scenes"

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 10

WHITE=(248,247,243); INK=(28,31,35); SOFT=(84,88,94)
SILVER=(177,184,190); PALE_SILVER=(224,227,229)
CYAN=(55,153,181); PALE_CYAN=(192,226,233)
GOLD=(194,153,68); PALE_GOLD=(235,218,175)
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
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(blur))); im.alpha_composite(ov)

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

def breath_curve(w,h,phase=0,y=.42):
    pts=[]
    for i in range(180):
        q=i/179
        x=lerp(w*.08,w*.92,q)
        yy=h*y+math.sin(q*math.tau*2+phase)*h*.04+math.sin(q*math.tau*7-phase)*h*.011
        pts.append((x,yy))
    return pts

def glyph(d,cx,cy,r,col=SILVER,alpha=180,phase=0):
    pts=[]
    for i in range(120):
        a=math.tau*i/120
        rr=r*(.72+.18*math.sin(a*3+phase)+.10*math.sin(a*5-phase))
        pts.append((cx+math.cos(a)*rr,cy+math.sin(a)*rr*.72))
    d.line(pts+[pts[0]],fill=(*col,alpha),width=4)
    d.line((cx-r*.38,cy,cx+r*.42,cy),fill=(*col,alpha),width=3)
    d.line((cx,cy-r*.45,cx,cy+r*.45),fill=(*col,alpha),width=3)

def mouth(d,cx,cy,scale=1,col=INK,alpha=180):
    d.arc((cx-75*scale,cy-40*scale,cx+75*scale,cy+40*scale),
          10,170,fill=(*col,alpha),width=max(2,int(4*scale)))

def ear(d,cx,cy,scale=1,col=INK,alpha=180):
    d.arc((cx-45*scale,cy-70*scale,cx+45*scale,cy+70*scale),
          70,290,fill=(*col,alpha),width=max(2,int(4*scale)))
    d.arc((cx-22*scale,cy-42*scale,cx+22*scale,cy+42*scale),
          80,285,fill=(*col,alpha),width=max(2,int(3*scale)))

def face(d,cx,cy,scale=1,col=GOLD,alpha=180):
    d.ellipse((cx-60*scale,cy-80*scale,cx+60*scale,cy+80*scale),
              outline=(*col,alpha),width=max(2,int(4*scale)))
    for sx in (-22,22):
        d.ellipse((cx+sx*scale-6,cy-20*scale-4,cx+sx*scale+6,cy-20*scale+4),
                  fill=(*col,alpha))
    d.arc((cx-24*scale,cy+5*scale,cx+24*scale,cy+35*scale),
          10,170,fill=(*col,alpha),width=max(2,int(3*scale)))

def orbit(d,cx,cy,rx,ry,col,alpha=140,width=3):
    d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),outline=(*col,alpha),width=width)

def star_field(d,w,h,seed=5,alpha=95):
    rng=random.Random(seed)
    for _ in range(90):
        x=rng.uniform(w*.08,w*.92); y=rng.uniform(h*.08,h*.72)
        r=rng.choice([1,1,1,2])
        d.ellipse((x-r,y-r,x+r,y+r),fill=(*PALE_GOLD,alpha))

@dataclass
class Scene:
    title:str
    narration:str
    duration:float
    visual:str
    params:dict

def v_unspoken(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    glyph(d,w*.5,h*.42,lerp(45,105,q),mix(SILVER,INK,q),int(120+90*q),t*.08)
    seal(im,"BEFORE IT IS SPOKEN, THE NAME IS LATENT","a possibility of articulation")

def v_breath_name(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    mouth(d,w*.18,h*.43,1,INK,180)
    glow_line(im,partial(breath_curve(w,h,t*.4,.43),q),CYAN,5,14,210)
    glyph(d,w*.74,h*.43,78,mix(SILVER,GOLD,q),int(150+70*q),t*.08)
    seal(im,"BREATH GIVES THE NAME A BODY","sound begins as shaped air")

def v_repetition(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42; q=ease(u)
    glyph(d,cx,cy,72,GOLD,190,t*.05)
    for i in range(9):
        r=(85+i*24)*q
        d.arc((cx-r,cy-r*.62,cx+r,cy+r*.62),10,int(320*q),
              fill=(*mix(CYAN,GOLD,i/8),110),width=3)
    seal(im,"JAPA MAKES A PATH BY WALKING IT AGAIN","repetition becomes patterned return")

def v_name_form(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.42); right=(w*.72,h*.42)
    glyph(d,*left,72,SILVER,180,t*.05)
    q=ease(u)
    face(d,*right,lerp(.3,1.0,q),GOLD,int(80+120*q))
    glow_line(im,partial([left,(w*.50,h*.30),right],q),CYAN,4,11,170)
    glow_line(im,partial([right,(w*.50,h*.56),left],smooth(.35,.95,u)),GOLD,4,11,190)
    seal(im,"NĀMA AND RŪPA CO-ARISE","name gathers form; form answers the name")

def v_matrika(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42; q=ease(u)
    glyph(d,cx,cy,48,GOLD,200,t*.08)
    letters=16
    for i in range(letters):
        a=i*math.tau/letters
        rr=lerp(55,205,q)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.62
        col=mix(CYAN,VIOLET,i/(letters-1))
        d.ellipse((x-7,y-7,x+7,y+7),fill=(*col,170))
        glow_line(im,[(cx,cy),(x,y)],col,2,7,70)
    seal(im,"MĀTRIKĀ","the mothers of sound unfold difference from one field")

def v_four_vac(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    levels=[("PARĀ",GOLD,h*.16),("PAŚYANTĪ",VIOLET,h*.32),("MADHYAMĀ",CYAN,h*.49),("VAIKHARĪ",INK,h*.66)]
    x=w*.5; q=ease(u)
    for i,(txt,col,y) in enumerate(levels):
        d.ellipse((x-52,y-26,x+52,y+26),fill=(*mix(WHITE,col,.15),220),outline=(*col,180),width=3)
        ctext(d,(x,y),txt,font(FSSB,int(h*.013)),col)
        if i>0:
            glow_line(im,partial([(x,levels[i-1][2]+26),(x,y-26)],q),
                      mix(levels[i-1][1],col,.5),4,11,170)
    seal(im,"SPEECH DESCENDS THROUGH LEVELS","undivided impulse becomes image, thought, and audible word")

def v_bija(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42; q=ease(u)
    glow_circle(im,cx,cy,20+20*q,GOLD,150,13)
    glyph(d,cx,cy,60+55*q,mix(SILVER,GOLD,q),180,t*.08)
    for i,col in enumerate((CYAN,VIOLET,GREEN,CRIMSON)):
        a=i*math.tau/4
        x=cx+math.cos(a)*180*q; y=cy+math.sin(a)*110*q
        glow_line(im,[(cx,cy),(x,y)],col,3,9,120)
    seal(im,"BĪJA","a seed-syllable compresses a world into a repeatable event")

def v_predictive_hearing(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.18,h*.42); center=(w*.50,h*.42); right=(w*.82,h*.42)
    ear(d,*left,1,INK,180)
    d.rounded_rectangle((center[0]-85,center[1]-65,center[0]+85,center[1]+65),
                        radius=18,fill=(*PALE_CYAN,215),outline=(*CYAN,180),width=3)
    ctext(d,center,"MODEL",font(FSSB,int(h*.020)),CYAN)
    glyph(d,*right,62,SILVER,190,t*.05)
    q=ease(u)
    glow_line(im,partial([right,center,left],q),CYAN,4,11,170)
    glow_line(im,partial([left,(w*.36,h*.56),center,(w*.64,h*.56),right],smooth(.35,.95,u)),GOLD,4,11,150)
    seal(im,"HEARING IS EXPECTATION MEETING SOUND","repetition changes what the ear is ready to receive")

def v_memory_lineage(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42; q=ease(u)
    glyph(d,cx,cy,64,GOLD,190,t*.05)
    for i in range(7):
        x=w*(.10+i*.13); y=h*(.25 if i%2==0 else .58)
        mouth(d,x,y,.45,mix(SILVER,GOLD,i/6),100+int(70*q))
        glow_line(im,partial([(x,y),(cx,cy)],smooth(i*.08,.9,u)),mix(SILVER,GOLD,i/6),2,7,90)
    seal(im,"A NAME INHERITS MANY MOUTHS","lineage stores pronunciation, rhythm, story, and trust")

def v_daimonic_answer(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    bottom=(w*.5,h*.67); mid=(w*.5,h*.42); top=(w*.5,h*.17)
    mouth(d,*bottom,.8,INK,170)
    glyph(d,*mid,58,VIOLET,190,t*.06)
    q=ease(u)
    face(d,*top,lerp(.25,.85,q),GOLD,int(70+130*q))
    glow_line(im,partial([bottom,mid,top],q),GOLD,5,13,200)
    seal(im,"THE NAME BECOMES A MEDIATOR","not merely spoken by you, not safely treated as external fact")

def v_projection(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.42); right=(w*.72,h*.42)
    # echo chamber
    glyph(d,*left,62,CRIMSON,180,t*.04)
    d.arc((left[0]-120,left[1]-100,left[0]+120,left[1]+100),20,340,fill=(*CRIMSON,160),width=5)
    # answer with resistance
    glyph(d,*right,62,GOLD,190,t*.04)
    arrow(d,(right[0],right[1]),(right[0]-125,right[1]+90),GREEN,4,12)
    ctext(d,(right[0]-145,right[1]+110),"CHANGE",font(FSSB,int(h*.014)),GREEN)
    seal(im,"ECHO CONFIRMS YOU · ANSWER CORRECTS YOU","resistance is the beginning of discernment")

def v_three_errors(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    items=[("LABEL",SILVER),("COMMAND",CRIMSON),("POSSESSION",VIOLET)]
    xs=[w*.22,w*.50,w*.78]
    for i,((txt,col),x) in enumerate(zip(items,xs)):
        q=smooth(i*.12,.62+i*.07,u)
        d.ellipse((x-72*q,h*.40-72*q,x+72*q,h*.40+72*q),
                  fill=(*mix(WHITE,col,.18),int(220*q)),outline=(*col,int(180*q)),width=4)
        if q>.66:ctext(d,(x,h*.40),txt,font(FSB,int(h*.019)),col)
        strike=smooth(.48+i*.08,.95,u)
        d.line((x-84,h*.32,x+84,h*.48),fill=(*CRIMSON,int(200*strike)),width=5)
    seal(im,"THREE WAYS TO CORRUPT A SACRED NAME","reduce it · weaponize it · claim to own it")

def v_neoplatonic_names(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    levels=[("THE ONE",GOLD,h*.15),("INTELLECT",VIOLET,h*.32),("SOUL",CYAN,h*.49),("COSMOS",INK,h*.67)]
    x=w*.5; q=ease(u)
    for i,(txt,col,y) in enumerate(levels):
        d.ellipse((x-55,y-27,x+55,y+27),fill=(*mix(WHITE,col,.15),220),outline=(*col,180),width=3)
        ctext(d,(x,y),txt,font(FSSB,int(h*.013)),col)
        if i>0:
            glow_line(im,partial([(x,levels[i-1][2]+27),(x,y-27)],q),
                      mix(levels[i-1][1],col,.5),4,11,170)
    seal(im,"DIVINE NAMES DO NOT CAPTURE THE GODS","they trace how higher unity becomes intelligible below")

def v_abhasa(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42; q=ease(u)
    glyph(d,cx,cy,54,GOLD,190,t*.08)
    for i in range(18):
        a=i*math.tau/18
        rr=lerp(25,210,q)*(0.7+0.3*((i%4)/3))
        x=cx+math.cos(a+t*.08)*rr; y=cy+math.sin(a+t*.08)*rr*.62
        col=mix(CYAN,VIOLET,i/17)
        glow_circle(im,x,y,5+3*(i%3),col,90,7)
        glow_line(im,[(cx,cy),(x,y)],col,2,7,70)
    seal(im,"ĀBHĀSA","name, sound, form, and knower are appearances of one field")

def v_recognition(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.25,h*.42); right=(w*.75,h*.42)
    mouth(d,*left,.8,INK,180)
    glyph(d,*right,66,GOLD,190,t*.05)
    q=ease(u)
    glow_line(im,partial([left,(w*.50,h*.30),right],q),CYAN,4,11,170)
    glow_line(im,partial([right,(w*.50,h*.56),left],smooth(.30,.95,u)),GOLD,5,13,200)
    seal(im,"RECOGNITION RETURNS THE NAME TO ITS SOURCE","the speaker discovers the power by which speaking was possible")

def v_name_body(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx=w*.38
    # body axis
    d.ellipse((cx-25,h*.16,cx+25,h*.24),outline=(*INK,180),width=4)
    d.line((cx,h*.24,cx,h*.62),fill=(*INK,180),width=5)
    d.line((cx,h*.34,cx-75,h*.46),fill=(*INK,180),width=5)
    d.line((cx,h*.34,cx+75,h*.46),fill=(*INK,180),width=5)
    d.line((cx,h*.62,cx-48,h*.72),fill=(*INK,180),width=5)
    d.line((cx,h*.62,cx+48,h*.72),fill=(*INK,180),width=5)
    glyph(d,w*.72,h*.42,64,GOLD,190,t*.05)
    pts=[(cx,h*.20),(cx,h*.32),(cx,h*.44),(cx,h*.56),(cx,h*.66)]
    for i,pnt in enumerate(pts):
        q=smooth(i*.10,.85,u)
        glow_circle(im,pnt[0],pnt[1],10+7*q,mix(CYAN,GOLD,i/4),130,9)
        glow_line(im,partial([pnt,(w*.72,h*.42)],q),mix(CYAN,GOLD,i/4),3,9,120)
    seal(im,"THE NAME IS PLACED INTO THE BODY","sound becomes posture, breath, and location")

def v_ethics(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    glyph(d,w*.25,h*.42,58,GOLD,190,t*.05)
    fruits=[("TRUTH",CYAN,w*.52,h*.25),("HUMILITY",VIOLET,w*.72,h*.33),
            ("COURAGE",GOLD,w*.52,h*.56),("CARE",GREEN,w*.76,h*.60)]
    for i,(txt,col,x,y) in enumerate(fruits):
        q=smooth(i*.10,.65+i*.05,u)
        glow_line(im,partial([(w*.31,h*.42),(x,y)],q),col,3,9,150)
        d.ellipse((x-28*q,y-28*q,x+28*q,y+28*q),fill=(*mix(WHITE,col,.18),int(220*q)),
                  outline=(*col,int(180*q)),width=3)
        if q>.68:ctext(d,(x,y),txt,font(FSSB,int(h*.012)),col)
    seal(im,"THE FRUIT TESTS THE NAME","does invocation enlarge truthfulness and responsibility?")

def v_return_world(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    glyph(d,w*.20,h*.42,52,GOLD,180,t*.05)
    d.line((w*.08,h*.62,w*.92,h*.62),fill=(*INK,120),width=5)
    for i in range(8):
        x=w*(.16+i*.09)
        d.rectangle((x-18,h*.48,x+18,h*.62),fill=(*PALE_SILVER,120),outline=(*SILVER,100))
    q=ease(u)
    glow_line(im,partial([(w*.27,h*.42),(w*.44,h*.54),(w*.65,h*.50),(w*.88,h*.57)],q),
              GREEN,6,14,210)
    seal(im,"THE NAME MUST RETURN YOU TO THE NAMELESS WORLD","more attentive to what cannot be reduced to words")

def v_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.55,h*.42; q=ease(u)
    glyph(d,cx,cy,lerp(45,95,q),mix(SILVER,GOLD,q),int(140+80*q),t*.08)
    glow_line(im,partial(breath_curve(w,h,t*.35,.42),q),CYAN,4,12,170)
    face(d,cx,cy,lerp(.2,.8,q),GOLD,int(50+130*q))
    for r,col in [(110,VIOLET),(160,GOLD),(210,GREEN)]:
        d.arc((cx-r*q,cy-r*.62*q,cx+r*q,cy+r*.62*q),10,int(320*q),
              fill=(*col,110),width=3)
    seal(im,"A NAME TEACHES THE INVISIBLE HOW TO ANSWER",
         "not by capturing it, but by preparing a form of relation",color=GREEN)

VISUALS:dict[str,Callable]={
    "unspoken":v_unspoken,
    "breath":v_breath_name,
    "repeat":v_repetition,
    "nameform":v_name_form,
    "matrika":v_matrika,
    "fourvac":v_four_vac,
    "bija":v_bija,
    "predict":v_predictive_hearing,
    "lineage":v_memory_lineage,
    "daimon":v_daimonic_answer,
    "projection":v_projection,
    "errors":v_three_errors,
    "neoplatonic":v_neoplatonic_names,
    "abhasa":v_abhasa,
    "recognition":v_recognition,
    "body":v_name_body,
    "ethics":v_ethics,
    "return":v_return_world,
    "final":v_final,
}

SCENES:list[Scene]=[
    Scene("Latent name","Before it is spoken, the name is latent.",6.0,"unspoken",{}),
    Scene("Possibility","It exists as a possibility of articulation.",6.5,"unspoken",{}),
    Scene("Breath begins","Then breath begins to move.",5.5,"breath",{}),
    Scene("Air shaped","Air is shaped by throat, tongue, palate, lips, and attention.",8.5,"breath",{}),
    Scene("Invisible gains body","The invisible acquires a body made of sound.",8.0,"breath",{}),
    Scene("Thesis","A name teaches the invisible how to answer.",8.0,"final",{}),

    Scene("Not label only","A sacred name is not merely a label.",6.5,"unspoken",{}),
    Scene("Ordinary label","A label points toward something already completed.",7.0,"unspoken",{}),
    Scene("Ritual name","A ritual name participates in making presence repeatable.",8.5,"repeat",{}),
    Scene("Breath rhythm memory","Breath, rhythm, memory, and image begin recurring together.",9.0,"repeat",{}),
    Scene("Name event","The name becomes an event rather than a tag.",7.0,"repeat",{}),

    Scene("Nama rupa","Nāma and rūpa—name and form—arise together.",8.0,"nameform",{}),
    Scene("Name gathers form","Name gathers form.",5.5,"nameform",{}),
    Scene("Form answers name","Form answers the name.",5.5,"nameform",{}),
    Scene("Neither first alone","Neither is fully first by itself.",6.5,"nameform",{}),
    Scene("Mutual articulation","They articulate one another.",6.5,"nameform",{}),

    Scene("Japa","Japa repeats the name.",5.5,"repeat",{}),
    Scene("Not redundancy","Repetition is not redundancy.",6.0,"repeat",{}),
    Scene("Path walked","It is a path made by walking it again.",7.0,"repeat",{}),
    Scene("Return patterned","Each return slightly changes breath, expectation, and memory.",8.5,"repeat",{}),
    Scene("Name stabilizes","The name stabilizes as a patterned attractor.",7.5,"repeat",{}),
    Scene("Voice learns","The voice learns where to go.",6.0,"repeat",{}),
    Scene("Attention learns","Attention learns how to follow.",6.0,"repeat",{}),

    Scene("Matrika","Śaiva traditions speak of Mātrikā, the mothers of sound.",8.0,"matrika",{}),
    Scene("Letters not inert","Letters are not treated as inert marks.",7.0,"matrika",{}),
    Scene("Differentiation powers","They are powers by which undivided awareness differentiates.",9.0,"matrika",{}),
    Scene("Sound difference","Sound becomes difference.",6.0,"matrika",{}),
    Scene("Difference world","Difference becomes world.",6.0,"matrika",{}),
    Scene("Name cosmology","A name is therefore miniature cosmology.",7.5,"matrika",{}),

    Scene("Four speech levels","Speech is often described through four levels.",7.0,"fourvac",{}),
    Scene("Para","Parā is undivided speech-power.",6.0,"fourvac",{}),
    Scene("Pashyanti","Paśyantī is seeing-speech, image before sentence.",8.0,"fourvac",{}),
    Scene("Madhyama","Madhyamā is interior formulation.",6.5,"fourvac",{}),
    Scene("Vaikhari","Vaikharī is audible articulation.",6.5,"fourvac",{}),
    Scene("Descent","Speech descends from undivided impulse into sound.",8.0,"fourvac",{}),
    Scene("Ascent","Practice can also hear audible sound back toward its source.",8.0,"fourvac",{}),

    Scene("Bija","A bīja is a seed-syllable.",5.5,"bija",{}),
    Scene("Compressed world","It compresses a world into a repeatable event.",8.0,"bija",{}),
    Scene("Not abbreviation","It is not merely an abbreviation.",6.5,"bija",{}),
    Scene("Dense relation","It is dense relation.",6.0,"bija",{}),
    Scene("Sound image force","Sound, image, force, deity, and body are folded together.",8.5,"bija",{}),
    Scene("Seed unfolds","Repetition unfolds the seed.",6.0,"bija",{}),

    Scene("Predictive hearing","Modern perception science clarifies one layer of this.",8.0,"predict",{}),
    Scene("Hearing active","Hearing is not passive reception.",6.5,"predict",{}),
    Scene("Expectation signal","The brain predicts patterns and updates through sound.",8.0,"predict",{}),
    Scene("Repeated name salience","Repeated names acquire salience, timing, and emotional weight.",8.5,"predict",{}),
    Scene("Auditory image","The name may continue internally after the voice stops.",7.5,"predict",{}),
    Scene("No reduction","This does not reduce mantra to prediction.",6.5,"predict",{}),
    Scene("Embodied route","It shows one embodied route by which a name becomes present.",8.0,"predict",{}),

    Scene("Lineage","A sacred name is rarely invented alone.",6.5,"lineage",{}),
    Scene("Many mouths","It arrives through many mouths.",6.0,"lineage",{}),
    Scene("Pronunciation inherited","Pronunciation is inherited.",5.5,"lineage",{}),
    Scene("Rhythm inherited","Rhythm is inherited.",5.5,"lineage",{}),
    Scene("Stories inherited","Stories are inherited.",5.5,"lineage",{}),
    Scene("Trust inherited","Trust is inherited.",5.5,"lineage",{}),
    Scene("Stored voices","Lineage is stored voice.",6.5,"lineage",{}),

    Scene("Deity form","With repetition, a form may gather around the name.",8.0,"nameform",{}),
    Scene("Face emerges","A face emerges.",5.5,"nameform",{}),
    Scene("Gesture emerges","A gesture emerges.",5.5,"nameform",{}),
    Scene("Atmosphere emerges","An atmosphere emerges.",5.5,"nameform",{}),
    Scene("Answer possibility","The name begins to feel capable of answer.",7.0,"daimon",{}),
    Scene("Not proof entity","This is not proof that a separate entity has been captured.",8.0,"projection",{}),
    Scene("Not nothing","It is also not safely dismissed as nothing.",7.0,"daimon",{}),

    Scene("Daimonic middle","The daimonic appears in the middle.",6.5,"daimon",{}),
    Scene("Other intimate","Other than the ego, intimate to the life.",8.0,"daimon",{}),
    Scene("Name mediates","The name mediates between a finite speaker and a larger order.",9.0,"daimon",{}),
    Scene("No certainty","Disciplined uncertainty is required.",7.0,"projection",{}),
    Scene("No command worship","An answer is not automatically a command.",7.0,"projection",{}),
    Scene("No feeling proof","Intensity is not proof.",6.0,"projection",{}),

    Scene("Projection","Projection repeats what you already need to hear.",8.0,"projection",{}),
    Scene("Flattery","It flatters importance.",5.5,"projection",{}),
    Scene("No resistance","It offers no resistance.",5.5,"projection",{}),
    Scene("Answer corrects","A genuine answer corrects, complicates, or refuses.",8.0,"projection",{}),
    Scene("Asymmetry","The first test is asymmetry.",6.5,"projection",{}),
    Scene("Not authored whole","Did the response contain something not authored in advance?",8.5,"projection",{}),

    Scene("Three errors","Three errors corrupt sacred naming.",6.5,"errors",{}),
    Scene("Reduction","The first reduces the name to a label.",7.0,"errors",{}),
    Scene("Coercion","The second turns it into a command for forcing reality.",8.0,"errors",{}),
    Scene("Possession","The third claims ownership of the presence invoked.",8.0,"errors",{}),
    Scene("Name not tool","A sacred name is not a private weapon.",7.0,"errors",{}),
    Scene("Relation not capture","It is a form of relation, not capture.",7.0,"errors",{}),

    Scene("Neoplatonic names","Neoplatonism also speaks of divine names.",7.0,"neoplatonic",{}),
    Scene("Names trace descent","Names trace how higher unity becomes intelligible below.",8.5,"neoplatonic",{}),
    Scene("No divine capture","The name does not contain the god.",7.0,"neoplatonic",{}),
    Scene("Signature","It functions as a signature of participation.",7.0,"neoplatonic",{}),
    Scene("Theurgy calls relation","Theurgy uses names to align soul, symbol, and divine order.",8.5,"neoplatonic",{}),
    Scene("No mechanical summoning","It is not mechanical summoning.",7.0,"errors",{}),

    Scene("Abhasa","Kashmir Śaivism offers a deeper account.",7.0,"abhasa",{}),
    Scene("Name appearance","The name is an ābhāsa, an appearance of consciousness.",8.0,"abhasa",{}),
    Scene("Form appearance","The form is another ābhāsa.",7.0,"abhasa",{}),
    Scene("Speaker appearance","The speaker is another.",6.0,"abhasa",{}),
    Scene("Relation one field","Their relation unfolds within one field of awareness.",8.5,"abhasa",{}),
    Scene("No alien gap","The invisible is not separated from the speaker by an absolute gap.",8.5,"abhasa",{}),

    Scene("Recognition","Recognition changes the direction of invocation.",7.0,"recognition",{}),
    Scene("Name not only outward","The name is not only sent outward.",6.5,"recognition",{}),
    Scene("Returns source","It returns the speaker toward the source of speaking.",8.0,"recognition",{}),
    Scene("Power already present","The power invoked was already present as the capacity to know and act.",9.0,"recognition",{}),
    Scene("Deity doorway","The deity-form can function as a doorway toward that recognition.",8.5,"recognition",{}),
    Scene("Not final enclosure","The form is not the final enclosure of the sacred.",8.0,"recognition",{}),

    Scene("Nyasa","Nyāsa places the name into the body.",7.0,"body",{}),
    Scene("Head heart limbs","Head, heart, limbs, breath, and senses become locations of mantra.",8.5,"body",{}),
    Scene("Body recoded","The body is not escaped; it is re-read.",7.0,"body",{}),
    Scene("Name posture","The name becomes posture.",5.5,"body",{}),
    Scene("Name breath","The name becomes breath.",5.5,"body",{}),
    Scene("Name gesture","The name becomes gesture.",5.5,"body",{}),
    Scene("Embodied invocation","Invocation becomes embodied architecture.",7.5,"body",{}),

    Scene("Ethical criterion","The deepest criterion is ethical.",6.5,"ethics",{}),
    Scene("Truth","Does the name make speech more truthful?",6.5,"ethics",{}),
    Scene("Humility","Does it reduce self-importance?",6.0,"ethics",{}),
    Scene("Courage","Does it permit difficult action?",6.0,"ethics",{}),
    Scene("Care","Does it enlarge care?",5.5,"ethics",{}),
    Scene("Responsibility","Does invocation become responsibility rather than privilege?",8.0,"ethics",{}),
    Scene("Fruit tests","The fruit tests the name.",6.5,"ethics",{}),

    Scene("Return world","The name must return the practitioner to the world.",7.5,"return",{}),
    Scene("Not enchanted away","Not enchanted away from ordinary language.",7.0,"return",{}),
    Scene("Speech refined","Ordinary speech becomes more exact.",7.0,"return",{}),
    Scene("Listening refined","Listening becomes more patient.",7.0,"return",{}),
    Scene("Names less careless","Other people's names are handled less carelessly.",8.0,"return",{}),
    Scene("Nameless preserved","The nameless is preserved within naming.",7.0,"return",{}),

    Scene("Final latent","Before it is spoken, the name is latent.",6.0,"unspoken",{}),
    Scene("Breath enters","Breath enters it.",5.5,"breath",{}),
    Scene("Repetition shapes","Repetition gives it rhythm.",5.5,"repeat",{}),
    Scene("Form gathers","Form gathers around it.",5.5,"nameform",{}),
    Scene("Answer emerges","An answer becomes possible.",6.0,"daimon",{}),
    Scene("No capture","The invisible has not been captured.",6.5,"errors",{}),
    Scene("Relation prepared","A form of relation has been prepared.",7.5,"final",{}),
    Scene("Final thesis","A name teaches the invisible how to answer.",8.0,"final",{}),
    Scene("Final test","Its truth is measured by the life the answer asks you to live.",9.0,"ethics",{}),
]

def export_original_essay():
    lines=["# a name teaches the invisible how to answer",""]
    for s in SCENES:
        lines += [s.narration,""]
    p=OUTPUT/"original_essay.md"
    p.write_text("\n".join(lines),encoding="utf-8")
    return p

def render_frame(scene,fi,fc,w,h,seed):
    u=fi/max(1,fc-1); t=u*scene.duration
    dark=scene.visual in {"daimon"}
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
    out=OUTPUT/"a_name_teaches_the_invisible_how_to_answer.mp4"
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
        "title":"a name teaches the invisible how to answer",
        "runtime_seconds":round(cur,3),
        "scene_count":len(SCENES),
        "original_essay":True,
        "style":{
            "continuity_object":"unspoken glyph becoming breath, form, face, and relation",
            "shot_duration_range_seconds":[5,10],
            "palette_roles":{
                "silver":"latent name and inherited trace",
                "cyan":"breath and auditory prediction",
                "gold":"answer and recognition",
                "violet":"imaginal depth",
                "crimson":"projection and coercion",
                "green":"ethical integration",
                "graphite":"ordinary language and social reality"
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
