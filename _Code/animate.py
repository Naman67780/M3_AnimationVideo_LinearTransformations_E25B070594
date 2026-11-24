"""Frame-accurate Cairo animation. Logical canvas 1440 x 810, output 1080p."""
import cairo as cr
import math, sys, subprocess, pathlib
from functools import lru_cache

W,H=1920,1080
INK='#f6f2e9'; MUT='#adbccc'; CY='#5ce5e5'; OR='#ffaf66'; PU='#ad93ff'; GRID='#37475c'; BG='#0a1423'; BLUE='#aacdf7'
sans='Open Sans'; serif='Liberation Serif'; mono='DejaVu Sans Mono'
def rgb(h): return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def col(h,a=1): c.set_source_rgba(*rgb(h),max(0,min(1,a)))
def smooth(t,a,b):
    u=max(0,min(1,(t-a)/(b-a)))
    return u*u*(3-2*u)
def line(x,y,X,Y,h,w=1,a=1):
    col(h,a); c.set_line_width(w); c.move_to(x,y); c.line_to(X,Y); c.stroke()
def dot(x,y,r,h,a=1):
    col(h,a); c.arc(x,y,r,0,math.tau);c.fill()
def txt(x,y,s,size=24,h=INK,f=sans,b=False,a=1):
    c.select_font_face(f,cr.FONT_SLANT_NORMAL,cr.FONT_WEIGHT_BOLD if b else cr.FONT_WEIGHT_NORMAL)
    c.set_font_size(size);col(h,a);c.move_to(x,y);c.show_text(s)
def rect(x,y,w,h,color,a=1):
    col(color,a);c.rectangle(x,y,w,h);c.fill()
def matrix(x,y,rows,color=INK,active=None):
    n=len(rows[0]); width=57 if n==1 else 107
    for i,row in enumerate(rows):
        for j,val in enumerate(row):
            txt(x+16+50*j,y+32+i*36,str(val),30,OR if j==active else color,mono)
    for edge,sgn in [(x,1),(x+width,-1)]:
        col(color);c.set_line_width(2.2);c.move_to(edge+8*sgn,y+2);c.line_to(edge,y+2);c.line_to(edge,y+79);c.line_to(edge+8*sgn,y+79);c.stroke()
    return width
A=[[2,1],[1,1]]
def equation(t,base,pair,out,idx=None):
    x,y=55,488
    matrix(x,y,A,INK,idx)
    matrix(x+128,y,[[pair[0]],[pair[1]]],CY)
    if t>base:
        txt(x+207,y+50,'=',34);matrix(x+258,y,[[out[0]],[out[1]]],OR)
def heading(k,words,desc):
    txt(55,180,k,16,CY,mono)
    for i,w in enumerate(words): txt(52,262+64*i,w,66,INK,serif)
    for i,d in enumerate(desc):txt(56,376+29*i,d,21,MUT)
def foot(label,sub):
    line(56,647,490,647,GRID);txt(56,683,label,18,INK,mono);txt(56,712,sub,17,MUT)
def mix(u,v,s):return u+(v-u)*s
def project(x,y):return ox+z*x,oy-z*y
def M(x,y):return (m[0]*x+m[1]*y,m[2]*x+m[3]*y)
def P(x,y):return project(*M(x,y))
def path(points,color,w=2,fill=0):
    col(color);c.set_line_width(w);c.move_to(*points[0])
    for q in points[1:]:c.line_to(*q)
    if fill:
        c.close_path();col(color,fill);c.fill_preserve();col(color)
    c.stroke()
def arr(start,end,color,w=5,a=1):
    x,y=start;X,Y=end;dx=X-x;dy=Y-y;d=math.hypot(dx,dy)
    if d<2:return
    dx/=d;dy/=d;L=min(d*.44,w*3.6)
    line(x,y,X-.7*L*dx,Y-.7*L*dy,color,w,a)
    col(color,a);c.move_to(X,Y);c.line_to(X-L*dx-.42*L*dy,Y-L*dy+.42*L*dx);c.line_to(X-L*dx+.42*L*dy,Y-L*dy-.42*L*dx);c.close_path();c.fill()
def vec(v,h,start=(0,0),w=5):arr(P(*start),P(*v),h,w)
def label(xy,s,dx,dy,h):
    if not s:return
    x,y=xy;x+=dx;y+=dy
    c.select_font_face(mono);c.set_font_size(17);width=c.text_extents(s)[4]
    rect(x-4,y-17,width+8,22,BG,.91);txt(x,y,s,17,h,mono)
