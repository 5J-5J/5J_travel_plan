"""Render an illustrated director's workbook from the approved V2 and its V2.1 expansion."""
from pathlib import Path
from html import escape
import json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
D=json.loads((P/'analysis/inspiration_v21_resolved.json').read_text(encoding='utf-8'))
B=json.loads((P/'analysis/baseline_annotated_v21.json').read_text(encoding='utf-8'))
PK=json.loads((P/'analysis/package_timelines_v21.json').read_text(encoding='utf-8'))['packages']
OUT=ROOT/'output/pdf/青甘旅拍_一瞥_V2.1_情绪与关联分镜.pdf'
pdfmetrics.registerFont(TTFont('CJK','C:/Windows/Fonts/msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('CJK-B','C:/Windows/Fonts/msyhbd.ttc',subfontIndex=0))
W,H=841.89,595.28
PAPER=HexColor('#f3f0e9');INK=HexColor('#17323a');MUTE=HexColor('#596d73')
BLUE=HexColor('#508291');SAND=HexColor('#b57b45');LINE=HexColor('#d2d7cf');DARK=HexColor('#102830')
WHITE=HexColor('#f9f7ef');checks=[];page=0
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('一瞥 V2.1 | 情绪与关联分镜创作册')
c.setAuthor('青甘旅拍创作项目')
def clean(s):return str(s).replace('—','-').replace('–','-').replace('\u2011','-')
def measure(s,width,fs=10,leading=None,bold=False):
 st=ParagraphStyle('p',fontName='CJK-B' if bold else 'CJK',fontSize=fs,leading=leading or fs*1.48,textColor=INK,wordWrap='CJK')
 q=Paragraph(escape(clean(s)).replace('\n','<br/>'),st);_,hh=q.wrap(width,H)
 return q,hh
def para(s,x,top,width,fs=10,leading=None,col=INK,bold=False):
 q,hh=measure(s,width,fs,leading,bold);q.style.textColor=col;q.drawOn(c,x,top-hh)
 return top-hh
def txt(s,x,y,fs=10,col=INK,bold=False):
 c.setFillColor(col);c.setFont('CJK-B' if bold else 'CJK',fs);c.drawString(x,y,clean(s))
def endcheck(label,bottom,limit=42):
 checks.append({'page':page,'label':label,'bottom':bottom,'limit':limit})
 if bottom<limit:raise ValueError(f'Overflow page {page} {label}: {bottom} < {limit}')
def new(title,kicker='一瞥 V2.1 / 导演创作册',dark=False):
 global page
 if page:c.showPage()
 page+=1;c.setFillColor(DARK if dark else PAPER);c.rect(0,0,W,H,fill=1,stroke=0)
 col=WHITE if dark else INK;small=HexColor('#abc1c2') if dark else MUTE
 txt(kicker,42,H-29,8.4,small)
 if title:txt(title,42,H-62,21,col,True)
 c.setStrokeColor(HexColor('#34505a') if dark else LINE);c.setLineWidth(.5);c.line(42,31,W-42,31)
 txt('90秒 / 青甘顺时针 / 单人主角 / 画面创作，音频暂缓',42,17,7.6,small)
 c.setFillColor(small);c.setFont('CJK',8);c.drawRightString(W-42,17,f'{page:02d}')
 c.bookmarkPage(f'p{page}');c.addOutlineEntry(title or '封面',f'p{page}',0,False)
def board(key,x,top,width):
 path=P/D['board_files'][key]
 if not path.exists():raise FileNotFoundError(path)
 ir=ImageReader(str(path));iw,ih=ir.getSize();hh=width*ih/iw
 c.drawImage(ir,x,top-hh,width=width,height=hh,mask='auto')
 return top-hh
def table(headers,rows,widths,top,fs=9.2,minheight=38):
 x0=42;xx=x0
 for h,w in zip(headers,widths):para(h,xx+6,top,w-12,9.8,14,INK,True);xx+=w
 y=top-27
 for ri,row in enumerate(rows):
  heights=[measure(val,w-12,fs,fs*1.4)[1] for val,w in zip(row,widths)]
  rh=max(minheight,max(heights)+16)
  c.setFillColor(HexColor('#e7e8df') if ri%2==0 else PAPER);c.rect(x0,y-rh,sum(widths),rh,fill=1,stroke=0)
  xx=x0
  for j,(val,w) in enumerate(zip(row,widths)):
   para(val,xx+6,y-8,w-12,fs,fs*1.4,INK if j<2 else MUTE,j==0);xx+=w
  y-=rh
 endcheck('table',y)
 return y
def n(x):return f'{x:g}'
def ranges(g):return ' / '.join(f'{n(a)}至{n(b)}秒' for a,b in g['range'])

new('',dark=True)
txt('一瞥',46,452,68,WHITE,True)
txt('让一个画面，改变另一个画面的意义。',49,404,19,HexColor('#c5d1c8'))
txt('情绪与关联分镜创作册 / V2.1',49,365,14,HexColor('#ceaa74'))
bottom=board('a',(W-640)/2,342,640)
txt('11个情绪阶段  /  12组关联分镜  /  36个新镜头段',49,bottom-28,11,WHITE)
txt('4张六格生图参考  /  3套90秒组合  /  沿已认可的V2方向继续',49,bottom-49,9.5,HexColor('#adc2c2'))
endcheck('cover',bottom-52)

new('两个高点，不同的释放')
py=para('一次尚未完成的转头，展开整段旅途。前半的兴奋来自身体跨过不连续的地点；后半的开放来自画面变宽、人物放松。中间的空缺和末尾的连续离开，使两次空景拥有不同感受。',42,H-92,W-84,11,17)
txt('曲线只表示相对创作意图，不是测量数据，也不规定每位观众的反应。',42,py-20,8.7,MUTE)
x0,y0,cw,ch=61,208,W-122,168
for level in [1,3,5]:
 yy=y0+level/5*ch;c.setStrokeColor(LINE);c.setLineWidth(.6);c.line(x0,yy,x0+cw,yy)
txt('高',42,y0+ch-3,8,MUTE);txt('低',42,y0+7,8,MUTE)
for t in [0,11,27.4,43,56.8,74,90]:
 xx=x0+t/90*cw;txt(n(t),xx-6,y0-20,8,MUTE)
for field,color in [('motion',BLUE),('openness',SAND)]:
 points=[(x0+(p['a']+p['b'])/2/90*cw,y0+p[field]/5*ch) for p in D['phases']]
 path=c.beginPath();path.moveTo(*points[0])
 for pt in points[1:]:path.lineTo(*pt)
 c.setStrokeColor(color);c.setLineWidth(2);c.drawPath(path)
 for xx,yy in points:c.setFillColor(color);c.circle(xx,yy,2.7,fill=1,stroke=0)
txt('蓝线：视觉动量（剪接、镜内运动、信息变化）',42,162,9.2,BLUE)
txt('赭线：开放感（空间、身体与观看余地）',432,162,9.2,SAND)
para('第一次高点 / 27.4至35.2秒\n惊奇、轻盈。短镜递减之后，脚必须落稳。',42,133,352,10.5,17,INK,True)
para('第二次高点 / 63.2至74秒\n剪接已放慢，情绪却更开放。给空间，也给一个真实的人。',432,133,367,10.5,17,INK,True)
para('阅读顺序：先看分段情绪，再从关联镜头中选一两组。现有35个镜头段是基线，新增镜头按原时间槽替换。',42,69,W-84,9.2,14,MUTE)

for offset in range(0,len(D['phases']),2):
 new(f'情绪导演谱 / {offset+1:02d}至{min(offset+2,11):02d}')
 for j,p in enumerate(D['phases'][offset:offset+2]):
  top=H-93-j*233;left=42;right=432;colw=352
  txt(f"{p['id']} / {n(p['a'])}至{n(p['b'])}秒",left,top,10,SAND,True)
  txt(p['title'],left+148,top,13,INK,True)
  yy=top-17
  for label,key in [('感受','feel'),('推进','arc'),('节奏','rhythm'),('构图','frame')]:
   yy=para(label+'：'+p[key],left,yy,colw,9.2,13.4)-7
  endcheck(p['id']+' left',yy,43 if j else 276)
  yy=top-17
  for label,key in [('剪法','cut'),('表演','act'),('偏离','watch'),('调整','fix')]:
   yy=para(label+'：'+p[key],right,yy,367,9.2,13.4,MUTE if label=='偏离' else INK)-7
  endcheck(p['id']+' right',yy,43 if j else 276)
  txt(p['anchor'],left,top-210,8.2,MUTE)
 if offset==10:
  y=258;txt('四处先保护的观看时间',42,y,14,INK,True)
  y=para('23.4至27.4秒：4秒站住。\n48.4至54.4秒：6秒空景。\n74至83秒：完整离开与空景，连续9秒。\n86至90秒：完成开头动作的后4秒。',42,y-19,351,11,21)
  para('每个停顿都应有可观看的小变化。镜内可以有风、呼吸、重心移动。要调整时长时，先判断动作是否已经读懂，再检查下一段是否仍有速度差。',432,238,367,11,18)

for g in D['chains']:
 new(g['id']+' / '+g['name'],'LINKED SHOTS / 关联分镜灵感库')
 txt(ranges(g)+'  |  '+g['tone'],42,H-90,9.6,SAND,True)
 y=para(g['relation'],42,H-109,W-84,11.2,17)
 y=para('剪辑：'+g['method'],42,y-9,W-84,9.8,15,MUTE)
 cardtop=min(y-19,405);gap=14;cardw=(W-84-2*gap)/3;cardh=178
 for i,s in enumerate(g['shots']):
  x=42+i*(cardw+gap);bot=cardtop-cardh
  c.setFillColor(WHITE);c.setStrokeColor(LINE);c.roundRect(x,bot,cardw,cardh,4,fill=1,stroke=1)
  txt(s['id']+' / '+s['scale'],x+11,cardtop-19,10.8,INK,True)
  txt(f"{s['timecode_in']}至{s['timecode_out']} / {n(s['duration'])}秒",x+11,cardtop-38,8.5,SAND)
  yy=para(s['picture'],x+11,cardtop-52,cardw-22,10.4,15.6)
  yy=para('拍法：'+s['shoot'],x+11,yy-11,cardw-22,9.3,13.5,MUTE)
  endcheck(s['id'],yy,bot+9)
 lower=cardtop-cardh-17
 yy=para('配对：'+g['pair'],42,lower,352,9.5,14.2)
 yy=para('替代：'+g['fallback'],42,yy-10,352,9.5,14.2,MUTE)
 endcheck(g['id']+' shooting',yy,45)
 yy=para('接回主线：'+g['bridge'],432,lower,367,9.5,14.2)
 yy=para('试着想：'+g['prompt'],432,yy-10,367,10,15,SAND,True)
 endcheck(g['id']+' meaning',yy,45)
 if g['board']:
  refpage=21+'abcd'.index(g['board'])
  txt('画面参考：'+g['board'].upper()+('上排' if g['row']==0 else '下排')+f' / 第{refpage}页',42,49,8.8,BLUE)
  c.linkRect('',f'p{refpage}',(42,44,220,60),relative=0,thickness=0)

board_info=[('a','开口与折线','上排E01：窗缝、山口、衣领；下排E02：折纸、沙脊、放下纸后的身体。','先保存现场山形，再反过来补窗框、衣领或折纸，匹配会更容易。'),('b','一个画幅里的不同时间','上排E06：分屏到单幅再停住；下排E08：空景、人物、再次空景。','分屏素材拍完整横屏。生成背景只近似匹配，实拍空景必须来自同机位长录。'),('c','从遮挡到开放','上排E09：衣料遮挡、大景展开、回到身体；下排E10：肩背、反应、辽阔中的小人。','空间展开与身体自然反应共同承担情绪。无需继续加速，也不规定必须笑。'),('d','离开与回到观看','上排E11：进入、完全出画、连续空景；下排E12：转头前半、窗边手、转头后半。','上排是一条连续画面的三段；下排首尾来自同一素材，画面板无法替代真实动作时间。')]
for key,title,label,note in board_info:
 new(title,'AI CONCEPT REFERENCE / 生成的拍摄参考')
 yy=board(key,42,H-90,W-84)-19
 yy=para(label,42,yy,W-84,10.4,16,INK,True)
 yy=para(note,42,yy-11,W-84,10.2,16)
 yy=para('人物、地貌与天气均为概念占位。保持同组服装与动作连续，实际机位和取景以现场为准。原始提示词与采用输出路径保存在项目中。',42,yy-14,W-84,9.1,14,MUTE)
 endcheck('board '+key,yy)

new('意象回来的时候，含义要改变')
rows=[[m['name'],m['first'],m['middle'],m['last']] for m in D['motifs']]
y=table(['意象','第一次','中间变化','最后一次'],rows,[109,211,227,211],H-100,9.4,77)
para('相同镜头再次出现，只能唤起记忆；改变尺度、动作功能或前后语境，才会让记忆往前走。每次回到手、山线或空景，都给观众一个新的关系。',42,y-19,W-84,10.2,16)

new('三套可以直接试剪的90秒组合')
gap=18;colw=(W-84-gap*2)/3
for i,p in enumerate(PK):
 x=42+i*(colw+gap);top=H-105
 txt('组合'+p['id']+' / '+p['name'],x,top,12,INK,True)
 txt('90秒 / 2250帧 / '+str(p['shot_segments'])+'个镜头段',x,top-23,9,SAND)
 yy=para(p['intent'],x,top-43,colw,10.2,16)
 yy=para('替换组：'+'＋'.join(p['chains']),x,yy-15,colw,10,15,INK,True)
 for gid in p['chains']:
  g=next(g for g in D['chains'] if g['id']==gid)
  yy=para(gid+' / '+ranges(g)+'\n'+g['name'],x,yy-10,colw,9.8,15)
 yy=para('保留：'+p['keep'],x,yy-15,colw,9.6,15,MUTE)
 yy=para('提醒：'+p['caution'],x,yy-12,colw,9.6,15,MUTE)
 endcheck('package '+p['id'],yy,86)
para('先选一套比较，再按实拍素材微调。E01与E02、E04与E07与E08等占用相同时间槽，不能直接叠加。所有单组替换和上述三套组合都已校验为90秒，无时间空隙或重叠。',42,69,W-84,9.2,14)

new('把关系一起带回来的四张对照卡')
cards=[('01 / 形状与方向','保存第一条参考帧，标主线位置、亮面侧与屏幕运动箭头。','相机向左摇，静止景物在屏幕里向右走。先确定屏幕方向，再决定运镜。'),('02 / 身体与动作相位','保存起、中、落三帧，记录机高、人物头脚位置、拍摄设备与帧率。','每站拍完整动作。两台设备透视难匹配时，一组尽量用同一台完成。'),('03 / 人物与空景','一条固定长录拍空、入画、站住、走出、再空20秒。','同样素材能支持省略或连续时间。焦点、曝光、机位都保持稳定。'),('04 / 分屏与宽幅','每处都保存完整横屏，人两侧留足空间，分屏只在剪辑时裁切。','中间一列回到单幅时，使用原始宽幅，不把窄画面拉宽。')]
for i,(title,a,b) in enumerate(cards):
 x=42+(i%2)*390;top=H-110-(i//2)*181
 txt(title,x,top,13,INK,True)
 yy=para(a,x,top-21,352,11,17)
 yy=para(b,x,yy-13,352,10.2,16,MUTE)
 endcheck(title,yy,88 if i//2 else 268)
para('动作前后各留5秒；环境纹理10至20秒；人物出画后的空景至少20秒。三脚架承担关键叙事；帮拍优先留给自然反应近景与短距离陪走。',42,77,W-84,9.5,15)

new('现场继续发明镜头')
rows=[['弯曲边界','手腕与袖口','湖岸、山肩','手放下，露出站在岸边的人'],['明亮开口','车窗亮缝','两道山肩之间的天空','衣领与真正的远山同框'],['细密纹理','皮肤、织物','波纹、沙纹','回到手与衣料的真实动作'],['提前出现的影响','地上的影子','鞋先进入','全身站住，再切同机位空景'],['遮住视野的东西','衣摆、包带','突然展开的远景','它落回身体，尺度重新成立'],['相近颜色','外套暖色','同机位地面色块','人物近景把颜色带回来'],['走向画外的运动','手指退出边缘','风、水接着向同侧动','人离开，环境仍在动'],['未完成的动作','转头前半','整段旅途联想','同一素材后半，完成真实时间']]
y=table(['看见什么','第一镜','第二镜','第三镜怎样回到你'],rows,[121,153,205,279],H-98,9.5,38)
para('今天只需抓住一个具体观察，再找两个与它有关的画面。把其中两镜换序看一次：如果含义变了，你已经开始用剪辑写作。',42,y-20,W-84,10.3,16)

for offset in range(0,len(B['shots']),7):
 new(f'主线逐镜情绪索引 / {offset+1:02d}至{min(offset+7,35):02d}','APPROVED V2 BASELINE / 镜号、时间与可选扩展')
 rows=[]
 for s in B['shots'][offset:offset+7]:
  rows.append([s['id'],s['timecode_in']+'\n至'+s['timecode_out']+'\n'+n(s['duration'])+'秒',s['scale'],s['picture'],s['phase']+' '+s['phase_title']+'\n可选：'+(' / '.join(s['options']) or '首轮保留')])
 yy=table(['镜号','时间码 / 25fps','景别','画面行动','情绪与替换组'],rows,[62,98,83,302,213],H-100,9.2,48)
 para('新增E组按整组替换；未选部分沿用主线。V2-32与33是一条连续9秒画面的两段，镜号分段不表示要切开。完整拍法、连接意义与替代见原版逐镜稿及本册关联分镜。',42,yy-15,W-84,8.9,13.5,MUTE)

new('回看片段时，先改关系，再加效果')
rows=[[a,b,c_] for a,b,c_ in D['fixes']]
yy=table(['观看感受','可能发生了什么','可以先做的调整'],rows,[125,270,363],H-99,10,54)
yy=para('生成画面已经归档，核心镜头仍由你现场拍摄。地点与天气可以变化；最值得保留的是一个动作的前后、同一机位的有人与无人，以及意象回来时多出来的含义。',42,yy-19,W-84,10.3,16)
endcheck('closing',yy)
c.save()
(P/'analysis/pdf_layout_v21.json').write_text(json.dumps({'pdf':str(OUT),'pages':page,'layout_checks':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pdf':str(OUT),'pages':page,'layout_checks':len(checks)},ensure_ascii=False))
