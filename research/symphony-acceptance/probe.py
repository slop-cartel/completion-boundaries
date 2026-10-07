#!/usr/bin/env python3
"""Run a real, pinned Symphony binary with local tracker/agent protocol doubles.
Usage: python3 probe.py --binary PATH [--run-id ID]
All listeners bind loopback. No model, tracker or GitHub credentials are used.
"""
import argparse, datetime, hashlib, http.server, json, os, pathlib, signal, shlex, socket, subprocess, threading, time, urllib.request
ROOT=pathlib.Path(__file__).resolve().parent

def free_port():
    with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]

def run_case(binary, run_root, case):
    folder=run_root/case;folder.mkdir()
    state={'name':'Todo'}
    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))))
            with (folder/'tracker.jsonl').open('a') as f:f.write(json.dumps({'at':time.time(),'path':self.path,'request':body,'state':state['name']})+'\n')
            if self.path=='/state':state['name']=body['state'];payload={'ok':True}
            else:
                variables=body.get('variables',{})
                states=variables.get('stateNames')
                included=states is None or state['name'] in states
                issue={'id':'probe-1','identifier':'PROBE-1','title':'Require verification before handoff','description':'Do not hand off before pytest passes.','priority':1,'state':{'name':state['name']},'url':'https://example.invalid/PROBE-1','labels':{'nodes':[]},'inverseRelations':{'nodes':[]},'createdAt':'2026-10-01T00:00:00Z','updatedAt':'2026-10-01T00:00:00Z'}
                payload={'data':{'issues':{'nodes':[issue] if included else [],'pageInfo':{'hasNextPage':False,'endCursor':None}}}}
            data=json.dumps(payload).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    tracker=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=tracker.serve_forever,daemon=True);thread.start()
    port=free_port();tracker_url=f'http://127.0.0.1:{tracker.server_port}'
    hook='''  after_create: |
    printf 'workspace-created\\n' > sentinel.txt
'''
    if case in ['failing_after_hook','failing_before_hook']:hook+='''  HOOK_NAME: |
    printf 'FAIL: injected hook check\\n' > verification.txt
    exit 1
'''
    hook=hook.replace('HOOK_NAME', 'before_run' if case=='failing_before_hook' else 'after_run')
    agent_command=json.dumps(shlex.join(['python3',str(ROOT/'fake_agent.py')]))
    workflow=f'''---
tracker:
  kind: linear
  provider:
    endpoint: {tracker_url}/graphql
    api_key: dummy-local-test-only
    project_slug: probe
  active_states: [Todo, In Progress]
  terminal_states: [Done, Closed, Cancelled]
polling:
  interval_ms: 100
workspace:
  root: {folder}/workspaces
hooks:
{hook}agent:
  max_concurrent_agents: 1
  max_turns: 1
codex:
  command: {agent_command}
  read_timeout_ms: 5000
  turn_timeout_ms: 5000
server:
  host: 127.0.0.1
---
Complete {{{{ issue.identifier }}}}. Run the verification before Human Review.
'''
    (folder/'WORKFLOW.md').write_text(workflow)
    env=dict(os.environ,PROBE_CASE=case,PROBE_AGENT_TRACE=str(folder/'agent.jsonl'),PROBE_TRACKER_URL=tracker_url,ERL_FLAGS='+S 2:2')
    start=time.monotonic(); log=(folder/'stdout.log').open('w')
    proc=subprocess.Popen([str(binary),'--i-understand-that-this-will-be-running-without-the-usual-guardrails','--logs-root',str(folder/'log'),'--port',str(port),str(folder/'WORKFLOW.md')],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    snapshots=[];turns=0;settled=0
    def runtime_log():
        return '\n'.join(f.read_text(errors='replace') for f in (folder/'log').rglob('symphony.log.*') if f.name.rsplit('.',1)[-1].isdigit())
    try:
        deadline=time.monotonic()+18
        while time.monotonic()<deadline:
            if proc.poll() is not None:raise RuntimeError(f'Symphony exited {proc.returncode}; inspect {folder}/stdout.log')
            fresh=False
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/v1/state',timeout=1) as response:snapshots.append(json.load(response));fresh=True
            except (OSError,ValueError):pass
            trace=folder/'agent.jsonl'
            if trace.exists():turns=sum(json.loads(s).get('message',{}).get('method')=='turn/start' and json.loads(s)['direction']=='in' for s in trace.read_text().splitlines())
            observed_log=runtime_log()
            ready=False
            if fresh and snapshots:
                if case=='failing_before_hook':ready=snapshots[-1]['counts']['retrying']>=1 and 'Workspace hook failed hook=before_run' in observed_log
                elif case=='active':ready=turns>=2
                else:ready=turns>=1 and 'Issue left active states, removing claim' in observed_log and all(snapshots[-1]['counts'][k]==0 for k in ['running','retrying'])
            settled=settled+1 if ready else 0
            if settled>=2:break
            time.sleep(.15)
        else:raise AssertionError('case did not reach observable stop condition')
        elapsed=time.monotonic()-start
        workspace=folder/'workspaces'/'PROBE-1'
        result={'case':case,'tracker_state':state['name'],'turns_started':turns,'elapsed_s':round(elapsed,3),'final_counts':snapshots[-1]['counts'],'workspace_retained':workspace.is_dir(),'sentinel':(workspace/'sentinel.txt').read_text() if (workspace/'sentinel.txt').exists() else None,'verification':(workspace/'verification.txt').read_text() if (workspace/'verification.txt').exists() else None,'model_calls':0,'quality_benchmark':False}
        assert workspace.is_dir(), 'workspace retention is part of the probe contract'
        if case=='failing_before_hook':assert turns==0 and state['name']=='Todo' and snapshots[-1]['counts']['retrying']>=1
        elif case=='active':assert turns>=2 and state['name']=='Todo'
        else:assert state['name']=='Human Review' and snapshots[-1]['counts']['running']==snapshots[-1]['counts']['retrying']==0
        if case in ['failing_after_hook','failing_before_hook']:
            assert 'FAIL' in result['verification']
            name='after_run' if case=='failing_after_hook' else 'before_run'
            assert any(f'Workspace hook failed hook={name}' in line and 'status=1' in line for line in runtime_log().splitlines()), 'hook exit status must be independently logged'
        if case=='failing_after_hook':
            assert 'Agent task completed' in runtime_log() and 'Issue left active states, removing claim' in runtime_log()
        (folder/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result),flush=True)
        return result
    finally:
        (folder/'snapshots.json').write_text(json.dumps(snapshots,indent=2)+'\n')
        if proc.poll() is None:
            os.killpg(proc.pid,signal.SIGTERM)
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
        log.close();tracker.shutdown();tracker.server_close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--binary',type=pathlib.Path,required=True);parser.add_argument('--run-id',default=datetime.datetime.now(datetime.timezone.utc).strftime('probe-%Y%m%dT%H%M%S.%fZ'));args=parser.parse_args()
    binary=args.binary.resolve();root=ROOT/'runs'/args.run_id;root.mkdir(parents=True)
    meta={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'binary_path':str(binary),'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'case_results':[]}
    try:
        for case in ['active','handoff','failing_after_hook','failing_before_hook']:meta['case_results'].append(run_case(binary,root,case))
    finally:(root/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
