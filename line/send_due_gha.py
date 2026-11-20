"""GitHub Actions 用。今の send_due.py と同じ選び方: JST 正午前=今日、正午以降=明日。
late があれば late だけ、無ければ early。同じ文は sent.jsonl のハッシュで二度送らない。1回に最大1通。"""
import os, sys, json, hashlib, uuid, datetime, urllib.request, urllib.error
L = os.path.dirname(os.path.abspath(__file__)); LOG = f'{L}/sent.jsonl'
now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)
day = (now if now.hour < 12 else now + datetime.timedelta(days=1)).strftime('%Y%m%d')
cand = [f'{L}/msg_{day}_late.txt', f'{L}/msg_{day}_early.txt']
cand = [f for f in cand if os.path.exists(f)][:1]
sent = set()
if os.path.exists(LOG):
    for l in open(LOG, encoding='utf-8'):
        try:
            j = json.loads(l)
            if j.get('status') == 200: sent.add(j.get('hash'))
        except Exception: pass
print('JST', now.strftime('%Y-%m-%d %H:%M'), 'day', day, 'files', [os.path.basename(f) for f in cand])
tok = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')
rc = 0
for p in cand:
    msg = open(p, encoding='utf-8').read().strip()
    h = hashlib.sha256(msg.encode()).hexdigest()[:16]
    if h in sent: print('already sent', os.path.basename(p)); continue
    if not tok: print('no token'); sys.exit(1)
    req = urllib.request.Request('https://api.line.me/v2/bot/message/broadcast',
        data=json.dumps({'messages': [{'type': 'text', 'text': msg}]}).encode(),
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tok, 'X-Line-Retry-Key': str(uuid.uuid4())}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as r: st, txt = r.status, r.read().decode()[:300]
    except urllib.error.HTTPError as e: st, txt = e.code, e.read().decode()[:300]
    except Exception as e: st, txt = -1, repr(e)[:300]
    open(LOG, 'a', encoding='utf-8').write(json.dumps({'at': datetime.datetime.utcnow().isoformat() + 'Z', 'file': os.path.basename(p), 'hash': h, 'status': st, 'resp': txt}, ensure_ascii=False) + '\n')
    print(os.path.basename(p), 'status', st); rc |= (st != 200)
sys.exit(rc)
