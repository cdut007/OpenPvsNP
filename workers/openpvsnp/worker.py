import os, json, base64, uuid, requests
from datetime import datetime, timezone
UP=os.getenv('OPENPVSNP_UPSTREAM','cdut007/OpenPvsNP')
PUSH=os.getenv('OPENPVSNP_PUSH_REPO',UP)
T=os.environ['GITHUB_TOKEN']; K=os.environ['MODEL_API_KEY']
BASE=os.getenv('MODEL_BASE_URL','https://api.openai.com/v1').rstrip('/')
MODEL=os.getenv('MODEL','gpt-4.1'); W=os.getenv('WORKER_ID','agent-'+uuid.uuid4().hex[:8])
s=requests.Session(); s.headers.update({'Authorization':'Bearer '+T,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
def gh(method,path,**kw):
 r=s.request(method,'https://api.github.com'+path,timeout=90,**kw); r.raise_for_status(); return r.json() if r.content else None
def main():
 issues=gh('GET','/repos/'+UP+'/issues',params={'state':'open','per_page':100})
 issue=next((x for x in issues if 'pull_request' not in x and x['title'].startswith('[') and ']' in x['title']),None)
 if not issue: print('No open research tasks'); return
 tid=issue['title'].split(']',1)[0][1:]
 item=gh('GET','/repos/'+UP+'/contents/tasks/queue/'+tid+'.json')
 task=json.loads(base64.b64decode(item['content']).decode())
 gh('POST','/repos/'+UP+'/issues/'+str(issue['number'])+'/comments',json={'body':'Worker '+W+' started a research run. Soft claim only; duplicate work may occur.'})
 sysmsg='Research this task rigorously. Audit worst-case complexity. Never claim P=NP without a complete proof. Return only JSON fields result_type, claim_status, summary, assumptions, argument, evidence, limitations, next_steps. Never invent citations.'
 response=requests.post(BASE+'/chat/completions',headers={'Authorization':'Bearer '+K},json={'model':MODEL,'temperature':0.2,'messages':[{'role':'system','content':sysmsg},{'role':'user','content':json.dumps(task)}]},timeout=900)
 response.raise_for_status(); raw=response.json()['choices'][0]['message']['content'].strip()
 if raw.startswith('```'): raw=raw.split('\n',1)[-1].rsplit('```',1)[0]
 result=json.loads(raw)
 required={'result_type','claim_status','summary','assumptions','argument','evidence','limitations','next_steps'}
 if not required.issubset(result): raise ValueError('Model response misses required fields')
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'); slug=''.join(c if c.isalnum() or c in '-_' else '-' for c in W)[:24]
 doc={'task_id':tid,'worker_id':W,'model':MODEL,'created_at':datetime.now(timezone.utc).isoformat(),**result}
 path='submissions/'+tid+'/'+slug+'-'+stamp+'.json'
 base=gh('GET','/repos/'+PUSH+'/git/ref/heads/main')['object']['sha']
 tree0=gh('GET','/repos/'+PUSH+'/git/commits/'+base)['tree']['sha']
 blob=gh('POST','/repos/'+PUSH+'/git/blobs',json={'content':json.dumps(doc,indent=2,ensure_ascii=False)+'\n','encoding':'utf-8'})
 tree=gh('POST','/repos/'+PUSH+'/git/trees',json={'base_tree':tree0,'tree':[{'path':path,'mode':'100644','type':'blob','sha':blob['sha']}]})
 commit=gh('POST','/repos/'+PUSH+'/git/commits',json={'message':'Research submission '+tid+' by '+W,'tree':tree['sha'],'parents':[base]})
 branch='agent/'+tid.lower()+'/'+slug.lower()+'-'+stamp.lower()
 gh('POST','/repos/'+PUSH+'/git/refs',json={'ref':'refs/heads/'+branch,'sha':commit['sha']})
 owner=PUSH.split('/')[0]; head=branch if PUSH==UP else owner+':'+branch
 pr=gh('POST','/repos/'+UP+'/pulls',json={'title':'['+tid+'] Research by '+W,'head':head,'base':'main','body':'Unverified AI research artifact. Human review and independent verification required.'})
 gh('POST','/repos/'+UP+'/issues/'+str(issue['number'])+'/comments',json={'body':'Submitted PR: '+pr['html_url']})
 print(pr['html_url'])
if __name__=='__main__': main()
