#!/usr/bin/env python3
"""
THE BODY CAN REMEMBER A SHAPE IT IS NOT WEARING
A complete Platinum-house procedural visual essay.

Source adapted from:
expansion-essays/the_body_can_remember_a_shape_it_is_not_wearing.md

DESIGN CONTRACT
---------------
• Every shot lasts 5–10 seconds.
• Every shot visibly performs the narrated operation.
• White regenerative-biology field; dark field only for attractor memory.
• No static slide layouts and no decorative loops.
• Gold = hidden target anatomy / remembered future form
• Cyan = present anatomy / visible physiological state
• Crimson = perturbation / wound / competing anatomical attractor
• Green = restored wild-type organization
• Violet = latent bioelectric state / cryptic memory
• Graphite = material tissue / geometry / physical body
• Sparse typography: terms function as seals, never paragraphs.
• Each mature frame around u=0.72 should work as a still.
• Continuity object: a gold hidden body-plan remains beneath the visible body.
• Current anatomy and future regenerative response must remain visually distinct.
• Scientific claims remain narrow: planarian bioelectric memory, not human mystical memory.

OUTPUT
------
output_hidden_shape_memory/
  frames/scene_001/*.jpg
  scenes/scene_001.mp4
  the_body_can_remember_a_shape_it_is_not_wearing.mp4
  narration_timeline.json
  contact_sheet.jpg
"""

from __future__ import annotations
import argparse, json, math, random, shutil, subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT/"output_hidden_shape_memory"
FRAMES=OUTPUT/"frames"
SCENES_DIR=OUTPUT/"scenes"

DEFAULT_WIDTH=1280
DEFAULT_HEIGHT=720
DEFAULT_FPS=10

WHITE=(248,247,243); INK=(29,31,35); SOFT=(84,88,94)
SILVER=(177,184,190); PALE_SILVER=(224,227,229)
CYAN=(55,153,181); PALE_CYAN=(192,226,233)
GOLD=(194,153,68); PALE_GOLD=(235,218,175)
GREEN=(70,139,98); PALE_GREEN=(194,225,206)
CRIMSON=(158,52,66); PALE_CRIMSON=(230,192,198)
VIOLET=(104,79,146); PALE_VIOLET=(216,205,232)
VOID=(22,25,31)

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
    rng=np.random.default_rng(seed); base=VOID if dark else WHITE
    arr=np.empty((h,w,3),np.float32); arr[:]=base
    arr += rng.normal(0,1.05 if not dark else 1.7,(h,w,1))
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8),"RGB").convert("RGBA")
def layer(im): return Image.new("RGBA",im.size,(0,0,0,0))
def ctext(d,xy,text,f,fill): d.text(xy,text,font=f,fill=fill,anchor="mm")
def seal(im,title,subtitle="",dark=False,color=INK):
    w,h=im.size; d=ImageDraw.Draw(im)
    ctext(d,(w/2,h*.875),title,font(FSB,max(22,int(h*.042))),WHITE if dark else color)
    if subtitle: ctext(d,(w/2,h*.925),subtitle,font(FSS,max(13,int(h*.020))),PALE_SILVER if dark else SOFT)
def border(im,dark=False):
    w,h=im.size
    ImageDraw.Draw(im).rounded_rectangle((25,25,w-25,h-25),radius=17,outline=(*(WHITE if dark else INK),42),width=2)
def glow_line(im,pts,col,width=4,blur=14,alpha=220):
    if len(pts)<2:return
    ov=layer(im); d=ImageDraw.Draw(ov)
    d.line(pts,fill=(*col,alpha),width=width,joint="curve")
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(blur))); im.alpha_composite(ov)
def glow_circle(im,x,y,r,col,alpha=180,blur=15):
    ov=layer(im); d=ImageDraw.Draw(ov)
    d.ellipse((x-r,y-r,x+r,y+r),fill=(*col,alpha))
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(im).ellipse((x-r*.38,y-r*.38,x+r*.38,y+r*.38),fill=(*mix(col,WHITE,.3),230))
def partial(pts,p):
    p=clamp(p)
    if len(pts)<2:return pts
    lens=[math.dist(a,b) for a,b in zip(pts[:-1],pts[1:])]
    total=sum(lens); target=total*p; out=[pts[0]]; walked=0
    for i,L in enumerate(lens):
        if walked+L<=target: out.append(pts[i+1]); walked+=L
        else:
            q=(target-walked)/L if L else 0
            a,b=pts[i],pts[i+1]
            out.append((lerp(a[0],b[0],q),lerp(a[1],b[1],q))); break
    return out
