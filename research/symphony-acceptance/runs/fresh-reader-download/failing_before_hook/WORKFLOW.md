---
tracker:
  kind: linear
  provider:
    endpoint: http://127.0.0.1:36849/graphql
    api_key: dummy-local-test-only
    project_slug: probe
  active_states: [Todo, In Progress]
  terminal_states: [Done, Closed, Cancelled]
polling:
  interval_ms: 100
workspace:
  root: /tmp/symphony-fresh-reader.KEldLq/symphony-acceptance/runs/fresh-check/failing_before_hook/workspaces
hooks:
  after_create: |
    printf 'workspace-created\n' > sentinel.txt
  before_run: |
    printf 'FAIL: injected hook check\n' > verification.txt
    exit 1
agent:
  max_concurrent_agents: 1
  max_turns: 1
codex:
  command: python3 /tmp/symphony-fresh-reader.KEldLq/symphony-acceptance/fake_agent.py
  read_timeout_ms: 5000
  turn_timeout_ms: 5000
server:
  host: 127.0.0.1
---
Complete {{ issue.identifier }}. Run the verification before Human Review.
