---
tracker:
  kind: linear
  provider:
    endpoint: http://127.0.0.1:38217/graphql
    api_key: dummy-local-test-only
    project_slug: probe
  active_states: [Todo, In Progress]
  terminal_states: [Done, Closed, Cancelled]
polling:
  interval_ms: 100
workspace:
  root: /tmp/symphony-final-reader.RBZ8lt/bundle with spaces/research/symphony-acceptance/runs/probe-20261007T201339.791981Z/failing_after_hook/workspaces
hooks:
  after_create: |
    printf 'workspace-created\n' > sentinel.txt
  after_run: |
    printf 'FAIL: injected hook check\n' > verification.txt
    exit 1
agent:
  max_concurrent_agents: 1
  max_turns: 1
codex:
  command: "python3 '/tmp/symphony-final-reader.RBZ8lt/bundle with spaces/research/symphony-acceptance/fake_agent.py'"
  read_timeout_ms: 5000
  turn_timeout_ms: 5000
server:
  host: 127.0.0.1
---
Complete {{ issue.identifier }}. Run the verification before Human Review.
