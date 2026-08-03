#!/usr/bin/env python3
"""
CELLS THAT SOLVE PROBLEMS
A Michael Levin–themed Platinum-house procedural visual essay.

SCIENTIFIC GROUNDING
--------------------
Inspired by Michael Levin's work on:

• basal cognition;
• TAME — the Technological Approach to Mind Everywhere;
• multiscale competency architecture;
• scale-free cognition;
• developmental bioelectricity;
• collective intelligence;
• competent navigation of metabolic, transcriptional, physiological,
  anatomical, and behavioral spaces;
• top-down control without micromanagement;
• the computational boundary of a self;
• biological plasticity, regeneration, and synthetic morphology.

The word "cognition" is used operationally:
memory, state integration, adaptive regulation, error correction,
goal-directed navigation, and flexible problem-solving.

The film does not claim that every cell has human-like phenomenal experience.

FILM THESIS
-----------
Life did not begin with a brain and then acquire intelligence.
Brains inherited and amplified older problem-solving loops.

Molecules navigate chemical state spaces.
Cells navigate metabolic and transcriptional spaces.
Tissues navigate physiological and anatomical spaces.
Animals navigate three-dimensional behavioral space.

Evolution scales agency by linking smaller competent systems into larger selves.
The crucial transition is not from non-mind to mind.
It is from narrow goals to wider goals.

VISUAL THESIS
-------------
One cyan agent crosses five spaces:
metabolic → transcriptional → physiological → anatomical → behavioral.

At each level:
current state → error → search → correction → preferred region.

The continuity object is a cyan compass that becomes a gold cognitive light cone.

HOUSE RULES
-----------
• Every shot lasts 5–10 seconds.
• Every shot performs before → operation → after.
• Clean ivory scientific/gallery field.
• No slideshow layouts.
• Sparse labels only.
• Every mature frame near u=0.72 should work as a still.
• Distinct compositions rather than recolored repetition.

PALETTE ROLES
-------------
IVORY    open possibility space
CYAN     local agent / sensing / communication
GOLD     preferred region / larger goal
GREEN    successful correction / viable state
CRIMSON  error / stress / local failure
VIOLET   memory / alternative state / latent competency
INK      current material configuration

OUTPUT
------
output_cells_solve/
  frames/scene_001/*.jpg
  scenes/scene_001.mp4
  cells_that_solve_problems.mp4
  narration_timeline.json
  contact_sheet.jpg

USAGE
-----
python cells_that_solve_problems_platinum.py
python cells_that_solve_problems_platinum.py --preview
python cells_that_solve_problems_platinum.py --scene 12
python cells_that_solve_problems_platinum.py --fps 12 --width 1920 --height 1080
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
OUTPUT = ROOT / "output_cells_solve"
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
    return Image.new("RGBA", size, (0,0,0,0))


def field(w, h, seed):
    rng = np.random.default_rng(seed)
    arr = np.empty((h,w,3), dtype=np.float32)
    arr[:] = IVORY
    arr += rng.normal(0,.9,(h,w,1))
    yy,xx = np.mgrid[0:h,0:w]
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
    centered(
        d,(w/2,h*.875),title,
        font(FONT_SERIF_BOLD,max(22,int(h*.04))),
        color
    )
    if subtitle:
        centered(
            d,(w/2,h*.923),subtitle,
            font(FONT_SANS,max(13,int(h*.019))),
            SOFT_INK
        )


def border(im):
    w,h = im.size
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((26,26,w-26,h-26),radius=18,
                        outline=(*INK,45),width=2)


def glow_circle(im,x,y,r,color,alpha=170,blur=14):
    gl = layer(im.size)
    gd = ImageDraw.Draw(gl)
    gd.ellipse((x-r,y-r,x+r,y+r),fill=(*color,alpha))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(blur)))
    fg = layer(im.size)
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
        pts,
        fill=(*mix(color,WHITE,.08),min(255,alpha+25)),
        width=width,
        joint="curve"
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
        p=(b[0]-math.cos(ang+s*.52)*head,
           b[1]-math.sin(ang+s*.52)*head)
        d.line((*b,*p),fill=color,width=width)


def draw_cell(d,cx,cy,r,color=CYAN,alpha=205):
    d.ellipse((cx-r,cy-r,cx+r,cy+r),
              fill=(*mix(WHITE,color,.12),alpha//2),
              outline=(*color,alpha),width=3)


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


def landscape_points(left,right,base,centers,depths,widths,samples=260):
    pts=[]
    for i in range(samples):
        q=i/(samples-1)
        y=base
        for c,d,w in zip(centers,depths,widths):
            y-=d*math.exp(-((q-c)/w)**2)
        pts.append((lerp(left,right,q),y))
    return pts


def compass(d,cx,cy,r,color=CYAN,alpha=210,angle=0.0):
    d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(*color,alpha),width=3)
    end=(cx+math.cos(angle)*r*.76,cy+math.sin(angle)*r*.76)
    arrow(d,(cx,cy),end,(*color,alpha),3,8)


# =============================================================================
# VISUALS
# =============================================================================

def vis_problem_loop(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    labels=[
        ("CURRENT",CYAN,-170,-75),
        ("COMPARE",VIOLET,0,-145),
        ("ERROR",CRIMSON,170,-75),
        ("ACT",GREEN,170,95),
        ("UPDATE",GOLD,-170,95),
    ]
    q=ease(u)
    for i,(lab,col,ox,oy) in enumerate(labels):
        local=clamp(q*len(labels)-i)
        x,y=cx+ox,cy+oy
        glow_circle(im,x,y,10,col,150,9)
        if local>.45:
            centered(d,(x,y+27),lab,font(FONT_SANS_BOLD,14),col)
        if i>0:
            px,py=cx+labels[i-1][2],cy+labels[i-1][3]
            arrow(d,(px,py),(x,y),(*col,int(160*local)),2,7)
    if q>.82:
        px,py=cx+labels[-1][2],cy+labels[-1][3]
        nx,ny=cx+labels[0][2],cy+labels[0][3]
        arrow(d,(px,py),(nx,ny),(*CYAN,160),2,7)
    glow_circle(im,cx,cy,14,GOLD,150,10)
    seal(im,"A MINIMAL PROBLEM-SOLVING LOOP",
         "sense, compare, act, remember, repeat")


def vis_metabolic_space(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left,right=w*.12,w*.88
    base=h*.65
    pts=landscape_points(left,right,base,[.22,.58,.82],[90,55,100],[.12,.10,.09])
    d.line(pts,fill=(*INK,190),width=4)
    q=ease(u)
    xq=lerp(.48,.82,q)
    idx=int(xq*(len(pts)-1))
    x,y=pts[idx]
    glow_circle(im,x,y-14,14,CYAN,180,10)
    target=pts[int(.82*(len(pts)-1))]
    glow_circle(im,target[0],target[1]-14,18,GOLD,170,11)
    centered(d,(w*.50,h*.18),"METABOLIC SPACE",font(FONT_SERIF_BOLD,28),GREEN)
    seal(im,"A CELL NAVIGATES CHEMICAL POSSIBILITY",
         "it corrects toward viable internal states")


def vis_transcription_space(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    rows,cols=7,12
    q=ease(u)
    target_col=int(lerp(2,9,q))
    for j in range(rows):
        for i in range(cols):
            x=w*.15+i*w*.70/(cols-1)
            y=h*.22+j*h*.40/(rows-1)
            active=math.exp(-abs(i-target_col)*.75)
            col=mix(PALE_SILVER,GOLD,active)
            d.rounded_rectangle((x-17,y-10,x+17,y+10),radius=5,
                                fill=(*col,190),
                                outline=(*mix(SILVER,GOLD,active),160),width=2)
    centered(d,(w*.50,h*.18),"TRANSCRIPTIONAL SPACE",
             font(FONT_SERIF_BOLD,27),VIOLET)
    seal(im,"GENE EXPRESSION IS A LANDSCAPE OF CHOICES",
         "cells shift programs in response to context")


def vis_physiological_space(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    draw_cell(d,cx,cy,135,CYAN,210)
    for i in range(12):
        a=i*math.tau/12
        x1=cx+math.cos(a)*100
        y1=cy+math.sin(a)*100
        x2=cx+math.cos(a)*155
        y2=cy+math.sin(a)*155
        d.line((x1,y1,x2,y2),fill=(*INK,100),width=4)
        ion=(t*.35+i/12)%1
        xx=lerp(x1,x2,ion if i%2==0 else 1-ion)
        yy=lerp(y1,y2,ion if i%2==0 else 1-ion)
        glow_circle(im,xx,yy,6,GOLD if i%2==0 else VIOLET,140,7)
    for rr in range(40,190,28):
        d.arc((cx-rr,cy-rr,cx+rr,cy+rr),210,330,
              fill=(*CYAN,int(75*q*(1-rr/210))),width=3)
    centered(d,(cx,h*.18),"PHYSIOLOGICAL SPACE",
             font(FONT_SERIF_BOLD,27),CYAN)
    seal(im,"CELLS REGULATE VOLTAGE, pH, AND OSMOTIC STATE",
         "homeostasis is problem-solving before brains")


def vis_anatomical_space(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    rng=random.Random(31)
    cells=[]
    for i in range(120):
        a=rng.random()*math.tau
        rr=(rng.random()**.58)*min(w,h)*.25
        cells.append((cx+math.cos(a)*rr*1.5,cy+math.sin(a)*rr))
    for i,(x,y) in enumerate(cells):
        target_x=cx+(x-cx)*(.72+.18*q)
        target_y=cy+(y-cy)*(.65+.15*q)
        xx=lerp(x,target_x,q)
        yy=lerp(y,target_y,q)
        draw_cell(d,xx,yy,6,mix(CYAN,GREEN,q),150)
    if q>.45:
        d.ellipse((cx-190,cy-115,cx+190,cy+115),
                  outline=(*GOLD,int(190*q)),width=5)
    centered(d,(cx,h*.18),"ANATOMICAL SPACE",
             font(FONT_SERIF_BOLD,27),GOLD)
    seal(im,"TISSUES NAVIGATE TOWARD LARGE-SCALE FORM",
         "cells become material for goals defined above their own scale")


def vis_behavior_space(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.28,h*.42
    q=ease(u)
    draw_body(d,cx,cy,.62,INK,180)
    targets=[
        (w*.72,h*.24,GREEN,"FOOD"),
        (w*.80,h*.45,CRIMSON,"THREAT"),
        (w*.68,h*.63,GOLD,"SHELTER"),
    ]
    for x,y,col,lab in targets:
        glow_circle(im,x,y,12,col,155,9)
        centered(d,(x,y+28),lab,font(FONT_SANS_BOLD,13),col)
    path=[(cx+50,cy),(w*.48,h*.50),(w*.68,h*.63)]
    glow_line(im,partial(path,q),GOLD,5,205,13)
    centered(d,(w*.50,h*.18),"BEHAVIORAL SPACE",
             font(FONT_SERIF_BOLD,27),GREEN)
    seal(im,"ANIMALS NAVIGATE THE FAMILIAR SPACE OF ACTION",
         "the loop is older than locomotion")


def vis_same_algorithm(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    spaces=[
        ("METABOLIC",w*.16,CYAN),
        ("TRANSCRIPTIONAL",w*.33,VIOLET),
        ("PHYSIOLOGICAL",w*.50,GREEN),
        ("ANATOMICAL",w*.67,GOLD),
        ("BEHAVIORAL",w*.84,CRIMSON),
    ]
    q=ease(u)
    for i,(lab,x,col) in enumerate(spaces):
        local=clamp(q*len(spaces)-i)
        compass(d,x,h*.40,32,col,int(210*local),angle=-.6+i*.28)
        centered(d,(x,h*.67),lab,font(FONT_SANS_BOLD,12),col)
        if i<len(spaces)-1:
            arrow(d,(x+38,h*.40),(spaces[i+1][1]-38,h*.40),
                  (*SILVER,int(140*local)),2,7)
    seal(im,"ONE LOGIC APPEARS IN MANY SPACES",
         "detect deviation and move toward a preferred region")


def vis_cell_memory(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    states=[(w*.22,CYAN),(w*.38,VIOLET),(w*.54,GREEN),(w*.70,CRIMSON),(w*.84,GOLD)]
    for x,col in states:
        glow_circle(im,x,cy,12,col,150,9)
    glow_line(im,partial([(x,cy) for x,_ in states],q),CYAN,4,190,11)
    if q>.58:
        centered(d,(cx,h*.67),"PAST STATE CHANGES PRESENT RESPONSE",
                 font(FONT_SERIF_BOLD,23),VIOLET)
    seal(im,"MEMORY NEED NOT LOOK LIKE RECOLLECTION",
         "a state can persist and alter what the cell does next")


def vis_learning(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left,right=w*.12,w*.88
    base=h*.63
    q=ease(u)
    before=landscape_points(left,right,base,[.28,.72],[55,75],[.12,.12])
    after=landscape_points(left,right,base,[.28,.72],[35,110],[.12,.10])
    blended=[]
    for a,b in zip(before,after):
        blended.append((a[0],lerp(a[1],b[1],q)))
    d.line(blended,fill=(*INK,190),width=4)
    xq=lerp(.28,.72,q)
    idx=int(xq*(len(blended)-1))
    x,y=blended[idx]
    glow_circle(im,x,y-14,14,CYAN,180,10)
    seal(im,"LEARNING CHANGES THE LANDSCAPE OF FUTURE ACTION",
         "experience reshapes which states are easy to reach")


def vis_exploration(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    rng=random.Random(91)
    paths=[]
    for k in range(9):
        pts=[(w*.14,cy)]
        for i in range(1,8):
            pts.append((w*.14+i*w*.72/7,
                        cy+rng.uniform(-130,130)*(i/7)))
        paths.append(pts)
    for i,pts in enumerate(paths):
        col=GOLD if i==6 else PALE_VIOLET
        alpha=210 if i==6 else 90
        glow_line(im,partial(pts,q),col,4 if i==6 else 2,alpha,10)
    glow_circle(im,w*.86,paths[6][-1][1],15,GOLD,180,11)
    seal(im,"COMPETENCY REVEALS ITSELF UNDER NOVEL CONDITIONS",
         "the agent searches rather than replaying one fixed response")


def vis_multiscale_agents(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    levels=[
        ("MOLECULE",w*.15,18,CYAN),
        ("CELL",w*.32,30,GREEN),
        ("TISSUE",w*.51,49,GOLD),
        ("ORGANISM",w*.73,76,VIOLET),
        ("GROUP",w*.90,105,CRIMSON),
    ]
    q=ease(u)
    for i,(lab,x,r,col) in enumerate(levels):
        local=clamp(q*len(levels)-i)
        glow_circle(im,x,h*.40,r*local,col,int(120+90*local),12)
        centered(d,(x,h*.68),lab,font(FONT_SANS_BOLD,13),col)
        if i<len(levels)-1:
            arrow(d,(x+r+8,h*.40),(levels[i+1][1]-levels[i+1][2]-8,h*.40),
                  (*SILVER,int(150*local)),2,7)
    seal(im,"ALL KNOWN AGENTS ARE MADE OF ACTIVE PARTS",
         "agency is nested rather than indivisible")


def vis_goal_hierarchy(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    q=ease(u)
    levels=[
        ("BIND",w*.18,h*.58,CYAN),
        ("SURVIVE",w*.35,h*.47,GREEN),
        ("REPAIR",w*.53,h*.36,GOLD),
        ("REPRODUCE",w*.71,h*.25,VIOLET),
        ("CARE",w*.86,h*.16,CRIMSON),
    ]
    for i,(lab,x,y,col) in enumerate(levels):
        local=clamp(q*len(levels)-i)
        glow_circle(im,x,y,11+i*3,col,150,9)
        centered(d,(x,y+30),lab,font(FONT_SANS_BOLD,13),col)
        if i<len(levels)-1:
            arrow(d,(x+18,y-8),(levels[i+1][1]-18,levels[i+1][2]+8),
                  (*col,int(160*local)),3,8)
    seal(im,"LARGER SELVES PURSUE WIDER GOALS",
         "the cognitive horizon expands with the scale of integration")


def vis_boundary_expansion(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    rng=random.Random(44)
    cells=[]
    for i in range(105):
        a=rng.random()*math.tau
        rr=(rng.random()**.58)*min(w,h)*.24
        cells.append((cx+math.cos(a)*rr*1.55,cy+math.sin(a)*rr))
    for x,y in cells:
        draw_cell(d,x,y,6,CYAN,145)
    q=ease(u)
    r=lerp(35,245,q)
    d.ellipse((cx-r,cy-r*.62,cx+r,cy+r*.62),
              outline=(*GOLD,195),width=5)
    seal(im,"THE COMPUTATIONAL BOUNDARY OF A SELF CAN EXPAND",
         "communication converts neighbors into parts of one larger concern")


def vis_conflict_alignment(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.30,h*.40)
    right=(w*.70,h*.40)
    q=ease(u)
    # local arrows disagree then align
    for center,col,phase in [(left,CRIMSON,0),(right,CYAN,math.pi)]:
        for i in range(9):
            a=i*math.tau/9+phase*(1-q)
            x=center[0]+math.cos(i*math.tau/9)*70
            y=center[1]+math.sin(i*math.tau/9)*45
            arrow(d,(x,y),(x+math.cos(a)*35,y+math.sin(a)*35),
                  (*col,170),2,7)
    if q>.48:
        glow_line(im,[(left[0],left[1]),(right[0],right[1])],GOLD,5,190,12)
    seal(im,"COLLECTIVE INTELLIGENCE REQUIRES GOAL ALIGNMENT",
         "coordination fails when subunits optimize incompatible futures")


def vis_shared_scarcity(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    agents=[
        (w*.27,h*.34,CYAN),
        (w*.43,h*.52,GREEN),
        (w*.62,h*.31,VIOLET),
        (w*.76,h*.53,CRIMSON),
    ]
    resource=(cx,h*.20)
    glow_circle(im,*resource,18,GOLD,180,11)
    for i,(x,y,col) in enumerate(agents):
        glow_circle(im,x,y,12,col,150,9)
        arrow(d,(x,y),resource,(*mix(col,GOLD,q),150),2,7)
    if q>.55:
        d.ellipse((cx-235,cy-160,cx+235,cy+160),
                  outline=(*GOLD,180),width=4)
    seal(im,"SHARED MODELS OF SCARCITY CAN GLUE AGENTS TOGETHER",
         "a collective forms around what must be protected or obtained")


def vis_top_down_control(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    rng=random.Random(19)
    points=[]
    for i in range(100):
        a=rng.random()*math.tau
        rr=(rng.random()**.6)*min(w,h)*.25
        points.append((cx+math.cos(a)*rr*1.5,cy+math.sin(a)*rr))
    q=ease(u)
    # top-down field changes landscape, cells use local rules
    for i,(x,y) in enumerate(points):
        target_x=cx+(x-cx)*(.75+.12*math.sin(i))
        target_y=cy+(y-cy)*(.62+.10*math.cos(i))
        xx=lerp(x,target_x,q)
        yy=lerp(y,target_y,q)
        draw_cell(d,xx,yy,6,mix(CYAN,GREEN,q),150)
    if q>.35:
        d.ellipse((cx-205,cy-125,cx+205,cy+125),
                  outline=(*GOLD,int(190*q)),width=5)
    seal(im,"TOP-DOWN CONTROL CHANGES THE GOAL, NOT EVERY MOVEMENT",
         "competent parts solve the details locally")


def vis_micromanagement_fail(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    rng=random.Random(55)
    q=ease(u)
    for i in range(70):
        x=rng.uniform(w*.15,w*.85)
        y=rng.uniform(h*.22,h*.62)
        target=(w*.50+math.cos(i)*150,h*.40+math.sin(i*1.7)*80)
        arrow(d,(x,y),(lerp(x,target[0],q),lerp(y,target[1],q)),
              (*CRIMSON,110),1,5)
    centered(d,(w*.50,h*.18),"CONTROL EVERY CELL",
             font(FONT_SERIF_BOLD,27),CRIMSON)
    seal(im,"MICROMANAGEMENT EXPLODES WITH COMPLEXITY",
         "the better interface is communication with the collective's setpoints")


def vis_anatomical_compiler(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.25,h*.40)
    right=(w*.75,h*.40)
    q=ease(u)
    # desired form input
    d.rounded_rectangle((left[0]-125,left[1]-95,left[0]+125,left[1]+95),
                        radius=18,fill=(*PALE_GOLD,140),outline=(*GOLD,180),width=3)
    d.ellipse((left[0]-80,left[1]-45,left[0]+80,left[1]+45),
              outline=(*GOLD,190),width=4)
    centered(d,(left[0],h*.66),"DESIRED ANATOMY",font(FONT_SANS_BOLD,15),GOLD)
    # signal transformation
    middle=[(w*.43,h*.28),(w*.50,h*.52),(w*.57,h*.28)]
    glow_line(im,partial([left,*middle,right],q),CYAN,5,200,13)
    # cells self-build
    rng=random.Random(76)
    for i in range(80):
        a=rng.random()*math.tau
        rr=rng.uniform(20,95)
        x=right[0]+math.cos(a)*rr
        y=right[1]+math.sin(a)*rr*.58
        draw_cell(d,x,y,6,mix(CYAN,GREEN,q),160)
    centered(d,(right[0],h*.66),"CELLULAR IMPLEMENTATION",font(FONT_SANS_BOLD,15),GREEN)
    seal(im,"AN ANATOMICAL COMPILER WOULD TRANSLATE GOALS INTO SIGNALS",
         "not print the body, but communicate what should be built")


def vis_novel_body(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    rng=random.Random(63)
    q=ease(u)
    for i in range(95):
        a=rng.random()*math.tau
        rr=rng.uniform(100,270)
        x=lerp(cx+math.cos(a)*rr,cx+math.cos(a)*105,q)
        y=lerp(cy+math.sin(a)*rr*.62,cy+math.sin(a)*62,q)
        draw_cell(d,x,y,6,mix(CYAN,GREEN,q),160)
    if q>.55:
        d.ellipse((cx-120,cy-75,cx+120,cy+75),
                  outline=(*GREEN,int(200*q)),width=5)
        compass(d,cx,cy,28,GOLD,210,angle=t*.4)
    seal(im,"COMPETENCE CAN SURVIVE A RADICALLY NEW BODY",
         "evolved cells can solve problems in unfamiliar architectures")


def vis_origin_agnostic(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    origins=[
        ("EVOLVED",w*.22,GREEN),
        ("ENGINEERED",w*.50,CYAN),
        ("HYBRID",w*.78,VIOLET),
    ]
    q=ease(u)
    for i,(lab,x,col) in enumerate(origins):
        local=clamp(q*len(origins)-i)
        compass(d,x,h*.40,45,col,int(210*local),angle=-.8+i*.8)
        centered(d,(x,h*.67),lab,font(FONT_SANS_BOLD,16),col)
    seal(im,"AGENCY SHOULD BE MEASURED BY COMPETENCY, NOT ORIGIN",
         "unfamiliar embodiment does not imply absence of intelligence")


def vis_observer_scale(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    # zoom circles reveal different agents
    radii=[230,165,105,55]
    labels=["ORGANISM","TISSUE","CELL","MOLECULAR NETWORK"]
    colors=[GOLD,VIOLET,GREEN,CYAN]
    for i,(r,lab,col) in enumerate(zip(radii,labels,colors)):
        local=clamp(q*len(radii)-i)
        d.ellipse((cx-r,cy-r*.62,cx+r,cy+r*.62),
                  outline=(*col,int(180*local)),width=4)
        if local>.55:
            centered(d,(cx,cy-r*.62-18),lab,font(FONT_SANS_BOLD,13),col)
    seal(im,"THE AGENT YOU SEE DEPENDS ON THE SCALE OF OBSERVATION",
         "competence can be hidden by looking only above or below it")


def vis_cognitive_light_cone(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    origin=(w*.24,h*.52)
    q=ease(u)
    sizes=[
        ("CELL",w*.23,CYAN),
        ("TISSUE",w*.45,GREEN),
        ("ORGANISM",w*.70,GOLD),
        ("SOCIETY",w*.90,VIOLET),
    ]
    for i,(lab,x,col) in enumerate(sizes):
        local=clamp(q*len(sizes)-i)
        y=lerp(origin[1],h*.20,i/(len(sizes)-1))
        glow_circle(im,x,y,11+i*5,col,150,9)
        centered(d,(x,y+32),lab,font(FONT_SANS_BOLD,13),col)
        if i>0:
            px,py=sizes[i-1][1],lerp(origin[1],h*.20,(i-1)/(len(sizes)-1))
            d.line((px,py,x,y),fill=(*col,int(145*local)),width=3)
    gl=layer(im.size)
    gd=ImageDraw.Draw(gl)
    gd.polygon([origin,(w*.94,h*.10),(w*.94,h*.70)],
               fill=(*GOLD,int(35*q)))
    im.alpha_composite(gl)
    seal(im,"A COGNITIVE LIGHT CONE MEASURES THE REACH OF GOALS",
         "how far across space, time, and possibility can the agent care?")


def vis_failure_modes(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    labels=[
        ("TOO NARROW",CRIMSON,w*.23),
        ("TOO RIGID",VIOLET,w*.50),
        ("TOO DIFFUSE",SILVER,w*.77),
    ]
    q=ease(u)
    for i,(lab,col,x) in enumerate(labels):
        local=clamp(q*len(labels)-i)
        if i==0:
            d.ellipse((x-45,h*.40-60,x+45,h*.40+60),
                      outline=(*col,int(200*local)),width=5)
        elif i==1:
            d.rectangle((x-65,h*.40-65,x+65,h*.40+65),
                        outline=(*col,int(200*local)),width=5)
        else:
            for rr in range(30,120,22):
                d.ellipse((x-rr,h*.40-rr,x+rr,h*.40+rr),
                          outline=(*col,int(70*local*(1-rr/140))),width=3)
        centered(d,(x,h*.67),lab,font(FONT_SANS_BOLD,15),col)
    seal(im,"AGENCY FAILS IN MORE THAN ONE WAY",
         "goals can shrink, freeze, or lose coherent boundaries")


def vis_cancer_scale(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    rng=random.Random(82)
    q=ease(u)
    cells=[]
    for i in range(100):
        a=rng.random()*math.tau
        rr=(rng.random()**.58)*min(w,h)*.24
        cells.append((cx+math.cos(a)*rr*1.55,cy+math.sin(a)*rr))
    focus=(cx+80,cy+10)
    for x,y in cells:
        dist=math.dist((x,y),focus)
        col=CRIMSON if dist<65*q else CYAN
        draw_cell(d,x,y,6,col,160)
    r=lerp(230,58,q)
    d.ellipse((focus[0]-r,focus[1]-r,focus[0]+r,focus[1]+r),
              outline=(*CRIMSON,190),width=4)
    seal(im,"CANCER CAN BE SEEN AS A SHRINKING COGNITIVE BOUNDARY",
         "the cell pursues its own future instead of the tissue's",CRIMSON)


def vis_healing_scale(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    rng=random.Random(82)
    cells=[]
    for i in range(100):
        a=rng.random()*math.tau
        rr=(rng.random()**.58)*min(w,h)*.24
        cells.append((cx+math.cos(a)*rr*1.55,cy+math.sin(a)*rr))
    for x,y in cells:
        draw_cell(d,x,y,6,mix(CRIMSON,CYAN,q),160)
    r=lerp(60,235,q)
    d.ellipse((cx-r,cy-r*.62,cx+r,cy+r*.62),
              outline=(*GOLD,190),width=5)
    seal(im,"HEALING CAN MEAN RESTORING THE LARGER SELF",
         "reconnect local behavior to tissue-level goals")


def vis_brain_inherits(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    stages=[
        ("CELL",w*.18,CYAN),
        ("TISSUE",w*.38,GREEN),
        ("NERVE NET",w*.60,VIOLET),
        ("BRAIN",w*.82,GOLD),
    ]
    q=ease(u)
    for i,(lab,x,col) in enumerate(stages):
        local=clamp(q*len(stages)-i)
        r=18+i*12
        glow_circle(im,x,h*.40,r,col,int(120+90*local),11)
        centered(d,(x,h*.68),lab,font(FONT_SANS_BOLD,14),col)
        if i<len(stages)-1:
            arrow(d,(x+r+8,h*.40),(stages[i+1][1]-(30+(i+1)*12)-8,h*.40),
                  (*SILVER,int(150*local)),2,7)
    seal(im,"BRAINS DID NOT INVENT PROBLEM-SOLVING",
         "they accelerated, centralized, and redirected older cellular loops")


def vis_human_nested(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    draw_body(d,cx,cy,.78,INK,185)
    layers=[
        (45,CYAN,"CELLULAR"),
        (95,GREEN,"PHYSIOLOGICAL"),
        (150,GOLD,"BEHAVIORAL"),
        (225,VIOLET,"SOCIAL"),
    ]
    for r,col,lab in layers:
        d.ellipse((cx-r*q,cy-r*.62*q,cx+r*q,cy+r*.62*q),
                  outline=(*col,int(170*q)),width=3)
        if q>.62:
            centered(d,(cx,cy-r*.62*q-16),lab,font(FONT_SANS_BOLD,12),col)
    seal(im,"A HUMAN SELF IS A STACK OF NEGOTIATED AGENCIES",
         "personhood does not erase the competent lives below it")


def vis_tantric_bridge(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    left=(w*.30,h*.40)
    right=(w*.70,h*.40)
    q=ease(u)
    compass(d,*left,60,CYAN,210,angle=t*.25)
    centered(d,(left[0],h*.67),"NAVIGATION OF GOAL SPACES",
             font(FONT_SANS_BOLD,15),CYAN)
    for rr in range(35,155,28):
        d.ellipse((right[0]-rr,right[1]-rr*.60,
                   right[0]+rr,right[1]+rr*.60),
                  outline=(*GOLD,int(85*q*(1-rr/180))),width=3)
    centered(d,(right[0],h*.67),"MANIFESTATION OF A SELF",
             font(FONT_SANS_BOLD,15),GOLD)
    glow_line(im,partial([left,(w*.50,h*.22),right],q),VIOLET,4,180,11)
    seal(im,"LEVIN STUDIES HOW A SELF SCALES",
         "ABHINAVAGUPTA ASKS WHAT IT MEANS FOR ANY SELF TO APPEAR")


def vis_caution(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    claims=[
        ("CELLS REGULATE AND REMEMBER","SUPPORTED",GREEN),
        ("ALL CELLS FEEL LIKE HUMANS","NOT ESTABLISHED",CRIMSON),
        ("AGENCY OCCURS AT MANY SCALES","TESTABLE FRAMEWORK",CYAN),
        ("BIOLOGY PROVES NONDUALISM","NOT ESTABLISHED",CRIMSON),
    ]
    q=ease(u)
    for i,(claim,status,col) in enumerate(claims):
        local=clamp(q*len(claims)-i)
        y=h*(.23+i*.13)
        d.rounded_rectangle((w*.15,y-28,w*.85,y+28),
                            radius=14,
                            fill=(*mix(WHITE,col,.10),int(220*local)),
                            outline=(*col,int(180*local)),width=2)
        centered(d,(w*.39,y),claim,font(FONT_SANS_BOLD,14),INK)
        centered(d,(w*.72,y),status,font(FONT_SANS_BOLD,14),col)
    seal(im,"DO NOT CONFUSE COMPETENCY WITH HUMAN CONSCIOUSNESS",
         "measure what the system can do before claiming what it feels")


def vis_final(im,u,t,p):
    w,h=im.size
    d=ImageDraw.Draw(im)
    cx,cy=w*.50,h*.40
    q=ease(u)
    # five spaces converge into one agent
    colors=[CYAN,VIOLET,GREEN,GOLD,CRIMSON]
    origins=[
        (w*.16,h*.26),
        (w*.16,h*.54),
        (w*.36,h*.18),
        (w*.36,h*.62),
        (w*.50,h*.18),
    ]
    for i,(x,y) in enumerate(origins):
        glow_circle(im,x,y,10,colors[i],150,9)
        glow_line(im,partial([(x,y),(cx,cy)],q),colors[i],3,150,9)
    draw_body(d,cx+145,cy,.67,INK,int(210*q))
    compass(d,cx,cy,46,GOLD,int(210*q),angle=t*.22)
    if q>.7:
        centered(d,(cx,h*.69),"TAME",font(FONT_SERIF_BOLD,30),GOLD)
    seal(im,"CELLS THAT SOLVE PROBLEMS",
         "intelligence grows when competent parts learn to care about a larger future",GOLD)


VISUALS: dict[str,Callable] = {
    "loop":vis_problem_loop,
    "metabolic":vis_metabolic_space,
    "transcription":vis_transcription_space,
    "physiology":vis_physiological_space,
    "anatomy":vis_anatomical_space,
    "behavior":vis_behavior_space,
    "same":vis_same_algorithm,
    "memory":vis_cell_memory,
    "learning":vis_learning,
    "explore":vis_exploration,
    "agents":vis_multiscale_agents,
    "goals":vis_goal_hierarchy,
    "boundary":vis_boundary_expansion,
    "align":vis_conflict_alignment,
    "scarcity":vis_shared_scarcity,
    "topdown":vis_top_down_control,
    "microfail":vis_micromanagement_fail,
    "compiler":vis_anatomical_compiler,
    "novel":vis_novel_body,
    "origin":vis_origin_agnostic,
    "observer":vis_observer_scale,
    "lightcone":vis_cognitive_light_cone,
    "failure":vis_failure_modes,
    "cancer":vis_cancer_scale,
    "healing":vis_healing_scale,
    "brain":vis_brain_inherits,
    "human":vis_human_nested,
    "bridge":vis_tantric_bridge,
    "caution":vis_caution,
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
    Scene("Before brains",
          "Life was solving problems long before there were brains.",
          7.0,"loop",{}),
    Scene("Ancient loop",
          "Sense a state. Compare it with a preferred state. Act. Remember the result. Try again.",
          10.0,"loop",{}),
    Scene("Basal cognition",
          "Michael Levin calls the study of these ancient competencies basal cognition.",
          8.5,"loop",{}),

    Scene("Metabolic space",
          "A bacterium does not only move through physical space.",
          7.0,"metabolic",{}),
    Scene("Chemical navigation",
          "It must navigate metabolic states: energy, acidity, redox balance, nutrient availability.",
          9.0,"metabolic",{}),
    Scene("Preferred region",
          "The cell continually corrects toward a region in which its organization can persist.",
          9.0,"metabolic",{}),

    Scene("Transcriptional space",
          "The same cell also moves through transcriptional space.",
          7.5,"transcription",{}),
    Scene("Programs",
          "Different patterns of gene expression open different physiological possibilities.",
          8.5,"transcription",{}),
    Scene("Context",
          "The cell changes program when stress, neighbors, nutrients, or developmental signals change.",
          9.5,"transcription",{}),

    Scene("Physiological space",
          "It navigates physiological space.",
          6.5,"physiology",{}),
    Scene("Regulation",
          "Voltage, pH, calcium, osmotic pressure, and membrane transport must remain within workable ranges.",
          10.0,"physiology",{}),
    Scene("Homeostasis",
          "Homeostasis is not stillness. It is competent return after disturbance.",
          8.5,"physiology",{}),

    Scene("Anatomical space",
          "When cells join a tissue, a new problem space appears.",
          8.0,"anatomy",{}),
    Scene("Large form",
          "Now the collective must navigate toward organ position, polarity, proportion, and whole-body shape.",
          9.5,"anatomy",{}),
    Scene("No single cell",
          "No cell contains the organism. Yet their local actions converge toward anatomy.",
          9.0,"anatomy",{}),

    Scene("Behavioral space",
          "Animals later navigate the familiar space of behavior.",
          7.0,"behavior",{}),
    Scene("Path and threat",
          "They seek food, avoid danger, choose shelter, remember routes, and pursue social goals.",
          9.0,"behavior",{}),
    Scene("Older algorithm",
          "The brain did not invent the loop. It inherited a much older algorithm.",
          8.5,"brain",{}),

    Scene("Same logic",
          "Across these spaces, the logic repeats.",
          7.0,"same",{}),
    Scene("Deviation",
          "Detect deviation. Search among possible actions. Move toward a preferred region.",
          9.0,"same",{}),
    Scene("Different embodiment",
          "The substrate changes. The problem-solving architecture remains recognizable.",
          8.5,"same",{}),

    Scene("Memory",
          "Even memory begins below the level of recollection.",
          7.5,"memory",{}),
    Scene("Persistent state",
          "A cell can retain a changed state after the original signal disappears.",
          8.5,"memory",{}),
    Scene("Future response",
          "The past survives as a difference in what the cell does next.",
          8.0,"memory",{}),

    Scene("Learning",
          "Learning is not restricted to organisms that can describe what they learned.",
          8.0,"learning",{}),
    Scene("Landscape change",
          "Experience can reshape which responses become easy, difficult, likely, or suppressed.",
          9.0,"learning",{}),
    Scene("Future altered",
          "The system has learned when its future behavior changes because of its past.",
          8.5,"learning",{}),

    Scene("Novelty",
          "Competency is revealed most clearly when the familiar solution no longer works.",
          8.5,"explore",{}),
    Scene("Search",
          "A rigid mechanism repeats. A competent system explores.",
          7.5,"explore",{}),
    Scene("Alternative path",
          "It reaches a preferred state through a route evolution may never have explicitly encountered.",
          9.5,"explore",{}),

    Scene("Nested agents",
          "All known cognitive beings are collectives.",
          7.0,"agents",{}),
    Scene("Active parts",
          "Organisms contain organs, tissues, cells, and molecular networks that remain active problem-solvers.",
          9.5,"agents",{}),
    Scene("No indivisible mind",
          "There is no known mind made from perfectly passive parts.",
          8.0,"agents",{}),

    Scene("Wider goals",
          "Evolution scales agency by linking narrow goals into wider goals.",
          8.5,"goals",{}),
    Scene("From binding to care",
          "A molecule binds. A cell survives. A tissue repairs. An organism reproduces. A person can care about decades and strangers.",
          10.0,"goals",{}),
    Scene("Cognitive horizon",
          "The difference is not simply intelligence present or absent. It is the size of the horizon.",
          9.0,"lightcone",{}),

    Scene("Boundary expands",
          "When cells communicate, the computational boundary of the self can expand.",
          8.5,"boundary",{}),
    Scene("Neighbor becomes self",
          "A neighboring cell's condition becomes relevant to one's own action.",
          8.0,"boundary",{}),
    Scene("Collective concern",
          "Local homeostasis becomes anatomical homeostasis.",
          7.5,"boundary",{}),

    Scene("Alignment",
          "But collective intelligence is not guaranteed.",
          7.0,"align",{}),
    Scene("Conflicting futures",
          "Subunits can pursue incompatible futures.",
          7.5,"align",{}),
    Scene("Shared model",
          "A larger agent forms when parts share enough of a model of what is scarce, threatened, or worth preserving.",
          10.0,"scarcity",{}),

    Scene("Top-down control",
          "Larger selves do not need to micromanage every molecule.",
          8.0,"topdown",{}),
    Scene("Setpoint",
          "They alter setpoints, constraints, and signals.",
          7.5,"topdown",{}),
    Scene("Local solution",
          "Competent parts solve the implementation details.",
          7.5,"topdown",{}),

    Scene("Micromanagement",
          "This is why micromanagement fails in biology.",
          7.5,"microfail",{}),
    Scene("Too many variables",
          "No external controller can specify every cell movement, gene-expression change, and molecular collision.",
          10.0,"microfail",{}),
    Scene("Communicate goal",
          "The more powerful interface is to communicate a desired outcome to the collective.",
          9.0,"compiler",{}),

    Scene("Anatomical compiler",
          "Levin imagines an anatomical compiler.",
          7.0,"compiler",{}),
    Scene("Translate desire",
          "Specify a desired anatomy, then translate that goal into signals cells can understand.",
          9.0,"compiler",{}),
    Scene("Not printer",
          "The device would not print the body or command each cell.",
          8.0,"compiler",{}),
    Scene("Recruit competence",
          "It would recruit the body's own problem-solving capacities.",
          8.0,"compiler",{}),

    Scene("Novel embodiment",
          "This matters because competence can survive a radically new body.",
          8.5,"novel",{}),
    Scene("Reconfigured cells",
          "Cells removed from their ordinary context can organize into unfamiliar living architectures.",
          9.5,"novel",{}),
    Scene("Latent ability",
          "Their abilities are not exhausted by the body plan in which evolution first displayed them.",
          9.0,"novel",{}),

    Scene("Origin agnostic",
          "TAME asks us to become origin-agnostic.",
          7.0,"origin",{}),
    Scene("Evolved or engineered",
          "An agent may be evolved, engineered, hybrid, synthetic, or assembled from living cells.",
          9.0,"origin",{}),
    Scene("Measure competency",
          "The relevant question is what spaces it can navigate, what goals it can pursue, and how flexibly it handles error.",
          10.0,"origin",{}),

    Scene("Observer scale",
          "Agency can disappear when we look at the wrong scale.",
          8.0,"observer",{}),
    Scene("Too close",
          "Zoom too far in, and an organism becomes molecular noise.",
          7.5,"observer",{}),
    Scene("Too far",
          "Zoom too far out, and cellular decisions become invisible beneath anatomy.",
          8.0,"observer",{}),
    Scene("Scale choice",
          "The observer must choose a scale at which goals, memories, and corrections become legible.",
          9.5,"observer",{}),

    Scene("Light cone",
          "Levin's cognitive light cone measures the reach of an agent's concern.",
          8.0,"lightcone",{}),
    Scene("Space and time",
          "How far across space and time can it detect error, preserve value, and act?",
          9.0,"lightcone",{}),
    Scene("Small cone",
          "A cell protects a local physiological future.",
          7.5,"lightcone",{}),
    Scene("Large cone",
          "A person can organize action around a future generation.",
          7.5,"lightcone",{}),

    Scene("Failure modes",
          "Not every expansion produces wisdom.",
          7.0,"failure",{}),
    Scene("Narrow",
          "A self can become too narrow.",
          6.0,"failure",{}),
    Scene("Rigid",
          "It can become too rigid to update.",
          6.0,"failure",{}),
    Scene("Diffuse",
          "Or too diffuse to coordinate action.",
          6.0,"failure",{}),

    Scene("Cancer",
          "Cancer can be understood partly as a shrinking cognitive boundary.",
          8.5,"cancer",{}),
    Scene("Local future",
          "The cell pursues proliferation while abandoning the anatomical future of the tissue.",
          9.0,"cancer",{}),
    Scene("Defection",
          "It has not lost all competency. Its competency has defected to a smaller self.",
          9.0,"cancer",{}),

    Scene("Healing",
          "Healing may therefore require more than destroying the rebel.",
          8.0,"healing",{}),
    Scene("Reconnect",
          "Restore communication, and local behavior may rejoin tissue-level goals.",
          8.5,"healing",{}),
    Scene("Larger self restored",
          "The cure becomes a restoration of the larger self.",
          7.5,"healing",{}),

    Scene("Brain inheritance",
          "Brains arrived late.",
          6.0,"brain",{}),
    Scene("Ancient loops",
          "They inherited homeostasis, memory, prediction, exploration, and collective control from older biological systems.",
          10.0,"brain",{}),
    Scene("Acceleration",
          "The nervous system accelerated the loop and projected it into larger spaces.",
          8.5,"brain",{}),

    Scene("Human stack",
          "A human being is not one agency replacing all others.",
          8.0,"human",{}),
    Scene("Negotiated agencies",
          "You are cellular, physiological, behavioral, and social agencies negotiating one life.",
          9.5,"human",{}),
    Scene("Coherent person",
          "The coherent person is a remarkable achievement of coordination, not evidence of indivisibility.",
          9.0,"human",{}),

    Scene("Bridge",
          "This is where Levin's biology can meet Kashmir Śaivism without pretending to prove it.",
          9.0,"bridge",{}),
    Scene("Scaling self",
          "Levin studies how active parts become a larger self with wider goals.",
          8.0,"bridge",{}),
    Scene("Appearing self",
          "Abhinavagupta asks what it means for self, goal, world, and relation to appear at all.",
          9.0,"bridge",{}),
    Scene("Complement",
          "One studies the architecture of agency. The other studies the luminosity of manifestation.",
          9.0,"bridge",{}),

    Scene("Discipline",
          "The language must remain disciplined.",
          7.0,"caution",{}),
    Scene("Operational cognition",
          "Cells regulate, remember, explore, and correct.",
          7.5,"caution",{}),
    Scene("Experience open",
          "These facts do not establish that every cell experiences a private world like ours.",
          9.0,"caution",{}),
    Scene("Measure first",
          "Measure competency first. Leave phenomenology open where evidence is incomplete.",
          8.5,"caution",{}),

    Scene("Return",
          "Life was solving problems before brains.",
          7.0,"final",{}),
    Scene("Five spaces",
          "Metabolic, transcriptional, physiological, anatomical, behavioral.",
          8.0,"final",{}),
    Scene("Larger future",
          "At every scale, a system detects error and moves toward a future it can preserve.",
          9.5,"final",{}),
    Scene("Closing",
          "Cells that solve problems become tissues that remember form, bodies that pursue goals, and minds that can ask what kind of larger self they are willing to become.",
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
    executable=shutil.which("ffmpeg")
    if not executable:
        raise RuntimeError("ffmpeg is required but was not found on PATH")
    return executable


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
        for output_index,frame_index in enumerate(samples):
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
    concat_file=OUTPUT/"concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in paths),
        encoding="utf-8"
    )
    output=OUTPUT/"cells_that_solve_problems.mp4"
    subprocess.run([
        ffmpeg_path(),"-y",
        "-f","concat","-safe","0",
        "-i",str(concat_file),
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

    path=OUTPUT/"narration_timeline.json"
    path.write_text(json.dumps({
        "title":"cells that solve problems",
        "scene_count":len(SCENES),
        "runtime_seconds":round(cursor,3),
        "shot_duration_range":[5,10],
        "continuity_object":"cyan compass becoming gold cognitive light cone",
        "scenes":records,
    },indent=2,ensure_ascii=False),encoding="utf-8")
    return path


def make_contact_sheet(width,height):
    thumb_width=320
    thumb_height=int(thumb_width*height/width)
    columns=4
    rows=math.ceil(len(SCENES)/columns)
    cell_height=thumb_height+48

    sheet=Image.new(
        "RGB",
        (columns*thumb_width,rows*cell_height),
        IVORY
    )
    d=ImageDraw.Draw(sheet)
    label_font=font(FONT_SANS_BOLD,14)

    for index,scene in enumerate(SCENES,1):
        frame_count=max(2,round(scene.duration*DEFAULT_FPS))
        image=render_frame(
            scene,int(frame_count*.72),frame_count,
            width,height,index*10000+72
        )
        image.thumbnail((thumb_width,thumb_height))
        slot=index-1
        x=(slot%columns)*thumb_width
        y=(slot//columns)*cell_height
        sheet.paste(image,(x,y))
        d.text(
            (x+8,y+thumb_height+7),
            f"{index:02d}  {scene.title}",
            font=label_font,
            fill=INK
        )

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
