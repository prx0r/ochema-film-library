#!/usr/bin/env python3
"""
A DREAM BECOMES A WORLD WHEN IT REMEMBERS WHERE YOU WERE
An original Imaginarium visual essay and Platinum-house procedural renderer.

ORIGINAL THESIS
---------------
A dream is usually treated as a private sequence of images.
But some dreams begin to acquire geography, continuity, recurring inhabitants,
local laws, memory, and consequence. The dream becomes world-like when it
appears to remember previous encounters and reorganize the dreamer in return.

This essay joins:
• dream geography, recurring places, lucid dreaming, and memory
• Corbin's mundus imaginalis and barzakh
• Kashmir Śaiva ābhāsa, svapna, pratibhā, and recognition
• Sufi visionary geography and angelic encounter
• predictive processing, generative models, and world-simulation
• safeguards against literalism, solipsism, escapism, and spiritual inflation

DESIGN CONTRACT
---------------
• Every shot lasts 5–10 seconds.
• Every shot visibly performs the narrated operation.
• Clean white atlas field; deep indigo only for dream-depth.
• No static slide layouts and no decorative loops.
• Silver = unstable dream trace / memory residue / unfinished path
• Gold = continuity, answer, recognition, world-like coherence
• Cyan = predictive construction, sensory synthesis, navigation
• Violet = dream-depth, imaginal geography, hidden law
• Crimson = literalism, obsession, false certainty, escapism
• Green = integration, returned action, ethical consequence
• Graphite = waking-world material orientation
• Continuity object: one silver path gradually gains landmarks and persistence.
• The dream must never become generic surrealism.
• Geography, recurrence, law, memory, and response are the core visual operations.
• Final criterion: the dream-world returns the dreamer to waking life with greater precision.

OUTPUT
------
output_dream_world/
  frames/scene_001/*.jpg
  scenes/scene_001.mp4
  a_dream_becomes_a_world_when_it_remembers_where_you_were.mp4
  narration_timeline.json
  original_essay.md
  contact_sheet.jpg

REQUIREMENTS
------------
pip install pillow numpy
ffmpeg must be on PATH.
"""

from __future__ import annotations
import argparse, json, math, random, shutil, subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT/"output_dream_world"
FRAMES=OUTPUT/"frames"
SCENES_DIR=OUTPUT/"scenes"

DEFAULT_WIDTH=1280
DEFAULT_HEIGHT=720
DEFAULT_FPS=10

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
            out.append((lerp(a[0],b[0],q),lerp(a[1],b[1],q))); break
    return out

def arrow(d,a,b,col=INK,width=3,head=11):
    d.line((*a,*b),fill=col,width=width)
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for delta in (2.55,-2.55):
        p=(b[0]+math.cos(ang+delta)*head,b[1]+math.sin(ang+delta)*head)
        d.line((*b,*p),fill=col,width=width)

def star_field(d,w,h,seed=5,alpha=95):
    rng=random.Random(seed)
    for _ in range(100):
        x=rng.uniform(w*.08,w*.92); y=rng.uniform(h*.08,h*.72)
        r=rng.choice([1,1,1,2])
        d.ellipse((x-r,y-r,x+r,y+r),fill=(*PALE_GOLD,alpha))

def path_curve(w,h,phase=0,offset=0):
    pts=[]
    for i in range(200):
        q=i/199
        x=lerp(w*.10,w*.90,q)
        y=h*(.58-offset)+math.sin(q*math.tau*1.5+phase)*h*.07+math.sin(q*math.tau*4-phase)*h*.018
        pts.append((x,y))
    return pts

