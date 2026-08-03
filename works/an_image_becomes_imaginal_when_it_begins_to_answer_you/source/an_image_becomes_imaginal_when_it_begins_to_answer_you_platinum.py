#!/usr/bin/env python3
"""
AN IMAGE BECOMES IMAGINAL WHEN IT BEGINS TO ANSWER YOU
An original Imaginarium visual essay and Platinum-house procedural renderer.

ORIGINAL THESIS
---------------
An image is imaginary when it is only handled by the mind.
It becomes imaginal when encounter reorganizes the one who sees.

This essay joins:
• Corbin's mundus imaginalis and active imagination
• Śaiva ābhāsa, pratibhā, recognition, and the freedom of appearance
• Neoplatonic symbol and theurgy
• predictive perception and active inference
• dreams, ritual icons, daimons, and visionary encounter
• disciplined criteria separating encounter from projection and literalism

DESIGN CONTRACT
---------------
• Every shot lasts 5–10 seconds.
• Every shot visibly performs the narrated operation.
• Clean white atlas field; deep indigo appears only when depth is conceptually required.
• No static slide layouts and no decorative loops.
• Silver = image as surface / representation / memory trace
• Gold = reciprocal presence / answer / recognition
• Cyan = perceptual construction / predictive model / sensory evidence
• Violet = imaginal depth / dream / symbolic intelligence
• Crimson = projection, inflation, possession, or false certainty
• Green = integration, ethical fruit, and returned embodiment
• Graphite = material support, practical distinction, and ordinary world
• Continuity object: a silver-gold doorway moves from flat image to reciprocal world.
• Typography is sparse; terms act as seals, never explanatory slides.
• Every mature frame around u=0.72 should work as a standalone illustration.
• The imaginal must never be represented as merely fuzzy fantasy.
• The essay must not claim scientific proof of metaphysical entities.
• Final criterion: encounter returns the viewer to the world with greater precision and responsibility.

OUTPUT
------
output_imaginal_answer/
  frames/scene_001/*.jpg
  scenes/scene_001.mp4
  an_image_becomes_imaginal_when_it_begins_to_answer_you.mp4
  narration_timeline.json
  original_essay.md
  contact_sheet.jpg

REQUIREMENTS
------------
pip install pillow numpy
ffmpeg must be on PATH.

USAGE
-----
python an_image_becomes_imaginal_when_it_begins_to_answer_you_platinum.py
python an_image_becomes_imaginal_when_it_begins_to_answer_you_platinum.py --preview
python an_image_becomes_imaginal_when_it_begins_to_answer_you_platinum.py --scene 8
python an_image_becomes_imaginal_when_it_begins_to_answer_you_platinum.py --fps 12 --width 1920 --height 1080
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


# =============================================================================
# CONFIGURATION
# =============================================================================

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output_imaginal_answer"
FRAMES = OUTPUT / "frames"
SCENES_DIR = OUTPUT / "scenes"

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 10

WHITE = (248, 247, 243)
PAPER = (242, 239, 232)
INK = (28, 31, 35)
SOFT_INK = (84, 88, 94)
SILVER = (177, 184, 190)
PALE_SILVER = (224, 227, 229)
GOLD = (194, 153, 68)
PALE_GOLD = (235, 218, 175)
CYAN = (55, 153, 181)
PALE_CYAN = (192, 226, 233)
VIOLET = (104, 79, 146)
PALE_VIOLET = (216, 205, 232)
CRIMSON = (158, 52, 66)
PALE_CRIMSON = (230, 192, 198)
GREEN = (70, 139, 98)
PALE_GREEN = (194, 225, 206)
LAPIS = (48, 72, 124)
NIGHT = (17, 23, 39)
VOID = (22, 25, 31)

FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


# =============================================================================
# DRAWING HELPERS
# =============================================================================

def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def mix(a, b, t):
    t = clamp(t)
    return tuple(int(lerp(x, y, t)) for x, y in zip(a, b))


def smoothstep(a: float, b: float, x: float) -> float:
    if a == b:
        return 1.0 if x >= b else 0.0
    q = clamp((x - a) / (b - a))
    return q*q*(3 - 2*q)


def ease(t: float) -> float:
    return .5 - .5*math.cos(math.pi*clamp(t))


def pulse(t: float, hz: float = 1.0, phase: float = 0.0) -> float:
    return .5 + .5*math.sin(math.tau*(hz*t + phase))


def load_font(path: str, size: int):
    for candidate in (path, FONT_SERIF, FONT_SANS):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def rgba_layer(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def background(width: int, height: int, seed: int, dark: bool = False):
    rng = np.random.default_rng(seed)
    base = NIGHT if dark else WHITE
    arr = np.empty((height, width, 3), dtype=np.float32)
    arr[:] = base
    arr += rng.normal(0, 1.05 if not dark else 1.7, (height, width, 1))
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def centered_text(draw, xy, text, font, fill=INK):
    draw.text(xy, text, font=font, fill=fill, anchor="mm")


def seal(im, title, subtitle="", color=INK, dark=False):
    w, h = im.size
    d = ImageDraw.Draw(im)
    centered_text(
        d, (w/2, h*.875), title,
        load_font(FONT_SERIF_BOLD, max(22, int(h*.042))),
        WHITE if dark else color,
    )
    if subtitle:
        centered_text(
            d, (w/2, h*.925), subtitle,
            load_font(FONT_SANS, max(13, int(h*.020))),
            PALE_SILVER if dark else SOFT_INK,
        )


def border(im, dark=False):
    w, h = im.size
    ImageDraw.Draw(im).rounded_rectangle(
        (25, 25, w-25, h-25), radius=17,
        outline=(*(WHITE if dark else INK), 42), width=2
    )


def glow_line(im, points, color, width=4, glow=14, alpha=220):
    if len(points) < 2:
        return
    layer = rgba_layer(im.size)
    d = ImageDraw.Draw(layer)
    d.line(points, fill=(*color, alpha), width=width, joint="curve")
    im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(glow)))
    im.alpha_composite(layer)


def glow_circle(im, cx, cy, radius, color, alpha=180, blur=16):
    layer = rgba_layer(im.size)
    d = ImageDraw.Draw(layer)
    d.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=(*color, alpha))
    im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(im).ellipse(
        (cx-radius*.38, cy-radius*.38, cx+radius*.38, cy+radius*.38),
        fill=(*mix(color, WHITE, .30), 230)
    )


def partial_polyline(points, progress):
    progress = clamp(progress)
    if len(points) < 2:
        return points
    lengths = [math.dist(a, b) for a, b in zip(points[:-1], points[1:])]
    total = sum(lengths)
    target = total*progress
    output = [points[0]]
    walked = 0.0
    for i, length in enumerate(lengths):
        if walked + length <= target:
            output.append(points[i+1])
            walked += length
        else:
            q = 0 if length == 0 else (target-walked)/length
            a, b = points[i], points[i+1]
            output.append((lerp(a[0], b[0], q), lerp(a[1], b[1], q)))
            break
    return output


def arrow(draw, start, end, color=INK, width=3, head=11):
    draw.line((*start, *end), fill=color, width=width)
    angle = math.atan2(end[1]-start[1], end[0]-start[0])
    for delta in (2.55, -2.55):
        p = (
            end[0] + math.cos(angle+delta)*head,
            end[1] + math.sin(angle+delta)*head,
        )
        draw.line((*end, *p), fill=color, width=width)


def organic_blob(draw, cx, cy, rx, ry, color, phase=0, points=100, outline=None):
    pts = []
    for i in range(points):
        a = math.tau*i/points
        wobble = 1 + .06*math.sin(a*3+phase) + .035*math.sin(a*7-phase*.5)
        pts.append((cx+math.cos(a)*rx*wobble, cy+math.sin(a)*ry*wobble))
    draw.polygon(pts, fill=color, outline=outline)
    return pts


def doorway(draw, cx, cy, width, height, color=SILVER, alpha=210, depth=0.0, open_amount=0.0):
    """Continuity object: a doorway that can remain flat or develop depth."""
    left = cx-width/2
    right = cx+width/2
    top = cy-height/2
    bottom = cy+height/2
    draw.rounded_rectangle(
        (left, top, right, bottom),
        radius=max(4, int(width*.08)),
        outline=(*color, alpha),
        width=max(2, int(width*.035))
    )
    if depth > 0:
        dx = width*.30*depth
        dy = height*.10*depth
        draw.line((right, top, right+dx, top+dy), fill=(*GOLD, int(alpha*.8)), width=3)
        draw.line((right, bottom, right+dx, bottom-dy), fill=(*GOLD, int(alpha*.8)), width=3)
        draw.line((right+dx, top+dy, right+dx, bottom-dy), fill=(*GOLD, int(alpha*.8)), width=3)
    if open_amount > 0:
        inner_w = width*.72*open_amount
        inner_h = height*.78*open_amount
        draw.rounded_rectangle(
            (cx-inner_w/2, cy-inner_h/2, cx+inner_w/2, cy+inner_h/2),
            radius=max(3, int(width*.05)),
            fill=(*mix(PALE_VIOLET, NIGHT, .55), int(230*open_amount)),
            outline=(*GOLD, int(190*open_amount)),
            width=3
        )


def eye(draw, cx, cy, rx, ry, color=INK):
    top=[]; bottom=[]
    for i in range(80):
        q=i/79
        x=lerp(cx-rx,cx+rx,q)
        arch=math.sin(q*math.pi)*ry
        top.append((x,cy-arch)); bottom.append((x,cy+arch))
    draw.line(top,fill=(*color,220),width=4)
    draw.line(bottom,fill=(*color,220),width=4)
    draw.ellipse((cx-ry*.52,cy-ry*.52,cx+ry*.52,cy+ry*.52),fill=(*LAPIS,205))
    draw.ellipse((cx-ry*.18,cy-ry*.18,cx+ry*.18,cy+ry*.18),fill=(*VOID,240))


def mirror_surface(draw, x0, y0, x1, y1, alpha=180):
    draw.rounded_rectangle((x0,y0,x1,y1),radius=22,fill=(*PALE_SILVER,110),outline=(*SILVER,alpha),width=4)
    for i in range(7):
        yy=lerp(y0+20,y1-20,i/6)
        draw.line((x0+20,yy,x1-20,yy-10),fill=(*WHITE,80),width=2)


def star_field(draw, w, h, seed=5, alpha=120):
    rng=random.Random(seed)
    for _ in range(90):
        x=rng.uniform(w*.08,w*.92); y=rng.uniform(h*.10,h*.72)
        r=rng.choice([1,1,1,2])
        draw.ellipse((x-r,y-r,x+r,y+r),fill=(*PALE_GOLD,alpha))


# =============================================================================
# SCENE DATA
# =============================================================================

@dataclass
class Scene:
    title: str
    narration: str
    duration: float
    visual: str
    params: dict


# =============================================================================
# VISUAL MODES
# =============================================================================

def visual_flat_image(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.41
    doorway(d,cx,cy,w*.23,h*.44,SILVER,210,depth=0,open_amount=0)
    # image remains handled by viewer's rays
    q=ease(u)
    eye(d,w*.18,h*.41,60,28)
    rays=[[(w*.23,h*.41),(cx-w*.12,h*.24)],
          [(w*.23,h*.41),(cx-w*.12,h*.41)],
          [(w*.23,h*.41),(cx-w*.12,h*.58)]]
    for i,path in enumerate(rays):
        glow_line(im,partial_polyline(path,smoothstep(i*.10,.75,u)),CYAN,3,9,150)
    seal(im,"AN IMAGE IS EASY TO CONTROL","you look; it receives")

def visual_answering_door(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.56,h*.41
    q=ease(u)
    doorway(d,cx,cy,w*.24,h*.45,mix(SILVER,GOLD,q),220,depth=q,open_amount=smoothstep(.25,.95,u))
    eye(d,w*.18,h*.41,60,28)
    # reciprocal ray returns
    glow_line(im,partial_polyline([(w*.24,h*.41),(cx-w*.12,h*.41)],q),CYAN,4,10,170)
    glow_line(im,partial_polyline([(cx-w*.12,h*.33),(w*.24,h*.33)],smoothstep(.45,.95,u)),GOLD,5,13,210)
    seal(im,"THE IMAGINAL BEGINS WITH RECIPROCITY","the image alters the one who sees")

def visual_predictive_loop(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.24,h*.42); right=(w*.76,h*.42); center=(w*.50,h*.42)
    eye(d,*left,55,27)
    doorway(d,*right,w*.20,h*.38,SILVER,200,0,0)
    d.rounded_rectangle((center[0]-90,center[1]-70,center[0]+90,center[1]+70),radius=18,
                        fill=(*PALE_CYAN,215),outline=(*CYAN,180),width=3)
    centered_text(d,center,"MODEL",load_font(FONT_SANS_BOLD,int(h*.021)),CYAN)
    q=ease(u)
    glow_line(im,partial_polyline([left,center,right],q),CYAN,4,11,180)
    glow_line(im,partial_polyline([right,(w*.62,h*.55),center,(w*.36,h*.55),left],smoothstep(.35,.95,u)),GOLD,4,11,170)
    seal(im,"PERCEPTION IS ALREADY AN INTERPRETIVE ACT","the world is encountered through expectation and correction")

def visual_remainder(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    # prediction net
    for j in range(9):
        y=h*(.20+j*.05)
        d.line((w*.14,y,w*.86,y),fill=(*CYAN,65),width=2)
    q=ease(u)
    # one gold anomaly cannot be captured
    path=[]
    for i in range(180):
        s=i/179
        x=lerp(w*.12,w*.88,s)
        y=cy+math.sin(s*math.tau*3+t*.4)*34
        path.append((x,y))
    glow_line(im,partial_polyline(path,q),GOLD,5,14,220)
    doorway(d,w*.76,h*.40,w*.14,h*.30,GOLD,170,q*.8,q*.6)
    seal(im,"SOMETIMES THE WORLD EXCEEDS THE MODEL","a remainder persists and begins to lead")

def visual_symbol_depth(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    doorway(d,cx,cy,w*.18,h*.36,SILVER,200,q,q)
    # symbol sends roots and branches across levels
    roots=[]; branches=[]
    for i in range(7):
        ox=(i-3)*35
        roots.append([(cx,cy+h*.10),(cx+ox*.5,cy+h*.20),(cx+ox,cy+h*.30)])
        branches.append([(cx,cy-h*.10),(cx+ox*.5,cy-h*.20),(cx+ox,cy-h*.30)])
    for i,path in enumerate(roots):
        glow_line(im,partial_polyline(path,smoothstep(i*.05,.80,u)),VIOLET,3,10,150)
    for i,path in enumerate(branches):
        glow_line(im,partial_polyline(path,smoothstep(.15+i*.05,.90,u)),GOLD,3,10,160)
    seal(im,"A SYMBOL IS NOT A LABEL","it binds levels that ordinary description keeps apart")

def visual_barzakh(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.24,h*.42); right=(w*.76,h*.42); cx=w*.5
    organic_blob(d,*left,110,125,(*PALE_CYAN,180),t*.2,outline=(*CYAN,170))
    organic_blob(d,*right,110,125,(*PALE_VIOLET,180),t*.2+1,outline=(*VIOLET,170))
    q=ease(u)
    doorway(d,cx,h*.42,w*.15,h*.42,GOLD,200,q,q)
    # currents cross without collapse
    glow_line(im,partial_polyline([(left[0]+90,left[1]),(cx,h*.32),(right[0]-90,right[1])],q),CYAN,4,12,170)
    glow_line(im,partial_polyline([(right[0]-90,right[1]+35),(cx,h*.54),(left[0]+90,left[1]+35)],q),VIOLET,4,12,170)
    seal(im,"BARZAKH","neither merely subjective nor simply material")

def visual_dream_city(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    star_field(d,w,h,11,90)
    q=ease(u)
    # city grows from reflective floor
    floor=h*.61
    d.line((w*.08,floor,w*.92,floor),fill=(*SILVER,120),width=3)
    for i in range(13):
        x=w*(.12+i*.065)
        height=(40+(i*37)%150)*q
        width=28+(i*11)%34
        d.rectangle((x-width/2,floor-height,x+width/2,floor),fill=(*mix(PALE_VIOLET,GOLD,i/13),120),outline=(*GOLD,100))
        if i%3==0:
            glow_circle(im,x,floor-height*.6,5,GOLD,90,6)
    doorway(d,w*.5,h*.39,w*.13,h*.30,GOLD,180,q,q*.8)
    seal(im,"DREAM DOES NOT PROVE ANOTHER WORLD","but it reveals that experience can organize itself as a world",dark=True)

def visual_icon_presence(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.40
    # icon panel
    d.rounded_rectangle((cx-w*.18,cy-h*.25,cx+w*.18,cy+h*.25),radius=24,
                        fill=(*PALE_GOLD,155),outline=(*GOLD,180),width=5)
    q=ease(u)
    # central face gradually gains gaze
    d.ellipse((cx-62,cy-90,cx+62,cy+34),outline=(*INK,180),width=4)
    eye(d,cx-25,cy-30,18,9,GOLD)
    eye(d,cx+25,cy-30,18,9,GOLD)
    d.arc((cx-24,cy-2,cx+24,cy+28),10,170,fill=(*INK,160),width=3)
    # viewer and reciprocal field
    eye(d,w*.18,h*.42,55,27)
    glow_line(im,partial_polyline([(w*.24,h*.42),(cx-w*.18,h*.42)],q),CYAN,4,10,160)
    glow_line(im,partial_polyline([(cx-w*.18,h*.32),(w*.24,h*.32)],smoothstep(.35,.95,u)),GOLD,5,13,210)
    seal(im,"THE ICON IS NOT ONLY SEEN","ritual trains the image to become a site of relation")

def visual_daimon_middle(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    top=(w*.5,h*.16); mid=(w*.5,h*.42); bottom=(w*.5,h*.68)
    glow_circle(im,*top,24,GOLD,170,13)
    doorway(d,*mid,w*.14,h*.28,VIOLET,190,ease(u),ease(u)*.7)
    eye(d,*bottom,60,28)
    glow_line(im,partial_polyline([top,mid,bottom],ease(u)),GOLD,5,13,200)
    # translator rays
    for i in range(5):
        x=w*(.33+i*.085)
        glow_line(im,partial_polyline([(mid[0],mid[1]),(x,h*.58)],smoothstep(.15+i*.06,.9,u)),mix(VIOLET,GOLD,i/4),2,8,120)
    seal(im,"THE DAIMON IS A MEDIATING FIGURE","not reducible to ego, not safely treated as an external fact")

def visual_projection_test(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.27,h*.42); right=(w*.73,h*.42)
    # projection loop: image only mirrors viewer
    mirror_surface(d,left[0]-105,left[1]-100,left[0]+105,left[1]+100,170)
    eye(d,left[0],left[1],55,27)
    d.arc((left[0]-135,left[1]-130,left[0]+135,left[1]+130),20,340,fill=(*CRIMSON,150),width=5)
    # encounter: asymmetry introduces new demand
    doorway(d,*right,w*.18,h*.38,GOLD,190,ease(u),ease(u)*.8)
    arrow(d,(right[0],right[1]),(right[0]-130,right[1]+95),GREEN,4,12)
    centered_text(d,(right[0]-150,right[1]+112),"CHANGE",load_font(FONT_SANS_BOLD,int(h*.014)),GREEN)
    seal(im,"PROJECTION CONFIRMS YOU · ENCOUNTER CORRECTS YOU","the answer must contain resistance")

def visual_three_failures(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    failures=[("FANTASY",VIOLET),("LITERALISM",CRIMSON),("INFLATION",GOLD)]
    xs=[w*.22,w*.50,w*.78]
    for i,((txt,col),x) in enumerate(zip(failures,xs)):
        q=smoothstep(i*.12,.62+i*.07,u)
        d.ellipse((x-70*q,h*.40-70*q,x+70*q,h*.40+70*q),
                  fill=(*mix(WHITE,col,.18),int(220*q)),outline=(*col,int(180*q)),width=4)
        if q>.66:
            centered_text(d,(x,h*.40),txt,load_font(FONT_SERIF_BOLD,int(h*.019)),col)
        # strike appears
        strike=smoothstep(.48+i*.08,.95,u)
        d.line((x-82,h*.32,x+82,h*.48),fill=(*CRIMSON,int(200*strike)),width=5)
    seal(im,"THREE WAYS TO LOSE THE IMAGINAL","make it unreal · make it crudely factual · make yourself its prophet")

def visual_recognition(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    # world of appearances radiates; viewer is one node
    glow_circle(im,cx,cy,22,GOLD,150,12)
    for i in range(18):
        a=i*math.tau/18
        rr=65+(i%3)*55
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.62
        col=mix(CYAN,VIOLET,i/17)
        d.ellipse((x-8,y-8,x+8,y+8),fill=(*col,180))
        d.line((cx,cy,x,y),fill=(*col,65),width=2)
    q=ease(u)
    d.ellipse((cx-w*.27*q,cy-h*.23*q,cx+w*.27*q,cy+h*.23*q),
              outline=(*GOLD,int(170*q)),width=5)
    seal(im,"PRATYABHIJÑĀ","recognition is not escape from appearances but recognition of their source")

def visual_abhasa(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    q=ease(u)
    for i in range(16):
        a=i*math.tau/16
        rr=lerp(20,210,q)*(0.65+0.35*((i%4)/3))
        x=cx+math.cos(a+t*.08)*rr; y=cy+math.sin(a+t*.08)*rr*.62
        col=mix(GOLD,CYAN,i/15)
        glow_circle(im,x,y,6+4*(i%3),col,100,7)
        glow_line(im,[(cx,cy),(x,y)],col,2,7,80)
    glow_circle(im,cx,cy,24,GOLD,170,13)
    seal(im,"ĀBHĀSA","appearance is not outside consciousness; it is consciousness taking form")

def visual_luminosity_caution(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.27,h*.42); right=(w*.73,h*.42)
    # physical light
    glow_circle(im,left[0],left[1],55,GOLD,180,18)
    centered_text(d,(left[0],h*.66),"PHYSICAL LIGHT",load_font(FONT_SANS_BOLD,int(h*.015)),GOLD)
    # phenomenal disclosure
    doorway(d,*right,w*.18,h*.38,VIOLET,180,ease(u),ease(u))
    centered_text(d,(right[0],h*.66),"LUMINOSITY OF APPEARING",load_font(FONT_SANS_BOLD,int(h*.015)),VIOLET)
    q=smoothstep(.35,.9,u)
    d.line((w*.49,h*.25,w*.51,h*.57),fill=(*CRIMSON,int(210*q)),width=6)
    seal(im,"DO NOT CONFUSE THE SUN WITH DISCLOSURE","one explains illumination; the other names that anything appears at all")

def visual_theurgy(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    # material symbol
    d.polygon([(cx,cy-100),(cx-90,cy+65),(cx+90,cy+65)],outline=(*INK,180))
    q=ease(u)
    # the symbol becomes a circuit between levels
    glow_line(im,partial_polyline([(cx,cy-100),(cx,cy-175)],q),GOLD,5,13,190)
    glow_line(im,partial_polyline([(cx-90,cy+65),(cx-170,cy+130)],q),CYAN,4,11,160)
    glow_line(im,partial_polyline([(cx+90,cy+65),(cx+170,cy+130)],q),VIOLET,4,11,160)
    doorway(d,cx,cy,w*.12,h*.24,GOLD,180,q,q*.7)
    seal(im,"THEURGY TREATS SYMBOLS AS OPERATIONS","material arrangement becomes a disciplined invitation to relation")

def visual_ethics_fruit(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    doorway(d,w*.30,h*.42,w*.18,h*.38,GOLD,190,ease(u),ease(u)*.7)
    # output fruits
    fruits=[("PRECISION",CYAN,w*.56,h*.27),("COURAGE",GOLD,w*.74,h*.35),
            ("HUMILITY",VIOLET,w*.58,h*.55),("CARE",GREEN,w*.78,h*.60)]
    for i,(txt,col,x,y) in enumerate(fruits):
        q=smoothstep(i*.10,.62+i*.06,u)
        glow_line(im,partial_polyline([(w*.39,h*.42),(x,y)],q),col,3,9,150)
        d.ellipse((x-28*q,y-28*q,x+28*q,y+28*q),fill=(*mix(WHITE,col,.18),int(220*q)),outline=(*col,int(180*q)),width=3)
        if q>.68:
            centered_text(d,(x,y),txt,load_font(FONT_SANS_BOLD,int(h*.012)),col)
    seal(im,"THE FRUIT TESTS THE ENCOUNTER","does it make perception clearer and responsibility larger?")

def visual_return_world(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    # ordinary street / world line
    d.line((w*.08,h*.62,w*.92,h*.62),fill=(*INK,130),width=5)
    for i in range(8):
        x=w*(.12+i*.10)
        d.rectangle((x-22,h*.45,x+22,h*.62),fill=(*PALE_SILVER,120),outline=(*SILVER,100))
    doorway(d,w*.22,h*.42,w*.15,h*.34,GOLD,180,ease(u),ease(u)*.7)
    q=ease(u)
    # green path returns into world
    path=[(w*.28,h*.50),(w*.45,h*.56),(w*.66,h*.52),(w*.86,h*.58)]
    glow_line(im,partial_polyline(path,q),GREEN,6,14,210)
    seal(im,"THE IMAGINAL MUST RETURN YOU TO THE ORDINARY","not thinner, but more exact")

def visual_final_answer(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.55,h*.41
    q=ease(u)
    doorway(d,cx,cy,w*.24,h*.46,mix(SILVER,GOLD,q),220,q,q)
    eye(d,w*.18,h*.41,60,28)
    # viewer enters, answer returns, world opens behind
    glow_line(im,partial_polyline([(w*.24,h*.41),(cx-w*.12,h*.41)],q),CYAN,4,10,170)
    glow_line(im,partial_polyline([(cx-w*.12,h*.31),(w*.24,h*.31)],smoothstep(.30,.85,u)),GOLD,5,13,210)
    for i in range(12):
        a=i*math.tau/12
        x=cx+math.cos(a)*lerp(30,185,q)
        y=cy+math.sin(a)*lerp(20,115,q)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*mix(VIOLET,GREEN,i/11),150))
    seal(im,"AN IMAGE BECOMES IMAGINAL WHEN IT BEGINS TO ANSWER YOU",
         "the answer is measured by the transformation it demands", color=GREEN)


VISUALS: dict[str, Callable] = {
    "flat": visual_flat_image,
    "answer": visual_answering_door,
    "predict": visual_predictive_loop,
    "remainder": visual_remainder,
    "symbol": visual_symbol_depth,
    "barzakh": visual_barzakh,
    "dream": visual_dream_city,
    "icon": visual_icon_presence,
    "daimon": visual_daimon_middle,
    "projection": visual_projection_test,
    "failures": visual_three_failures,
    "recognition": visual_recognition,
    "abhasa": visual_abhasa,
    "luminosity": visual_luminosity_caution,
    "theurgy": visual_theurgy,
    "ethics": visual_ethics_fruit,
    "return": visual_return_world,
    "final": visual_final_answer,
}


# =============================================================================
# ORIGINAL ESSAY
# =============================================================================

SCENES: list[Scene] = [
    Scene("A controlled image","An ordinary image is easy to control.",6.0,"flat",{}),
    Scene("Look away","You can look at it, interpret it, dismiss it, and look away.",8.0,"flat",{}),
    Scene("It receives","You remain the active side. The image receives.",7.0,"flat",{}),
    Scene("Answering image","But sometimes an image begins to answer.",6.5,"answer",{}),
    Scene("Unexpected demand","A face in a dream asks something you had not planned to ask yourself.",9.0,"answer",{}),
    Scene("Icon gaze","An icon stops feeling like paint arranged on wood and becomes a gaze.",8.5,"icon",{}),
    Scene("Landscape summons","A landscape ceases to be scenery and begins to summon a decision.",8.5,"answer",{}),
    Scene("Imaginal thesis","An image becomes imaginal when encounter reorganizes the one who sees.",9.0,"final",{}),

    Scene("Not imagination alone","This does not mean every vivid fantasy belongs to another world.",8.0,"failures",{}),
    Scene("Not factual object","It also does not mean the figure is simply a physical object hidden behind perception.",9.0,"barzakh",{}),
    Scene("Third demand","The imaginal requires a more difficult category.",7.0,"barzakh",{}),
    Scene("Real as encounter","Real enough to resist invention.",6.5,"projection",{}),
    Scene("Symbolic as mode","Symbolic enough not to become crude literalism.",7.5,"symbol",{}),
    Scene("Transformative criterion","Transformative enough to alter conduct.",7.5,"ethics",{}),

    Scene("Predictive perception","Modern theories of perception already weaken the idea of a passive eye.",8.5,"predict",{}),
    Scene("Model and signal","The nervous system predicts hidden causes and corrects itself through sensory evidence.",9.0,"predict",{}),
    Scene("Constructed encounter","What you see is neither a copy of the world nor a private invention.",9.0,"predict",{}),
    Scene("Negotiated result","It is a negotiated result between model and signal.",7.0,"predict",{}),
    Scene("No imaginal proof","This does not prove an imaginal realm.",6.5,"predict",{}),
    Scene("Opening","But it opens a useful doorway.",5.5,"answer",{}),
    Scene("Perception interpretation","Perception is already interpretation before deliberate imagination begins.",9.0,"predict",{}),

    Scene("Model failure","Most of the time the model succeeds by making the world familiar.",8.0,"predict",{}),
    Scene("Remainder","Sometimes something refuses full assimilation.",6.5,"remainder",{}),
    Scene("Dream figure surprises","A dream figure answers with a sentence you did not expect.",8.0,"dream",{}),
    Scene("Symbol returns","A symbol returns across months with new implications.",7.0,"symbol",{}),
    Scene("Place exceeds description","A place produces a demand no description had prepared.",8.5,"remainder",{}),
    Scene("Remainder leads","A remainder persists and begins to lead.",6.5,"remainder",{}),

    Scene("Corbin objection","Henry Corbin objected to confusing the imaginal with the imaginary.",8.0,"barzakh",{}),
    Scene("Imaginary meaning","The imaginary means unreal fabrication in ordinary language.",7.0,"flat",{}),
    Scene("Imaginal meaning","The imaginal names a mode of disclosure with its own forms, distances, and events.",9.5,"barzakh",{}),
    Scene("Intermediate world","It is intermediate between sensory matter and abstract intellect.",8.0,"barzakh",{}),
    Scene("Barzakh","A barzakh separates and joins at once.",6.5,"barzakh",{}),
    Scene("Door not wall","It is a door that preserves difference rather than a wall that prevents relation.",9.0,"barzakh",{}),

    Scene("No geography","The imaginal world is not another planet located behind the moon.",8.0,"dream",{}),
    Scene("No private fantasy","Nor is it merely private fantasy sealed inside the skull.",8.0,"flat",{}),
    Scene("World character","It has world-character: orientation, depth, encounter, memory, and consequence.",9.0,"dream",{}),
    Scene("Dream city","A dream city may be impossible in physical space and still possess streets, thresholds, and laws.",9.5,"dream",{}),
    Scene("Worlding capacity","Consciousness does not merely display images; it can world them.",8.5,"dream",{}),

    Scene("Symbol depth","A symbol belongs to this intermediate logic.",7.0,"symbol",{}),
    Scene("Not code","It is not a code with one hidden translation.",6.5,"symbol",{}),
    Scene("More meaning","It carries more meaning than a proposition can exhaust.",8.0,"symbol",{}),
    Scene("Vertical binding","It binds bodily feeling, memory, cosmology, ethical demand, and metaphysical intuition.",10.0,"symbol",{}),
    Scene("Living symbol","A living symbol changes as the knower changes without becoming arbitrary.",9.0,"symbol",{}),
    Scene("Depth not vagueness","Its depth is not vagueness. It is structured surplus.",8.0,"symbol",{}),

    Scene("Ritual icon","Ritual traditions cultivate this surplus deliberately.",7.0,"icon",{}),
    Scene("Material support","An icon is wood, pigment, geometry, name, gesture, and inherited attention.",9.0,"icon",{}),
    Scene("Not art appreciation","The practitioner does not merely appreciate it as art.",7.0,"icon",{}),
    Scene("Address","The image is addressed.",5.5,"icon",{}),
    Scene("Gaze returned","Over time, the gaze may feel returned.",6.5,"icon",{}),
    Scene("Relation site","The icon becomes a site where relation is enacted.",8.0,"icon",{}),
    Scene("Discipline matters","The discipline matters because spontaneous intensity alone cannot distinguish encounter from projection.",10.0,"projection",{}),

    Scene("Theurgy","Neoplatonic theurgy treats symbols as operations rather than illustrations.",8.0,"theurgy",{}),
    Scene("Material arrangement","Stone, sound, number, fragrance, and gesture are arranged as a circuit.",9.0,"theurgy",{}),
    Scene("Invitation","The ritual does not manufacture a god like a machine manufactures an object.",9.0,"theurgy",{}),
    Scene("Correspondence","It prepares correspondences through which relation may become possible.",9.0,"theurgy",{}),
    Scene("Symbol acts","The symbol acts because it joins levels of reality in one disciplined form.",9.0,"theurgy",{}),

    Scene("Daimon","The daimon appears at the dangerous center of this problem.",7.0,"daimon",{}),
    Scene("Other and intimate","It is described as other than the ego and intimately bound to the person.",8.5,"daimon",{}),
    Scene("Messenger","It mediates between a larger order and a finite life.",8.0,"daimon",{}),
    Scene("Psychological reduction","Reduce it entirely to psychology and something in the encounter may be lost.",9.0,"daimon",{}),
    Scene("External certainty","Treat it as an unquestionable external being and discernment may be lost.",9.5,"daimon",{}),
    Scene("Middle discipline","The imaginal asks for disciplined uncertainty in the middle.",8.5,"daimon",{}),

    Scene("Projection test","Projection repeats what you already need to believe.",8.0,"projection",{}),
    Scene("Flattery","It flatters your importance.",6.0,"projection",{}),
    Scene("No resistance","It contains no genuine resistance.",6.0,"projection",{}),
    Scene("Encounter correction","Encounter corrects, complicates, or refuses you.",8.0,"projection",{}),
    Scene("New obligation","It creates a new obligation rather than a new decoration for identity.",9.0,"ethics",{}),
    Scene("Asymmetry","The first test of an answer is asymmetry.",7.0,"projection",{}),
    Scene("Not authored whole","Did the response contain something you did not author in advance?",9.0,"projection",{}),

    Scene("Three failures","Three failures surround the imaginal.",6.5,"failures",{}),
    Scene("Fantasy failure","Fantasy makes the image unreal and therefore harmless.",7.0,"failures",{}),
    Scene("Literalism failure","Literalism makes the image a crude object and therefore unquestionable.",8.0,"failures",{}),
    Scene("Inflation failure","Inflation makes the experiencer a prophet whose feeling becomes proof.",8.0,"failures",{}),
    Scene("Imaginal discipline","Imaginal discipline rejects all three.",6.5,"failures",{}),
    Scene("Neither nothing nor fact","The figure is neither nothing nor a simple fact.",8.0,"barzakh",{}),
    Scene("Relation event","It is an event of relation requiring interpretation.",8.0,"barzakh",{}),

    Scene("Śaiva appearance","Kashmir Śaivism begins from another side.",7.0,"abhasa",{}),
    Scene("Abhasa","Every experienced form is an ābhāsa, an appearance of consciousness.",8.5,"abhasa",{}),
    Scene("Not external object","The object is not outside consciousness as an alien substance.",8.0,"abhasa",{}),
    Scene("Not private thought","Nor is it merely a private thought trapped in one mind.",8.0,"abhasa",{}),
    Scene("Consciousness forms","Consciousness appears as object, subject, relation, memory, and recognition.",9.5,"abhasa",{}),
    Scene("Freedom of appearing","Its freedom is precisely the capacity to appear as more than one perspective.",9.0,"abhasa",{}),

    Scene("Imaginal Shaiva bridge","This creates a powerful but careful bridge to the imaginal.",8.0,"recognition",{}),
    Scene("Appearance real mode","An appearance can be real as a mode of consciousness without being a separate physical thing.",9.5,"recognition",{}),
    Scene("Not hallucination dismissal","It need not be dismissed as hallucination merely because it lacks public material extension.",9.0,"recognition",{}),
    Scene("Not automatic truth","But intensity does not make every appearance truthful.",8.0,"failures",{}),
    Scene("Recognition needed","The question becomes: what does this appearance reveal about the structure of awareness?",9.0,"recognition",{}),

    Scene("Pratyabhijna","Pratyabhijñā means recognition.",5.5,"recognition",{}),
    Scene("Not new object","Recognition does not acquire a new metaphysical object.",7.0,"recognition",{}),
    Scene("Source recognition","It recognizes the source already present in every act of knowing.",8.0,"recognition",{}),
    Scene("Imaginal figure role","An imaginal figure can function as a mirror angled toward that recognition.",8.5,"recognition",{}),
    Scene("Not final source","The figure is not necessarily the final source.",7.0,"recognition",{}),
    Scene("Doorway role","It may be a doorway through which awareness encounters its own depth in differentiated form.",10.0,"answer",{}),

    Scene("Luminosity confusion","The language of luminosity easily creates confusion.",7.0,"luminosity",{}),
    Scene("Sun explains light","Physical light explains why surfaces become visible to eyes.",8.0,"luminosity",{}),
    Scene("Not appearing itself","It does not explain the fact that any visual event appears in experience.",8.5,"luminosity",{}),
    Scene("Disclosure luminosity","Phenomenological luminosity names disclosure, not photons.",8.0,"luminosity",{}),
    Scene("Two questions","One question concerns illumination in the world. The other concerns the appearing of a world.",9.5,"luminosity",{}),
    Scene("Do not collapse","Do not collapse them.",5.5,"luminosity",{}),

    Scene("Dream evidence","Dreams provide a laboratory for world-making.",7.0,"dream",{}),
    Scene("No sensory city","A dream city may arise without current sensory input.",7.0,"dream",{}),
    Scene("Encounter still real","You can become lost, addressed, ashamed, instructed, or transformed within it.",9.5,"dream",{}),
    Scene("No ontological proof","This does not prove that every dream occurs in an independent realm.",8.0,"dream",{}),
    Scene("Capacity shown","It proves that experience has the capacity to produce structured worlds and reciprocal figures.",9.0,"dream",{}),
    Scene("Imaginal question","The imaginal question begins where that capacity acquires resistance, continuity, and consequence.",10.0,"answer",{}),

    Scene("Ethical criterion","The deepest criterion is ethical rather than spectacular.",7.0,"ethics",{}),
    Scene("Vision not enough","A vision is not validated by brightness, terror, beauty, or emotional force.",9.0,"ethics",{}),
    Scene("Fruit","It is tested by its fruit.",5.5,"ethics",{}),
    Scene("Precision","Does it make perception more precise?",6.5,"ethics",{}),
    Scene("Humility","Does it reduce self-importance rather than enlarge it?",7.0,"ethics",{}),
    Scene("Courage","Does it permit difficult action?",6.5,"ethics",{}),
    Scene("Care","Does it increase care for bodies, promises, places, and other people?",8.0,"ethics",{}),
    Scene("Return","An encounter that cannot return to the ordinary world has not completed its circuit.",9.0,"return",{}),

    Scene("Imaginal not escape","The imaginal is not an escape hatch from material life.",8.0,"return",{}),
    Scene("Ordinary deepened","It is a way the ordinary acquires depth.",7.0,"return",{}),
    Scene("Tree more tree","The tree remains a tree and becomes more than a category.",7.5,"return",{}),
    Scene("Person irreducible","A person remains embodied and becomes irreducible to your model of them.",8.5,"return",{}),
    Scene("Place memory","A place remains geographical and begins to carry memory and demand.",8.5,"return",{}),
    Scene("Matter not abolished","Matter is not abolished by meaning.",7.0,"return",{}),
    Scene("Meaning enters matter","Meaning enters matter as relation.",7.0,"return",{}),

    Scene("Disciplined practice","A practical imaginal discipline therefore begins modestly.",8.0,"projection",{}),
    Scene("Attend image","Attend to an image without forcing interpretation.",7.0,"flat",{}),
    Scene("Describe exactly","Describe exactly what appears before explaining it.",7.5,"flat",{}),
    Scene("Notice response","Notice bodily response, memory, resistance, and surprise.",8.0,"predict",{}),
    Scene("Ask one question","Ask one question rather than demanding revelation.",7.0,"answer",{}),
    Scene("Record answer","Record the answer without treating it as command or proof.",8.0,"projection",{}),
    Scene("Test fruit","Test it against conduct, evidence, time, and trusted others.",8.5,"ethics",{}),
    Scene("Keep doorway","Keep the doorway open without removing the doorframe.",8.0,"barzakh",{}),

    Scene("Final return","An image is imaginary when it remains entirely available to your control.",9.0,"flat",{}),
    Scene("Begins answering","It becomes imaginal when it begins to answer.",7.0,"answer",{}),
    Scene("Answer resistance","The answer may arrive as resistance, correction, obligation, or recognition.",9.0,"projection",{}),
    Scene("No proof","It is not proof of another world.",6.0,"failures",{}),
    Scene("Not mere fantasy","It is not safely dismissed as fantasy.",6.5,"barzakh",{}),
    Scene("Event between","It is an event between image and perceiver in which both acquire new depth.",9.0,"final",{}),
    Scene("Transformation demand","The answer is measured by the transformation it demands.",8.0,"ethics",{}),
    Scene("Return exact","And by whether you return to this world more exact than you left it.",9.0,"return",{}),
]


# =============================================================================
# EXPORT ESSAY
# =============================================================================

def export_original_essay() -> Path:
    paragraphs = ["# an image becomes imaginal when it begins to answer you", ""]
    for scene in SCENES:
        paragraphs.append(scene.narration)
        paragraphs.append("")
    path = OUTPUT / "original_essay.md"
    path.write_text("\n".join(paragraphs), encoding="utf-8")
    return path


# =============================================================================
# RENDER PIPELINE
# =============================================================================

def render_frame(scene: Scene, frame_index: int, frame_count: int,
                 width: int, height: int, seed: int) -> Image.Image:
    u = frame_index / max(1, frame_count-1)
    t = u * scene.duration
    dark = scene.visual in {"dream"}
    im = background(width, height, seed, dark)
    VISUALS[scene.visual](im, u, t, scene.params)
    border(im, dark)
    return im.convert("RGB")


def require_ffmpeg() -> str:
    executable = shutil.which("ffmpeg")
    if not executable:
        raise RuntimeError("ffmpeg is required but was not found on PATH")
    return executable


def encode_scene(scene_index: int, fps: int) -> Path:
    frame_dir = FRAMES / f"scene_{scene_index:03d}"
    output_path = SCENES_DIR / f"scene_{scene_index:03d}.mp4"
    subprocess.run([
        require_ffmpeg(), "-y",
        "-framerate", str(fps),
        "-i", str(frame_dir / "%05d.jpg"),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_path),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path


def render_scene(scene_index: int, scene: Scene, fps: int,
                 width: int, height: int, preview: bool) -> Path:
    frame_dir = FRAMES / f"scene_{scene_index:03d}"
    frame_dir.mkdir(parents=True, exist_ok=True)
    SCENES_DIR.mkdir(parents=True, exist_ok=True)
    frame_count = max(2, round(scene.duration*fps))

    if preview:
        for out_index, frame_index in enumerate(
            [0, int(frame_count*.35), int(frame_count*.72), frame_count-1]
        ):
            render_frame(
                scene, frame_index, frame_count, width, height,
                scene_index*1000+frame_index
            ).save(frame_dir / f"preview_{out_index:02d}.jpg", quality=95)
        return frame_dir

    for frame_index in range(frame_count):
        path = frame_dir / f"{frame_index:05d}.jpg"
        if path.exists():
            continue
        render_frame(
            scene, frame_index, frame_count, width, height,
            scene_index*1000+frame_index
        ).save(path, quality=95, subsampling=0)

    return encode_scene(scene_index, fps)


def concatenate(scene_paths: list[Path]) -> Path:
    concat_file = OUTPUT / "concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{path.resolve()}'" for path in scene_paths),
        encoding="utf-8",
    )
    output_path = OUTPUT / "an_image_becomes_imaginal_when_it_begins_to_answer_you.mp4"
    subprocess.run([
        require_ffmpeg(), "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        "-movflags", "+faststart",
        str(output_path),
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path


def export_timeline() -> Path:
    cursor = 0.0
    payload = []
    for index, scene in enumerate(SCENES, start=1):
        record = asdict(scene)
        record["scene_id"] = f"scene_{index:03d}"
        record["start_seconds"] = round(cursor, 3)
        cursor += scene.duration
        record["end_seconds"] = round(cursor, 3)
        payload.append(record)

    path = OUTPUT / "narration_timeline.json"
    path.write_text(json.dumps({
        "title": "an image becomes imaginal when it begins to answer you",
        "runtime_seconds": round(cursor, 3),
        "scene_count": len(SCENES),
        "original_essay": True,
        "style": {
            "continuity_object": "silver-gold doorway developing reciprocal depth",
            "shot_duration_range_seconds": [5, 10],
            "palette_roles": {
                "silver": "flat image, representation, memory trace",
                "gold": "reciprocity, answer, recognition",
                "cyan": "predictive model and sensory construction",
                "violet": "imaginal depth, dream, symbolic intelligence",
                "crimson": "projection, literalism, inflation",
                "green": "integration and ethical fruit",
                "graphite": "material support and ordinary world",
            },
        },
        "scenes": payload,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def make_contact_sheet(width: int, height: int) -> Path:
    thumb_w = 320
    thumb_h = int(thumb_w*height/width)
    thumbs = []
    for index, scene in enumerate(SCENES, start=1):
        frame_count = max(2, round(scene.duration*DEFAULT_FPS))
        im = render_frame(
            scene, int(frame_count*.72), frame_count,
            width, height, index*1000+72
        )
        im.thumbnail((thumb_w, thumb_h))
        thumbs.append((index, scene.title, im.copy()))

    columns = 4
    rows = math.ceil(len(thumbs)/columns)
    cell_h = thumb_h + 52
    sheet = Image.new("RGB", (columns*thumb_w, rows*cell_h), WHITE)
    d = ImageDraw.Draw(sheet)
    label_font = load_font(FONT_SANS_BOLD, 15)

    for index, title, im in thumbs:
        slot = index-1
        x = (slot % columns)*thumb_w
        y = (slot // columns)*cell_h
        sheet.paste(im, (x, y))
        d.text((x+10, y+thumb_h+8), f"{index:03d}  {title}",
               font=label_font, fill=INK)

    path = OUTPUT / "contact_sheet.jpg"
    sheet.save(path, quality=94)
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS)
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--scene", type=int, default=None)
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--no-contact-sheet", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    SCENES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Essay: {export_original_essay()}")
    print(f"Timeline: {export_timeline()}")
    print(f"Scenes: {len(SCENES)}")
    print(f"Runtime: {sum(scene.duration for scene in SCENES)/60:.2f} minutes")

    if args.scene is not None:
        if not 1 <= args.scene <= len(SCENES):
            raise ValueError(f"--scene must be between 1 and {len(SCENES)}")
        print(render_scene(
            args.scene, SCENES[args.scene-1],
            args.fps, args.width, args.height, args.preview
        ))
        return

    rendered = []
    for index, scene in enumerate(SCENES, start=1):
        print(f"[{index:03d}/{len(SCENES):03d}] {scene.title} ({scene.duration:.1f}s)")
        result = render_scene(
            index, scene, args.fps,
            args.width, args.height, args.preview
        )
        if not args.preview:
            rendered.append(result)

    if not args.no_contact_sheet:
        print(f"Contact sheet: {make_contact_sheet(args.width, args.height)}")
    if not args.preview:
        print(f"Final video: {concatenate(rendered)}")


if __name__ == "__main__":
    main()