def arrow(d,a,b,col=INK,width=3,head=11):
    d.line((*a,*b),fill=col,width=width)
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for delta in (2.55,-2.55):
        p=(b[0]+math.cos(ang+delta)*head,b[1]+math.sin(ang+delta)*head)
        d.line((*b,*p),fill=col,width=width)
def cell(d,x,y,r,col,alpha=210,nucleus=True):
    d.ellipse((x-r,y-r,x+r,y+r),fill=(*mix(WHITE,col,.16),alpha),outline=(*col,min(255,alpha+10)),width=3)
    if nucleus:d.ellipse((x-r*.25,y-r*.25,x+r*.25,y+r*.25),fill=(*mix(col,VIOLET,.35),150))
def planarian(d,cx,cy,length,height,col,alpha=200,width=4,heads=1):
    pts=[]
    for i in range(120):
        q=i/119; x=lerp(cx-length/2,cx+length/2,q); taper=math.sin(q*math.pi)**.68
        pts.append((x,cy-height*taper*.5))
    for i in range(119,-1,-1):
        q=i/119; x=lerp(cx-length/2,cx+length/2,q); taper=math.sin(q*math.pi)**.68
        pts.append((x,cy+height*taper*.5))
    d.line(pts+[pts[0]],fill=(*col,alpha),width=width)
    if heads==1:
        d.ellipse((cx+length/2-10,cy-10,cx+length/2+10,cy+10),fill=(*col,alpha))
    else:
        d.ellipse((cx+length/2-10,cy-10,cx+length/2+10,cy+10),fill=(*col,alpha))
        d.ellipse((cx-length/2-10,cy-10,cx-length/2+10,cy+10),fill=(*col,alpha))
def tissue_points(w,h,cols=14,rows=8):
    out=[]
    for j in range(rows):
        for i in range(cols):
            out.append((w*(.12+i*(.76/(cols-1))),h*(.18+j*(.48/(rows-1))),i,j))
    return out
def electric_field(im,phase=0,alpha=80):
    w,h=im.size
    for j in range(9):
        pts=[]
        for i in range(180):
            q=i/179
            x=lerp(w*.08,w*.92,q)
            y=h*(.16+j*.06)+math.sin(q*math.tau*2+phase+j*.45)*10
            pts.append((x,y))
        glow_line(im,pts,CYAN,2,7,alpha)

@dataclass
class Scene:
    title:str; narration:str; duration:float; visual:str; params:dict

