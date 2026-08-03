#!/usr/bin/env python3
"""
THE BODY KNOWS THE SHAPE IT WANTS
A Michael Levin–themed Platinum-house procedural visual essay.

SCIENTIFIC GROUNDING
--------------------
The film is inspired by experimental and conceptual work on:

• anatomical homeostasis;
• endogenous bioelectric signaling;
• membrane-potential patterns across non-neural tissues;
• ion channels and gap junctions;
• planarian anterior–posterior polarity;
• persistent and editable regenerative target morphologies;
• collective cellular decision-making;
• top-down control of growth and form;
• competency architectures across biological scales.

The phrase "the body knows" is used operationally:
a cell collective behaves as though it represents a target state, detects
deviation, recruits lower-level actions, and stops when the target is reached.
The film does not claim that all tissue has human-like conscious awareness.

FILM THESIS
-----------
Genes provide components and constraints.
Cells provide local competencies.
Bioelectric networks integrate those competencies into larger-scale goals.
Regeneration reveals a remarkable fact: damaged tissue does not merely grow.
It detects what is missing, acts toward a target morphology, and stops when a
coherent anatomy has been restored.

The philosophical coda compares this biological organization with Kashmir
Śaivism without claiming that Levin's experiments prove Tantric metaphysics.

HOUSE RULES
-----------
• Every shot lasts 5–10 seconds.
• Every shot shows before → operation → after.
• Clean ivory scientific/gallery field.
• No static slide layouts.
• Sparse labels only.
• Mature frame near u=0.72.
• Continuity object: a cyan voltage contour that becomes a gold target outline.

PALETTE ROLES
-------------
IVORY    open morphospace
CYAN     bioelectric communication / tissue state
GOLD     target morphology / successful correction
GREEN    viable growth / repair
CRIMSON  wound / pattern error / cancer-like defection
VIOLET   alternative stable morphology / cryptic memory
INK      visible anatomy / material structure

OUTPUT
------
output_body_knows_shape/
  frames/scene_001/*.jpg
  scenes/scene_001.mp4
  body_knows_shape.mp4
  narration_timeline.json
  contact_sheet.jpg

USAGE
-----
python body_knows_shape_platinum.py
python body_knows_shape_platinum.py --preview
python body_knows_shape_platinum.py --scene 12
python body_knows_shape_platinum.py --fps 12 --width 1920 --height 1080
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


# =============================================================================
# CONFIG
# =============================================================================

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output_body_knows_shape"
FRAMES = OUTPUT / "frames"
SCENES_DIR = OUTPUT / "scenes"

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 10

IVORY = (249, 247, 241)
WHITE = (255, 254, 250)
INK = (29, 33, 39)
SOFT_INK = (86, 91, 98)
SILVER = (180, 187, 194)
PALE_SILVER = (226, 229, 232)
CYAN = (57, 156, 180)
DEEP_CYAN = (34, 101, 129)
PALE_CYAN = (196, 227, 233)
GOLD = (194, 156, 72)
PALE_GOLD = (236, 219, 175)
GREEN = (70, 139, 99)
PALE_GREEN = (198, 225, 208)
CRIMSON = (162, 58, 69)
PALE_CRIMSON = (231, 198, 202)
VIOLET = (109, 83, 153)
PALE_VIOLET = (220, 211, 237)

FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


# =============================================================================
# HELPERS
# =============================================================================

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def lerp(a, b, t):
    return a + (b - a) * clamp(t)


def mix(a, b, t):
    return tuple(int(lerp(x, y, t)) for x, y in zip(a, b))


def smoothstep(a, b, x):
    if a == b:
        return 1.0 if x >= b else 0.0
    q = clamp((x-a)/(b-a))
    return q*q*(3-2*q)


def ease(t):
    t = clamp(t)
    return .5-.5*math.cos(math.pi*t)


def pulse(t, speed=1.0, phase=0.0):
    return .5+.5*math.sin(math.tau*(speed*t+phase))


def font(path, size):
    for candidate in (path, FONT_SERIF, FONT_SANS):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def layer(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def field(w, h, seed):
    rng = np.random.default_rng(seed)
    arr = np.empty((h, w, 3), dtype=np.float32)
    arr[:] = IVORY
    arr += rng.normal(0, .9, (h, w, 1))
    yy, xx = np.mgrid[0:h, 0:w]
    halo = np.exp(
        -(((xx-w*.5)/(w*.37))**2 + ((yy-h*.40)/(h*.31))**2)*2.0
    )
    arr[...,1] += halo*3.4
    arr[...,2] += halo*5.0
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8),"RGB").convert("RGBA")


def centered(d, xy, text, fnt, fill=INK):
    d.text(xy, text, font=fnt, fill=fill, anchor="mm")


def seal(im, title, subtitle="", color=INK):
    w,h = im.size
    d = ImageDraw.Draw(im)
    centered(d,(w/2,h*.875),title,font(FONT_SERIF_BOLD,max(22,int(h*.04))),color)
    if subtitle:
        centered(d,(w/2,h*.923),subtitle,font(FONT_SANS,max(13,int(h*.019))),SOFT_INK)


def border(im):
    w,h = im.size
    d = ImageDraw.Draw(im)
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
    if len(pts)<2:
        return
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


def partial(pts, amount):
    if not pts:
        return []
    amount=clamp(amount)
    if amount>=1:
        return pts
    target=amount*(len(pts)-1)
    idx=int(target)
    frac=target-idx
    out=list(pts[:idx+1])
    if idx+1<len(pts):
        a,b=pts[idx],pts[idx+1]
        out.append((lerp(a[0],b[0],frac),lerp(a[1],b[1],frac)))
    return out


def arrow(d,a,b,color=INK,width=3,head=10):
    d.line((*a,*b),fill=color,width=width)
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for s in (-1,1):
        p=(b[0]-math.cos(ang+s*.52)*head,b[1]-math.sin(ang+s*.52)*head)
        d.line((*b,*p),fill=color,width=width)


def draw_cell(d,cx,cy,r,color=CYAN,alpha=210):
    d.ellipse((cx-r,cy-r,cx+r,cy+r),
              fill=(*mix(WHITE,color,.12),alpha//2),
              outline=(*color,alpha),width=3)


def planarian_polygon(cx,cy,length,width,phase=0.0):
    top=[]
    bottom=[]
    for i in range(100):
        q=i/99
        x=cx-length/2+q*length
        envelope=math.sin(math.pi*q)**.60
        local=width*(.20+.80*envelope)
        local*=1+.025*math.sin(q*math.tau*3+phase)
        top.append((x,cy-local/2))
        bottom.append((x,cy+local/2))
    return top+list(reversed(bottom))


def draw_planarian(d,cx,cy,length,width,heads=1,
                   body=PALE_CYAN,outline=DEEP_CYAN,alpha=235,phase=0.0):
    poly=planarian_polygon(cx,cy,length,width,phase)
    d.polygon(poly,fill=(*body,alpha),outline=(*outline,alpha),width=3)
    # tail
    if heads==1:
        d.polygon([(cx+length/2-width*.08,cy-width*.12),
                   (cx+length/2+width*.24,cy),
                   (cx+length/2-width*.08,cy+width*.12)],
                  fill=(*body,alpha),outline=(*outline,alpha))
    head_positions=[cx-length/2+width*.18]
    if heads>=2:
        head_positions.append(cx+length/2-width*.18)
    for hx in head_positions:
        direction=-1 if hx<cx else 1
        d.polygon([(hx,cy-width*.18),
                   (hx-direction*width*.18,cy-width*.42),
                   (hx+direction*width*.05,cy-width*.28)],
                  fill=(*body,alpha),outline=(*outline,alpha))
        d.polygon([(hx,cy+width*.18),
                   (hx-direction*width*.18,cy+width*.42),
                   (hx+direction*width*.05,cy+width*.28)],
                  fill=(*body,alpha),outline=(*outline,alpha))
        ex=hx+direction*width*.03
        for oy in (-width*.10,width*.10):
            d.ellipse((ex-4,cy+oy-4,ex+4,cy+oy+4),fill=(*INK,alpha))


def voltage_path(cx,cy,length,amp,t,phase=0.0,samples=180):
    pts=[]
    for i in range(samples):
        q=i/(samples-1)
        x=cx-length/2+q*length
        env=math.sin(math.pi*q)**.55
        y=cy+math.sin(q*math.tau*4+t*.65+phase)*amp*env
        pts.append((x,y))
    return pts


# =============================================================================
# VISUALS
# =============================================================================

def vis_fragment_question(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.41
    q=ease(u)
    draw_planarian(d,cx,cy,w*.62,h*.15,1,phase=t*.18)
    cut=smoothstep(.15,.35,u)
    for x in (w*.42,w*.58):
        d.line((x,cy-h*.12,x,cy+h*.12),fill=(*CRIMSON,int(220*cut)),width=5)
    if q>.45:
        centered(d,(cx,h*.19),"WHAT IS MISSING?",font(FONT_SERIF_BOLD,28),GOLD)
    seal(im,"THE WOUND DOES NOT SPECIFY THE ANSWER",
         "a fragment must infer which anatomy should exist")


def vis_fragments_regrow(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cy=h*.41
    q=ease(u)
    pieces=[(w*.24,1),(w*.50,1),(w*.76,1)]
    for i,(cx,heads) in enumerate(pieces):
        local=clamp(q*3-i*.35)
        draw_planarian(
            d,cx,cy,
            lerp(w*.08,w*.20,local),
            lerp(h*.07,h*.13,local),
            heads,
            body=mix(PALE_CYAN,PALE_GREEN,local*.55),
            outline=GREEN,
            phase=t*.18
        )
        if local<.78:
            d.line((cx,cy-h*.08,cx,cy+h*.08),fill=(*CRIMSON,150),width=3)
    seal(im,"EACH FRAGMENT REBUILDS THE WHOLE RELATION",
         "growth stops when a coherent target morphology is reached")


def vis_blueprint_vs_goal(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.30,h*.40)
    right=(w*.70,h*.40)
    q=ease(u)
    # literal blueprint
    d.rounded_rectangle((left[0]-150,left[1]-120,left[0]+150,left[1]+120),
                        radius=18,fill=(*PALE_SILVER,160),outline=(*INK,160),width=3)
    draw_planarian(d,left[0],left[1],220,80,1,body=WHITE,outline=INK,alpha=170)
    centered(d,(left[0],h*.67),"STATIC PLAN",font(FONT_SANS_BOLD,16),INK)
    # target attractor
    for rr in range(35,145,24):
        d.ellipse((right[0]-rr,right[1]-rr*.58,right[0]+rr,right[1]+rr*.58),
                  outline=(*GOLD,int(80*q*(1-rr/170))),width=3)
    draw_planarian(d,right[0],right[1],220,80,1,body=PALE_GOLD,outline=GOLD,alpha=int(220*q))
    centered(d,(right[0],h*.67),"CORRECTABLE GOAL",font(FONT_SANS_BOLD,16),GOLD)
    seal(im,"TARGET MORPHOLOGY IS NOT A TINY PICTURE",
         "it is a control state toward which many routes can converge")


def vis_cell_collective(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    rng=random.Random(17)
    cx,cy=w*.50,h*.40
    q=ease(u)
    cells=[]
    for i in range(105):
        a=rng.uniform(0,math.tau)
        rr=(rng.random()**.6)*min(w,h)*.25
        cells.append((cx+math.cos(a)*rr*1.65,cy+math.sin(a)*rr))
    for i,(x,y) in enumerate(cells):
        draw_cell(d,x,y,7,CYAN,160)
        if i>0 and i%3:
            px,py=cells[i-1]
            d.line((px,py,x,y),fill=(*CYAN,60),width=1)
    if q>.35:
        draw_planarian(d,cx,cy,w*.42,h*.13,1,body=WHITE,outline=GOLD,
                       alpha=int(190*(q-.35)/.65),phase=t*.14)
    seal(im,"LOCAL CELLS COORDINATE TOWARD A GLOBAL OUTCOME",
         "no single cell contains or inhabits the whole body")


def vis_gap_junctions(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cols,rows=10,5
    nodes=[]
    rng=random.Random(28)
    for j in range(rows):
        for i in range(cols):
            x=w*.15+i*w*.70/(cols-1)+rng.uniform(-8,8)
            y=h*.22+j*h*.39/(rows-1)+rng.uniform(-7,7)
            nodes.append((x,y))
    q=ease(u)
    for j in range(rows):
        for i in range(cols):
            idx=j*cols+i
            if i<cols-1:
                x1,y1=nodes[idx]; x2,y2=nodes[idx+1]
                d.line((x1,y1,x2,y2),fill=(*CYAN,110),width=3)
            if j<rows-1:
                x1,y1=nodes[idx]; x2,y2=nodes[idx+cols]
                d.line((x1,y1,x2,y2),fill=(*CYAN,80),width=2)
    for x,y in nodes:
        draw_cell(d,x,y,10,CYAN,190)
    wave=lerp(w*.12,w*.88,q)
    gl=layer(im.size)
    gd=ImageDraw.Draw(gl)
    gd.rectangle((wave-28,h*.16,wave+28,h*.68),fill=(*GOLD,45))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(18)))
    seal(im,"GAP JUNCTIONS CREATE A PHYSIOLOGICAL NETWORK",
         "electrical states can propagate far beyond one cell")


def vis_voltage_map(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.41
    draw_planarian(d,cx,cy,w*.62,h*.15,1,phase=t*.17)
    q=ease(u)
    path=voltage_path(cx,cy,w*.50,h*.045,t)
    glow_line(im,partial(path,q),CYAN,5,210,14)
    # polarity ends
    glow_circle(im,cx-w*.23,cy,13,GOLD,180,10)
    glow_circle(im,cx+w*.23,cy,13,VIOLET,160,10)
    seal(im,"ANATOMY HAS AN ELECTRICAL TOPOLOGY",
         "resting-potential patterns carry instructive positional information")


def vis_edit_voltage(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.41
    draw_planarian(d,cx,cy,w*.62,h*.15,1,phase=t*.15)
    normal=voltage_path(cx,cy,w*.50,h*.035,t)
    altered=voltage_path(cx,cy,w*.50,h*.060,t,1.4)
    switch=smoothstep(.22,.74,u)
    glow_line(im,normal,CYAN,5,int(200*(1-switch)),13)
    glow_line(im,partial(altered,switch),VIOLET,5,int(110+100*switch),14)
    gl=layer(im.size)
    ImageDraw.Draw(gl).rectangle((w*.43,h*.22,w*.57,h*.61),
                                 fill=(*CRIMSON,int(85*(1-smoothstep(.55,.78,u)))))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(20)))
    seal(im,"A BRIEF PERTURBATION CAN REWRITE THE PATTERN STATE",
         "the intervention ends; the altered anatomical memory can persist",VIOLET)


def vis_two_headed(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cy=h*.41
    cut=smoothstep(.08,.28,u)
    grow=smoothstep(.30,.96,u)
    if grow<.72:
        draw_planarian(d,w*.50,cy,w*.60,h*.15,1,alpha=int(230*(1-grow*.45)),phase=t*.15)
        d.line((w*.50,cy-h*.12,w*.50,cy+h*.12),fill=(*CRIMSON,int(220*cut)),width=5)
    if grow>.15:
        draw_planarian(d,w*.50,cy,lerp(w*.18,w*.58,grow),
                       lerp(h*.09,h*.16,grow),2,
                       body=PALE_VIOLET,outline=VIOLET,alpha=int(230*grow),phase=t*.16)
    seal(im,"THE SAME GENOME CAN SUPPORT A DIFFERENT TARGET ANATOMY",
         "bioelectric state can override the default regenerative outcome",VIOLET)


def vis_cryptic_memory(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.41
    q=ease(u)
    draw_planarian(d,cx,cy,w*.62,h*.15,1,phase=t*.16)
    # hidden double-headed attractor
    path=voltage_path(cx,cy,w*.50,h*.055,t,1.1)
    glow_line(im,path,VIOLET,5,int(45+150*q),14)
    if q>.55:
        ghost=layer(im.size)
        gd=ImageDraw.Draw(ghost)
        draw_planarian(gd,cx,cy,w*.62,h*.16,2,body=WHITE,outline=VIOLET,
                       alpha=int(105*(q-.55)/.45),phase=t*.16)
        im.alpha_composite(ghost)
    seal(im,"NORMAL ANATOMY CAN HIDE AN ALTERNATIVE FUTURE",
         "the cryptic state appears only when injury asks the system to rebuild")


def vis_reset_state(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.41
    q=ease(u)
    draw_planarian(d,cx,cy,w*.62,h*.15,1,phase=t*.16)
    altered=voltage_path(cx,cy,w*.50,h*.060,t,1.2)
    normal=voltage_path(cx,cy,w*.50,h*.032,t)
    glow_line(im,altered,VIOLET,5,int(210*(1-q)),14)
    glow_line(im,partial(normal,q),CYAN,5,int(110+100*q),13)
    if q>.65:
        centered(d,(cx,h*.69),"WILD-TYPE TARGET RESTORED",
                 font(FONT_SERIF_BOLD,24),GREEN)
    seal(im,"PATTERN MEMORY IS PERSISTENT, NOT IMMUTABLE",
         "the physiological state can be reset")


def vis_error_correction(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.26,h*.41)
    right=(w*.74,h*.41)
    q=ease(u)
    # damaged
    draw_planarian(d,*left,w*.25,h*.12,1,body=PALE_CRIMSON,outline=CRIMSON,alpha=210)
    d.rectangle((left[0]+15,left[1]-70,left[0]+100,left[1]+70),
                fill=(*IVORY,255))
    # target
    draw_planarian(d,*right,w*.25,h*.12,1,body=PALE_GOLD,outline=GOLD,alpha=210)
    # error signal and correction
    glow_line(im,partial([left,(w*.50,h*.24),right],q),CYAN,5,200,13)
    if q>.42:
        arrow(d,(left[0]+60,left[1]),(right[0]-125,right[1]),(*GREEN,190),4,10)
    seal(im,"REGENERATION IS ERROR CORRECTION IN MORPHOLOGICAL SPACE",
         "the system compares present anatomy with an implicit target")


def vis_stop_condition(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.41
    q=ease(u)
    length=lerp(w*.12,w*.58,smoothstep(.05,.72,u))
    draw_planarian(d,cx,cy,length,lerp(h*.08,h*.16,q),1,
                   body=PALE_GREEN,outline=GREEN,phase=t*.12)
    # growth arrows vanish at completion
    alpha=int(200*(1-smoothstep(.68,.92,u)))
    for a in (-1,1):
        arrow(d,(cx+a*length*.25,cy),(cx+a*length*.48,cy),(*GREEN,alpha),3,8)
    if q>.78:
        centered(d,(cx,h*.69),"STOP",font(FONT_SERIF_BOLD,28),GOLD)
    seal(im,"A GOAL IS ALSO A STOP CONDITION",
         "growth and remodeling cease when the target relation is restored")


def vis_competency_scale(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    levels=[
        ("MOLECULE",w*.18,20,CYAN),
        ("CELL",w*.38,35,GREEN),
        ("TISSUE",w*.60,58,GOLD),
        ("ORGANISM",w*.82,90,VIOLET),
    ]
    q=ease(u)
    for i,(lab,x,r,col) in enumerate(levels):
        local=clamp(q*len(levels)-i)
        glow_circle(im,x,h*.40,r*local,col,int(120+90*local),12)
        if local>.45:
            centered(d,(x,h*.67),lab,font(FONT_SANS_BOLD,15),col)
        if i<len(levels)-1:
            arrow(d,(x+r+10,h*.40),(levels[i+1][1]-levels[i+1][2]-10,h*.40),
                  (*SILVER,int(150*local)),2,7)
    seal(im,"BIOLOGICAL COMPETENCE EXISTS AT MANY SCALES",
         "larger goals recruit smaller agents without erasing their abilities")


def vis_stress_propagation(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cols,rows=12,5
    q=ease(u)
    for j in range(rows):
        for i in range(cols):
            x=w*.12+i*w*.76/(cols-1)
            y=h*.24+j*h*.35/(rows-1)
            dist=abs(i-(cols-1)*q)
            col=mix(CYAN,CRIMSON,math.exp(-dist*.55))
            draw_cell(d,x,y,9,col,180)
    seal(im,"STRESS PROPAGATES ACROSS THE COLLECTIVE",
         "a local problem becomes a tissue-level signal")


def vis_cancer_defection(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    rng=random.Random(81)
    q=ease(u)
    cells=[]
    for i in range(95):
        a=rng.random()*math.tau
        rr=(rng.random()**.58)*min(w,h)*.24
        cells.append((cx+math.cos(a)*rr*1.5,cy+math.sin(a)*rr))
    rebel=(cx+80,cy+20)
    for x,y in cells:
        dist=math.dist((x,y),rebel)
        col=CRIMSON if dist<65*q else CYAN
        draw_cell(d,x,y,7,col,175)
    if q>.45:
        for rr in range(25,100,20):
            d.ellipse((rebel[0]-rr,rebel[1]-rr,rebel[0]+rr,rebel[1]+rr),
                      outline=(*CRIMSON,int(90*q*(1-rr/120))),width=3)
    seal(im,"WHEN CELLS LOSE THE LARGER GOAL, LOCAL SUCCESS CAN BECOME DISEASE",
         "cancer can be viewed partly as defection from anatomical cooperation",CRIMSON)


def vis_reintegration(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    rng=random.Random(81)
    q=ease(u)
    cells=[]
    for i in range(95):
        a=rng.random()*math.tau
        rr=(rng.random()**.58)*min(w,h)*.24
        cells.append((cx+math.cos(a)*rr*1.5,cy+math.sin(a)*rr))
    rebel=(cx+80,cy+20)
    for x,y in cells:
        dist=math.dist((x,y),rebel)
        col=mix(CRIMSON,CYAN,q) if dist<65 else CYAN
        draw_cell(d,x,y,7,col,175)
    glow_line(im,partial(voltage_path(cx,cy,w*.50,h*.05,t),q),CYAN,5,205,13)
    seal(im,"RECONNECTING CELLS CAN RESTORE PARTICIPATION IN THE WHOLE",
         "the aim is not always to kill the part, but to repair the communication")


def vis_morphospace(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    organisms=[
        (w*.22,h*.28,1,GREEN),
        (w*.40,h*.54,2,VIOLET),
        (w*.62,h*.28,1,CYAN),
        (w*.80,h*.54,2,GOLD),
    ]
    q=ease(u)
    for x,y,heads,col in organisms:
        draw_planarian(d,x,y,w*.16,h*.075,heads,
                       body=mix(WHITE,col,.12),outline=col,alpha=190,phase=t*.1)
    trajectory=[(w*.18,h*.60),(w*.34,h*.36),(w*.52,h*.54),(w*.70,h*.30),(w*.84,h*.45)]
    glow_line(im,partial(trajectory,q),GOLD,5,200,13)
    seal(im,"MORPHOSPACE CONTAINS MULTIPLE VIABLE BODIES",
         "development and regeneration are trajectories through possible form")


def vis_xenobot(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    # loose cells gather into novel organism
    rng=random.Random(52)
    for i in range(80):
        a=rng.random()*math.tau
        rr=rng.uniform(100,260)
        x=lerp(cx+math.cos(a)*rr,cx+math.cos(a)*90,q)
        y=lerp(cy+math.sin(a)*rr*.60,cy+math.sin(a)*55,q)
        draw_cell(d,x,y,7,mix(CYAN,GREEN,q),170)
    if q>.55:
        d.ellipse((cx-105,cy-70,cx+105,cy+70),outline=(*GREEN,int(200*q)),width=5)
        glow_line(im,partial([(cx-60,cy),(cx,cy-35),(cx+70,cy+10)],q),GOLD,4,180,11)
    seal(im,"CELLS CAN BE RECOMBINED INTO NEW COMPETENT BODIES",
         "evolution supplies capacities that can operate in unfamiliar architectures")


def vis_goal_space(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    levels=[
        ("ION",w*.18,h*.53,CYAN),
        ("CELL",w*.36,h*.42,GREEN),
        ("TISSUE",w*.55,h*.31,GOLD),
        ("BODY",w*.76,h*.20,VIOLET),
    ]
    q=ease(u)
    for i,(lab,x,y,col) in enumerate(levels):
        glow_circle(im,x,y,12+i*4,col,160,10)
        centered(d,(x,y+35),lab,font(FONT_SANS_BOLD,14),col)
        if i<len(levels)-1:
            arrow(d,(x+22,y-8),(levels[i+1][1]-25,levels[i+1][2]+8),
                  (*col,int(170*q)),3,8)
    seal(im,"GOALS EXPAND WITH THE SCALE OF THE SELF",
         "larger networks can pursue outcomes unavailable to isolated parts")


def vis_collective_self(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    rng=random.Random(23)
    q=ease(u)
    nodes=[]
    for i in range(100):
        a=rng.random()*math.tau
        rr=(rng.random()**.55)*min(w,h)*.25
        nodes.append((cx+math.cos(a)*rr*1.55,cy+math.sin(a)*rr))
    for x,y in nodes:
        draw_cell(d,x,y,6,CYAN,150)
    r=lerp(40,240,q)
    d.ellipse((cx-r,cy-r*.62,cx+r,cy+r*.62),
              outline=(*GOLD,190),width=5)
    seal(im,"THE BOUNDARY OF THE SELF CAN GROW",
         "communication links local competencies into a larger agent")


def vis_science_caution(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    rows=[
        ("BIOELECTRIC PATTERNS GUIDE MORPHOGENESIS","SUPPORTED",GREEN),
        ("TISSUES SHOW HUMAN-LIKE CONSCIOUSNESS","NOT ESTABLISHED",CRIMSON),
        ("TARGET STATES CAN BE EDITED","SUPPORTED",CYAN),
        ("EXPERIMENTS PROVE TANTRIC METAPHYSICS","NOT ESTABLISHED",CRIMSON),
    ]
    q=ease(u)
    for i,(claim,status,col) in enumerate(rows):
        local=clamp(q*len(rows)-i)
        y=h*(.23+i*.13)
        d.rounded_rectangle((w*.15,y-28,w*.85,y+28),radius=14,
                            fill=(*mix(WHITE,col,.10),int(220*local)),
                            outline=(*col,int(180*local)),width=2)
        centered(d,(w*.41,y),claim,font(FONT_SANS_BOLD,14),INK)
        centered(d,(w*.73,y),status,font(FONT_SANS_BOLD,14),col)
    seal(im,"KEEP THE CLAIM AT THE SCALE OF THE EVIDENCE",
         "goal-directed behavior is observable; subjective experience remains open")


def vis_tantric_bridge(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.30,h*.40)
    right=(w*.70,h*.40)
    q=ease(u)
    # biological target network
    draw_planarian(d,*left,w*.24,h*.11,1,body=PALE_CYAN,outline=CYAN,alpha=190)
    glow_line(im,voltage_path(left[0],left[1],w*.20,h*.035,t),CYAN,4,180,11)
    centered(d,(left[0],h*.67),"HOW FORM IS REGULATED",font(FONT_SANS_BOLD,15),CYAN)
    # luminous appearance
    for rr in range(35,150,28):
        d.ellipse((right[0]-rr,right[1]-rr*.60,right[0]+rr,right[1]+rr*.60),
                  outline=(*GOLD,int(85*q*(1-rr/175))),width=3)
    centered(d,(right[0],h*.67),"WHAT IT MEANS TO APPEAR",font(FONT_SANS_BOLD,15),GOLD)
    glow_line(im,partial([left,(w*.50,h*.22),right],q),VIOLET,4,180,11)
    seal(im,"LEVIN AND ABHINAVAGUPTA ASK DIFFERENT QUESTIONS",
         "biology studies organized goals; Tantra studies manifestation and recognition")


def vis_final(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.41
    q=ease(u)
    # damaged fragment becomes full organism inside golden attractor
    if q<.55:
        draw_planarian(d,cx,cy,w*.24,h*.11,1,body=PALE_CRIMSON,outline=CRIMSON,alpha=210)
        d.rectangle((cx+10,cy-h*.09,cx+w*.16,cy+h*.09),fill=(*IVORY,255))
    draw_planarian(d,cx,cy,lerp(w*.24,w*.62,q),lerp(h*.11,h*.16,q),1,
                   body=mix(PALE_CYAN,PALE_GREEN,q),outline=GREEN,
                   alpha=int(220*q),phase=t*.14)
    path=voltage_path(cx,cy,w*.50,h*.042,t)
    glow_line(im,partial(path,q),CYAN,5,210,13)
    for rr in range(35,270,32):
        d.ellipse((cx-rr,cy-rr*.60,cx+rr,cy+rr*.60),
                  outline=(*GOLD,int(75*q*(1-rr/300))),width=3)
    if q>.72:
        centered(d,(cx,h*.69),"ANATOMICAL HOMEOSTASIS",
                 font(FONT_SERIF_BOLD,27),GOLD)
    seal(im,"THE BODY KNOWS THE SHAPE IT WANTS",
         "not as a little mind, but as a collective that detects error and acts toward form",GOLD)


VISUALS: dict[str,Callable] = {
    "question":vis_fragment_question,
    "regrow":vis_fragments_regrow,
    "goal":vis_blueprint_vs_goal,
    "collective":vis_cell_collective,
    "junctions":vis_gap_junctions,
    "voltage":vis_voltage_map,
    "edit":vis_edit_voltage,
    "twohead":vis_two_headed,
    "cryptic":vis_cryptic_memory,
    "reset":vis_reset_state,
    "error":vis_error_correction,
    "stop":vis_stop_condition,
    "scale":vis_competency_scale,
    "stress":vis_stress_propagation,
    "cancer":vis_cancer_defection,
    "reintegrate":vis_reintegration,
    "morphospace":vis_morphospace,
    "xenobot":vis_xenobot,
    "goalspace":vis_goal_space,
    "self":vis_collective_self,
    "caution":vis_science_caution,
    "bridge":vis_tantric_bridge,
    "final":vis_final,
}


# =============================================================================
# FILM-FIRST ESSAY
# =============================================================================

@dataclass
class Scene:
    title:str
    narration:str
    duration:float
    visual:str
    params:dict


SCENES = [
    Scene("Cut",
          "Cut a planarian into pieces.",
          5.5,"question",{}),
    Scene("Question",
          "Each fragment now faces a problem the wound itself does not answer.",
          8.0,"question",{}),
    Scene("What body",
          "What body should exist here?",
          6.0,"question",{}),
    Scene("Not just growth",
          "The tissue must determine what is missing, which end is anterior, how much to build, and when to stop.",
          10.0,"question",{}),

    Scene("Regrowth",
          "Then the fragments begin rebuilding.",
          6.5,"regrow",{}),
    Scene("Whole relation",
          "A middle piece does not merely produce more cells. It restores a head-tail relation appropriate to a complete animal.",
          10.0,"regrow",{}),
    Scene("Stop",
          "When the correct anatomy is reached, extensive remodeling stops.",
          8.0,"stop",{}),

    Scene("Target morphology",
          "Michael Levin calls this kind of outcome a target morphology.",
          7.0,"goal",{}),
    Scene("Not blueprint",
          "The target is not a tiny anatomical picture stored in one special cell.",
          8.0,"goal",{}),
    Scene("Correctable goal",
          "It is better understood as a correctable state toward which many cellular actions can converge.",
          9.5,"goal",{}),

    Scene("Cell collective",
          "No individual cell sees the whole worm.",
          7.0,"collective",{}),
    Scene("Local competencies",
          "Each cell senses local conditions, communicates, changes gene expression, migrates, divides, or differentiates.",
          10.0,"collective",{}),
    Scene("Global outcome",
          "Together, these local competencies produce a global anatomy none of the cells can inhabit alone.",
          9.5,"collective",{}),

    Scene("Electrical society",
          "The body is not only a chemical society. It is an electrical one.",
          8.0,"junctions",{}),
    Scene("Resting potentials",
          "Every cell maintains a resting membrane potential through ion channels and pumps.",
          8.5,"voltage",{}),
    Scene("Gap junctions",
          "Gap junctions connect neighboring cells into physiological networks.",
          8.0,"junctions",{}),
    Scene("Long-range state",
          "Slow voltage patterns can coordinate information across tissues before nerves or muscles act.",
          9.0,"voltage",{}),

    Scene("Electrical topology",
          "A regenerating body therefore has an electrical topology.",
          7.0,"voltage",{}),
    Scene("Polarity",
          "Different voltage states help distinguish anterior from posterior and influence which structures wounds build.",
          9.5,"voltage",{}),
    Scene("Instruction",
          "The pattern is not merely a side effect of anatomy. In experiments, changing it changes the anatomical result.",
          10.0,"edit",{}),

    Scene("Brief edit",
          "A brief perturbation can alter the network.",
          7.0,"edit",{}),
    Scene("Treatment gone",
          "The treatment disappears.",
          5.5,"edit",{}),
    Scene("Different body",
          "Yet some fragments regenerate with two heads.",
          7.5,"twohead",{}),
    Scene("Same genome",
          "The genome remains the ordinary planarian genome. The large-scale target has changed.",
          9.0,"twohead",{}),

    Scene("Cryptic future",
          "The strangest result appears in worms that look normal.",
          7.5,"cryptic",{}),
    Scene("Hidden state",
          "Their anatomy, histology, and ordinary behavior may reveal no second head.",
          8.5,"cryptic",{}),
    Scene("Cut again",
          "But cut them again in plain water, and the altered regenerative outcome can reappear.",
          9.5,"cryptic",{}),
    Scene("Memory",
          "A normal-looking body can carry a cryptic memory of another morphology.",
          9.0,"cryptic",{}),

    Scene("Reset",
          "That memory is persistent, but it is not absolute.",
          7.5,"reset",{}),
    Scene("Restore state",
          "Resetting the bioelectric state can restore the usual regenerative target.",
          8.5,"reset",{}),
    Scene("Anatomical switch",
          "The tissue behaves like a multistable anatomical switch.",
          8.0,"reset",{}),

    Scene("Error correction",
          "Regeneration now looks less like construction from a blueprint and more like error correction.",
          9.5,"error",{}),
    Scene("Present versus target",
          "The collective detects a mismatch between present anatomy and a target state.",
          8.5,"error",{}),
    Scene("Corrective action",
          "It recruits growth, migration, patterning, and remodeling until the mismatch becomes small enough.",
          9.5,"error",{}),
    Scene("Goal includes stopping",
          "A genuine goal is not only a direction. It is also a condition for stopping.",
          8.5,"stop",{}),

    Scene("Competency architecture",
          "This suggests a competency architecture.",
          7.0,"scale",{}),
    Scene("Nested agents",
          "Molecules solve local binding problems. Cells solve physiological problems. Tissues solve patterning problems.",
          10.0,"scale",{}),
    Scene("Larger self",
          "The organism coordinates these smaller competencies toward outcomes defined at a larger scale.",
          9.0,"goalspace",{}),

    Scene("Stress",
          "When one region is damaged, stress does not remain private.",
          7.5,"stress",{}),
    Scene("Distributed signal",
          "Electrical and chemical changes propagate across the collective.",
          8.0,"stress",{}),
    Scene("Larger response",
          "A local wound recruits a body-level response.",
          7.0,"stress",{}),

    Scene("Defection",
          "Cancer reveals the inverse problem.",
          6.5,"cancer",{}),
    Scene("Local success",
          "A cell can become highly successful at proliferation while defecting from the anatomical goals of the tissue.",
          9.5,"cancer",{}),
    Scene("Shrunken self",
          "Its computational boundary has contracted. The larger body is no longer the self whose future it serves.",
          10.0,"cancer",{}),
    Scene("Reintegration",
          "Some bioelectric approaches therefore aim not only to kill aberrant cells, but to reconnect them to tissue-level pattern control.",
          10.0,"reintegrate",{}),

    Scene("Morphospace",
          "The possible bodies available to living matter form a morphospace.",
          8.0,"morphospace",{}),
    Scene("Trajectories",
          "Development, regeneration, evolution, and engineering trace different paths through that space.",
          9.0,"morphospace",{}),
    Scene("Alternative attractors",
          "A single genome may participate in more than one stable anatomical outcome.",
          8.5,"morphospace",{}),

    Scene("Reconfigured cells",
          "Remove cells from their usual embryonic context and place them into a new architecture.",
          8.5,"xenobot",{}),
    Scene("New body",
          "They can sometimes organize into novel motile bodies with competencies their original anatomy never expressed.",
          10.0,"xenobot",{}),
    Scene("Latent capacities",
          "Evolution has produced cells with capacities deeper than the single body plan in which we normally meet them.",
          9.5,"xenobot",{}),

    Scene("Goal space",
          "Levin's deeper proposal is that cognition is not restricted to brains.",
          8.5,"goalspace",{}),
    Scene("Scale of concern",
          "Cognition can be studied through the scale of goals a system can pursue and the errors it can correct.",
          9.5,"goalspace",{}),
    Scene("Expand self",
          "Connect cells into wider communication networks and the boundary of the biological self can expand.",
          9.5,"self",{}),
    Scene("New goals",
          "The collective gains access to goals no isolated cell could represent or achieve.",
          9.0,"self",{}),

    Scene("Careful language",
          "But the phrase the body knows must remain disciplined.",
          8.0,"caution",{}),
    Scene("Operational knowing",
          "It means the collective stores state, detects deviation, chooses among actions, and corrects toward a target.",
          10.0,"caution",{}),
    Scene("Experience open",
          "It does not by itself prove that tissue experiences its goal as a human experiences intention.",
          9.5,"caution",{}),

    Scene("Bridge",
          "This is where biology and Tantra can meet without being confused.",
          8.0,"bridge",{}),
    Scene("Levin question",
          "Levin asks how living collectives represent and pursue large-scale form.",
          8.0,"bridge",{}),
    Scene("Abhinava question",
          "Abhinavagupta asks what it means for form, goal, organism, and world to appear within awareness.",
          9.0,"bridge",{}),
    Scene("No proof",
          "Bioelectric regeneration does not prove Kashmir Śaivism.",
          7.0,"caution",{}),
    Scene("Complementary levels",
          "It gives us a concrete biology of distributed agency to place beside a phenomenology of manifestation and recognition.",
          10.0,"bridge",{}),

    Scene("Return to fragment",
          "Return to the fragment.",
          5.5,"final",{}),
    Scene("Missing relation",
          "It has no head, no tail, and no complete body.",
          7.0,"final",{}),
    Scene("Collective answer",
          "Yet its cells communicate, evaluate, correct, and stop.",
          8.0,"final",{}),
    Scene("Closing",
          "The body knows the shape it wants—not because a little mind hides inside the tissue, but because living collectives can remember a target, detect an error, and act together until matter becomes anatomy again.",
          10.0,"final",{}),
]


# =============================================================================
# PIPELINE
# =============================================================================

def render_frame(scene, frame_index, frame_count, width, height, seed):
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
        for output_index,frame_index in enumerate([0,int(count*.33),int(count*.72),count-1]):
            render_frame(
                scene,frame_index,count,width,height,index*10000+frame_index
            ).save(frame_dir/f"preview_{output_index:02d}.jpg",quality=95)
        return frame_dir

    for frame_index in range(count):
        p=frame_dir/f"{frame_index:05d}.jpg"
        if p.exists():
            continue
        render_frame(
            scene,frame_index,count,width,height,index*10000+frame_index
        ).save(p,quality=95,subsampling=0)

    return encode_scene(index,fps)


def concatenate(paths):
    txt=OUTPUT/"concat.txt"
    txt.write_text("\n".join(f"file '{p.resolve()}'" for p in paths),encoding="utf-8")
    output=OUTPUT/"body_knows_shape.mp4"
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
        record=asdict(scene)
        record["scene_id"]=f"scene_{index:03d}"
        record["start_seconds"]=round(cursor,3)
        cursor+=scene.duration
        record["end_seconds"]=round(cursor,3)
        records.append(record)

    p=OUTPUT/"narration_timeline.json"
    p.write_text(json.dumps({
        "title":"the body knows the shape it wants",
        "scene_count":len(SCENES),
        "runtime_seconds":round(cursor,3),
        "shot_duration_range":[5,10],
        "continuity_object":"cyan voltage contour becoming gold target outline",
        "scenes":records,
    },indent=2,ensure_ascii=False),encoding="utf-8")
    return p


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
        d.text((x+8,y+th+7),f"{index:02d}  {scene.title}",font=lf,fill=INK)

    p=OUTPUT/"contact_sheet.jpg"
    sheet.save(p,quality=94)
    return p


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

    print(f"Timeline: {export_timeline()}")
    print(f"Scenes: {len(SCENES)}")
    print(f"Runtime: {sum(scene.duration for scene in SCENES)/60:.2f} minutes")

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
        result=render_scene(
            index,scene,args.fps,args.width,args.height,args.preview
        )
        if not args.preview:
            rendered.append(result)

    if not args.no_contact_sheet:
        print(f"Contact sheet: {make_contact_sheet(args.width,args.height)}")

    if not args.preview:
        print(f"Final video: {concatenate(rendered)}")


if __name__=="__main__":
    main()
