#!/usr/bin/env python3
"""
CONSCIOUSNESS IS NON-COMPUTABLE
Penrose, Godel, and the Quantum Mind

An original Platinum-house procedural visual essay.

CENTRAL CLAIM
-------------
Roger Penrose argues that human consciousness cannot be replicated by
any computational system — not because computers aren't fast enough,
but because the brain uses non-computable physics at the quantum level.

The argument rests on Godel's Incompleteness Theorem: for any formal
system, there are truths the system cannot prove. Humans can see these
truths. Computers cannot. Therefore the mind is not a computer.

The mechanism: quantum computations in microtubules, resolved by
objective reduction (OR), produce moments of conscious experience.

This does not mean computers are useless or that AI is impossible.
It means conscious AI is impossible — because consciousness is not
computation.

FILM THESIS
-----------
The computational theory of mind:
brain is a computer → consciousness is software → AI can be conscious

Penrose's alternative:
brain uses quantum physics → consciousness is non-computable → AI cannot be conscious

The critical question is not whether machines can think.
It is whether thinking is computation.

OUTPUT
------
output_penrose_orch_or/
"""

from __future__ import annotations
import argparse, json, math, random, shutil, subprocess
from dataclasses import asdict, dataclass
from pathlib import Path; from typing import Callable
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT=Path(__file__).resolve().parent
OUTPUT=Path("/mnt/HC_Volume_106427611/goldrender/output_penrose_orch_or")
FRAMES=OUTPUT/"frames"; SCENES_DIR=OUTPUT/"scenes"; W=1280; H=720; FPS=10
IVORY=(249,247,241); WHITE=(255,254,250); INK=(29,33,39); SOFT_INK=(86,91,98)
SILVER=(180,187,194); PALE_SILVER=(224,228,228); CYAN=(57,156,180); PALE_CYAN=(196,227,233)
GOLD=(194,156,72); PALE_GOLD=(236,219,175); GREEN=(70,139,99); PALE_GREEN=(196,225,206)
CRIMSON=(162,58,69); VIOLET=(109,83,153); PALE_VIOLET=(218,208,235)
FS="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"; FSB=FS.replace("Serif","Serif-Bold")
FNS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FNSB=FNS.replace("Sans","Sans-Bold")
def clamp(x,l=0.0,h=1.0): return max(l,min(h,x))
def lerp(a,b,t): return a+(b-a)*clamp(t)
def mix(a,b,t): return tuple(int(lerp(x,y,t)) for x,y in zip(a,b))
def smoothstep(a,b,x):
    if a==b: return 1.0 if x>=b else 0.0
    q=clamp((x-a)/(b-a)); return q*q*(3-2*q)
def ease(t): t=clamp(t); return .5-.5*math.cos(math.pi*t)
def font(p,s):
    for c in (p,FS,FNS):
        try: return ImageFont.truetype(c,s)
        except: pass
    return ImageFont.load_default()
def layer(s): return Image.new("RGBA",s,(0,0,0,0))
def field(w,h,seed):
    r=np.random.default_rng(seed); a=np.empty((h,w,3),dtype=np.float32); a[:]=IVORY
    a+=r.normal(0,.9,(h,w,1)); yy,xx=np.mgrid[0:h,0:w]
    h2=np.exp(-(((xx-w*.5)/(w*.37))**2+((yy-h*.40)/(h*.31))**2)*2)
    a[...,1]+=h2*3.2; a[...,2]+=h2*4.6
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8),"RGB").convert("RGBA")
def centered(d,xy,t,f,fill=INK): d.text(xy,t,font=f,fill=fill,anchor="mm")
def seal(im,t,s="",c=INK):
    w2,h2=im.size; d=ImageDraw.Draw(im)
    centered(d,(w2/2,h2*.875),t,font(FSB,max(22,int(h2*.04))),c)
    if s: centered(d,(w2/2,h2*.923),s,font(FNS,max(13,int(h2*.019))),SOFT_INK)
def border(im):
    w2,h2=im.size; d=ImageDraw.Draw(im)
    d.rounded_rectangle((26,26,w2-26,h2-26),radius=18,outline=(*INK,45),width=2)