def deform(t):
    # Two simultaneous shears. Their product preserves area throughout.
    return (1+t*t,t,t,1)
def grid(alpha):
    for i in range(-14,15):
        line(*project(-20,i),*project(20,i),GRID,1,.68*alpha)
        line(*project(i,-20),*project(i,20),GRID,1,.68*alpha)
    if m!=(1,0,0,1):
        for i in range(-17,18):
            line(*P(-28,i),*P(28,i),PU,1.35,.52*alpha)
            line(*P(i,-28),*P(i,28),PU,1.35,.52*alpha)
    line(573,oy,1384,oy,INK,1.5,.7*alpha);line(ox,708,ox,118,INK,1.5,.7*alpha)
    txt(1364,oy-12,'x',20,INK,serif);txt(ox+12,138,'y',20,INK,serif)
    for j in range(-8,10):
        x,y=project(j,0)
        if 593<x<1350 and j: txt(x-5,oy+22,str(j),13,MUT,mono)
        x,y=project(0,j)
        if 147<y<688 and j: txt(ox-24,y+5,str(j),13,MUT,mono)
def square(amount=1):
    pts=[P(0,0),P(1,0),P(1,1),P(0,1)]
    path(pts,OR,2,.19*amount)
    for p in pts:dot(*p,4,INK)
def basis(s=1,labels=True):
    for x,y,name,off in [(1,0,'e₁',(9,18)),(0,1,'e₂',(-29,-12))]:
        if s>.001:
            arr(project(0,0),project(x,y),CY,3,.54)
        end=P(x,y); arr(P(0,0),end,OR if s>.001 else CY,5)
        if labels:label(end,('A'+name if s>.999 else name if s<.001 else ''),*off,OR if s>.001 else CY)
def ticks(t,starts,labels):
    i=max(j for j,v in enumerate(starts) if t>=v)
    return labels[i]