def landmark(d,x,y,kind,col,alpha=180,scale=1.0):
    if kind=="tower":
        d.rectangle((x-18*scale,y-65*scale,x+18*scale,y),fill=(*mix(WHITE,col,.15),alpha),outline=(*col,alpha))
        d.polygon([(x-25*scale,y-65*scale),(x,y-95*scale),(x+25*scale,y-65*scale)],
                  fill=(*mix(WHITE,col,.12),alpha),outline=(*col,alpha))
    elif kind=="tree":
        d.line((x,y-5*scale,x,y-55*scale),fill=(*col,alpha),width=max(2,int(5*scale)))
        for a in (-.8,-.2,.4,1.0):
            d.ellipse((x-28*scale+math.sin(a)*12,y-85*scale+math.cos(a)*12,
                       x+28*scale+math.sin(a)*12,y-35*scale+math.cos(a)*12),
                      fill=(*mix(WHITE,col,.16),alpha),outline=(*col,alpha))
    elif kind=="bridge":
        d.arc((x-55*scale,y-45*scale,x+55*scale,y+25*scale),180,360,fill=(*col,alpha),width=max(2,int(5*scale)))
        d.line((x-55*scale,y-10*scale,x+55*scale,y-10*scale),fill=(*col,alpha),width=max(2,int(4*scale)))
    elif kind=="gate":
        d.rectangle((x-42*scale,y-70*scale,x+42*scale,y),outline=(*col,alpha),width=max(2,int(5*scale)))
        d.line((x,y-70*scale,x,y),fill=(*col,alpha),width=max(2,int(3*scale)))

def person(d,cx,cy,scale=1,col=INK,alpha=190):
    d.ellipse((cx-12*scale,cy-54*scale,cx+12*scale,cy-30*scale),outline=(*col,alpha),width=3)
    d.line((cx,cy-30*scale,cx,cy+25*scale),fill=(*col,alpha),width=4)
    d.line((cx,cy-5*scale,cx-28*scale,cy+20*scale),fill=(*col,alpha),width=4)
    d.line((cx,cy-5*scale,cx+28*scale,cy+20*scale),fill=(*col,alpha),width=4)
    d.line((cx,cy+25*scale,cx-18*scale,cy+62*scale),fill=(*col,alpha),width=4)
    d.line((cx,cy+25*scale,cx+18*scale,cy+62*scale),fill=(*col,alpha),width=4)

def map_grid(d,w,h,alpha=60):
    for i in range(9):
        x=w*(.10+i*.10); d.line((x,h*.16,x,h*.68),fill=(*SILVER,alpha),width=2)
    for j in range(7):
        y=h*(.18+j*.08); d.line((w*.08,y,w*.92,y),fill=(*SILVER,alpha),width=2)

@dataclass
class Scene:
    title:str
    narration:str
    duration:float
    visual:str
    params:dict