def v_hidden_shape(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    # visible one-head body
    planarian(d,w*.5,h*.42,w*.52,h*.18,CYAN,210,5,1)
    # hidden two-head target beneath
    q=smooth(.25,.92,u)
    planarian(d,w*.5,h*.42,w*.55,h*.20,GOLD,int(40+130*q),3,2)
    seal(im,"THE BODY IS WEARING ONE SHAPE","while carrying the memory of another")

def v_cut_reveal(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    if q<.35:
        planarian(d,w*.5,h*.42,w*.52,h*.18,CYAN,210,5,1)
        x=lerp(w*.32,w*.68,q/.35)
        d.line((x,h*.23,x,h*.61),fill=(*CRIMSON,220),width=5)
    else:
        pieces=[w*.25,w*.50,w*.75]; local=(q-.35)/.65
        for i,x in enumerate(pieces):
            heads=2 if i==1 and p.get("two",True) else 1
            planarian(d,x,h*.42,lerp(w*.11,w*.22,local),lerp(h*.07,h*.13,local),mix(CRIMSON,GREEN,local),200,4,heads)
    seal(im,"THE WOUND ACTS LIKE AN EXAMINATION","the hidden attractor supplies the answer")

def v_network_memory(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    electric_field(im,t*.12,95)
    pts=tissue_points(w,h)
    for x,y,i,j in pts:
        v=.5+.5*math.sin(i*.55+j*.72+t*.2)
        cell(d,x,y,9,mix(CYAN,VIOLET,v),180,False)
        if i<13:d.line((x+9,y,x+w*.76/13-9,y),fill=(*CYAN,60),width=2)
    # hidden gold rule across network
    q=ease(u)
    d.arc((w*.25,h*.24,w*.75,h*.61),180,360,fill=(*GOLD,int(180*q)),width=5)
    seal(im,"THE PATTERN BELONGS TO NO SINGLE CELL","it exists across their relation")

def v_switch_memory(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.27,h*.42); right=(w*.73,h*.42)
    planarian(d,*left,w*.28,h*.13,GREEN,190,4,1)
    planarian(d,*right,w*.28,h*.13,CRIMSON,190,4,2)
    # toggle
    q=ease(u)
    d.rounded_rectangle((w*.44,h*.30,w*.56,h*.54),radius=25,fill=(*PALE_SILVER,190),outline=(*INK,150),width=3)
    knob_y=lerp(h*.48,h*.35,q)
    d.ellipse((w*.47,knob_y-18,w*.53,knob_y+18),fill=(*GOLD,210))
    ctext(d,(w*.5,h*.65),"MULTISTABLE SWITCH",font(FSSB,int(h*.015)),GOLD)
    seal(im,"A BRIEF INPUT CAN CHANGE A FUTURE ANATOMICAL DECISION","the state persists after the hand leaves")

def v_memory_not_picture(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.42); right=(w*.72,h*.42)
    # crossed-out picture
    d.rounded_rectangle((left[0]-100,left[1]-80,left[0]+100,left[1]+80),radius=20,outline=(*CRIMSON,170),width=4)
    planarian(d,left[0],left[1],140,55,GOLD,150,3,2)
    q=smooth(.35,.9,u)
    d.line((left[0]-120,left[1]-95,left[0]+120,left[1]+95),fill=(*CRIMSON,int(220*q)),width=6)
    # rule
    d.rounded_rectangle((right[0]-135,right[1]-80,right[0]+135,right[1]+80),radius=20,fill=(*PALE_CYAN,210),outline=(*CYAN,180),width=3)
    ctext(d,(right[0],right[1]-18),"WHEN INJURED",font(FSSB,int(h*.016)),CYAN)
    ctext(d,(right[0],right[1]+22),"COMPLETE THIS RELATION",font(FSSB,int(h*.016)),GOLD)
    seal(im,"THE MEMORY MAY BE MORE LIKE A RULE THAN A PICTURE","past state becomes a reactivatable instruction")

def v_counterfactual_identity(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    current=(w*.30,h*.42); future=(w*.72,h*.42)
    planarian(d,*current,w*.28,h*.13,CYAN,200,4,1)
    planarian(d,*future,w*.28,h*.13,GOLD,160,4,2)
    # question paths
    q=ease(u)
    paths=[[(current[0]+120,current[1]),(w*.5,h*.28),(future[0]-120,future[1])],
           [(current[0]+120,current[1]),(w*.5,h*.55),(future[0]-120,future[1])]]
    for i,path in enumerate(paths):
        glow_line(im,partial(path,q),GOLD if i==0 else VIOLET,4,11,170)
    seal(im,"IDENTITY INCLUDES COUNTERFACTUALS","what would this body rebuild if disturbed?")

def v_polling_network(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    pts=tissue_points(w,h,11,7)
    for x,y,i,j in pts:cell(d,x,y,8,CYAN,170,False)
    q=ease(u)
    # long-range polling arcs
    for i in range(0,len(pts),8):
        a=pts[i]; b=pts[(i*3+17)%len(pts)]
        glow_line(im,partial([a,(w*.5,h*.28),b],q),GOLD,2,8,110)
    seal(im,"LOCAL CELLS POLL THE LARGER NETWORK","the whole becomes partially available to the parts")

def v_local_captured_by_goal(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    d.ellipse((w*.14,h*.15,w*.86,h*.70),outline=(*GOLD,150),width=5)
    rng=random.Random(33)
    for i in range(70):
        a=rng.random()*math.tau; rr=math.sqrt(rng.random())
        x=cx+math.cos(a)*w*.28*rr; y=cy+math.sin(a)*h*.23*rr
        cell(d,x,y,7,mix(CYAN,GREEN,i/70),160,False)
    q=ease(u)
    # one wound cell differentiates
    x,y=w*.35,h*.43
    cell(d,x,y,22,mix(CRIMSON,GREEN,q),220)
    arrows=[(w*.55,h*.26,GREEN),(w*.58,h*.42,CYAN),(w*.55,h*.58,VIOLET)]
    for ax,ay,col in arrows: arrow(d,(x+22,y),(ax,ay),col,3,9)
    seal(im,"MULTICELLULARITY IS LOCAL COMPETENCE CAPTURED BY A LARGER GOAL","the cell contributes to a body it cannot inhabit alone")

def v_turnover_memory(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42
    planarian(d,cx,cy,w*.55,h*.18,GOLD,150,4,1)
    rng=random.Random(55)
    q=ease(u)
    for i in range(100):
        a=rng.random()*math.tau; rr=math.sqrt(rng.random())
        x=cx+math.cos(a)*w*.25*rr; y=cy+math.sin(a)*h*.08*rr
        replace=(i/100+q)%1
        col=mix(CRIMSON,CYAN,replace)
        cell(d,x,y,5,col,150,False)
    seal(im,"THE MESSAGE PERSISTS WHILE THE MESSENGERS CHANGE","memory must survive turnover and geometry change")

def v_reset_attractor(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    # two basins
    pts=[]
    for i in range(260):
        q=i/259; x=lerp(w*.08,w*.92,q)
        y=h*.68-h*.20*math.exp(-((q-.30)/.13)**2)-h*.22*math.exp(-((q-.72)/.13)**2)
        pts.append((x,y))
    d.line(pts,fill=(*PALE_SILVER,190),width=4)
    q=ease(u); x=lerp(w*.72,w*.30,q)
    y=h*.68-h*.20*math.exp(-(((x/w)-.30)/.13)**2)-h*.22*math.exp(-(((x/w)-.72)/.13)**2)
    glow_circle(im,x,y-12,14,mix(CRIMSON,GREEN,q),190,10)
    arrow(d,(w*.72,h*.45),(w*.42,h*.45),GOLD,5,13)
    seal(im,"PERSISTENT DOES NOT MEAN FIXED","physiological memory can be edited",dark=True)

def v_morphoceutical(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.25,h*.42); right=(w*.75,h*.42)
    # manual cell control
    for i in range(6):
        a=i*math.tau/6
        x=left[0]+math.cos(a)*65; y=left[1]+math.sin(a)*50
        cell(d,x,y,13,CRIMSON,180)
        arrow(d,(left[0],left[1]),(x,y),CRIMSON,2,8)
    # control layer
    electric_field(im,t*.12,50)
    planarian(d,right[0],right[1],w*.28,h*.13,GOLD,170,4,1)
    glow_circle(im,right[0],right[1],18,GREEN,150,11)
    seal(im,"CHANGE THE CONTROL LAYER, NOT EVERY CELL","the promise of morphoceuticals remains a research program")

def v_identity_layers(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    layers=[("GENOME",VIOLET,55),("PHYSIOLOGY",CYAN,95),("ANATOMY",GOLD,140),("RESPONSE",GREEN,190)]
    cx,cy=w*.5,h*.42
    for i,(txt,col,r) in enumerate(layers):
        q=smooth(i*.12,.62+i*.07,u)
        d.ellipse((cx-r*q,cy-r*.62*q,cx+r*q,cy+r*.62*q),outline=(*col,int(185*q)),width=4)
        if q>.66:ctext(d,(cx,cy-r*.62*q-17),txt,font(FSSB,int(h*.013)),col)
    seal(im,"THE BODY'S IDENTITY IS DISTRIBUTED","material, memory, anatomy, and response")

def v_scientific_narrowness(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    claims=["PLATONIC FORM","FUNDAMENTAL CONSCIOUSNESS","HUMANLIKE CELL BELIEFS"]
    for i,txt in enumerate(claims):
        y=h*(.28+i*.14)
        ctext(d,(w*.72,y),txt,font(FSB,int(h*.018)),CRIMSON)
        q=smooth(.25+i*.1,.9,u)
        d.line((w*.57,y,w*.87,y),fill=(*CRIMSON,int(220*q)),width=5)
    d.rounded_rectangle((w*.10,h*.23,w*.45,h*.60),radius=24,fill=(*PALE_CYAN,220),outline=(*CYAN,180),width=3)
    ctext(d,(w*.275,h*.34),"TEMPORARY BIOELECTRIC",font(FSSB,int(h*.016)),CYAN)
    ctext(d,(w*.275,h*.41),"PERTURBATION CAN CREATE",font(FSSB,int(h*.016)),CYAN)
    ctext(d,(w*.275,h*.48),"PERSISTENT REWRITEABLE",font(FSSB,int(h*.016)),GOLD)
    ctext(d,(w*.275,h*.55),"REGENERATIVE OUTCOMES",font(FSSB,int(h*.016)),GREEN)
    seal(im,"THE NARROW CLAIM IS ALREADY STRANGE ENOUGH","precision protects the wonder")

def v_human_analogy(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    states=[("CALM",CYAN),("DEFENSIVE STATE",CRIMSON),("HIDDEN SKILL",GOLD),("SCAR HISTORY",VIOLET)]
    for i,(txt,col) in enumerate(states):
        x=w*(.18+i*.21); q=smooth(i*.10,.60+i*.07,u)
        d.ellipse((x-42*q,h*.40-42*q,x+42*q,h*.40+42*q),fill=(*mix(WHITE,col,.15),int(220*q)),outline=(*col,int(180*q)),width=3)
        if q>.66:ctext(d,(x,h*.60),txt,font(FSSB,int(h*.012)),col)
    seal(im,"PRESENT FORM DOES NOT EXHAUST STORED POSSIBILITY","the analogy is structural, not mechanistic")

def v_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    planarian(d,w*.5,h*.42,w*.52,h*.18,CYAN,210,5,1)
    planarian(d,w*.5,h*.42,w*.57,h*.21,GOLD,int(55+130*q),3,2)
    # future-response arrows
    for i in range(10):
        a=-math.pi/2+i*math.pi/9
        x=w*.5+math.cos(a)*w*.30; y=h*.42+math.sin(a)*h*.24
        glow_line(im,partial([(w*.5,h*.42),(x,y)],smooth(i*.05,.88,u)),mix(CYAN,GOLD,i/9),2,8,110)
    seal(im,"THE BODY CAN REMEMBER A SHAPE IT IS NOT WEARING","what it is includes how it will answer disruption",color=GREEN)

VISUALS:dict[str,Callable]={
    "hidden":v_hidden_shape,
    "cut":v_cut_reveal,
    "network":v_network_memory,
    "switch":v_switch_memory,
    "rule":v_memory_not_picture,
    "counterfactual":v_counterfactual_identity,
    "poll":v_polling_network,
    "goal":v_local_captured_by_goal,
    "turnover":v_turnover_memory,
    "reset":v_reset_attractor,
    "morpho":v_morphoceutical,
    "layers":v_identity_layers,
    "narrow":v_scientific_narrowness,
    "human":v_human_analogy,
    "final":v_final,
}

SCENES=[
Scene("Ordinary body","A flatworm can look completely ordinary while carrying the memory of another body.",9.0,"hidden",{}),
Scene("One head one tail","One head. One tail. Normal movement. Normal anatomy.",8.0,"hidden",{}),
Scene("Cut","Then it is cut.",5.0,"cut",{}),
Scene("Different answers","Some fragments rebuild the expected animal. Others produce two heads.",8.0,"cut",{"two":True}),
Scene("Hidden before knife","The hidden difference was present before the knife.",7.0,"hidden",{}),
Scene("Wearing one remembering another","The body was wearing one shape while remembering another.",8.0,"hidden",{}),

Scene("Regeneration problem","A middle fragment must determine front, back, missing structures, amount, and stopping.",9.0,"poll",{}),
Scene("Genes matter","Genes, stem cells, patterning pathways, nerves, and muscles all matter.",8.0,"network",{}),
Scene("Genome not blueprint","The genome alone does not specify the answer like a blueprint.",8.0,"rule",{}),
Scene("Same genome","The same genome can support more than one regenerative outcome.",8.0,"switch",{}),
Scene("Which whole","The question is which whole the collective is trying to restore.",7.5,"counterfactual",{}),

Scene("Bioelectricity","One important answer involves bioelectricity.",6.0,"network",{}),
Scene("Membrane voltage","Every living cell maintains voltage through ion channels and pumps.",8.0,"network",{}),
Scene("Gap junctions","Gap junctions allow ions and small signals to pass between neighbors.",8.0,"network",{}),
Scene("Electrical tissue","A tissue can form an electrical network.",6.5,"network",{}),
Scene("No single owner","The pattern belongs to no single cell.",6.5,"network",{}),
Scene("Relational state","It exists across their relation.",6.0,"network",{}),

Scene("2017 perturbation","A brief perturbation of bioelectric communication produced persistent regenerative change.",9.0,"switch",{}),
Scene("No DNA rewrite","The treatment did not permanently rewrite DNA.",7.0,"switch",{}),
Scene("No permanent treatment","It did not remain present during later injuries.",7.0,"switch",{}),
Scene("Two headed outcome","Some trunk fragments regenerated with two heads.",7.0,"switch",{}),
Scene("Normal but altered","Some looked normal yet carried an altered future.",8.0,"hidden",{}),
Scene("Cut again","When cut again, their fragments repeated the altered outcome mixture.",9.0,"cut",{"two":True}),
Scene("Future decision changed","A temporary intervention changed a future anatomical decision.",8.0,"switch",{}),
Scene("Current body incomplete","Current anatomy did not reveal the system's whole state.",8.0,"hidden",{}),

Scene("Multistable switch","The result was described as a multistable anatomical switch.",8.0,"switch",{}),
Scene("More than one configuration","The system can settle into more than one enduring configuration.",8.0,"switch",{}),
Scene("Light switch analogy","A brief input selects a state that persists after the hand leaves.",8.0,"switch",{}),
Scene("Biological attractors","Biological networks can possess attractors.",7.0,"reset",{}),
Scene("Head tail attractor","One attractor guides head-tail anatomy.",6.5,"reset",{}),
Scene("Head head attractor","Another guides head-head anatomy.",6.5,"reset",{}),
Scene("Interpret wound","The tissue interprets the wound from inside a stabilized physiological state.",9.0,"rule",{}),

Scene("Memory useful","This is why the word memory becomes useful.",6.5,"rule",{}),
Scene("Past alters future","A past event leaves a stable, reactivatable trace changing later action.",8.5,"rule",{}),
Scene("Not conscious recall","This is not necessarily conscious recollection.",7.0,"rule",{}),
Scene("No worm picture","No evidence suggests the worm recalls a picture of two heads.",8.0,"rule",{}),
Scene("Thermostat setpoint","A thermostat can retain a set point without remembering winter.",7.0,"rule",{}),
Scene("Tissue target","A tissue can retain target anatomy without imagining its future.",8.0,"rule",{}),

Scene("Mystical language danger","Biological language can become mystical by accident.",7.0,"narrow",{}),
Scene("Decide know remember","Cells decide, tissues know, bodies remember.",7.0,"rule",{}),
Scene("Useful metaphors","These metaphors can reveal functional structure.",7.0,"rule",{}),
Scene("Tiny human danger","They can also smuggle a tiny human mind into the system.",8.0,"narrow",{}),
Scene("No miniature worm","Voltage does not contain a miniature worm image.",7.0,"rule",{}),
Scene("Instructive polarity","Distributed state carries instructive information about polarity and head number.",9.0,"network",{}),
Scene("Rule relation","The memory may be a rule: when injured, complete the body according to this relation.",9.0,"rule",{}),

Scene("Normal now altered later","A normal-looking worm can carry an altered future.",8.0,"hidden",{}),
Scene("Present and response split","Visible present and preferred future response can come apart.",8.0,"counterfactual",{}),
Scene("Bridge test","A bridge can look stable until weight tests it.",6.5,"counterfactual",{}),
Scene("Belief reactivation","A belief can seem absent until conflict reactivates it.",7.0,"human",{}),
Scene("Cryptic attractor","A biological attractor can remain cryptic until injury forces an answer.",8.0,"counterfactual",{}),
Scene("Wound exam","The wound acts like an examination.",6.0,"cut",{}),
Scene("Memory answer","The hidden memory supplies the answer.",6.0,"rule",{}),

Scene("Meaning of anatomy","This changes the meaning of anatomy.",6.5,"counterfactual",{}),
Scene("Shape not final truth","Current shape is not the final truth of a body.",7.0,"counterfactual",{}),
Scene("Capacities beneath form","Beneath visible form are capacities, constraints, and target states.",8.5,"layers",{}),
Scene("Range of defended forms","The body includes the shapes it will defend, repair, or regenerate.",8.5,"counterfactual",{}),
Scene("Identity counterfactual","Identity includes counterfactuals.",6.5,"counterfactual",{}),
Scene("What if cut","What would this system do if cut here?",6.0,"counterfactual",{}),
Scene("What rebuild","What would it rebuild if one part vanished?",6.0,"counterfactual",{}),
Scene("Correct or accept","Which deviations would it correct, and which accept as normal?",8.0,"counterfactual",{}),

Scene("Spatial information","Regeneration is a problem of spatial information.",7.0,"poll",{}),
Scene("Where am I","Cells must determine where they are and what remains elsewhere.",8.0,"poll",{}),
Scene("Long range signals","Nerves and gap junctions participate in long-range coordination.",8.0,"poll",{}),
Scene("No master cell","No master cell must supervise the project.",7.0,"poll",{}),
Scene("Distributed information","Information can be distributed.",6.0,"poll",{}),
Scene("Poll network","Local cells poll the larger network.",6.5,"poll",{}),
Scene("Whole available","The body coordinates by making the whole partially available to parts.",8.5,"poll",{}),

Scene("Larger biological self","This coordination creates a larger biological self.",7.0,"goal",{}),
Scene("Local survival","Each cell regulates itself and pursues local survival.",7.0,"goal",{}),
Scene("Larger outcome","Regeneration requires action for an anatomical outcome larger than any cell.",9.0,"goal",{}),
Scene("Differentiate by pattern","A wound cell becomes tissue according to a pattern beyond its boundary.",8.5,"goal",{}),
Scene("Future body","The cell contributes to a future body it cannot inhabit alone.",8.0,"goal",{}),
Scene("Multicellularity","Multicellularity is local competence captured by a larger goal.",8.5,"goal",{}),

Scene("Local and collective","Bioelectric states can be both local and collective.",7.0,"network",{}),
Scene("Individual channels","Ion channels operate in individual membranes.",6.5,"network",{}),
Scene("Tissue spread","Gap junctions spread voltage and signaling across tissue.",7.5,"network",{}),
Scene("Global pattern stable","Feedback stabilizes a global pattern while cells change.",8.0,"turnover",{}),
Scene("General neural analogy","This resembles neural memory only at a general network level.",8.0,"network",{}),
Scene("Ancient language","Evolution may have used electrical coordination before nervous systems.",8.5,"network",{}),
Scene("Brain inherited voltage","The brain inherited an ancient language and accelerated it.",8.0,"network",{}),

Scene("Robust patterns","Bioelectric patterns must survive changes in cell number and geometry.",8.0,"turnover",{}),
Scene("Arrangement destroyed","Injury destroys exact arrangements.",6.5,"turnover",{}),
Scene("Information survives material","The system must preserve information while its material carriers change.",8.5,"turnover",{}),
Scene("City repair","Imagine repairing a city while roads, maps, workers, and communication lines change.",9.0,"turnover",{}),
Scene("Memory survives turnover","Their memory must survive turnover.",7.0,"turnover",{}),
Scene("Message persists","The message persists while the messengers change.",7.0,"turnover",{}),

Scene("Reset possible","The altered state could also be reset.",6.0,"reset",{}),
Scene("Wild type restored","Further manipulation restored wild-type regenerative outcomes.",8.0,"reset",{}),
Scene("Persistent not fixed","The hidden pattern was persistent but not absolutely fixed.",8.0,"reset",{}),
Scene("Editable memory","Physiological memory could be edited.",6.5,"reset",{}),
Scene("Neither destiny nor chaos","Future anatomy was neither DNA destiny nor shapeless plasticity.",8.5,"reset",{}),
Scene("Landscape of goals","Between them lies a landscape of remembered goals.",8.0,"reset",{}),

Scene("Biomedical possibility","This is where biomedical possibility appears.",6.5,"morpho",{}),
Scene("Rewrite target states","Medicine might learn to rewrite preferred tissue states.",8.0,"morpho",{}),
Scene("No micromanagement","An intervention could alter collective guidance rather than every cell.",8.5,"morpho",{}),
Scene("Morphoceuticals","Morphoceuticals target the control layer of growth and form.",8.0,"morpho",{}),
Scene("Research program","This remains a research program.",6.0,"narrow",{}),
Scene("No easy human regeneration","Planarian results do not prove easy human organ regeneration.",8.5,"narrow",{}),
Scene("Clinical difficulty","Translation to clinical medicine is difficult.",7.0,"narrow",{}),
Scene("Promise not treatment","The promise should not be confused with treatment.",7.0,"narrow",{}),

Scene("Where true form","Where is the body's true form?",6.0,"layers",{}),
Scene("Genome anatomy network history","Genome, anatomy, electrical network, and developmental history all matter.",9.0,"layers",{}),
Scene("No single answer","No single answer is sufficient.",6.5,"layers",{}),
Scene("Genes possibilities","Genes define components and possibilities.",6.5,"layers",{}),
Scene("Physiology selects","Physiology selects and stabilizes patterns.",6.5,"layers",{}),
Scene("Anatomy expresses","Anatomy expresses one current outcome.",6.5,"layers",{}),
Scene("Injury reveals","Injury reveals the target the system will attempt to recover.",8.0,"counterfactual",{}),
Scene("Distributed identity","Identity is distributed across material, memory, and response.",8.0,"layers",{}),

Scene("No Platonic proof","This does not prove a Platonic Form beyond matter.",7.0,"narrow",{}),
Scene("No consciousness proof","It does not prove consciousness is fundamental.",7.0,"narrow",{}),
Scene("No beliefs","It does not show humanlike cell beliefs.",6.5,"narrow",{}),
Scene("Narrow evidence","The evidence concerns persistent, rewriteable regenerative outcomes after temporary bioelectric perturbation.",9.5,"narrow",{}),
Scene("Strange enough","That claim is already strange enough.",6.0,"narrow",{}),
Scene("Hidden shape information","A body can contain information about a shape it is not displaying.",8.0,"hidden",{}),

Scene("Human futures","Your own body also preserves futures beneath present appearance.",8.0,"human",{}),
Scene("Cautious analogy","Human identity and planarian pattern memory are not the same mechanism.",8.0,"human",{}),
Scene("Calm defensive state","A person can seem calm until an old defensive state reactivates.",8.0,"human",{}),
Scene("Skill hidden","A skill can remain invisible until conditions call it forth.",7.0,"human",{}),
Scene("Scar history","A scar can encode a history no current pain reveals.",7.0,"human",{}),
Scene("Stored possibility","Present form does not exhaust stored possibility.",7.5,"human",{}),
Scene("Answer disruption","What a system is includes how it will answer disruption.",8.0,"final",{}),

Scene("Return ordinary","A body can look ordinary.",5.5,"hidden",{}),
Scene("Future hidden","Its future response can still be altered.",6.5,"counterfactual",{}),
Scene("Knife reveals","The knife does not create the memory; it reveals which attractor governs repair.",9.0,"cut",{}),
Scene("Current not whole","The current body is not the whole state of the system.",8.0,"hidden",{}),
Scene("Remembered future","The body can remember a shape it is not wearing.",8.0,"final",{}),
Scene("Identity response","What it is includes how it will answer the next disturbance.",8.5,"final",{}),
]

def render_frame(scene,fi,fc,w,h,seed):
    u=fi/max(1,fc-1); t=u*scene.duration
    dark=scene.visual=="reset"
    im=bg(w,h,seed,dark)
    VISUALS[scene.visual](im,u,t,scene.params)
    border(im,dark)
    return im.convert("RGB")

def ffmpeg_path():
    p=shutil.which("ffmpeg")
    if not p: raise RuntimeError("ffmpeg not found on PATH")
    return p

def encode(i,fps):
    fd=FRAMES/f"scene_{i:03d}"
    out=SCENES_DIR/f"scene_{i:03d}.mp4"
    subprocess.run([ffmpeg_path(),"-y","-framerate",str(fps),"-i",str(fd/"%05d.jpg"),
                    "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",
                    "-movflags","+faststart",str(out)],
                   check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return out

def render_scene(i,s,fps,w,h,preview):
    fd=FRAMES/f"scene_{i:03d}"; fd.mkdir(parents=True,exist_ok=True); SCENES_DIR.mkdir(parents=True,exist_ok=True)
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
    out=OUTPUT/"the_body_can_remember_a_shape_it_is_not_wearing.mp4"
    subprocess.run([ffmpeg_path(),"-y","-f","concat","-safe","0","-i",str(c),"-c","copy",
                    "-movflags","+faststart",str(out)],
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
        "title":"the body can remember a shape it is not wearing",
        "runtime_seconds":round(cur,3),
        "scene_count":len(SCENES),
        "style":{
            "continuity_object":"gold hidden anatomical attractor",
            "shot_duration_range_seconds":[5,10],
            "palette_roles":{
                "gold":"remembered target form",
                "cyan":"visible present anatomy",
                "crimson":"wound and competing attractor",
                "green":"restored wild-type organization",
                "violet":"latent bioelectric memory",
                "graphite":"material tissue"
            }
        },
        "scenes":items
    },indent=2,ensure_ascii=False),encoding="utf-8")
    return p

def make_contact_sheet(w,h):
    tw=320; th=int(tw*h/w); thumbs=[]
    for i,s in enumerate(SCENES,1):
        fc=max(2,round(s.duration*DEFAULT_FPS))
        im=render_frame(s,int(fc*.72),fc,w,h,i*1000+72)
        im.thumbnail((tw,th)); thumbs.append((i,s.title,im.copy()))
    cols=4; rows=math.ceil(len(thumbs)/cols)
    sheet=Image.new("RGB",(cols*tw,rows*(th+52)),WHITE); d=ImageDraw.Draw(sheet); f=font(FSSB,15)
    for idx,title,im in thumbs:
        k=idx-1; x=(k%cols)*tw; y=(k//cols)*(th+52)
        sheet.paste(im,(x,y)); d.text((x+10,y+th+8),f"{idx:03d}  {title}",font=f,fill=INK)
    p=OUTPUT/"contact_sheet.jpg"; sheet.save(p,quality=94); return p

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
    a=parse_args()
    OUTPUT.mkdir(parents=True,exist_ok=True); FRAMES.mkdir(parents=True,exist_ok=True); SCENES_DIR.mkdir(parents=True,exist_ok=True)
    print(f"Timeline: {export_timeline()}")
    print(f"Scenes: {len(SCENES)}")
    print(f"Runtime: {sum(s.duration for s in SCENES)/60:.2f} minutes")
    if a.scene:
        if not 1<=a.scene<=len(SCENES): raise ValueError("scene out of range")
        print(render_scene(a.scene,SCENES[a.scene-1],a.fps,a.width,a.height,a.preview)); return
    rendered=[]
    for i,s in enumerate(SCENES,1):
        print(f"[{i:03d}/{len(SCENES):03d}] {s.title} ({s.duration:.1f}s)")
        r=render_scene(i,s,a.fps,a.width,a.height,a.preview)
        if not a.preview: rendered.append(r)
    if not a.no_contact_sheet: print(make_contact_sheet(a.width,a.height))
    if not a.preview: print(concatenate(rendered))

if __name__=="__main__":
    main()
