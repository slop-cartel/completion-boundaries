# Run index

- **probe-01:** initial three-case smoke run; superseded for repetition counts by the full four-case harness. All raw output retained.
- **probe-02, probe-03, probe-04:** four cases each, complete, 12 case outcomes matched expectations. Source v0.0.3; binary hash in manifest.json. No model calls.

Each complete case has result.json, WORKFLOW.md, tracker.jsonl (requests/state), snapshots.json, stdout.log and Symphony log/log/symphony.log.1. Cases that launch the fake agent also have agent.jsonl (protocol in/out); the before-run failure case launches none. Invalid harness runs may lack result.json. The failing hook creates a synthetic failure marker and exits 1; this is injected failure, not a real repository test.

## Fresh-reader checks and resulting repair

- `fresh-reader-download`: independent fresh download, all four cases passed; reviewer-generated evidence retained from its temporary directory.
- `fresh-reader-space-failure`: active probe timed out because our shell command did not quote a path containing spaces. Invalid harness run, not a Symphony finding. Retained.
- `portability-fix`: rerun of all four cases from a directory containing spaces after quoting the command. Stronger assertions check the real exit-status warning, workspace retention and two fresh settled snapshots.

The original 12 case executions refer only to probe-02 through probe-04. Fresh-reader, failed portability and repair checks are additional validation, not added to a coding success denominator.

- `final-reader-download`: final reader reran the entire release subset from a space-containing directory, fresh binary download; four corrected case checks passed. Retained, not part of the original 12 case executions.
