#!/usr/bin/env python3
"""Deterministic protocol double, not an LLM and not a quality benchmark."""
import json, os, pathlib, sys, urllib.request
trace = pathlib.Path(os.environ['PROBE_AGENT_TRACE'])
case = os.environ['PROBE_CASE']
def emit(x):
    with trace.open('a') as f: f.write(json.dumps({'direction':'out','message':x})+'\n')
    print(json.dumps(x), flush=True)
for line in sys.stdin:
    msg=json.loads(line)
    with trace.open('a') as f:f.write(json.dumps({'direction':'in','message':msg,'cwd':os.getcwd()})+'\n')
    method=msg.get('method'); ident=msg.get('id')
    if method=='initialize':emit({'id':ident,'result':{}})
    elif method=='thread/start':emit({'id':ident,'result':{'thread':{'id':'probe-thread'}}})
    elif method=='turn/start':
        emit({'id':ident,'result':{'turn':{'id':'probe-turn'}}})
        if case!='active':
            request=urllib.request.Request(os.environ['PROBE_TRACKER_URL']+'/state',data=b'{"state":"Human Review"}',headers={'Content-Type':'application/json'})
            urllib.request.urlopen(request,timeout=5).read()
        emit({'method':'turn/completed','params':{'threadId':'probe-thread','turn':{'id':'probe-turn','status':'completed'}}})
