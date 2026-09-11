"""Validate delivery structure; --visual-review-complete records a separate human/agent image review."""
from pathlib import Path
from collections import Counter
from urllib.parse import unquote
import argparse
import hashlib
import json
import re
import pdfplumber
from pypdf import PdfReader

P=Path(__file__).resolve().parents[1]
ROOT=P.parents[1]
REPORT=P/'analysis/review_v2.json'
PDF=ROOT/'output/pdf/青甘旅拍_一瞥_V2_蒙太奇分镜.pdf'
args=argparse.ArgumentParser()
args.add_argument('--visual-review-complete',action='store_true')
opt=args.parse_args()
d=json.loads((P/'analysis/montage_v2.json').read_text(encoding='utf-8'))
shots=d['shots'];fps=d['fps']
assert len(shots)==35 and d['duration']==90 and fps==25
def tc_frames(tc):
 m,s,f=map(int,tc.split(':'))
 assert 0<=s<60 and 0<=f<fps
 return (60*m+s)*fps+f
end=0
for s in shots:
 assert s['start']==end and s['end']>s['start']
 assert tc_frames(s['timecode_in'])==round(s['start']*fps)
 assert tc_frames(s['timecode_out'])==round(s['end']*fps)
 assert round(s['duration']*fps)==round((s['end']-s['start'])*fps)
 for f in ['scale','location','picture','montage','execution','alternative']:assert s[f].strip()
 end=s['end']
assert end==90
ids=[s['id'] for s in shots]
assert len(set(ids))==len(ids)
assert Counter(x for g in d['groups'] for x in g['shots'])==Counter(ids)
assert d['stages'][0]['start']==0 and d['stages'][-1]['end']==90
assert all(a['end']==b['start'] for a,b in zip(d['stages'],d['stages'][1:]))
for g in d['groups']:
 assert all(next(s for s in shots if s['id']==sid)['group']==g['id'] for sid in g['shots'])

mds=[ROOT/'README.md',*P.glob('*.md')]
links=0
for f in mds:
 t=f.read_text(encoding='utf-8')
 for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',t):
  target=unquote(target.strip('<>').split('#')[0])
  if not target or re.match(r'^[A-Za-z]+://',target):continue
  dest=(f.parent/target).resolve()
  assert dest==REPORT or dest.exists(),f'{f.name}: missing {target}'
  links+=1
 assert not re.search(r'^\|[ :|\-]+\|\n\s*\n\|',t,re.M),f'{f.name}: broken table'
main=(P/'07_一瞥_V2_蒙太奇分镜.md').read_text(encoding='utf-8')
assert re.findall(r'^\| (V2-\d+) / G\d+ \|',main,re.M)==ids

layout=json.loads((P/'analysis/pdf_layout_v2.json').read_text(encoding='utf-8'))
assert all(x['bottom_y']>=x['limit'] for x in layout['checks'])
r=PdfReader(PDF)
assert len(r.pages)==17
text='\n'.join(p.extract_text() for p in r.pages)
assert all(sid in text for sid in ids)
assert all(sid in '\n'.join(p.extract_text() for p in r.pages[6:15]) for sid in ids)
assert len(r.pages[2].images)>=1 and len(r.pages[3].images)>=1
out_of_page=[]
with pdfplumber.open(PDF) as p:
 for i,page in enumerate(p.pages,1):
  for ch in page.chars:
   if ch['x0']<0 or ch['x1']>page.width+.1 or ch['top']<0 or ch['bottom']>page.height+.1:
    out_of_page.append({'page':i,'text':ch['text']})
assert not out_of_page,out_of_page
manifest=json.loads((P/'analysis/image_manifest_v2.json').read_text(encoding='utf-8'))
for asset in manifest['selected_assets']:
 assert hashlib.sha256((P/asset['asset']).read_bytes()).hexdigest()==asset['sha256']
 assert all((P/p).exists() for p in asset['prompts'])

report={'version':'v2','shot_count':35,'group_count':8,'duration_seconds':90,'total_frames':2250,'timeline_and_group_checks':'passed','markdown_local_links_checked':links,'markdown_tables':'passed','pdf_page_count':len(r.pages),'pdf_contains_all_shots':True,'pdf_text_inside_page':True,'layout_space_checks':len(layout['checks']),'selected_image_boards':len(manifest['selected_assets']),'image_hashes_and_prompts':'passed','pdf_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'visual_review':{'completed':opt.visual_review_complete,'method':'Poppler 110 dpi PNG review of all 17 pages, then reinspection of all changed pages after corrections' if opt.visual_review_complete else 'not recorded by this run','notes':'Visual review is separate from numerical checks; artistic acceptance belongs to the user.'},'audio_scope':'paused; validator does not read source audio or historical mix'}
REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
