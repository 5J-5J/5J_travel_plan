"""Check delivery integrity. Visual review is an explicit separate confirmation."""
from pathlib import Path
from urllib.parse import unquote
import argparse,hashlib,json,re
import pdfplumber
from pypdf import PdfReader

P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
OUT=ROOT/'output/pdf/青甘旅拍_一瞥_V2.1_情绪与关联分镜.pdf'
REPORT=P/'analysis/review_v21.json'
parser=argparse.ArgumentParser();parser.add_argument('--visual-review-complete',action='store_true');args=parser.parse_args()
D=json.loads((P/'analysis/inspiration_v21_resolved.json').read_text(encoding='utf-8'))
V=json.loads((P/'analysis/validation_v21.json').read_text(encoding='utf-8'))
assert V['emotion_phases']==11 and V['new_groups']==12 and V['new_shot_segments']==36
packages=json.loads((P/'analysis/package_timelines_v21.json').read_text(encoding='utf-8'))['packages']
def frames(tc):
 m,s,f=map(int,tc.split(':'));assert s<60 and f<25;return (m*60+s)*25+f
for p in packages:
 seq=p['timeline'];assert seq[0]['start']==0 and seq[-1]['end']==90
 assert all(a['end']==b['start'] for a,b in zip(seq,seq[1:]))
 assert sum(round(s['duration']*25) for s in seq)==2250
 for s in seq:
  assert frames(s['timecode_in'])==round(s['start']*25)
  assert frames(s['timecode_out'])==round(s['end']*25)
 # These initial holds remain in every supplied comparison package.
 assert any(s['start']==23.4 and s['end']==27.4 for s in seq)
 assert any(s['start']==48.4 and s['end']==54.4 for s in seq)
 assert any(s['start']==78 and s['end']==83 for s in seq)
 assert any(s['start']==86 and s['end']==90 for s in seq)

links=0
for f in [ROOT/'README.md',*P.glob('*.md')]:
 text=f.read_text(encoding='utf-8')
 for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text):
  target=unquote(target.strip('<>').split('#')[0])
  if not target or re.match(r'^[A-Za-z]+://',target):continue
  dest=(f.parent/target).resolve();assert dest==REPORT or dest.exists(),(f.name,target)
  links+=1
 assert not re.search(r'^\|[ :|\-]+\|\n\s*\n\|',text,re.M),f.name

r=PdfReader(OUT);assert len(r.pages)==34
alltext='\n'.join(p.extract_text() for p in r.pages)
assert all(p['id'] in alltext for p in D['phases'])
assert all(s['id'] in alltext for g in D['chains'] for s in g['shots'])
base='\n'.join(p.extract_text() for p in r.pages[28:33])
assert all(f'V2-{i:02d}' in base for i in range(1,36))
assert all(len(r.pages[i].images)>=1 for i in range(20,24))
layout=json.loads((P/'analysis/pdf_layout_v21.json').read_text(encoding='utf-8'))
assert all(v['bottom']>=v['limit'] for v in layout['layout_checks'])
bad=[]
with pdfplumber.open(OUT) as pdf:
 for i,page in enumerate(pdf.pages,1):
  for ch in page.chars:
   if ch['x0']<0 or ch['x1']>page.width+.1 or ch['top']<0 or ch['bottom']>page.height+.1:bad.append((i,ch['text']))
assert not bad,bad
image_manifest=json.loads((P/'analysis/image_manifest_v21.json').read_text(encoding='utf-8'))
assert len(image_manifest['selected_boards'])==4
for a in image_manifest['selected_boards']:
 assert hashlib.sha256((P/a['asset']).read_bytes()).hexdigest()==a['sha256']
 assert all((P/p).exists() for p in a['prompts'])
assert len(list((P/'tmp/pdfs/v21').glob('page-*.png')))==34
annotations=sum(len(p.get('/Annots',[])) for p in r.pages)
assert annotations==8
result={'version':'v2.1','pdf_pages':34,'all_11_emotion_phases_present':True,'all_36_new_shot_segments_present':True,'all_35_baseline_segments_present':True,'all_three_packages_90_seconds_2250_frames':True,'protected_holds_retained':True,'markdown_links_checked':links,'no_broken_markdown_tables':True,'pdf_text_within_page':True,'layout_space_checks':len(layout['layout_checks']),'reference_board_links':annotations,'image_boards':4,'image_hashes_and_prompts_verified':True,'pdf_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'visual_review':{'complete':args.visual_review_complete,'method':'All 34 Poppler 110dpi pages reviewed via contact sheets; changed pages and dense text checked again at page size.' if args.visual_review_complete else 'not confirmed','scope':'layout and legibility; emotional effect remains an artistic judgement'},'audio_scope':'paused; no audio read by this validator'}
REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
