"""Generate the approved-direction expansion and verify interchangeable 90-second sequences."""
from pathlib import Path
from copy import deepcopy
from collections import Counter
import json

P=Path(__file__).resolve().parents[1]
D=json.loads((P/'analysis/inspiration_v21.json').read_text(encoding='utf-8'))
B=json.loads((P/'analysis/montage_v2.json').read_text(encoding='utf-8'))
FPS=25
def n(x):return f'{x:g}'
def tc(x):
 f=round(x*FPS);return f'{f//1500:02d}:{f//25%60:02d}:{f%25:02d}'
def interval(ranges):return ' / '.join(n(a)+'至'+n(b)+'秒' for a,b in ranges)
def write(name,parts):
 (P/name).write_text('\n'.join(x.rstrip() for x in parts)+'\n',encoding='utf-8')

assert D['phases'][0]['a']==0 and D['phases'][-1]['b']==90
assert all(a['b']==b['a'] for a,b in zip(D['phases'],D['phases'][1:]))
base_by_id={s['id']:s for s in B['shots']}
chain_by_id={g['id']:g for g in D['chains']}

for g in D['chains']:
 slots=g['range'];pos=slots[0][0];slot=0
 expected={s['id'] for s in B['shots'] if any(s['start']>=a and s['end']<=b for a,b in slots)}
 assert expected==set(g['replaces']),g['id']
 assert abs(sum(s['duration'] for s in g['shots'])-sum(b-a for a,b in slots))<1e-7
 for s in g['shots']:
  if abs(pos-slots[slot][1])<1e-7:
   slot+=1;pos=slots[slot][0]
  s['start']=round(pos,3);s['end']=round(pos+s['duration'],3)
  assert s['end']<=slots[slot][1]+1e-7
  assert all(abs(x*FPS-round(x*FPS))<1e-7 for x in [s['start'],s['end']])
  s['timecode_in']=tc(s['start']);s['timecode_out']=tc(s['end']);s['group']=g['id']
  pos=s['end']
 assert abs(pos-slots[-1][1])<1e-7

def assemble(gids):
 removed=[];extra=[]
 for gid in gids:
  g=chain_by_id[gid];removed+=g['replaces'];extra+=g['shots']
 assert len(set(removed))==len(removed),'Overlapping replacement choices'
 shots=deepcopy([s for s in B['shots'] if s['id'] not in removed])+deepcopy(extra)
 shots.sort(key=lambda s:s['start'])
 assert shots[0]['start']==0 and shots[-1]['end']==90
 assert all(a['end']==b['start'] for a,b in zip(shots,shots[1:]))
 assert sum(round(s['duration']*FPS) for s in shots)==2250
 return shots

for g in D['chains']:assemble([g['id']])
packages=[]
for p in D['packages']:
 timeline=assemble(p['chains']);packages.append(dict(**p,shot_segments=len(timeline),total_frames=2250,duration=90,timeline=timeline))