def v_fragile_path(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    pts=path_curve(w,h,t*.15)
    glow_line(im,partial(pts,q),SILVER,4,10,150)
    if u>.55:
        fade=1-smooth(.55,.95,u)
        ov=layer(im); od=ImageDraw.Draw(ov)
        od.line(pts,fill=(*SILVER,int(150*fade)),width=4)
        im.alpha_composite(ov)
    seal(im,"MOST DREAMS LEAVE ONLY A TRACE","a path dissolving at waking")

def v_recurring_landmark(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    pts=path_curve(w,h,t*.08)
    glow_line(im,partial(pts,ease(u)),SILVER,4,10,150)
    q=ease(u)
    landmark(d,w*.62,h*.48,"tower",GOLD,int(80+120*q),q)
    glow_circle(im,w*.62,h*.40,10+10*q,GOLD,120,10)
    seal(im,"RECURRENCE GIVES DREAM SPACE A MEMORY","the tower waits where it was before")

def v_map_build(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    map_grid(d,w,h,50)
    q=ease(u)
    pts=path_curve(w,h,t*.08)
    glow_line(im,partial(pts,q),CYAN,5,12,180)
    landmarks=[(w*.24,h*.49,"tree",GREEN),(w*.48,h*.46,"bridge",VIOLET),
               (w*.70,h*.45,"tower",GOLD),(w*.84,h*.50,"gate",CYAN)]
    for i,(x,y,k,col) in enumerate(landmarks):
        qq=smooth(i*.12,.75+i*.04,u)
        landmark(d,x,y,k,col,int(170*qq),qq)
    seal(im,"A WORLD BEGINS WHEN LOCATIONS RELATE","not images in sequence, but places with distance between them")

def v_predictive_world(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.18,h*.42); center=(w*.50,h*.42); right=(w*.82,h*.42)
    person(d,*left,.65,INK,180)
    d.rounded_rectangle((center[0]-88,center[1]-66,center[0]+88,center[1]+66),
                        radius=18,fill=(*PALE_CYAN,215),outline=(*CYAN,180),width=3)
    ctext(d,center,"WORLD MODEL",font(FSSB,int(h*.017)),CYAN)
    landmark(d,*right,"gate",GOLD,190,.9)
    q=ease(u)
    glow_line(im,partial([left,center,right],q),CYAN,4,11,170)
    glow_line(im,partial([right,(w*.66,h*.57),center,(w*.35,h*.57),left],smooth(.35,.95,u)),GOLD,4,11,150)
    seal(im,"DREAMING IS GENERATIVE WORLD-MAKING","a model runs with reduced sensory correction")

def v_local_laws(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    q=ease(u)
    zones=[("GRAVITY",CYAN,w*.22),("TIME",VIOLET,w*.42),("IDENTITY",GOLD,w*.62),("CAUSALITY",GREEN,w*.82)]
    for i,(txt,col,x) in enumerate(zones):
        qq=smooth(i*.1,.62+i*.06,u)
        d.ellipse((x-55*qq,h*.42-55*qq,x+55*qq,h*.42+55*qq),
                  fill=(*mix(WHITE,col,.15),int(220*qq)),outline=(*col,int(180*qq)),width=3)
        if qq>.67:ctext(d,(x,h*.42),txt,font(FSSB,int(h*.012)),col)
    # one broken law at far left
    arrow(d,(w*.12,h*.62),(w*.12,h*.25),CRIMSON,4,12)
    seal(im,"WORLD-LIKENESS REQUIRES LOCAL LAW","even impossible worlds become coherent through regularity")

def v_inhabitant_memory(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.28,h*.42); right=(w*.72,h*.42)
    person(d,*left,.72,INK,180)
    person(d,*right,.72,VIOLET,180)
    q=ease(u)
    glow_line(im,partial([left,(w*.50,h*.30),right],q),CYAN,4,11,160)
    glow_line(im,partial([right,(w*.50,h*.56),left],smooth(.30,.95,u)),GOLD,5,13,190)
    ctext(d,(right[0],h*.22),"YOU LEFT THE KEY HERE",font(FSB,int(h*.018)),GOLD)
    seal(im,"AN INHABITANT BECOMES WORLD-LIKE WHEN IT REMEMBERS YOU","continuity appears on the other side of encounter")

def v_barzakh_world(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.24,h*.42); right=(w*.76,h*.42)
    map_grid(d,w*.48,h,40)
    star_field(d,w,h,9,70)
    q=ease(u)
    # central threshold
    d.rounded_rectangle((w*.46,h*.20,w*.54,h*.64),radius=20,
                        fill=(*mix(PALE_VIOLET,NIGHT,.65),int(220*q)),
                        outline=(*GOLD,int(180*q)),width=4)
    glow_line(im,partial([(left[0],left[1]),(w*.50,h*.34),(right[0],right[1])],q),CYAN,4,11,160)
    glow_line(im,partial([(right[0],right[1]+40),(w*.50,h*.54),(left[0],left[1]+40)],q),VIOLET,4,11,160)
    seal(im,"BARZAKH","the dream-world joins and separates psyche, symbol, and world",dark=True)

def v_corbin_city(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    star_field(d,w,h,17,85)
    floor=h*.63; q=ease(u)
    d.line((w*.08,floor,w*.92,floor),fill=(*SILVER,110),width=3)
    for i in range(14):
        x=w*(.10+i*.06)
        hh=(45+(i*41)%160)*q
        ww=24+(i*13)%30
        d.rectangle((x-ww/2,floor-hh,x+ww/2,floor),
                    fill=(*mix(PALE_VIOLET,PALE_GOLD,i/13),100),outline=(*GOLD,90))
    landmark(d,w*.72,floor,"tower",GOLD,int(180*q),1.1*q)
    seal(im,"MUNDUS IMAGINALIS","a world with form and consequence, not merely private fantasy",dark=True)

def v_lucid_control(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    map_grid(d,w,h,40)
    q=ease(u)
    person(d,w*.25,h*.48,.68,INK,180)
    # world obeys hand at first
    landmarks=[(w*.50,h*.48,"tree",GREEN),(w*.68,h*.47,"bridge",CYAN),(w*.82,h*.46,"tower",GOLD)]
    for i,(x,y,k,col) in enumerate(landmarks):
        qq=smooth(i*.12,.70+i*.06,u)
        landmark(d,x,y,k,col,int(170*qq),qq)
    arrow(d,(w*.31,h*.43),(w*.47,h*.38),CYAN,4,11)
    seal(im,"LUCIDITY CAN INCREASE CONTROL","but control is not the same as encounter")

def v_resistance(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    person(d,w*.25,h*.48,.68,INK,180)
    landmark(d,w*.72,h*.49,"gate",GOLD,190,1)
    q=ease(u)
    # command path stops; answer path bends
    cmd=[(w*.32,h*.44),(w*.50,h*.35),(w*.64,h*.44)]
    glow_line(im,partial(cmd,min(q,.62)),CRIMSON,4,11,170)
    ans=[(w*.72,h*.44),(w*.55,h*.58),(w*.34,h*.54)]
    glow_line(im,partial(ans,smooth(.35,.95,u)),GOLD,5,13,190)
    seal(im,"ENCOUNTER BEGINS WHERE THE DREAM RESISTS COMMAND","the world answers with its own demand")

def v_three_failures(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    items=[("LITERALISM",CRIMSON),("SOLIPSISM",VIOLET),("ESCAPISM",GOLD)]
    xs=[w*.22,w*.50,w*.78]
    for i,((txt,col),x) in enumerate(zip(items,xs)):
        q=smooth(i*.12,.62+i*.07,u)
        d.ellipse((x-76*q,h*.40-76*q,x+76*q,h*.40+76*q),
                  fill=(*mix(WHITE,col,.18),int(220*q)),outline=(*col,int(180*q)),width=4)
        if q>.66:ctext(d,(x,h*.40),txt,font(FSB,int(h*.017)),col)
        strike=smooth(.48+i*.08,.95,u)
        d.line((x-85,h*.32,x+85,h*.48),fill=(*CRIMSON,int(200*strike)),width=5)
    seal(im,"THREE WAYS TO LOSE THE DREAM-WORLD","make it crude fact · make it only you · use it to abandon life")

def v_abhasa_dream(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    cx,cy=w*.5,h*.42; q=ease(u)
    glow_circle(im,cx,cy,18,GOLD,150,12)
    for i in range(18):
        a=i*math.tau/18
        rr=lerp(25,210,q)*(0.7+0.3*((i%4)/3))
        x=cx+math.cos(a+t*.08)*rr; y=cy+math.sin(a+t*.08)*rr*.62
        col=mix(CYAN,VIOLET,i/17)
        glow_circle(im,x,y,5+3*(i%3),col,90,7)
        glow_line(im,[(cx,cy),(x,y)],col,2,7,70)
    seal(im,"SVAPNA AS ĀBHĀSA","dream and waking are different organizations of appearing")

def v_recognition(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    left=(w*.25,h*.42); right=(w*.75,h*.42)
    person(d,*left,.7,INK,180)
    landmark(d,*right,"gate",GOLD,190,1)
    q=ease(u)
    glow_line(im,partial([left,(w*.50,h*.30),right],q),CYAN,4,11,170)
    glow_line(im,partial([right,(w*.50,h*.56),left],smooth(.30,.95,u)),GOLD,5,13,200)
    seal(im,"RECOGNITION DOES NOT CHOOSE DREAM OVER WAKING","it recognizes the field in which both arise")

def v_waking_integration(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    # waking city grid
    map_grid(d,w,h,55)
    landmark(d,w*.20,h*.52,"gate",GOLD,180,.8)
    q=ease(u)
    path=[(w*.28,h*.50),(w*.45,h*.36),(w*.62,h*.52),(w*.86,h*.44)]
    glow_line(im,partial(path,q),GREEN,6,14,210)
    person(d,w*.86,h*.46,.6,GREEN,180)
    seal(im,"THE DREAM MUST RETURN AS CONDUCT","a world is tested by what it changes after waking")

def v_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    star_field(d,w,h,21,75)
    q=ease(u)
    pts=path_curve(w,h,t*.08)
    glow_line(im,partial(pts,q),mix(SILVER,GOLD,q),5,13,190)
    landmarks=[(w*.24,h*.49,"tree",GREEN),(w*.47,h*.46,"bridge",VIOLET),
               (w*.70,h*.45,"tower",GOLD),(w*.84,h*.50,"gate",CYAN)]
    for i,(x,y,k,col) in enumerate(landmarks):
        qq=smooth(i*.10,.78+i*.04,u)
        landmark(d,x,y,k,col,int(170*qq),qq)
    person(d,w*.18,h*.50,.58,INK,180)
    glow_circle(im,w*.70,h*.37,12+15*q,GOLD,120,10)
    seal(im,"A DREAM BECOMES A WORLD WHEN IT REMEMBERS WHERE YOU WERE",
         "continuity turns image into place, and place into relation",dark=True,color=GREEN)

VISUALS:dict[str,Callable]={
    "trace":v_fragile_path,
    "landmark":v_recurring_landmark,
    "map":v_map_build,
    "predict":v_predictive_world,
    "laws":v_local_laws,
    "inhabitant":v_inhabitant_memory,
    "barzakh":v_barzakh_world,
    "corbin":v_corbin_city,
    "lucid":v_lucid_control,
    "resistance":v_resistance,
    "failures":v_three_failures,
    "abhasa":v_abhasa_dream,
    "recognition":v_recognition,
    "return":v_waking_integration,
    "final":v_final,
}

SCENES:list[Scene]=[
    Scene("Trace","Most dreams leave only a trace.",6.0,"trace",{}),
    Scene("Dissolution","A street, a room, a face—and then dissolution.",7.0,"trace",{}),
    Scene("No geography","The images do not remain long enough to become geography.",8.0,"trace",{}),
    Scene("Recurring tower","Then a tower appears again.",6.0,"landmark",{}),
    Scene("Same road","The same road bends beneath it.",6.0,"landmark",{}),
    Scene("Memory elsewhere","The place seems to remember what happened there before.",8.0,"inhabitant",{}),
    Scene("Thesis","A dream becomes a world when it remembers where you were.",8.5,"final",{}),

    Scene("Image sequence","A dream is usually described as a sequence of images.",7.0,"trace",{}),
    Scene("World requires more","But a world requires more than vividness.",7.0,"map",{}),
    Scene("Locations","It requires locations.",5.5,"map",{}),
    Scene("Distances","Distances.",5.0,"map",{}),
    Scene("Routes","Routes.",5.0,"map",{}),
    Scene("Return","The possibility of return.",6.0,"map",{}),
    Scene("Consequences","And consequences that survive the scene in which they began.",8.5,"inhabitant",{}),

    Scene("Dream map","Some dreamers discover recurring maps.",7.0,"map",{}),
    Scene("Bridge beyond station","A bridge always lies beyond the station.",7.0,"map",{}),
    Scene("Forest below city","A forest descends below the city.",7.0,"map",{}),
    Scene("Locked district","A locked district remains inaccessible.",7.0,"map",{}),
    Scene("Places relate","The places relate even when no single dream contains the whole.",9.0,"map",{}),
    Scene("Distributed geography","Geography is distributed across nights.",7.5,"map",{}),

    Scene("Predictive world","Dreaming is generative world-making.",7.0,"predict",{}),
    Scene("Reduced sensory correction","A world-model runs with reduced correction from current sensation.",9.0,"predict",{}),
    Scene("Vision synthesized","Vision is synthesized.",6.0,"predict",{}),
    Scene("Space synthesized","Space is synthesized.",6.0,"predict",{}),
    Scene("Bodies synthesized","Bodies are synthesized.",6.0,"predict",{}),
    Scene("Yet coherent","Yet the result can remain coherent enough to navigate.",8.0,"predict",{}),
    Scene("No imaginal proof","This does not prove an independent imaginal realm.",8.0,"predict",{}),
    Scene("Capacity shown","It shows that experience can organize itself as a world.",8.0,"predict",{}),

    Scene("World laws","World-likeness also requires local law.",7.0,"laws",{}),
    Scene("Dream gravity","Dream gravity may differ from waking gravity.",7.0,"laws",{}),
    Scene("Time loops","Time may loop.",5.5,"laws",{}),
    Scene("Identity shifts","Identity may shift.",5.5,"laws",{}),
    Scene("Doors impossible","Doors may open into impossible places.",6.5,"laws",{}),
    Scene("Regular impossibility","But impossibility can still be regular.",7.0,"laws",{}),
    Scene("Law creates trust","The dreamer learns what this world permits.",7.0,"laws",{}),

    Scene("Inhabitants","Recurring inhabitants deepen the world.",7.0,"inhabitant",{}),
    Scene("Not background","They cease to feel like disposable background figures.",8.0,"inhabitant",{}),
    Scene("Recognition across nights","One recognizes you across nights.",7.0,"inhabitant",{}),
    Scene("Unfinished conversation","A conversation resumes where it stopped.",8.0,"inhabitant",{}),
    Scene("Object remembered","An object left behind is returned.",7.0,"inhabitant",{}),
    Scene("Continuity other side","Continuity appears on the other side of encounter.",8.5,"inhabitant",{}),
    Scene("No automatic ontology","This still does not settle what kind of being the inhabitant is.",9.0,"inhabitant",{}),

    Scene("Corbin","Henry Corbin needed a category for worlds like this.",8.0,"corbin",{}),
    Scene("Mundus imaginalis","The mundus imaginalis is neither physical geography nor private fantasy.",9.0,"corbin",{}),
    Scene("Form and consequence","It possesses form, orientation, encounter, and consequence.",8.5,"corbin",{}),
    Scene("Barzakh","A barzakh joins and separates levels.",7.0,"barzakh",{}),
    Scene("Dream world threshold","The dream-world can function as such a threshold.",8.0,"barzakh",{}),
    Scene("Psyche symbol world","Psyche, symbol, and world meet without becoming identical.",8.5,"barzakh",{}),

    Scene("No hidden planet","The imaginal city is not a hidden planet behind the moon.",8.0,"corbin",{}),
    Scene("No mere fabrication","Nor is it merely a fabrication with no claim upon the dreamer.",8.5,"corbin",{}),
    Scene("World character","Its reality lies in world-character and transformative consequence.",9.0,"corbin",{}),
    Scene("Deeds matter there","What is done there can matter here.",7.0,"return",{}),
    Scene("But interpretation required","But interpretation remains necessary.",7.0,"failures",{}),

    Scene("Lucidity","Lucid dreaming introduces a new complication.",7.0,"lucid",{}),
    Scene("Control increases","The dreamer may gain control.",6.0,"lucid",{}),
    Scene("Fly","You can fly.",5.0,"lucid",{}),
    Scene("Change scene","Change the scene.",5.5,"lucid",{}),
    Scene("Summon figure","Summon a figure.",5.5,"lucid",{}),
    Scene("Control not encounter","But control is not the same as encounter.",7.5,"resistance",{}),
    Scene("World obeys fantasy","A fully obedient dream may remain fantasy.",7.5,"lucid",{}),

    Scene("Resistance","Encounter begins where the dream resists command.",8.0,"resistance",{}),
    Scene("Door stays shut","The door stays shut.",5.5,"resistance",{}),
    Scene("Figure refuses","The figure refuses the role assigned.",6.5,"resistance",{}),
    Scene("Landscape redirects","The landscape redirects the journey.",6.5,"resistance",{}),
    Scene("Unexpected obligation","An unexpected obligation appears.",7.0,"resistance",{}),
    Scene("Asymmetry","The world seems to contain a direction not authored in advance.",8.5,"resistance",{}),

    Scene("Three failures","Three failures surround dream worlds.",6.5,"failures",{}),
    Scene("Literalism","Literalism treats every dream event as crude external fact.",8.0,"failures",{}),
    Scene("Solipsism","Solipsism treats every figure as only the ego in costume.",8.0,"failures",{}),
    Scene("Escapism","Escapism uses dream-depth to abandon waking life.",8.0,"failures",{}),
    Scene("Discipline","Imaginal discipline rejects all three.",6.5,"failures",{}),
    Scene("Neither fact nor nothing","The dream-world is neither simple fact nor nothing.",8.0,"barzakh",{}),

    Scene("Shaiva dream","Kashmir Śaivism compares waking and dream without making them identical.",9.0,"abhasa",{}),
    Scene("Svapna","Svapna is dream as a mode of manifestation.",7.0,"abhasa",{}),
    Scene("Abhasa","Both waking and dream are ābhāsas—appearances of consciousness.",8.0,"abhasa",{}),
    Scene("Different constraints","Their constraints differ.",6.0,"laws",{}),
    Scene("Different continuity","Their continuity differs.",6.0,"map",{}),
    Scene("Same appearing field","Yet both arise within the field of appearing.",8.0,"abhasa",{}),

    Scene("Dream not inferior copy","Dream is not merely a defective copy of waking.",8.0,"abhasa",{}),
    Scene("Waking not absolute","Waking is not automatically absolute because it is stable.",8.0,"recognition",{}),
    Scene("Recognition question","The question becomes: what is the field in which both are known?",9.0,"recognition",{}),
    Scene("Source not scene","Recognition turns from the scene toward the source of appearing.",8.0,"recognition",{}),
    Scene("No choosing dream","It does not choose dream over waking.",7.0,"recognition",{}),
    Scene("Includes both","It includes both without confusing their practical differences.",9.0,"recognition",{}),

    Scene("Memory criterion","Memory is the decisive threshold.",6.5,"landmark",{}),
    Scene("Place remembers","A place becomes world-like when it remembers.",7.0,"landmark",{}),
    Scene("Path remembers","A path remembers where it led.",6.5,"map",{}),
    Scene("Figure remembers","A figure remembers what was promised.",6.5,"inhabitant",{}),
    Scene("Dreamer remembers differently","The dreamer returns already altered by prior visits.",8.5,"inhabitant",{}),
    Scene("Reciprocal continuity","Continuity becomes reciprocal.",6.5,"inhabitant",{}),

    Scene("Ethical test","The deepest test is not spectacle.",6.5,"return",{}),
    Scene("Not vividness","Not vividness.",5.0,"failures",{}),
    Scene("Not lucidity","Not lucidity.",5.0,"lucid",{}),
    Scene("Not prophecy","Not apparent prophecy.",5.0,"failures",{}),
    Scene("Fruit","The test is fruit.",5.5,"return",{}),
    Scene("Clarity waking","Does the dream make waking perception clearer?",7.5,"return",{}),
    Scene("Unfinished action","Does it reveal an unfinished action?",7.0,"return",{}),
    Scene("Humility","Does it reduce certainty rather than inflate it?",7.0,"return",{}),
    Scene("Care","Does it enlarge care for the living world?",7.0,"return",{}),

    Scene("Return waking","A dream-world must return as conduct.",7.5,"return",{}),
    Scene("Road changes choice","The road seen there changes a choice here.",7.0,"return",{}),
    Scene("Figure changes speech","The figure encountered there changes how one speaks.",7.5,"return",{}),
    Scene("Threshold changes attention","The threshold crossed there changes attention here.",8.0,"return",{}),
    Scene("Circuit complete","Only then has the circuit completed.",6.5,"return",{}),

    Scene("Final trace","At first there is only a dissolving trace.",6.5,"trace",{}),
    Scene("Landmark returns","Then a landmark returns.",5.5,"landmark",{}),
    Scene("Map forms","A map forms across nights.",6.0,"map",{}),
    Scene("Inhabitant remembers","An inhabitant remembers.",6.0,"inhabitant",{}),
    Scene("Law persists","A local law persists.",5.5,"laws",{}),
    Scene("World answers","The world begins to answer.",6.0,"resistance",{}),
    Scene("Final thesis","A dream becomes a world when it remembers where you were.",8.5,"final",{}),
    Scene("Final criterion","Its truth is measured by whether you wake more capable of inhabiting this world.",9.5,"return",{}),
]

def export_original_essay():
    lines=["# a dream becomes a world when it remembers where you were",""]
    for s in SCENES: lines += [s.narration,""]
    p=OUTPUT/"original_essay.md"
    p.write_text("\n".join(lines),encoding="utf-8")
    return p

def render_frame(scene,fi,fc,w,h,seed):
    u=fi/max(1,fc-1); t=u*scene.duration
    dark=scene.visual in {"barzakh","corbin","final"}
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
    out=OUTPUT/"a_dream_becomes_a_world_when_it_remembers_where_you_were.mp4"
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
        "title":"a dream becomes a world when it remembers where you were",
        "runtime_seconds":round(cur,3),
        "scene_count":len(SCENES),
        "original_essay":True,
        "style":{
            "continuity_object":"silver path gaining landmarks and reciprocal memory",
            "shot_duration_range_seconds":[5,10],
            "palette_roles":{
                "silver":"unstable dream trace",
                "gold":"continuity and answer",
                "cyan":"world-model and navigation",
                "violet":"imaginal depth and hidden law",
                "crimson":"literalism and escapism",
                "green":"integration and ethical return",
                "graphite":"waking material orientation"
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
    p=OUTPUT/"contact_sheet.jpg"; sheet.save(p,quality=94); return p

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
