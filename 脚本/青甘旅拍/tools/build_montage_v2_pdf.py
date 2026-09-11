"""Render the v2 director's review booklet. Diagrams are vectors, not location photos."""
from pathlib import Path
import json
import math
from html import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

P=Path(__file__).resolve().parents[1]
ROOT=P.parents[1]
OUT=ROOT/'output'/'pdf'/'青甘旅拍_一瞥_V2_蒙太奇分镜.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
D=json.loads((P/'analysis'/'montage_v2.json').read_text(encoding='utf-8'))
pdfmetrics.registerFont(TTFont('CJK','C:/Windows/Fonts/msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('CJK-B','C:/Windows/Fonts/msyhbd.ttc',subfontIndex=0))
W,H=841.89,595.28
INK=HexColor('#172c35');MUTED=HexColor('#596b70');PAPER=HexColor('#f3f0e9');LINE=HexColor('#d6d8d0')
BLUE=HexColor('#5a8794');SAND=HexColor('#b87d47');OLIVE=HexColor('#737c62');DARK=HexColor('#102830')
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('一瞥 | 青甘大环线蒙太奇分镜 V2')
c.setAuthor('青甘旅拍创作项目')
page=0; checks=[]

def clean(t):return t.replace('\u2011','-').replace('–','-').replace('—','-')
def para(t,x,top,width,size=10.2,leading=None,color=INK,bold=False):
 st=ParagraphStyle('p',fontName='CJK-B' if bold else 'CJK',fontSize=size,leading=leading or size*1.5,textColor=color,wordWrap='CJK',spaceAfter=0)
 p=Paragraph(escape(clean(t)).replace('\n','<br/>'),st)
 aw,ah=p.wrap(width,H)
 p.drawOn(c,x,top-ah)
 return top-ah
def text(t,x,y,size=10,color=INK,bold=False):
 c.setFillColor(color);c.setFont('CJK-B' if bold else 'CJK',size);c.drawString(x,y,clean(t))
def right(t,x,y,size=9,color=MUTED):
 c.setFillColor(color);c.setFont('CJK',size);c.drawRightString(x,y,clean(t))
def newpage(title,eyebrow='一瞥 / 导演工作稿 V2',dark=False):
 global page
 if page:c.showPage()
 page+=1
 c.setFillColor(DARK if dark else PAPER);c.rect(0,0,W,H,fill=1,stroke=0)
 fg=HexColor('#eaece5') if dark else INK
 small=HexColor('#9db2b5') if dark else MUTED
 text(eyebrow,42,H-30,8.5,small)
 if title:text(title,42,H-59,20,fg,True)
 c.setStrokeColor(HexColor('#34505a') if dark else LINE);c.setLineWidth(.5);c.line(42,31,W-42,31)
 text('青甘顺时针 · 9/26-10/5 · 单人主角',42,17,7.6,small)
 right(f'{page:02d}',W-42,17,8,small)

def pathpoly(points,fill,stroke=None,width=.7):
 p=c.beginPath();p.moveTo(*points[0])
 for pt in points[1:]:p.lineTo(*pt)
 p.close();c.setFillColor(fill);c.setStrokeColor(stroke or fill);c.setLineWidth(width);c.drawPath(p,fill=1,stroke=bool(stroke))
def human(x=110,y=15,scale=1,walking=False,phase=None):
 c.saveState();c.translate(x,y);c.scale(scale,scale)
 c.setFillColor(INK);c.circle(0,35,3.3,fill=1,stroke=0)
 pathpoly([(-4,29),(4,29),(6,12),(-4,12)],SAND)
 c.setStrokeColor(INK);c.setLineWidth(2)
 if phase:
  c.line(-1,13,-4,0)
  knee,foot={'walk_lake':((7,19),(9,12)),'walk_salt':((8,13),(13,5)),'walk_sand':((7,7),(12,0))}[phase]
  c.line(2,13,*knee);c.line(*knee,*foot)
 else:
  c.line(-1,13,(-6 if walking else -2),0);c.line(2,13,(8 if walking else 3),0)
 c.setLineWidth(1.4);c.line(-4,25,-7,15);c.line(4,25,(8 if walking else 5),16)
 c.restoreState()
def arrow(x1,y1,x2,y2,color=BLUE):
 c.setStrokeColor(color);c.setLineWidth(.9);c.line(x1,y1,x2,y2)
 ang=math.atan2(y2-y1,x2-x1)
 for da in [-.5,.5]:c.line(x2,y2,x2-4*math.cos(ang+da),y2-4*math.sin(ang+da))

def frame(x,y,w,h,kind,caption=None):
 c.saveState();clip=c.beginPath();clip.rect(x,y,w,h);c.clipPath(clip,stroke=0,fill=0)
 c.translate(x,y);c.scale(w/160,h/90)
 c.setFillColor(HexColor('#dce3df'));c.rect(0,0,160,90,fill=1,stroke=0)
 def hills():
  pathpoly([(0,32),(20,49),(42,35),(66,57),(88,40),(110,52),(139,35),(160,44),(160,0),(0,0)],HexColor('#adbab7'))
  pathpoly([(0,22),(34,28),(60,20),(94,35),(124,29),(160,37),(160,0),(0,0)],HexColor('#c7b597'))
 if kind in ('fabric','dune','mountain'):
  if kind=='mountain':hills()
  c.setFillColor(HexColor('#b3aa83') if kind=='fabric' else HexColor('#c4a276'));c.rect(0,0,160,90,fill=1,stroke=0) if kind=='fabric' else None
  pathpoly([(0,22),(160,68),(160,0),(0,0)],HexColor('#706d58') if kind=='fabric' else HexColor('#a77d55'))
  c.setStrokeColor(HexColor('#efe0b7'));c.setLineWidth(1.2);c.line(0,22,160,68)
  if kind=='fabric':
   c.setStrokeColor(HexColor('#929578'));c.setLineWidth(.25)
   for i in range(8,160,11):c.line(i,0,i+12,90)
  if kind=='dune':
   c.setStrokeColor(HexColor('#c49c6f'));c.setLineWidth(.35)
   for i in range(5,50,7):c.line(0,i,130,i+26)
 elif kind in ('palm','hand'):
  c.setFillColor(HexColor('#d7b59b'));p=c.beginPath();p.moveTo(25,0);p.curveTo(18,29,28,55,46,70);p.curveTo(65,85,82,75,86,54);p.curveTo(109,83,136,82,139,65);p.curveTo(157,43,120,9,119,0);p.close();c.drawPath(p,fill=1,stroke=0)
  for off in [0,8,16]:
   q=c.beginPath();q.moveTo(39,20+off);q.curveTo(57,49+off,97,34+off,126,58+off);c.setStrokeColor(HexColor('#9b7769'));c.setLineWidth(.6);c.drawPath(q)
 elif kind in ('ripples','shore'):
  c.setFillColor(HexColor('#82a5ae'));c.rect(0,0,160,90,fill=1,stroke=0)
  if kind=='shore':
   p=c.beginPath();p.moveTo(0,0);p.lineTo(0,60);p.curveTo(80,70,26,10,160,20);p.lineTo(160,0);p.close();c.setFillColor(HexColor('#e0d6ba'));c.drawPath(p,fill=1,stroke=0)
  else:
   for off in range(-15,70,9):
    p=c.beginPath();p.moveTo(0,off);p.curveTo(50,off+27,110,off+1,160,off+28);c.setStrokeColor(HexColor('#d1e0df'));c.setLineWidth(.75);c.drawPath(p)
 elif kind in ('window','window_hand'):
  hills();c.setFillColor(Color(.12,.22,.25,alpha=.14));c.rect(0,0,160,90,fill=1,stroke=0)
  c.setStrokeColor(INK);c.setLineWidth(5);c.line(142,0,126,90);c.line(0,84,128,84)
  if kind=='window':
   c.setFillColor(Color(.17,.27,.30,alpha=.6));c.ellipse(30,20,69,73,fill=1,stroke=0);pathpoly([(41,24),(80,0),(8,0),(23,26)],Color(.17,.27,.30,alpha=.5));arrow(74,53,97,53)
  else:
   pathpoly([(56,0),(64,44),(72,47),(79,3)],HexColor('#b99c85'));c.setStrokeColor(HexColor('#e9dbc0'));c.setLineWidth(.7);c.line(32,30,125,64)
 elif kind=='foot':
  c.setFillColor(HexColor('#c6ad85'));c.rect(0,0,160,31,fill=1,stroke=0);pathpoly([(51,89),(70,89),(77,29),(58,24)],HexColor('#334750'));pathpoly([(57,28),(77,32),(110,21),(113,14),(57,13)],INK);arrow(111,42,136,31)
 elif kind in ('grass','fabric_wind','cloud'):
  if kind=='grass':
   c.setFillColor(HexColor('#c8ba88'));c.rect(0,0,160,32,fill=1,stroke=0)
   for i in range(5,160,8):
    c.setStrokeColor(OLIVE);c.setLineWidth(.8);p=c.beginPath();p.moveTo(i,0);p.curveTo(i,21,i+12,30,i+19,49);c.drawPath(p)
  elif kind=='cloud':
   hills();pathpoly([(5,23),(47,59),(85,41),(108,26),(99,8),(45,10)],HexColor('#82958f'))
  else:
   pathpoly([(0,72),(48,78),(93,42),(136,54),(160,31),(150,7),(99,21),(48,14),(0,30)],SAND);c.setStrokeColor(HexColor('#dbc18c'));c.setLineWidth(1);p=c.beginPath();p.moveTo(0,56);p.curveTo(44,66,77,23,157,36);c.drawPath(p)
  arrow(100,75,140,75)
 elif kind=='curve':
  hills();p=c.beginPath();p.moveTo(2,8);p.curveTo(54,50,58,14,103,37);p.curveTo(122,48,134,39,160,57);c.setStrokeColor(HexColor('#f0e4c5'));c.setLineWidth(5);c.drawPath(p);arrow(109,73,141,73)
 else:
  hills()
  if kind=='walk_lake':
   c.setFillColor(BLUE);c.rect(0,17,160,24,fill=1,stroke=0)
  elif kind=='walk_salt':
   c.setFillColor(HexColor('#ede7d6'));c.rect(0,0,160,36,fill=1,stroke=0)
  elif kind=='walk_sand':
   c.setFillColor(HexColor('#c1a174'));c.rect(0,0,160,36,fill=1,stroke=0)
  if kind=='shadow':pathpoly([(60,8),(90,13),(130,61),(111,70)],HexColor('#6c7062'))
  elif kind=='absence':pass
  elif kind in ('profile','shoulder','turn'):
   human(63,-23,2.3)
   if kind=='turn':arrow(104,74,139,74)
  else:
   human(50 if kind.startswith('walk') else 116,12,.95,kind.startswith('walk') or kind=='run',kind if kind in ('walk_lake','walk_salt','walk_sand') else None)
   if kind.startswith('walk') or kind=='run' or kind=='turn':arrow(104,74,139,74)
 c.restoreState()
 c.setStrokeColor(HexColor('#a7b0aa'));c.setLineWidth(.4);c.rect(x,y,w,h,fill=0,stroke=1)
 if caption:para(caption,x,y-4,w,8.1,11,MUTED)

def timeline(x,y,w,h):
 cols=[BLUE,HexColor('#76959a'),SAND,HexColor('#566670'),HexColor('#bc8f59'),OLIVE]
 for stage,col in zip(D['stages'],cols):
  a=stage['start']/90*w;b=stage['end']/90*w;c.setFillColor(col);c.rect(x+a,y,b-a-.8,h,fill=1,stroke=0)
  text(f"{stage['start']:g}",x+a,y-15,7.8,MUTED)
 right('90s',x+w,y-15,7.8,MUTED)

# 1 - cover
newpage('',eyebrow='QINGHAI + GANSU / A SOLO TRAVEL FILM',dark=True)
text('一瞥',44,427,76,HexColor('#eee9dc'),True)
text('一条线，一次跨步，一段被折叠的时间。',49,386,18,HexColor('#c6d0c7'))
text('90秒蒙太奇旅拍 / V2',50,343,14,HexColor('#bda478'))
fw=(W-100-24)/3
for i,(k,lab) in enumerate([('fabric','衣褶'),('dune','沙脊'),('mountain','远山')]):
 frame(50+i*(fw+12),137,fw,fw*9/16,k)
 text(lab,50+i*(fw+12),119,9,HexColor('#b8c7c7'))
text('35镜  /  8组蒙太奇  /  大胆段落与停顿并存',50,76,11,HexColor('#e3e4d7'))
text('本轮验收画面叙事、镜头关系与可拍性；音频工作暂缓。',50,54,9,HexColor('#9eb3b4'))

# 2 - idea and visual pacing
newpage('让故事发生在镜头之间')
y=H-105
text('故事简介',42,y,13,INK,True)
y=para('车窗上映着你的侧脸。转头刚开始，镜头便离开连续时间。衣褶接沙脊，再长成山；掌纹接水纹，一步跨过湖岸、盐地与沙地。',42,y-16,352,11,18)
y=para('你在一个地方站住，下一镜只剩相同的空地，像记忆漏掉一拍。衣摆、草、水和山坡开始沿同一方向运动，分散的地方共享一阵风。',42,y-14,352,11,18)
y=para('你再次出现，又完整地走出画面。这一次观众看见了离开，空景变得平静。最后回到车窗，开头的转头继续完成。九十秒的旅行，被折叠进一次观看。',42,y-14,352,11,18)
para('人物是这段旅行的感知者。表演以看、走、转身、停留为主，情绪由意象的重复、空缺与重现产生。',42,y-20,352,10,16,MUTED)
rx=432;ry=H-106
for st in D['stages']:
 text(f"{st['start']:g}-{st['end']:g}s",rx,ry,9,SAND,True)
 text(st['name'],rx+91,ry,11,INK,True)
 para(st['feeling']+'。'+st['rhythm'],rx+91,ry-11,271,9.2,14,MUTED)
 ry-=62
timeline(42,69,W-84,13)

# 3 and 4 - unaltered generated reference contact sheets when present
boards=[('v2_materials.png','材质、形状与尺度','上排对应V2-02/03/04；下排对应V2-06/07/08。','从身体表面到山河，再从近距离纹理扩展到辽阔。'),('v2_presence.png','动作、空缺与回环','上排对应V2-12/13/14；下排对应V2-20/21及G0车窗。','上排看同一步的跨地衔接；下排看人物和空景的关系。')]
for fname,title,label,meaning in boards:
 newpage(title,eyebrow='AI CONCEPT REFERENCE / 概念画面')
 img=P/'assets'/fname
 if img.exists():
  ir=ImageReader(str(img));iw,ih=ir.getSize();ww=W-84;hh=min(ww*ih/iw,342);ww=hh*iw/ih
  c.drawImage(ir,(W-ww)/2,H-96-hh,width=ww,height=hh,preserveAspectRatio=True,mask='auto')
  by=H-112-hh
 else:
  for row in range(2):
   for col in range(3):frame(42+col*259,H-225-row*154,245,138,['fabric','dune','mountain','palm','ripples','shore'][row*3+col])
  by=155
 para(label,42,by,W-84,10.3,16,INK,True)
 para(meaning,42,by-27,W-84,10,16)
 para('AI画面用于比较构图与气质，不代表用户相貌、实际机位或天气。精确的动作相位和线条位置以后续逐镜卡与现场配对记录为准。',42,by-56,W-84,9,14,MUTED)

# 5-6 - montage relationship cards, four per page
diagrams={
 'G0':(['window','shore','window'],['转头前半','被展开的旅途','原动作下一帧']),
 'G1':(['fabric','dune','mountain'],['身体表面','沙地','远山']),
 'G2':(['palm','ripples','shore'],['掌纹','水纹','岸线']),
 'G3':(['walk_lake','walk_salt','walk_sand'],['抬起 / 1.6秒','前送 / 1.2秒','将落 / 0.8秒']),
 'G4':(['turn','curve','profile'],['人转动','景观接住运动','人停住']),
 'G5':(['presence','absence','profile'],['人在','人已离开','人物重新出现']),
 'G6':(['fabric_wind','grass','ripples'],['衣摆','草','水']),
 'G7':(['walk_grass','absence','window'],['完整走出','空景停留','回到一瞥']),
}
cw=(W-84-20)/2;ch=220
for gi in range(0,len(D['groups']),4):
 newpage(f'蒙太奇关系 / {gi//4+1:02d}')
 for j,g in enumerate(D['groups'][gi:gi+4]):
  x=42+(j%2)*(cw+20);y=H-91-(j//2)*232
  text(g['id']+' / '+g['name'],x,y,12.3,INK,True)
  text(g['method'],x,y-18,8.7,SAND)
  fw=(cw-16)/3; fh=fw*9/16
  kinds,labels=diagrams[g['id']]
  for k,(kind,lab) in enumerate(zip(kinds,labels)):frame(x+k*(fw+8),y-33-fh,fw,fh,kind,lab)
  py=y-51-fh
  py=para(g['meaning'],x,py,cw,9.1,13.4)
  py=para('拍摄：'+g['capture'],x,py-7,cw,8.6,12.3,MUTED)
  checks.append({'kind':'group','id':g['id'],'page':page,'bottom_y':py,'limit':38 if j//2 else 271})
  if py < (38 if j//2 else 271):raise ValueError(f"Group overflow {g['id']}: {py}")

# 7 onward - four shot cards per page
cardw=(W-84-18)/2;cardh=232
for offset in range(0,len(D['shots']),4):
 newpage(f"逐镜卡 / {offset+1:02d}-{min(offset+4,len(D['shots'])):02d}",eyebrow='PICTURE SCRIPT / 成片时间码为 分:秒:帧 · 25fps')
 for j,s in enumerate(D['shots'][offset:offset+4]):
  x=42+(j%2)*(cardw+18);top=H-83-(j//2)*(cardh+12);bottom=top-cardh
  c.setFillColor(HexColor('#faf8f2'));c.setStrokeColor(LINE);c.setLineWidth(.55);c.roundRect(x,bottom,cardw,cardh,4,fill=1,stroke=1)
  text(s['id']+' / '+s['group'],x+11,top-18,11,INK,True)
  right(f"{s['timecode_in']} - {s['timecode_out']}  |  {s['duration']:g}s",x+cardw-11,top-18,8.1,MUTED)
  fw=143;fh=fw*9/16; fy=top-33-fh
  frame(x+11,fy,fw,fh,s['diagram'])
  rx=x+fw+21; rw=cardw-fw-32
  pt=para(s['scale']+' / '+s['location'],rx,top-32,rw,8.4,11.5,SAND,True)
  pt=para(s['picture'],rx,pt-6,rw,8.6,12.3)
  # Text continues below the 16:9 composition thumbnail.
  start=min(fy,pt)-9
  fields=[('连接：',s['montage']),('拍法：',s['execution']),('替代：',s['alternative'])]
  # Select a readable size using the actual remaining space, then draw once.
  chosen=None
  for fs in [8.5,8.2,8.0]:
   htotal=0
   for label,body in fields:
    st=ParagraphStyle('measure',fontName='CJK',fontSize=fs,leading=fs*1.35,wordWrap='CJK')
    q=Paragraph(escape(clean(label+body)),st);_,hh=q.wrap(cardw-22,H);htotal+=hh+4
   if start-htotal >= bottom+7:chosen=fs;break
  if chosen is None:raise ValueError(f"Shot text overflow: {s['id']}")
  py=start
  for label,body in fields:py=para(label+body,x+11,py,cardw-22,chosen,chosen*1.35,MUTED if label=='替代：' else INK)-4
  checks.append({'kind':'shot','id':s['id'],'page':page,'bottom_y':py,'limit':bottom+7,'font_size':chosen})
 if offset+4>=len(D['shots']):
  # The unfilled fourth card becomes a compact production reminder.
  x=42+cardw+18;top=H-83-(cardh+12)
  text('每条镜头都多留一点时间',x+12,top-30,13,INK,True)
  yy=para('动作前后各留5秒。\n纹理与环境每条录10-20秒。\n人物出画后，空镜至少再录20秒。',x+12,top-52,cardw-24,11,19)
  para('本页的小图为构图与运动示意。摄影参考页为AI生成的气质预演；人物与地点均以实拍为准。',x+12,yy-24,cardw-24,9.2,15,MUTED)

# shoot route page
newpage('把互相连接的镜头一起带回来')
routes=[
 ('准备 / 西宁','G0转头首尾；G1布料；G2掌纹','一条连续转头素材；三张动作相位参考。'),
 ('青海湖','G3湖岸一步；G2水纹；G6水面运动','固定人物画面高度与左到右方向。'),
 ('茶卡','G3浅白背景同一步；衣摆','从允许停留区域取白色层次。'),
 ('大柴旦','G2弯曲岸线；V2-31平静宽景','纯景航拍有条件才拍，同步留地面版本。'),
 ('向敦煌转移','G4地貌曲线；车窗反射备份','不改变路线只为追一个插镜。'),
 ('敦煌','G1沙脊；G3落脚；G5人物/空景','三脚架不动，一条素材拍站住、走出、空录。'),
 ('张掖','G6山线展开；G1山肩备份','使用地面开放观景位置。'),
 ('祁连','G1远山；G6草；G7完整走出','人物出画后的同机位空景至少20秒。'),
 ('返程','核对配对齐全，补可移植细节','不把关键组压到返程最后一天。'),
]
xcols=[42,185,502];y=H-111
for lab,x in zip(['路线段','优先带回的素材','收工前核对'],xcols):text(lab,x,y,10.5,INK,True)
y-=15
for idx,(route,material,note) in enumerate(routes):
 rowh=43;c.setFillColor(HexColor('#e6e7de') if idx%2==0 else PAPER);c.rect(42,y-rowh,W-84,rowh,fill=1,stroke=0)
 para(route,48,y-9,129,9.6,14,INK,True);para(material,191,y-9,296,9.6,14);para(note,508,y-9,282,9.2,14,MUTED);y-=rowh
para('顺序由用户确认；日期和交通住宿仍按实际行程调整。详细镜号与配对要求见工作区《08_V2_蒙太奇配对拍摄单》。',42,y-13,W-84,8.8,13,MUTED)

# acceptance / continuity page
newpage('现场与剪辑共用的五条判断')
items=[
 ('转头真的连续','开头和结尾从同一条素材拆分。让最后一个动作接回最初的观看，而不是补拍一个近似姿势。'),
 ('线条之外还有一次回到人','衣褶、沙脊、山线之后，保留肩背与远山同框。形状匹配在这里成为人物和环境的关系。'),
 ('动作有起、中、落','三地一步可以大胆跳，但最后要看见脚落地。身体相位决定切点，镜头长度只提供初始框架。'),
 ('两次空景的时间处理不同','第一次省略离开，第二次完整看见离开。空景相似，观看的感受会因前后镜头而改变。'),
 ('短镜与停顿各有位置','0.8秒短镜集中在跨地动作与风的接力，4-6秒镜头负责容纳观看。保留这两种速度之间的落差。'),
]
y=H-112
for i,(title,body) in enumerate(items,1):
 c.setFillColor(SAND);c.circle(55,y-4,12,fill=1,stroke=0);text(str(i),51,y-8,11,HexColor('#fffaf0'),True)
 text(title,82,y,12,INK,True);y=para(body,82,y-15,W-132,10,16,MUTED)-24
para('版本边界：当前只验收视觉叙事与可拍性。音频暂停，V1音乐结构不约束本版时间线。35镜已校验为90秒、2250帧；后续可在不破坏关键配对的前提下调整镜长。',42,97,W-84,9.5,15,INK)
para('文件入口：README.md / 07_一瞥_V2_蒙太奇分镜.md / 08_V2_蒙太奇配对拍摄单.md。生成参考的提示词与原始输出路径均记录在项目中。',42,60,W-84,8.4,12,MUTED)
c.save()
(P/'analysis'/'pdf_layout_v2.json').write_text(json.dumps({'pdf':str(OUT),'page_count':page,'checks':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pdf':str(OUT),'pages':page,'layout_checks':len(checks)},ensure_ascii=False))
