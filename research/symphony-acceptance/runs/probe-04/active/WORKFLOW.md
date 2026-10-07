---
tracker:
  kind: linear
  provider:
    endpoint: http://127.0.0.1:35715/graphql
    api_key: dummy-local-test-only
    project_slug: probe
  active_states: [Todo, In Progress]
  terminal_states: [Done, Closed, Cancelled]
polling:
  interval_ms: 100
workspace:
  root: /srv/exo1007/slopcartel-live/company/runtime/.exocorp/runtime-host/runner-state/workspaces/workspace/company-9267343a762b0d1643c6e82a1458124ec46e0d3f4f7236e783b8b87f83e12277/workspace-91e7020030e812078ad10dea07c628d9e13555f4e2bda1a73e5e4d05fc7f6b57/research/symphony-acceptance/runs/probe-04/active/workspaces
hooks:
  after_create: |
    printf 'workspace-created\n' > sentinel.txt
agent:
  max_concurrent_agents: 1
  max_turns: 1
codex:
  command: python3 /srv/exo1007/slopcartel-live/company/runtime/.exocorp/runtime-host/runner-state/workspaces/workspace/company-9267343a762b0d1643c6e82a1458124ec46e0d3f4f7236e783b8b87f83e12277/workspace-91e7020030e812078ad10dea07c628d9e13555f4e2bda1a73e5e4d05fc7f6b57/research/symphony-acceptance/fake_agent.py
  read_timeout_ms: 5000
  turn_timeout_ms: 5000
server:
  host: 127.0.0.1
---
Complete {{ issue.identifier }}. Run the verification before Human Review.