(P/'analysis/package_timelines_v21.json').write_text(json.dumps({'version':'v2.1','baseline_segments':35,'packages':packages},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(P/'analysis/inspiration_v21_resolved.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

parts=['''# 《一瞥》V2.1｜情绪与剪辑导演谱

用户已认可V2方向，本轮沿同一主线扩展。**主时间线仍是90秒；现有35个镜头段作为基线，新增关联分镜作为可替换选项。**音频继续暂缓。

一次没有完成的转头，展开布料、山河、身体与时间。影片不是靠人物表演越来越强烈来推进：前半让观看变得轻盈，中间留下一个时间缺口，后半让身体与环境重新连上，最后完成开头的一瞥。

## 两个高点承担不同的感受

27.4至35.2秒是第一次兴奋：身体连续、地点跳跃，观众惊讶时间竟然可以被折起来。56.8至63.2秒达到剪接密度的峰值；63.2至74秒则通过更长的画面、辽阔空间与自然人物反应，达到情绪上的开放。

因此，最短镜头与情绪最高点不必重合。兴奋之后要有重量，空落之后要有人，高潮之后要有真实时间。

## 90秒情绪总谱

下表是创作意图，不是对所有观众的心理反应作保证。镜长不能单独决定情绪；画面信息、动作结果和前后关系同样重要。

| 时间 | 希望的感受 | 画面节奏 | 剪辑手法 |
| --- | --- | --- | --- |''']
for p in D['phases']:parts.append(f"| {n(p['a'])}至{n(p['b'])}秒 | {p['title']} | {p['rhythm']} | {p['cut']} |")
parts.append('\n## 分段导演说明\n')
for p in D['phases']:
 parts.append(f"### {p['id']} · {n(p['a'])}至{n(p['b'])}秒 · {p['title']}\n\n**观看感受：**{p['feel']}\n\n**情绪推进：**{p['arc']}\n\n**画面节奏：**{p['rhythm']}\n\n**剪辑手法：**{p['cut']}\n\n**构图与身体：**{p['frame']} {p['act']}\n\n**容易偏离的地方：**{p['watch']}\n\n**调整方式：**{p['fix']}\n\n**对应镜头：**{p['anchor']}\n")
parts.append('## 情绪转弯发生在哪里\n')
for title,body,time in D['recipes']:parts.append(f'**{time}｜{title}。**{body}\n')
parts.append('''## 第一轮剪辑先保护这四处

1. 23.4至27.4秒：固定人物4秒，第一次主动停留。
2. 48.4至54.4秒：人物突然不在之后的6秒空景。可改变前后素材，先保住这段时间供判断。
3. 74至83秒：4秒完整走出与5秒空景，同一条连续画面。
4. 86至90秒：接回原始转头的后4秒，完成开头留住的动作。

这些是首轮判断节奏的支点，不是未来不能调整的禁令。若修改镜长，要同时检查观众能否读懂动作、90秒总长是否仍成立，以及下一段是否还有速度差。

## 怎样看镜头内部的节奏

同样四秒，一条画面可以经历“进入—看清—小变化—停留”，也可以什么都没发生。拍长镜时先决定观众在等待什么：等草抬起来、等脚落稳、等衣摆安静，或等一个人走出边缘。后期在这个过程完成之后稍留一点，余韵才有来处。

运动快也不等于必须快切。一条稳定远景里人快速经过，已经有足够动量；反过来，连续几个完全静止的细节短切，也能产生强烈节奏。不要把人物速度、相机速度、剪接速度同时推到最高。

## 色彩与光线怎样参与情绪

前半保留蓝灰环境与真实肤色的差别，让靠近身体的镜头更可触；后半可以让天空和地面在构图里占更大面积，人物更自然地进入光线。优先使用同一天真实光线的变化，不强制“冷色等于悲伤、暖色等于快乐”。同一场人物/空景关系必须保持曝光稳定，避免调色替剪辑解释情绪。

继续阅读：[关联分镜灵感库](11_V2.1_关联分镜灵感库.md)、[拍摄启发与组合](12_V2.1_拍摄启发与组合.md)、[参考画面](13_V2.1_参考画面.md)、[35镜情绪索引](14_V2.1_90秒逐镜情绪索引.md)。
''')
write('10_V2.1_情绪与剪辑导演谱.md',parts)

parts=['''# 《一瞥》V2.1｜关联分镜灵感库

**12组、36个新设计镜头段。**每组给出能直接替换的原版时间槽，单组或指定组合仍为90秒；它们不是要全部塞进同一支短片。E编号是灵感库镜号，V2编号是已认可的基线。E11的三个描述属于一条连续画面。

每组都从“这一镜怎样改变上一镜的意义”出发。可先选最想拍的一两组，带着同组的三个镜头一起采集。焦段仍按取景功能确定，机位与场景为候选，真实环境可替换。

## 快速选择

| 新组 | 联想 | 替换时间 | 感受 |
| --- | --- | --- | --- |''']
for g in D['chains']:parts.append(f"| {g['id']} | {g['name']} | {interval(g['range'])} | {g['tone']} |")
for g in D['chains']:
 parts.append(f"\n## {g['id']} · {g['name']}\n\n**情绪：**{g['tone']}\n\n**镜头之间发生什么：**{g['relation']}\n\n**剪辑手法：**{g['method']}\n\n**替换位置：**{interval(g['range'])}；替换 {' / '.join(g['replaces'])}。\n\n| 镜号 | 成片时间码（25fps） | 时长 | 景别 | 画面 | 拍法 |\n| --- | --- | ---: | --- | --- | --- |")
 for s in g['shots']:parts.append(f"| {s['id']} | {s['timecode_in']}至{s['timecode_out']} | {n(s['duration'])}秒 | {s['scale']} | {s['picture']} | {s['shoot']} |")
 parts.append(f"\n**一起带回来的配对：**{g['pair']}\n\n**怎样接回原版：**{g['bridge']}\n\n**现场替代：**{g['fallback']}\n\n**留给你的创作触发：**{g['prompt']}\n")
 if g['board']:parts.append(f"**生图参考：**[画面板{g['board'].upper()} {'上排' if g['row']==0 else '下排'}](assets/v21_board_{g['board']}.png)。动作与机位以此处文字为准。\n")
parts.append('''## 剪辑时怎样保留它的艺术性

匹配只是入口：相似的形状使观众注意到两镜的关系，回到人物才使关系属于这段旅途。每组最后问自己：观众对这个人、这个空间或这段时间的理解，有没有发生变化？如果没有，尝试改换第三镜，而不是继续增加转场效果。

一个连接也可以来自差异。近景忽然切远景，行动忽然切空景，或者一条短镜之后留完整动作，都会改变观看方式。先写清楚想让观众多知道什么、少知道什么，再决定技术。

[回情绪导演谱](10_V2.1_情绪与剪辑导演谱.md) · [三套90秒组合](12_V2.1_拍摄启发与组合.md)
''')
write('11_V2.1_关联分镜灵感库.md',parts)

parts=['''# 《一瞥》V2.1｜拍摄启发与组合

## 意象怎样在90秒里长出不同含义

| 意象 | 第一次 | 中间变化 | 最后一次 |
| --- | --- | --- | --- |''']
for m in D['motifs']:parts.append(f"| {m['name']} | {m['first']} | {m['middle']} | {m['last']} |")
for m in D['motifs']:parts.append(f"\n**{m['name']}的使用方法：**{m['rule']}")
parts.append('''
## 三套可以直接试剪的90秒组合

三套均沿用已认可的《一瞥》结构；只替换列出的组，其他镜头按V2原时间码保留。它们是供比较的创作选择，不是三个新故事。完整逐镜时间线保存在[可计算组合数据](analysis/package_timelines_v21.json)。
''')
for p in packages:
 parts.append(f"### 组合{p['id']} · {p['name']}\n\n{p['intent']}\n\n替换：{'＋'.join(p['chains'])}。总长90秒，2250帧，{p['shot_segments']}个镜头段。\n\n保留：{p['keep']}\n\n剪辑提醒：{p['caution']}\n\n| 替换组 | 时间槽 | 替换后段落 |\n| --- | --- | --- |")
 for gid in p['chains']:
  g=chain_by_id[gid];parts.append(f"| {gid} | {interval(g['range'])} | {' → '.join(s['id'] for s in g['shots'])} |")
parts.append('''
## 到现场以后，怎样继续发明镜头

先观察一个具体东西：不是“今天风景很美”，而是“一道影子先于身体进入画面”。接着找与它有关的第二个画面，再找第三个画面改变前两者的含义。给每个连接留一个可执行的机位和一个不依赖天气的版本。

| 看见的东西 | 第一镜可以是什么 | 第二镜可以接什么 | 第三镜怎样让它属于你 |
| --- | --- | --- | --- |
| 一条弯曲边界 | 手腕与袖口 | 湖岸或山肩 | 手放下，露出真正站在岸边的人 |
| 两道线围出的开口 | 窗框亮缝 | 山口天空 | 衣领与真实远山同框 |
| 重复的细密纹理 | 皮肤或织物 | 波纹、沙纹 | 回到手接触衣料的动作 |
| 一个先出现的影子 | 地面上的身体投影 | 脚进入 | 人站住，再切同机位空景 |
| 暂时遮住视野的东西 | 衣摆或近处包带 | 大片开放天空 | 它落回身体，尺度重新成立 |
| 一块相近颜色 | 外套局部 | 同机位自然地面的色块 | 人物近景再次带回这块颜色 |
| 一个去往画外的动作 | 手指从边缘退出 | 风或水接着向同侧运动 | 人完整走出后，运动仍继续 |
| 一次尚未完成的动作 | 转头的前半 | 旅途中的主观联想 | 同一素材的后半，完成真实时间 |

## 每组带回一张对照卡

**形状与方向。**留第一条参考帧，标主要线的位置、亮面侧和屏幕运动箭头。相机向左摇，静止地景在屏幕里向右走；不要混淆两种方向。

**身体与相位。**保存同一动作起、中、落三帧，记录机高、人物头脚位置和使用设备。两台设备的透视与视角难匹配时，一组尽量用同一台拍完。

**人物与空景。**固定机位长录：先空、人入画、站住、人走出、再空20秒。焦点与曝光保持，脚架不移动。这一条素材既能支持省略，也能支持连续时间。

**分屏与宽幅。**每一处都拍完整横屏原素材，人物两侧留足空间。三列是剪辑时的裁切，拍摄时不要只录一个窄竖条；回到单幅画面时才有原始宽幅可用。

## 一个可带到现场的拍摄记录模板

`组号 / 地点 / 设备与取景 / 镜头编号 / 机高 / 人物头脚位置 / 屏幕方向 / 动作起中落 / 光线与亮面 / 对应素材文件 / 是否已有替代`

动作前后各留5秒，环境纹理每条10至20秒，人物出画后的空镜至少20秒。先把同组关系拍齐，再追求更好光线；素材保留三条完整动作，比只录三个瞬间更容易剪。

## 自摄与帮拍怎样分工

三脚架完成车窗、跨地动作、人物/空景及结尾连续离开。自己拍时先用包或同行者短暂站位对焦，再确认人物走到预设区域；实际对焦方式按手头镜头和现场情况选择。有帮拍者时，把协助优先用于自然反应近景与短距离陪走。Air 2S承担可替换纯景，关键叙事都有地面拍法；Action用于低机位和脚步，不额外承诺机型功能。

## 收工后的十分钟回看

先把今天的一组素材按原意连起来看，再有意把其中两镜换序，观察意义怎样变。这里的顺序实验比补一个花哨转场更能发现新方向。只检验画面，本轮不恢复BGM工作。

| 看起来的问题 | 可能原因 | 可以先做的调整 |
| --- | --- | --- |''')
for a,b,c in D['fixes']:parts.append(f'| {a} | {b} | {c} |')
parts.append('\n[情绪导演谱](10_V2.1_情绪与剪辑导演谱.md) · [关联分镜灵感库](11_V2.1_关联分镜灵感库.md) · [参考画面](13_V2.1_参考画面.md)')
write('12_V2.1_拍摄启发与组合.md',parts)

board_info=[('a','开口与折线','E01：窗缝、山口、衣领','E02：折纸、沙脊、放下纸后的身体','取同方向开口或斜线即可，不需要同一个景点。折纸是可选小道具。'),('b','一个画幅里的不同时间','E06：三列分屏、中间画面回到宽幅、稳定人物','E08：空景、人物、再次空景','分屏素材拍完整横屏；下排生成背景近似一致，实拍要求一条固定机位长录。'),('c','从遮挡到开放','E09：衣料遮挡、大景展开、衣料回到身体','E10：肩背、自然反应、小人与辽阔','图像只给情绪和尺度方向，衣料运动与人物反应要现场完整拍下。'),('d','离开与回到观看','E11：进入、完整走出、连续空景','E12：转头前半、窗边手、同一转头后半','上排三格是一条连续画面；下排首尾必须来自同一真实素材。')]
parts=['''# 《一瞥》V2.1｜参考画面

本轮新增4张六格画面板，共24格，由内置imagegen生成并按需要校正。它们用来帮助判断构图、尺度和镜头并置，人物与地点均为概念占位；没有使用用户肖像。

生成图不能替代动作的真实时间。精确相位、机位位置与连续空景，以[关联分镜](11_V2.1_关联分镜灵感库.md)和现场参考帧为准。不同画面板的占位服装细节可能不同，实际出镜沿用自己的装束并保持同组连续。
''']
for key,title,top,btm,note in board_info:
 parts.append(f'## 画面板{key.upper()} · {title}\n\n![{title}](assets/v21_board_{key}.png)\n\n**上排：**{top}。\n\n**下排：**{btm}。\n\n**拍摄时：**{note}\n\n[原始提示词](prompts/v21_board_{key}.txt)。\n')
 if key=='b':parts.append('另做了[上排中间人物尺度校正](prompts/v21_board_b_refine.txt)，使分屏回到完整横屏的意图更清楚。\n')
parts.append('''采用文件的原始输出路径、尺寸与哈希记录在[图像清单](analysis/image_manifest_v21.json)。[上一轮12格参考](09_V2_参考画面.md)继续适用于布料、掌纹、水纹和三地一步。

图像文件从内置工具输出直接复制到项目，没有用程序改动像素。排版里的缩放与图像展示不代表现场必须精确复刻。
''')
write('13_V2.1_参考画面.md',parts)

parts=['''# 《一瞥》V2.1｜90秒逐镜情绪索引

这是已认可V2主线的35个镜头段，并为每镜补上所属情绪与可选新组。当前主时间线不自动采用全部灵感库内容。详细单人拍法仍见[原版逐镜稿](07_一瞥_V2_蒙太奇分镜.md)。

| 镜号 | 时间码（25fps） | 时长 | 景别 | 画面 | 情绪阶段 | 可选替换组 |
| --- | --- | ---: | --- | --- | --- | --- |''']
for s in B['shots']:
 phase=next(p for p in D['phases'] if s['start']>=p['a'] and s['end']<=p['b'])
 s['phase']=phase['id'];s['phase_title']=phase['title']
 opts=[g['id'] for g in D['chains'] if s['id'] in g['replaces']]
 s['options']=opts
 parts.append(f"| {s['id']} | {s['timecode_in']}至{s['timecode_out']} | {n(s['duration'])}秒 | {s['scale']} | {s['picture']} | {phase['id']} {phase['title']} | {' / '.join(opts) or '首轮保留'} |")
parts.append('''
V2-32与V2-33是同一条9秒连续画面的两段，不增加切口。成片镜头段计数与现场素材条数并不相同。所有替换组都按原时间槽校验，三套组合均为90秒；镜头段数量不同不代表片长不同。

[情绪与剪辑导演谱](10_V2.1_情绪与剪辑导演谱.md) · [关联分镜灵感库](11_V2.1_关联分镜灵感库.md)
''')
write('14_V2.1_90秒逐镜情绪索引.md',parts)
(P/'analysis/baseline_annotated_v21.json').write_text(json.dumps(B,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report={'version':'v2.1','baseline_seconds':90,'baseline_frames':2250,'baseline_segments':35,'emotion_phases':len(D['phases']),'phase_coverage_contiguous':True,'new_groups':len(D['chains']),'new_shot_segments':sum(len(g['shots']) for g in D['chains']),'each_group_fits_original_time_slots':True,'single_group_90_second_checks':12,'package_checks':[{'id':p['id'],'seconds':90,'frames':2250,'segments':p['shot_segments'],'overlaps':False,'gaps':False} for p in packages],'audio_scope':'paused; no audio files read or modified'}
(P/'analysis/validation_v21.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