def glow_circle(im,x,y,r,c,a=170,b=14):
    gl=layer(im.size); ImageDraw.Draw(gl).ellipse((x-r,y-r,x+r,y+r),fill=(*c,int(a)))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(b)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).ellipse((x-r*.34,y-r*.34,x+r*.34,y+r*.34),fill=(*mix(c,WHITE,.35),min(255,int(a)+50)))
    im.alpha_composite(fg)
def glow_line(im,pts,c,w=4,a=210,b2=11):
    if len(pts)<2: return; gl=layer(im.size)
    ImageDraw.Draw(gl).line(pts,fill=(*c,int(a)),width=w*3,joint="curve")
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(b2)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).line(pts,fill=(*mix(c,WHITE,.08),min(255,int(a)+25)),width=w,joint="curve")
    im.alpha_composite(fg)
def partial(pts,a):
    if not pts: return []; a=clamp(a)
    if a>=1: return pts; k=a*(len(pts)-1); i=int(k); f=k-i
    out=list(pts[:i+1])
    if i+1<len(pts): p,q=pts[i],pts[i+1]; out.append((lerp(p[0],q[0],f),lerp(p[1],q[1],f)))
    return out
def arrow(d,a,b,c=INK,w=3,h2=10):
    d.line((*a,*b),fill=c,width=w); ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for s2 in(-1,1): p=(b[0]-math.cos(ang+s2*.52)*h2,b[1]-math.sin(ang+s2*.52)*h2); d.line((*b,*p),fill=c,width=w)

def draw_microtubule(im,cx,cy,w2,reveal=1.0,phase=0.0):
    d=ImageDraw.Draw(im); prev=None
    for i in range(int(20*reveal)):
        q=i/19; x=cx-w2/2+q*w2; y=cy+math.sin(q*math.tau*6+phase)*6
        d.ellipse((x-3,y-3,x+3,y+3),fill=(*CYAN,200),outline=(*CYAN,150),width=1)
        if prev: d.line((prev[0],prev[1],x,y),fill=(*CYAN,120),width=2)
        prev=(x,y)

def draw_godel(im,cx,cy,size,alpha=200):
    d=ImageDraw.Draw(im)
    d.text((cx-size*.4,cy-size*.2),"G -> ~Provable(G)",font=font(FNS,16),fill=(*INK,alpha))
    d.text((cx-size*.4,cy+size*.1),"~Provable(G) is TRUE",font=font(FNS,16),fill=(*CRIMSON,alpha))

