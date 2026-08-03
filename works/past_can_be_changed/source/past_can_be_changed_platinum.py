#!/usr/bin/env python3
"""THE PAST CAN BE CHANGED — Remission Is Retroactive Alteration"""
from __future__ import annotations
import argparse, json, math, random, shutil, subprocess
from dataclasses import asdict, dataclass
from pathlib import Path; from typing import Callable
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT=Path(__file__).resolve().parent
OUTPUT=Path("/mnt/HC_Volume_106427611/goldrender/output_past_can_be_changed")
FRAMES=OUTPUT/"frames"; SCENES_DIR=OUTPUT/"scenes"
W,H,FPS=1280,720,10
IVORY=(249,247,241); WHITE=(255,254,250); INK=(29,33,39); SOFT_INK=(86,91,98)
SILVER=(180,187,194); PALE_SILVER=(224,228,228); CYAN=(57,156,180)
GOLD=(194,156,72); PALE_GOLD=(236,219,175); GREEN=(70,139,99); PALE_GREEN=(196,225,206)
CRIMSON=(162,58,69); VIOLET=(109,83,153)
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
    r=np.random.default_rng(seed)
    a=np.empty((h,w,3),dtype=np.float32); a[:]=IVORY
    a+=r.normal(0,.9,(h,w,1))
    yy,xx=np.mgrid[0:h,0:w]
    h2=np.exp(-(((xx-w*.5)/(w*.37))**2+((yy-h*.40)/(h*.31))**2)*2)
    a[...,1]+=h2*3.2; a[...,2]+=h2*4.6
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8),"RGB").convert("RGBA")
def centered(d,xy,t,f,fill=INK): d.text(xy,t,font=f,fill=fill,anchor="mm")
def seal(im,t,s="",c=INK):
    w2,h2=im.size; d=ImageDraw.Draw(im)
    tf=font(FSB,max(22,int(h2*.04))); sf=font(FNS,max(13,int(h2*.019)))
    centered(d,(w2/2,h2*.875),t,tf,c)
    if s: centered(d,(w2/2,h2*.923),s,sf,SOFT_INK)
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
    if len(pts)<2: return
    gl=layer(im.size); ImageDraw.Draw(gl).line(pts,fill=(*c,int(a)),width=w*3,joint="curve")
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(b2)))
    fg=layer(im.size)
    ImageDraw.Draw(fg).line(pts,fill=(*mix(c,WHITE,.08),min(255,int(a)+25)),width=w,joint="curve")
    im.alpha_composite(fg)
def partial(pts,a):
    if not pts: return []
    a=clamp(a)
    if a>=1: return pts
    k=a*(len(pts)-1); i=int(k); f=k-i
    out=list(pts[:i+1])
    if i+1<len(pts):
        p,q=pts[i],pts[i+1]
        out.append((lerp(p[0],q[0],f),lerp(p[1],q[1],f)))
    return out
def arrow(d,a,b,c=INK,w=3,h2=10):
    d.line((*a,*b),fill=c,width=w)
    ang=math.atan2(b[1]-a[1],b[0]-a[0])
    for s2 in(-1,1):
        p=(b[0]-math.cos(ang+s2*.52)*h2,b[1]-math.sin(ang+s2*.52)*h2)
        d.line((*b,*p),fill=c,width=w)

def draw_timeline(im,cx,cy,w2,reveal=1.0,mode="arrow"):
    d=ImageDraw.Draw(im)
    pts=[(cx-w2/2+i*w2/39,cy+math.sin(i/39*math.tau*2)*12) for i in range(40)]
    glow_line(im,partial(pts,reveal),INK,4,180,10)
    if mode=="arrow":
        arrow(d,pts[-1],(pts[-1][0]+20,pts[-1][1]),INK,3,8)
    return pts

def draw_figure(d,cx,cy,s=1.0,c=INK,a=200):
    d.ellipse((cx-10*s,cy-30*s,cx+10*s,cy-16*s),fill=(*PALE_GOLD,a),outline=(*c,a),width=2)
    d.line((cx,cy-16*s,cx,cy+10*s),fill=(*c,a),width=3)
    d.line((cx-12*s,cy-6*s,cx+12*s,cy-6*s),fill=(*c,a),width=3)
    d.line((cx,cy+10*s,cx-12*s,cy+28*s),fill=(*c,a),width=3)
    d.line((cx,cy+10*s,cx+12*s,cy+28*s),fill=(*c,a),width=3)