bounds=[0,35,75,140,200,270,300]; names=['The guiding question','Two rules of linearity','Reading the columns','Mapping the plane','Area and orientation','Three takeaways']
def frame(t):
    global c,ox,oy,z,m
    surf=cr.ImageSurface(cr.FORMAT_RGB24,W,H);c=cr.Context(surf);c.scale(4/3,4/3)
    col(BG);c.paint();k=next(i for i in range(6) if bounds[i]<=t<bounds[i+1])
    txt(55,56,'M3   /   LINEAR ALGEBRA AND CALCULUS',16,MUT,mono)
    txt(1042,56,'GEOMETRY   /   '+f'CHAPTER 0{k+1}',16,MUT,mono)
    line(55,78,1385,78,GRID)
    ox,oy,z=805,540,100
    s=0;mode='basis'
    if k==0:
        s=smooth(t,12.5,19);z=110+8*smooth(t,1,20)
        if t<20:
            heading('VECTOR TRANSFORMATIONS',['How matrices','transform vectors'],['Understanding linear transformations','through geometry'])
            txt(56,525,'Naman Saini',30,INK,serif);txt(56,557,'E25B070594',17,MUT,mono)
            foot('THE GUIDING QUESTION','Where will the two arrows land?')
        else:
            heading('A VISUAL EXPLORATION',['How matrices','transform vectors'],['Understanding linear transformations','through geometry'])
            txt(56,525,'Presented by Naman Saini',29,INK,serif);txt(56,557,'E25B070594',17,MUT,mono)
            foot('THE AREA PUZZLE','A new shape. The same area.')
    elif k==1:
        if t<62.7:
            heading('01   /   ADDITION',['Two routes,','one endpoint'],['Place the second arrow at the tip','of the first. Trace the diagonal.'])
            txt(54,530,'T(u + v) = T(u) + T(v)',31,INK,serif)
            foot('ADD FIRST OR TRANSFORM FIRST','Both paths lead to the same point.')
            s=smooth(t,50,56);mode='sum'
        else:
            heading('02   /   SCALING',['Twice the','distance'],['A scalar counts copies of a vector.','Here the scalar is 2.'])
            txt(54,530,'T(cv) = cT(v)',42,INK,serif)
            foot('SCALAR MULTIPLICATION','The rule holds for every real scalar c.')
            s=smooth(t,68,72);mode='double'
    elif k==2:
        if t<88:
            heading('THE TRANSFORMATION MATRIX',['Four entries,','one map'],['v is the input vector.','Av is the output vector.'])
            txt(55,539,'T(v) =',39,INK,serif);matrix(177,490,A);matrix(310,490,[['x'],['y']],CY)
            foot('COLUMN VECTORS','Read coordinates from top to bottom.')
        elif t<111.6:
            heading('FIRST BASIS VECTOR',['One step','to the right'],['One copy of column one.','Zero copies of column two.'])
            equation(t,99,(1,0),(2,1),0);s=smooth(t,101,106);mode='first'
            foot('FIRST COLUMN','2 steps right, 1 step up.')
        elif t<126:
            heading('SECOND BASIS VECTOR',['One step','upward'],['Zero copies of column one.','One copy of column two.'])
            equation(t,117,(0,1),(1,1),1);s=smooth(t,117,122);mode='second'
            foot('SECOND COLUMN','1 step right, 1 step up.')
        else:
            heading('THE BASIS PRINCIPLE',['Keep the counts.','Map the steps.'],['Any vector is a combination','of the two basis vectors.'])
            txt(55,508,'v = x e₁ + y e₂',32,CY,serif);txt(55,560,'Av = x Ae₁ + y Ae₂',32,OR,serif)
            s=smooth(t,128,135);foot('TWO COLUMNS','Two destinations determine the map.')
    elif k==3:
        if t<178.7:
            heading('THE UNIT SQUARE',['From square to','parallelogram'],['Follow the four marked vertices.','The origin remains fixed.'])
            s=smooth(t,151,161);mode='corners'
            for i,st in enumerate(['(0, 0)  →  (0, 0)','(1, 0)  →  (2, 1)','(0, 1)  →  (1, 1)','(1, 1)  →  (3, 2)']):
                txt(55,477+i*35,st,24,OR if i==3 else INK,mono,a=.35+.65*smooth(t,142+i*2,145+i*2))
            foot('FAR CORNER','Ae₁ + Ae₂ gives the fourth vertex.')
        else:
            heading('WORKED EXAMPLE',['Where does','this arrow go?'],['One first step and two second steps.','Reuse the transformed basis.'])
            equation(t,190,(1,2),(4,3));s=smooth(t,184,191);mode='example'
            txt(55,610,'2·1 + 1·2 = 4     1·1 + 1·2 = 3',19,INK,mono)
            foot('FOLLOW THE COMPONENTS','First column + twice the second column.')
    elif k==4:
        if t<241:
            heading('THE DETERMINANT',['What happens','to area?'],['The absolute determinant gives','the area scale factor.'])
            txt(55,496,'det A = (2 × 1) − (1 × 1)',28,INK,serif)
            if t>220:txt(55,547,'= 2 − 1',34,INK,serif)
            if t>226:txt(55,601,'= 1',45,OR,serif)
            foot('UNIT SQUARE   /   AREA = 1','The parallelogram also has area 1.')
            s=smooth(t,202,213);mode='area';z=138
        else:
            heading('THE SIGN OF THE DETERMINANT',['Which way','around?'],['Trace the marked corners in order.','Their order reveals orientation.'])
            sign=ticks(t,[241,249,258],['+1','−1','0'])
            value=(1-2*smooth(t,249,252)) if 249<=t<258 else (1-smooth(t,258,263)) if t>=258 else 1
            moving=249<=t<252 or 258<=t<263
            txt(55,520,'det = '+(f'{value:.2f}' if moving else sign),50,OR,serif)
            desc={'+1':'Orientation preserved','−1':'Orientation reversed','0':'Area collapses to zero'}[sign]
            foot('DEFORMING THE SQUARE' if moving else desc.upper(),{'+1':'The original matrix A.','−1':'Reflection across the vertical axis.','0':'Projection onto the horizontal axis.'}[sign])
            mode='trace';s=1;ox=949;oy=558;z=135
    else:
        heading('SUMMARY   /   LINEAR TRANSFORMATIONS',['Geometry in','two columns'],[])
        for i,st in enumerate(['01   Map input vectors to outputs.','02   Basis images determine the grid.','03   det A gives area scale¹ and orientation.']):
            txt(55,403+i*37,st,18,INK if t>270+i*4 else MUT,sans)
        txt(55,503,'¹ Use |det A| for the area scale.',15,MUT)
        if t>=289:
            txt(55,565,'Thank you for watching',34,INK,serif);txt(55,600,'Narrated by Naman Saini  /  E25B070594',18,CY,mono)
            line(55,640,525,640,GRID);txt(55,671,'Reference: M3 project brief; standard basis derivation.',16,MUT)
            txt(55,702,'AI assistance: scripting, animation code and subtitles.',16,MUT)
        else:foot('Naman Saini   /   E25B070594','Linear Algebra and Calculus (M3)')
        s=1-smooth(t,270,275)+smooth(t,279,288);mode='final'
    m=deform(s)
    if mode=='trace':
        if t<249:m=deform(1)
        elif t<258:m=(1-2*smooth(t,249,252),0,0,1)
        else:m=(1,0,0,1-smooth(t,258,263))
    # Confine the plot to its own viewport; all formulas use the fixed frame.
    c.save();c.rectangle(570,104,816,615);c.clip()
    gradient=cr.RadialGradient(980,405,5,980,405,570)
    gradient.add_color_stop_rgb(0,.095,.142,.212);gradient.add_color_stop_rgb(1,.043,.079,.13)
    c.set_source(gradient);c.paint()
    grid(.18+.82*smooth(t,0,3) if k==0 else 1)
    if mode in ('basis','first','second','corners','area','final'):
        if mode in ('corners','area','final') or k==0 and t>12:square()
        if mode in ('first','second'):
            v=(1,0) if mode=='first' else (0,1)
            arr(project(0,0),project(*v),CY,4,.7);vec(v,OR if s else CY)
            label(P(*v),str(tuple(int(i) for i in M(*v))) if s in (0,1) else '',12,-9,INK)
        elif t<3:
            for x,y in [(1,0),(0,1)]:
                q=smooth(t,.4,3);arr(P(0,0),P(x*q,y*q),CY)
        else:basis(s)
        if mode=='corners' and (s==0 or s==1):
            label(P(1,1),'(3, 2)' if s else '(1, 1)',10,-13,INK)
        if mode=='area':label(P(1,1),'area = 1',17,-12,INK)
    elif mode=='sum':
        u=(1,0);v=(0,1);d=smooth(t,39,45)
        vec(u,CY if s==0 else OR);vec((d,1),CY if s==0 else OR,(d,0))
        if t>=44:vec((smooth(t,44,48),smooth(t,44,48)),INK,w=3)
        label(P(1,0),'u' if not s else 'T(u)',6,25,INK)
        label(P(d,1),'v' if not s else 'T(v)',-36,-12,INK)
        if t>48:label(P(.55,.55),'u + v' if not s else 'T(u + v)',8,22,INK)
    elif mode=='double':
        n=1+smooth(t,64,67);vec((n,0),CY if not s else OR)
        dot(*P(1,0),5,INK);label(P(n,0),'2v' if s==0 and n==2 else '2T(v)' if s==1 else '',10,-8,INK)
    elif mode=='example':
        arr(project(0,0),project(1,2),CY,3,.7);vec((1,2),OR if s else CY)
        if t>=191:
            prev=(0,0)
            for j,pt in enumerate([(1,0),(1,1),(1,2)]):
                f=smooth(t,191+j*1.5,192.5+j*1.5);vec((mix(prev[0],pt[0],f),mix(prev[1],pt[1],f)),INK,prev,3);prev=pt
        if s in (0,1):label(P(1,2),'(4, 3)' if s else '(1, 2)',12,-8,INK)
    else:
        square()
        trip=[(0,0),(1,0),(1,1),(0,1),(0,0)]
        phase=(t-241)*.75%4;j=int(phase);f=phase-j
        p,q=trip[j:j+2];moving=P(mix(p[0],q[0],f),mix(p[1],q[1],f))
        arr(P(*p),moving,INK,4);dot(*moving,6,CY)
    dot(*P(0,0),4,INK)
    c.restore()
    line(55,747,1385,747,GRID)
    line(55,747,55+1330*t/300,747,CY,2)
    txt(55,780,f'0{k+1} / 06     '+names[k].upper(),15,MUT,mono)
    txt(1228,780,f'{int(t)//60:02}:{int(t)%60:02}  /  05:00',14,MUT,mono)
    return surf

if __name__=='__main__':
    if sys.argv[1]=='still':
        frame(float(sys.argv[2])).write_to_png(sys.argv[3]);sys.exit()
    start,end=map(int,sys.argv[1:3]);pathlib.Path('build').mkdir(exist_ok=True)
    proc=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr0','-s','1920x1080','-r','30','-i','-','-c:v','libx264','-threads','3','-preset','ultrafast','-crf','17','-pix_fmt','yuv420p',f'build/{start:03}.mp4'],stdin=subprocess.PIPE)
    for i in range(start*30,end*30):
        surf=frame(i/30);proc.stdin.write(surf.get_data())
    proc.stdin.close();sys.exit(proc.wait())
