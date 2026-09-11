"""Build the authored 90 s shot list and a measurable music edit for review."""
from pathlib import Path
import json
import sys
import hashlib

P = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(P / "tmp" / "audio_packages"))
import numpy as np
import soundfile as sf

FPS = 25
music = [
 {"id":"M01","timeline_in":0.0,"timeline_out":64.0,"source_in":16.0,"source_out":80.0,"fade_in":0.16,"fade_out":0.08,"purpose":"从准备进入追赶，再保留原曲自身的能量回落"},
 {"id":"M02","timeline_in":64.0,"timeline_out":80.0,"source_in":160.0,"source_out":176.0,"fade_in":0.08,"fade_out":0.12,"purpose":"低处重新蓄力，约成片66秒展开放松的大景"},
 {"id":"M03","timeline_in":80.0,"timeline_out":90.0,"source_in":202.4,"source_out":212.4,"fade_in":0.12,"fade_out":0.8,"purpose":"固定长镜头中的余韵；拼接乐句待耳审"},
]

# ID, in, out, scale/location, visible action, execution, sound, priority/alternative
raw = [
 ("S001",0,2,"特写｜青海湖岸","手停在相机旁；后期简洁叠入一次『10s』，同时看见远处预留的人物位置。","Action 5 Pro拍ZR与手，保持可对焦距离后裁切；由摄影者机位补手部。","第一声自拍提示音，短而干；音乐由原曲16秒进入。","必拍；不伪造ZR真实菜单。参考图1。"),
 ("S002",2,4,"中景｜同一湖岸","你在三脚架后校水平，把远处一个点当成目标，起身离开。","Action侧后固定；ZR在画内当道具，也在录制备用角度。","旋钮轻响、衣料摩擦。","必拍；不要求额外摄影者。"),
 ("S003",4,6.4,"远景｜同一湖岸","你从画面左边急着跑入，位置偏左，地平线保持稳定。","ZR三脚架；先对标记点预对焦，再录长一条挑动作。","脚步渐近，倒计时继续。","必拍；岸上可行走地面。参考图2。"),
 ("S004",6.4,8,"近景｜湖岸","侧脸刚转向镜头，又低头找脚下站位。表情只需认真。","ZR固定，拍完大景后另录表情；可请同行者轻微横移。","保留一次短促吸气。","可缩；单人用固定半身。"),
 ("S005",8,10,"特写｜湖岸","手急着拉直外套下摆，身体尚未站稳。","ZR近取手部，固定机位；焦段以现有镜头为准。","9秒附近最后一次提示，10秒轻快门声。","必拍；为后面松手建立对照。"),
 ("S006",10,12,"全景→定格｜湖岸","身体还在调整姿势时定格；边缘裁掉一小部分手臂，留下刻意过正的中心空位。","由S003同机位素材截帧，停留约0.7秒再回到活动影像。","快门后留短空隙；不用白屏闪光轰炸。","必拍；观众读到『还没准备好』。"),
 ("S007",12,16,"中近景｜湖岸","你回看屏幕，轻轻抿嘴，折起三脚架。把不满意收进下一次尝试。","ZR拍人，Action拍屏幕外侧；画内不必展示可读照片。","合脚架声提前接下一镜的车内低声。","必拍；情绪克制，不演大失落。"),
 ("S008",16,18.4,"中景｜转场途中","车窗里叠着你的淡淡倒影，窗外风景从湖蓝变成浅白。","Action由乘员侧固定；车辆运动镜头另拍，演员不兼任驾驶动作。","车内低频衔接音乐能量上升。","可选；停着的车窗反射也成立。"),
 ("S009",18.4,20.4,"特写｜茶卡","相同的手，再拧紧一次脚架旋钮。动作更快。","ZR近拍旋钮或Action中近景裁切；记录一致的手向。","第二轮倒计时从18秒声先行；旋钮声踩画面动作。","必拍；和S001/S005形成重复。"),
 ("S010",20.4,23.2,"全景｜茶卡允许停留的步道/平台","你跨进预留位置；风拉起衣角，刚整理好的姿势又变了。","ZR三脚架；广角留大量白色与天空，不踩未开放盐壳。","一阵清楚的衣料拍打声。","必拍；镜面不成立时改浅白背景与步道纵深。"),
 ("S011",23.2,25.6,"近景｜茶卡或大柴旦","你转头追着相机方向看，眼神专注，肩膀有点紧。","ZR固定或由帮拍者短弧横移；动作方向与下一场一致。","倒计时持续，不叠加长呼啸音效。","可选；单人可取侧背。"),
 ("S012",25.6,28,"大远景｜大柴旦候选点","淡色盐地切出一块青绿色，画面突然很大；人物可以不出现。","Air 2S只做稳定缓升/俯视，地点允许且条件合适才拍；不要求FPV。","环境声短暂远去，让空间拉开。","可选；地面较高观景点的静态远景替代。"),
 ("S013",28,30.4,"中景｜大柴旦","第二次快门后，你抬手看画面，又迅速把视线抬向下一个地方。","ZR三脚架，中景；肩头转动接下一镜。","28秒快门轻响；下一场沙地脚步先进入。","可缩；维持『再来一次』的行动。"),
 ("S014",30.4,33.2,"中景｜敦煌可进入的低缓沙地","新地点，同一套动作：支脚架、压住外套、看向自己选好的点。","Action侧面记录；三脚架稳置，不设置在陡坡。","支架轻碰与细沙摩擦，音乐推动动作。","必拍；沙地只是候选，非固定某座沙丘。"),
 ("S015",33.2,36,"近景｜低缓沙地","鞋踏进软沙，一步比预想的短；你停半拍，再继续。","Action低机位固定；无需奔跑下坡或故意摔倒。","只突出一次陷入沙面的脚步。","必拍；挫折来自节奏被打断。"),
 ("S016a",36,36.8,"全景｜青海湖","同一只脚刚迈出，身体向右前方跨步。","ZR固定机高约腰部；严格统一运动方向和人物画面高度。","第三轮提示音开始；一声贯穿三镜。","必拍匹配组；提前在湖岸补录。"),
 ("S016b",36.8,37.6,"全景｜茶卡","保持同一跨步位置，背景瞬间换成浅白。","重复S016a构图；剪在身体遮住背景最多的一帧附近。","音乐延续，不另加转场轰声。","必拍匹配组；没有平台则换普通浅色岸边。"),
 ("S016c",37.6,38.4,"全景｜敦煌低缓沙地","跨步落地，背景变成赭色沙地。","重复前两镜；步长自然，以裁切微调人物大小。","让最后一脚真实落地声可听见。","必拍匹配组；三个地点代表多次尝试的压缩。"),
 ("S017",38.4,41.2,"特写｜沙地","手又捏紧外套下摆，这一次抓得更用力，停了一瞬。","ZR固定拍手；构图对应S005。","提示音进入近景声场。","必拍；给S022的松手明确意义。"),
 ("S018",41.2,44,"大远景｜同一低缓沙地","你仍想走到画面的理想位置，却显得很小；终于停住。","ZR三脚架远景，稍长的取景距离压小人物；帮拍可缓慢后退。","脚步停，提示音还在继续。","必拍；一个镜头交代人和尺度的关系。"),
 ("S019",44,46,"特写｜相机侧面/手的记忆插镜","取景框边缘叠一次『1』，你还没转好身。不要连打多个数字。","Action拍相机侧背；数字为后期视觉语言，不模仿菜单。","最后一声提示；46秒快门。","可缩；无UI版本直接看你未完成的转身。"),
 ("S020",46,48,"全景→定格｜沙地","快门定住一个转到一半的背影；衣角斜着。完美姿势又错过了。","从同机位视频取一帧，停约0.6–0.8秒；保留真实风。","快门之后音乐沿原曲自然回落。","必拍；参考图3。"),
 ("S021",48,53,"中近景｜同一沙地","你在低缓处坐/蹲下，喘一口气，视线从相机移到远方。保持五秒。","ZR三脚架或帮拍者稳住机位；正常速度，不慢放呼吸。","原曲64–69秒能量降低；呼吸和风来到前景。","必拍；参考图4。不加失恋/创伤背景。"),
 ("S022",53,56,"特写｜同一位置","捏住衣角的手慢慢松开，衣料由风带动。","对应S005/S017的构图，固定拍完整动作。","现场衣料声接住音乐空隙。","必拍；情绪转变的可见动作。"),
 ("S023",56,60,"近景｜相机旁","你走回相机，开始录影；出现一个简洁红点/REC，手不再慌。","Action拍ZR操作；具体按键以实际机身为准，录影状态可后期抽象表达。","一声录制提示即可；自拍滴声从这里消失。","必拍；交代『让相机一直等』。"),
 ("S024",60,64,"全景｜沙地","你先站在脚架旁，看一眼风景，再慢慢走开。多留半秒不动。","Action侧后固定记录人与ZR；也可分开拍机位与人物。","这一段原曲处于低能量，留风，不塞旁白。","必拍；前面跑，这里走。"),
 ("S025",64,66,"近景｜沙地","同一只脚再次踩进沙里。这次不急着拔出来，重量缓慢落稳。","Action低位；与S015同位置/方向，取自然动作。","切入原曲160秒，先保留低处再抬升。","必拍；转折后第一个动作。"),
 ("S026",66,70,"大远景｜敦煌候选开放场景","地貌展开，你静静处在画面里，终于无需修正站姿。","首选ZR高一点的地面机位；有帮拍者时可做缓退。航拍替代只拍环境。","原曲约162秒后的能量抬升；此镜不碎切。","必拍的大景功能；航拍可选。参考图5。"),
 ("S027",70,73.2,"中近景｜沙地","风吹来，你下意识偏头，露出很轻的笑；把自然反应留住。","帮拍者用稳定器短跟；单人以ZR固定机位走入近景。","让一声衣料/轻笑穿过音乐，若没录到就用风。","必拍；不要求夸张张臂。"),
 ("S028",73.2,76.4,"远景｜张掖观景区域","色层顺着一个方向延伸；同向轻摇，接上人的转头。","ZR地面观景平台拍，短摇或固定后期小幅裁切。","音乐持续；不添加旅游介绍字幕。","可选；无丹霞条件则换沿途山脉层次。"),
 ("S029",76.4,79,"全景｜祁连候选开放步道","你拎着相机慢慢走过秋草边缘，停一下，把画面留给眼前。","ZR三脚架或稳定器帮拍；走可通行路径。","脚步放缓，风声提前进入最后一镜。","可选；衣服仍保持同一视觉连续性。"),
 ("S030",79,90,"大远景｜祁连同一开放位置","完整11秒不切：先空景约2秒，你慢慢走入，站定看远山，最后仍有风在动。89秒小字『第十一秒』出现。","ZR三脚架，机位与曝光固定；预留入画路线，人物偏离正中心也成立。","79–80秒沿M02；80秒切尾段M03。没有自拍快门，风声贯穿。","必拍；参考图6。山体/草地不合适时用沙地完成同结构。"),
]