def vis_claim(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    draw_timeline(im,cx,cy,w*.55,r)
    if r>.5:
        q=(r-.5)/.5
        d.rounded_rectangle((w*.14,h*.26,w*.86,h*.50),radius=14,
                            fill=(*mix(WHITE,GOLD,.08),int(200*q)),
                            outline=(*GOLD,int(160*q)),width=2)
        centered(d,(w*.50,h*.34),'"REMISSION MEANS TO SEND BACK"',font(FNS,18),(*GOLD,int(220*q)))
        centered(d,(w*.50,h*.46),"the early Christians knew the past could be altered",font(FNS,14),SOFT_INK)
    seal(im,"THE PAST CAN BE CHANGED","remission of sins is not forgiveness — it is retroactive alteration")

def vis_static_past(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    pts=draw_timeline(im,cx,cy,w*.50,r)
    for i,x in enumerate([cx-w*.15,cx,cx+w*.15]):
        fig_y=cy-30+math.sin(i*2)*6
        draw_figure(d,x,fig_y,.7,INK,int(180*r))
    if r>.5:
        q=(r-.5)/.5
        centered(d,(cx,cy+55),"THE PAST IS FIXED",font(FNSB,16),(*CRIMSON,int(200*q)))
        centered(d,(cx,cy+65),"or so we assume",font(FNS,13),SOFT_INK)
    seal(im,"THE FIXED PAST","conventional view: what happened is unchangeable")

def vis_quantum_eraser(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    # delayed choice diagram
    d.line((w*.15,cy,w*.40,cy),fill=(*CYAN,int(180*r)),width=3)
    d.line((w*.60,cy,w*.85,cy),fill=(*CYAN,int(180*r)),width=3)
    d.line((w*.40,cy,w*.50,cy-40),fill=(*GOLD,int(180*r)),width=3)
    d.line((w*.50,cy-40,w*.60,cy),fill=(*GOLD,int(180*r)),width=3)
    if r>.4:
        q=(r-.4)/.6
        glow_circle(im,w*.50,cy-40,8,GOLD,int(160*q),8)
        centered(d,(w*.50,cy-55),"DETECTOR",font(FNSB,13),GOLD)
        arrow(d,(w*.85,cy),(w*.90,cy),CYAN,3,8)
        centered(d,(w*.50,h*.72),"FUTURE MEASUREMENT DECIDES PAST PATH",font(FNSB,13),(*CYAN,int(200*q)))
    seal(im,"THE QUANTUM ERASER","a choice made now determines which path the photon 'took' in the past")

def vis_present_power(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    glow_circle(im,cx,cy,20,GOLD,int(180*r),14)
    for i in range(int(8*r)):
        a=i*math.tau/8+t*0.2
        rr=45+25*math.sin(t+i)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*.5
        d.line((cx,cy,x,y),fill=(*GOLD,int(80*r)),width=3)
        d.ellipse((x-6,y-6,x+6,y+6),fill=(*PALE_GOLD,int(150*r)),outline=(*GOLD,int(120*r)),width=2)
    if r>.6:
        q=(r-.6)/.4
        centered(d,(cx,cy+55),"THE PRESENT IS THE POINT OF POWER",font(FNSB,15),(*GOLD,int(200*q)))
        centered(d,(cx,cy+65),"what you do now changes all moments",font(FNS,13),SOFT_INK)
    seal(im,"THE PRESENT MOMENT","all time is accessible from the now")

def vis_seth_past(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    arrow(d,(cx,cy+20),(cx-w*.15,cy-20),GOLD,4,12)
    arrow(d,(cx,cy+20),(cx+w*.15,cy-20),GOLD,4,12)
    centered(d,(cx,cy+45),"PRESENT",font(FNSB,16),GOLD)
    centered(d,(cx-w*.15,cy-35),"PAST",font(FNSB,14),VIOLET)
    centered(d,(cx+w*.15,cy-35),"FUTURE",font(FNSB,14),CYAN)
    if r>.5:
        q=(r-.5)/.5
        d.rounded_rectangle((w*.12,h*.60,w*.88,h*.76),radius=10,
                            fill=(*mix(WHITE,VIOLET,.08),int(180*q)),
                            outline=(*VIOLET,int(140*q)),width=2)
        centered(d,(w*.50,h*.68),"EACH PRESENT BRINGS ITS OWN PAST",font(FNSB,14),(*VIOLET,int(200*q)))
    seal(im,"SETH: THE PAST IS NOT GIVEN","each present moment creates a past that fits it")

def vis_caution(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im)
    rows=[("QUANTUM ERASER IS EXPERIMENTALLY VERIFIED","FACT",GREEN),
          ("THE PAST CAN BE CHANGED","METAPHYSICAL CLAIM",CRIMSON),
          ("RETROCAUSALITY HAS THEORETICAL SUPPORT","EMERGING",CYAN),
          ("THIS MEANS YOU CAN UNDO PAST TRAUMA","THERAPEUTIC — NOT PHYSICAL",GOLD)]
    q=ease(u)
    for i,(claim,status,col) in enumerate(rows):
        local=clamp(q*len(rows)-i); y=h*(.23+i*.13)
        d.rounded_rectangle((w*.14,y-28,w*.86,y+28),radius=14,
                            fill=(*mix(WHITE,col,.10),int(220*local)),
                            outline=(*col,int(180*local)),width=2)
        centered(d,(w*.35,y),claim,font(FNSB,13),INK)
        centered(d,(w*.77,y),status,font(FNSB,13),col)
    seal(im,"DISCIPLINE","the physics is suggestive — the metaphysics is transformative")

def vis_final(im,u,t,p):
    w,h=im.size; d=ImageDraw.Draw(im); cx,cy=w*.50,h*.40; r=ease(u)
    pts=draw_timeline(im,cx,cy,w*.55,r,"none")
    if r>.5:
        glow_circle(im,cx,cy,16,GOLD,int(180*(r-.5)*2),13)
    if r>.7:
        q=(r-.7)/.3
        centered(d,(cx,cy),"THE PAST IS NOT A PRISON",font(FSB,20),(*GOLD,int(200*q)))
        centered(d,(cx,cy+32),"it is a story you can rewrite",font(FNS,15),(*SOFT_INK,int(160*q)))
    seal(im,"THE PAST CAN BE CHANGED","remission means to send back — and you can send healing",GOLD)

VISUALS={}
for k,v in list(locals().items()):
    if k.startswith('vis_'): VISUALS[k[4:]]=v

@dataclass
class Scene:
    title:str; narration:str; duration:float; visual:str; params:dict

SCENES=[
    Scene("The claim","Remission of sins means 'to send back' — the past can be altered.",8.5,"claim",{}),
    Scene("Early Christian knowledge","The early Christians understood that forgiveness is retroactive healing.",8.0,"claim",{}),
    Scene("The fixed past","We assume the past is settled — immutable, unchangeable.",7.5,"static_past",{}),
    Scene("The assumption","But is this an assumption about reality or a limitation of perception?",8.0,"static_past",{}),
    Scene("The quantum eraser","In the lab, a future measurement determines a past event's trajectory.",9.5,"quantum_eraser",{}),
    Scene("Delayed choice","Wheeler's delayed choice experiment: choice now decides what happened.",9.0,"quantum_eraser",{}),
    Scene("The present as power","If the past is not fixed, the present is the only point of power.",8.5,"present_power",{}),
    Scene("Now changes everything","What you do now reaches backward and forward.",8.0,"present_power",{}),
    Scene("Seth on the past","'Each present moment brings its own built-in past along with it.'",8.5,"seth_past",{}),
    Scene("Not given — chosen","The past is not a given — it is a selection from probability.",9.0,"seth_past",{}),
    Scene("Caution","Quantum eraser is real. Retroactive causality is theoretical.",8.5,"caution",{}),
    Scene("The therapeutic truth","Whether or not the past physically changes, your relationship to it can.",9.0,"caution",{}),
    Scene("Closing","The past is not a prison. It is a story you can rewrite.",9.0,"final",{}),
    Scene("Final frame","Send healing backward. The past is listening.",7.0,"final",{}),
]

def rf(sc,fi,fc,w2,h2,se):
    u=fi/max(1,fc-1); t=u*sc.duration; im=field(w2,h2,se)
    VISUALS[sc.visual](im,u,t,sc.params); border(im); return im.convert("RGB")
def _ff():
    f2=shutil.which("ffmpeg")
    if not f2: raise RuntimeError("ffmpeg required"); return f2
def es(idx,f2):
    o=SCENES_DIR/f"scene_{idx:03d}.mp4"; d=FRAMES/f"scene_{idx:03d}"
    subprocess.run([_ff(),"-y","-framerate",str(f2),"-i",str(d/"%05d.jpg"),
        "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(o)],
        check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); return o
def rs(idx,s,f2,w2,h2,prev):
    d=FRAMES/f"scene_{idx:03d}"; d.mkdir(parents=True,exist_ok=True)
    SCENES_DIR.mkdir(parents=True,exist_ok=True); cnt=max(2,round(s.duration*f2))
    if prev:
        for oi,fi2 in enumerate([0,int(cnt*.33),int(cnt*.72),cnt-1]):
            rf(s,fi2,cnt,w2,h2,idx*10000+fi2).save(d/f"preview_{oi:02d}.jpg",quality=95)
        return d
    for fi2 in range(cnt):
        p=d/f"{fi2:05d}.jpg"
        if p.exists(): continue
        rf(s,fi2,cnt,w2,h2,idx*10000+fi2).save(p,quality=95,subsampling=0)
    return es(idx,f2)
def concat(paths):
    cp=OUTPUT/"concat.txt"
    cp.write_text("\n".join(f"file '{p.resolve()}'" for p in paths),encoding="utf-8")
    final=OUTPUT/"past_can_be_changed.mp4"
    subprocess.run([_ff(),"-y","-f","concat","-safe","0","-i",str(cp),"-c","copy","-movflags","+faststart",str(final)],
        check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); return final
def export_timeline():
    cursor=0.0; recs=[]
    for i,s in enumerate(SCENES,1):
        item=asdict(s); item["scene_id"]=f"scene_{i:03d}"
        item["start_seconds"]=round(cursor,3); cursor+=s.duration; item["end_seconds"]=round(cursor,3); recs.append(item)
    p=OUTPUT/"narration_timeline.json"
    p.write_text(json.dumps({"title":"the past can be changed","subtitle":"remission is retroactive alteration",
        "scene_count":len(SCENES),"runtime_seconds":round(cursor,3),"shot_duration_range":[5,10],
        "continuity_object":"timeline being rewritten from the present moment",
        "scenes":recs},indent=2,ensure_ascii=False),encoding="utf-8"); return p
def contact_sheet(w2,h2):
    tw,th=320,int(320*h2/w2); cols,rows=4,math.ceil(len(SCENES)/4); ch=th+48
    s=Image.new("RGB",(cols*tw,rows*ch),IVORY); d2=ImageDraw.Draw(s); lf=font(FNSB,14)
    for i,sc in enumerate(SCENES,1):
        cnt=max(2,round(sc.duration*FPS))
        im=rf(sc,int(cnt*.72),cnt,w2,h2,i*10000+72)
        im.thumbnail((tw,th)); sl=i-1; x=(sl%cols)*tw; y=(sl//cols)*ch
        s.paste(im,(x,y)); d2.text((x+9,y+th+7),f"{i:02d}  {sc.title}",font=lf,fill=INK)
    p=OUTPUT/"contact_sheet.jpg"; s.save(p,quality=94); return p
def parse_args():
    p2=argparse.ArgumentParser()
    p2.add_argument("--fps",type=int,default=FPS); p2.add_argument("--width",type=int,default=W)
    p2.add_argument("--height",type=int,default=H); p2.add_argument("--scene",type=int)
    p2.add_argument("--preview",action="store_true"); p2.add_argument("--no-contact-sheet",action="store_true")
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