def vis_penrose(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    glow_circle(im,cx,cy,18,GOLD,int(180*r),13)
    centered(d,(cx,cy+40),"ROGER PENROSE",font(FSB,20),GOLD)
    if r>.5: centered(d,(cx,cy+60),"NOT A COMPUTER",font(FNSB,16),(*CRIMSON,int(200*(r-.5)*2)))
    seal(im,"THE MIND IS NOT A COMPUTER","Penrose: consciousness uses non-computable physics")

def vis_godel(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    draw_godel(d,cx,cy,100,int(200*r))
    if r>.5: centered(d,(cx,h*.78),"HUMANS SEE TRUTH COMPUTERS CANNOT PROVE",font(FNSB,14),(*GOLD,int(200*(r-.5)*2)))
    seal(im,"GODEL'S INCOMPLETENESS THEOREM","for any formal system, there are truths it cannot prove")

def vis_microtubule(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for i in range(int(6*r)):
        y=cy-40+i*16; draw_microtubule(im,cx,y,w*.50,r,t+i)
    if r>.5: centered(d,(cx,h*.78),'MICROTUBULES: QUANTUM PROCESSORS',font(FNSB,14),(*CYAN,int(200*(r-.5)*2)))
    seal(im,"THE HAMEROFF-PENROSE MODEL","microtubules sustain quantum coherence — collapse produces consciousness")

def vis_orch(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    for rr in range(20,100,20):
        d.ellipse((cx-rr,cy-rr*.5,cx+rr,cy+rr*.5),outline=(*GOLD,int(60*(1-rr/120))),width=2)
    glow_circle(im,cx,cy,12,GOLD,int(180*r),12)
    if r>.5: centered(d,(cx,cy+45),"OBJECTIVE REDUCTION",font(FNSB,16),(*GOLD,int(200*(r-.5)*2)))
    seal(im,"ORCH-OR","orchestrated objective reduction — quantum collapse as conscious moment")

def vis_caution(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    rows=[("GODEL THEOREM IS MATHEMATICALLY CERTAIN","FACT",GREEN),
          ("ORCH-OR IS A SPECULATIVE HYPOTHESIS","NOT ESTABLISHED",CRIMSON),
          ("CONSCIOUSNESS IS NON-COMPUTABLE","DISPUTED",GOLD),
          ("QUANTUM COHERENCE IN MICROTUBULES","EVIDENCE EMERGING",CYAN)]
    q=ease(u)
    for i,(claim,status,col) in enumerate(rows):
        local=clamp(q*len(rows)-i); y=h*(.23+i*.13)
        d.rounded_rectangle((w*.14,y-28,w*.86,y+28),radius=14,fill=(*mix(WHITE,col,.10),int(220*local)),outline=(*col,int(180*local)),width=2)
        centered(d,(w*.36,y),claim,font(FNSB,12),INK); centered(d,(w*.77,y),status,font(FNSB,12),col)
    seal(im,"DISCIPLINE","the Godel argument is strong — the quantum mechanism is speculative")

def vis_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    glow_circle(im,cx,cy,14,GOLD,int(180*r),12)
    for i in range(int(8*r)):
        a=i*math.tau/8+t*0.2; rr=35+20*math.sin(t*0.3+i)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.line((cx,cy,x,y),fill=(*GOLD,int(60*r)),width=2)
        d.ellipse((x-4,y-4,x+4,y+4),fill=(*PALE_GOLD,int(150*r)),outline=(*GOLD,int(120*r)),width=2)
    if r>.7: centered(d,(cx,cy-h*.08),"THE MIND IS NOT A COMPUTER",font(FSB,20),(*GOLD,int(200*(r-.7)*3.3)))
    seal(im,"CONSCIOUSNESS IS NON-COMPUTABLE","AI can simulate — but it cannot be",GOLD)

VISUALS={}
for k,v in list(locals().items()):
    if k.startswith('vis_'): VISUALS[k[4:]]=v
@dataclass
class Scene:
    title:str; narration:str; duration:float; visual:str; params:dict
SCENES=[
    Scene("Penrose's challenge","Roger Penrose argues that consciousness cannot be simulated because it uses non-computable physics.",9.0,"penrose",{}),
    Scene("The orthodox view","Most AI researchers assume consciousness emerges from computation. Penrose says this is a category error.",8.5,"penrose",{}),
    Scene("Godel's theorem","Kurt Godel proved that any formal system contains truths it cannot prove.",8.5,"godel",{}),
    Scene("The insight","Humans can see these truths. Computers cannot. Therefore the mind is not a formal system.",9.0,"godel",{}),
    Scene("Microtubules","Stuart Hameroff discovered that brain cells contain microtubules — tiny protein cylinders.",8.0,"microtubule",{}),
    Scene("Quantum processors","The microtubules may sustain quantum coherence long enough for computation.",8.5,"microtubule",{}),
    Scene("Objective reduction","Penrose: quantum superposition collapses by an objective physical threshold, not measurement.",9.0,"orch",{}),
    Scene("Orch-OR","Each collapse is a moment of consciousness. The 'OR' in Orch-OR means objective reduction.",8.5,"orch",{}),
    Scene("Criticism and defense","Decoherence times are too short. But evidence is emerging for quantum effects in biology.",9.0,"caution",{}),
    Scene("AI implications","If consciousness is non-computable, AI can never be conscious — no matter how powerful.",9.5,"caution",{}),
    Scene("Closing","The question is not whether machines can think. It is whether thinking is computation.",9.5,"final",{}),
    Scene("Final frame","The mind sees what no computer can prove.",7.0,"final",{}),
]

def rf(sc,fi,fc,w2,h2,se):
    u=fi/max(1,fc-1); t=u*sc.duration; im=field(w2,h2,se)
    VISUALS[sc.visual](im,u,t,sc.params); border(im); return im.convert("RGB")
def _ff():
    f2=shutil.which("ffmpeg")
    if not f2: raise RuntimeError("ffmpeg required"); return f2
def es(idx,f2):
    o=SCENES_DIR/f"scene_{idx:03d}.mp4"; d=FRAMES/f"scene_{idx:03d}"
    subprocess.run([_ff(),"-y","-framerate",str(f2),"-i",str(d/"%05d.jpg"),"-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(o)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); return o
def rs(idx,s,f2,w2,h2,prev):
    d=FRAMES/f"scene_{idx:03d}"; d.mkdir(parents=True,exist_ok=True); SCENES_DIR.mkdir(parents=True,exist_ok=True)
    cnt=max(2,round(s.duration*f2))
    if prev:
        for oi,fi2 in enumerate([0,int(cnt*.33),int(cnt*.72),cnt-1]): rf(s,fi2,cnt,w2,h2,idx*10000+fi2).save(d/f"preview_{oi:02d}.jpg",quality=95); return d
    for fi2 in range(cnt):
        p=d/f"{fi2:05d}.jpg"
        if p.exists(): continue; rf(s,fi2,cnt,w2,h2,idx*10000+fi2).save(p,quality=95,subsampling=0)
    return es(idx,f2)
def concat(paths):
    cp=OUTPUT/"concat.txt"; cp.write_text("\n".join(f"file '{p.resolve()}'" for p in paths),encoding="utf-8")
    final=OUTPUT/"penrose_orch_or.mp4"
    subprocess.run([_ff(),"-y","-f","concat","-safe","0","-i",str(cp),"-c","copy","-movflags","+faststart",str(final)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); return final
def export_timeline():
    cursor=0.0; recs=[]
    for i,s in enumerate(SCENES,1):
        item=asdict(s); item["scene_id"]=f"scene_{i:03d}"; item["start_seconds"]=round(cursor,3); cursor+=s.duration; item["end_seconds"]=round(cursor,3); recs.append(item)
    p=OUTPUT/"narration_timeline.json"
    p.write_text(json.dumps({"title":"consciousness is non-computable","scene_count":len(SCENES),"runtime_seconds":round(cursor,3),"shot_duration_range":[5,10],"scenes":recs},indent=2,ensure_ascii=False),encoding="utf-8"); return p
def contact_sheet(w2,h2):
    tw,th=320,int(320*h2/w2); cols,rows=4,math.ceil(len(SCENES)/4); ch=th+48
    s=Image.new("RGB",(cols*tw,rows*ch),IVORY); d2=ImageDraw.Draw(s); lf=font(FNSB,14)
    for i,sc in enumerate(SCENES,1):
        cnt=max(2,round(sc.duration*FPS)); im=rf(sc,int(cnt*.72),cnt,w2,h2,i*10000+72); im.thumbnail((tw,th)); sl=i-1
        x=(sl%cols)*tw; y=(sl//cols)*ch; s.paste(im,(x,y)); d2.text((x+9,y+th+7),f"{i:02d}  {sc.title}",font=lf,fill=INK)
    p=OUTPUT/"contact_sheet.jpg"; s.save(p,quality=94); return p
def parse_args():
    p2=argparse.ArgumentParser()
    p2.add_argument("--fps",type=int,default=FPS); p2.add_argument("--width",type=int,default=W); p2.add_argument("--height",type=int,default=H)
    p2.add_argument("--scene",type=int); p2.add_argument("--preview",action="store_true"); p2.add_argument("--no-contact-sheet",action="store_true")
    return p2.parse_args()
def main():
    a2=parse_args()
    OUTPUT.mkdir(parents=True,exist_ok=True); FRAMES.mkdir(parents=True,exist_ok=True); SCENES_DIR.mkdir(parents=True,exist_ok=True)
    tl=export_timeline(); total=sum(s.duration for s in SCENES)
    print(f"Timeline: {tl}\nScenes: {len(SCENES)}\nRuntime: {total/60:.2f} min")
    if a2.scene:
        if not 1<=a2.scene<=len(SCENES): raise ValueError("scene range")
        print(rs(a2.scene,SCENES[a2.scene-1],a2.fps,a2.width,a2.height,a2.preview)); return
    rendered=[]
    for i,s in enumerate(SCENES,1):
        print(f"[{i:02d}/{len(SCENES):02d}] {s.title} ({s.duration:.1f}s)")
        rendered.append(rs(i,s,a2.fps,a2.width,a2.height,a2.preview))
    final=concat(rendered); print(f"Final: {final}")
    if not a2.no_contact_sheet: print(f"Contact: {contact_sheet(a2.width,a2.height)}")
    print("Done.")
if __name__=="__main__": main()