def tc(s):
    f=round(s*FPS)
    return f"{f//1500:02d}:{f//25%60:02d}:{f%25:02d}"

shots=[]
for rid,a,b,scale,action,execution,sound,priority in raw:
    assert abs(round(a*FPS)-a*FPS)<1e-6 and abs(round(b*FPS)-b*FPS)<1e-6, rid
    segments=[]
    for m in music:
        left=max(a,m['timeline_in']); right=min(b,m['timeline_out'])
        if right>left:
            si=m['source_in']+left-m['timeline_in']; so=si+right-left
            segments.append({"music_id":m['id'],"source_in":round(si,4),"source_out":round(so,4)})
    shots.append(dict(id=rid,timeline_in=a,timeline_out=b,duration=round(b-a,3),timecode_in=tc(a),timecode_out=tc(b),scale_location=scale,action=action,execution=execution,sound=sound,priority_alternative=priority,music=segments))
assert shots[0]['timeline_in']==0 and shots[-1]['timeline_out']==90
assert all(a['timeline_out']==b['timeline_in'] for a,b in zip(shots,shots[1:]))
assert sum(round(s['duration']*FPS) for s in shots)==2250
assert shots[-1]['duration']==11

plan={"version":"v1","working_title":"第十一秒","status":"creative proposal; music joins need aural review","fps":FPS,"duration":90,"aspect_ratio":"16:9","source":"bgm/dc39D5yN-Places-Portair.mp3","music":music,"shots":shots}
(P/'analysis'/'film_v1.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

intro='''# 《第十一秒》｜90 秒青甘旅拍分镜 v1

**创作提案 · 2026-09-11**

主角：你。旅行：9/26–10/5，青甘顺时针。器材：ZR / Air 2S / Action 5 Pro / 三脚架 / 稳定器。

成片：90秒，横屏；工作规格16:9、25fps。无必需旁白或对白，简单行动表演。故事是为这次拍摄设计的虚构框架。

## 故事简介

你想带回一张自己站在西北风景里的照片。设好十秒自拍，跑进青海湖的画面，整理衣角，快门却落在姿势尚未完成的瞬间。你把这个小小的不满意带到盐湖，再带到沙地；地方越来越辽阔，脚步越来越急。

沙地里，一次转到一半的背影又被定格。你停下来，松开紧抓衣角的手，第一次安静地看向远方。随后，你走回相机，按下录影，让它继续等。接下来的路开始有呼吸、有风，也有自然露出的笑。最后是一条完整的十一秒长镜头：风景先在那里，你从容走进去。

**一句话：一个想赶上十秒自拍的人，在十天的西北路上，给自己多留了一秒。**

片中不需要解释人生困境，也不需要恋人、旧信或失去某个人的背景。观众能直接看见的变化是：同一只手从捏紧到放开，同一步从急跑到缓落，同一个人从不断修正位置到安静站住。

## 情绪与音乐结构

| 成片 | 人物状态 | 画面节奏 | 音乐依据 / 声音主次 |
| --- | --- | --- | --- |
| 00–16s | 认真，带一点急 | 先看清目标，再第一次定格 | 原曲16–32s；提示音建立任务 |
| 16–48s | 兴奋逐渐变成用力 | 跨地点匹配，0.8秒短镜与2–3秒镜头交错 | 原曲32–64s的较高能量段；脚步与动作声点到即止 |
| 48–64s | 泄气、观察、作出小决定 | 5秒呼吸镜头，手松开，录影红点出现 | 原曲64–80s自然回落；风、呼吸来到前景 |
| 64–79s | 松弛后的释放 | 先慢一步，66秒展开4秒大景，再回到人 | 原曲160秒后重新抬升；大景不切得过碎 |
| 79–90s | 已经到场，仍有余韵 | 完整11秒固定长镜头 | 80秒切至原曲202.4–212.4s尾段；没有自拍快门 |

**音乐说明：**已实际解码并测量能量/瞬态；上述情绪是导演设计，不是把波形当作听感。原曲拼接已制成90秒结构小样，但人声断句、和声衔接及具体重拍尚未完成耳听复核。时间码是可执行的v1工作版，后续允许围绕转折点微调数帧。

## 看图

计划制作六格AI概念预演，按 S001 → S003 → S020 → S021 → S026 → S030 阅读。服装与匿名旅人仅作连续性建议，光线、地貌、可进入区域以现场为准。

**当前生图状态：内置服务连续两次网络失败，尚无参考图片文件。**完整提示词已保存为 [storyboard_v1.txt](prompts/storyboard_v1.txt)，逐格构图说明见 [参考与视觉设计](06_参考与视觉设计.md)。不以占位图冒充生成结果。

## 逐镜脚本

时间码为 **分:秒:帧（25fps）**；如 `00:06:10` 为6.4秒。入点包含、出点不包含。原曲对应列为解码后源时间（秒）。景别写在第四列；人物镜头默认正常速度，慢动作只留给无同步声音的风、衣角和环境。

| 镜号 | 成片入–出 | 时长 | 景别 / 场景 | 画面行动 | 器材 / 运镜 / 单人执行 | 声音 | 原曲对应 | 优先级 / 替代 |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- |
'''
rows=[]
for s in shots:
    links='；'.join(f"{m['music_id']} {m['source_in']:.2f}–{m['source_out']:.2f}s" for m in s['music'])
    rows.append(f"| {s['id']} | {s['timecode_in']}–{s['timecode_out']} | {s['duration']:g}s | {s['scale_location']} | {s['action']} | {s['execution']} | {s['sound']} | {links} | {s['priority_alternative']} |")
end='''

## 三个值得投入时间的设计

1. **同一步穿过三种地貌（S016a–c）。**三个地点都记录相同机高、人物画面高度、方向和起脚顺序。每条从静止开始，跨两步后再停，前后各多录5秒。它把多次赶赴压成一瞬，不需要复杂三维特效。
2. **三次捏衣角，最后一次松开（S005 / S017 / S022）。**拍手的尺寸和位置保持接近。表演越小，越容易让转折可信。
3. **最后十一秒（S030）。**提前录30秒完整素材，剪出连续11秒。让人慢慢进入风景，进入后留时间站住。不要在末尾再补航拍、片尾LOGO或一串地点名，否则这次等待会被打断。

## 视觉与剪辑约定

- 衣服建议同一件低饱和赭橙外套，形成人物识别点；若你已有别的衣服，选一件能同时区别于湖蓝、盐白、沙金的即可。
- 前半段多用框中框、偏中心空位、短动作；后半段减少前景阻挡，留出天空与人物周围的空间。色彩从冷蓝/浅白走向沙地暖色，再回到祁连克制的冷暖关系。
- ZR负责主要人物质感和最终固定镜头；Action负责拍你和相机、低机位脚步、车内过渡；Air 2S补充地貌尺度。镜头焦段尚未提供，先按广角/标准/较窄取景功能安排。
- 稳定器用于短距离陪走和轻微横移。没有帮拍者时，人物走过固定机位即可。每个关键剧情都可在不依赖航拍的情况下成立。
- 两个定格使用短暂画面停顿和干净快门声，不堆叠曝光闪白。跨地点转场靠动作和声音连接；避免连续旋转、每镜变速与无原因的穿越特效。
- 自拍状态、数字与REC是剪辑中的抽象提示；现场用长时间录影反复表演，无需让相机真的在10秒时停掉。三轮提示音代表三个独立的尝试，不构成一条贯穿全片的实时倒计时。

拍摄日安排见 [05_拍摄执行](05_拍摄执行.md)。音乐取段与试听入口见 [03_音乐分析](03_音乐分析.md)。所有可计算数据保存在 [film_v1.json](analysis/film_v1.json)。
'''
(P/'04_第十一秒_分镜v1.md').write_text(intro+'\n'.join(rows)+end,encoding='utf-8')

source=P.parents[1]/'bgm'/'dc39D5yN-Places-Portair.mp3'
x,sr=sf.read(source,always_2d=True,dtype='float32')
mix=np.zeros((90*sr,x.shape[1]),dtype='float32')
for m in music:
    a,b=round(m['source_in']*sr),round(m['source_out']*sr)
    assert 0<=a<b<=len(x)
    z=x[a:b].copy()
    assert len(z)==round((m['timeline_out']-m['timeline_in'])*sr)
    n=round(m['fade_in']*sr);z[:n]*=np.sin(np.linspace(0,np.pi/2,n))[:,None]
    n=round(m['fade_out']*sr);z[-n:]*=np.cos(np.linspace(0,np.pi/2,n))[:,None]
    start=round(m['timeline_in']*sr)
    mix[start:start+len(z)]+=z
mix*=10**(-2/20)
peak=float(np.abs(mix).max())
assert np.isfinite(mix).all() and peak<1
preview=P/'audio'; preview.mkdir(exist_ok=True)
sf.write(preview/'places_90s_structure_v1.mp3',mix,sr,format='MP3',subtype='MPEG_LAYER_III',bitrate_mode='CONSTANT',compression_level=0.0)
# Keep an exact sample-count PCM master locally; only the compact review MP3 is committed.
sf.write(P/'tmp'/'places_90s_structure_v1.wav',mix,sr,subtype='PCM_24')
decoded,dsr=sf.read(preview/'places_90s_structure_v1.mp3',always_2d=True,dtype='float32')
report={"shot_count":len(shots),"video_frames":2250,"timeline_fps":FPS,"duration_s":90,"last_shot_continuous_s":11,
        "continuous_shot_timeline":True,"source_intervals_within_audio":True,"raw_source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "pcm_duration_s":len(mix)/sr,"decoded_preview_duration_s":len(decoded)/dsr,"sample_rate_hz":sr,
        "pcm_sample_peak_dbfs":round(20*np.log10(peak),3),"decoded_mp3_sample_peak_dbfs":round(20*np.log10(max(float(np.abs(decoded).max()),1e-10)),3),
        "preview":"audio/places_90s_structure_v1.mp3","preview_includes":"Original user music edit only; no dialogue, no real-location ambience, no synthetic guide effects",
        "audio_processing":"No time stretch, no overlapping source clips; short per-clip edge fades; -2 dB gain.",
        "not_checked":["aural quality / vocals and phrase continuity","true peak","integrated LUFS","precise musical downbeat alignment"]}
assert abs(report['decoded_preview_duration_s']-90)<0.1
(P/'analysis'/'validation_v1.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
