# Issue tracker: GitHub

Issues and specs live in GitHub Issues for `reiganarmstrong/ascii-wallpaper-generator`.
Use the `gh` CLI from this repo; it infers the repository from `origin`.

## Issue operations

- Create: `gh issue create --title "..." --body-file <file>`.
- Read: `gh issue view <number> --comments --json number,title,body,labels,comments`.
- List: `gh issue list --state open --json number,title,body,labels`, with appropriate filters.
- Comment: `gh issue comment <number> --body-file <file>`.
- Add or remove labels: `gh issue edit <number> --add-label "..."` or `--remove-label "..."`.
- Close: `gh issue close <number> --comment "..."`.

For multiline bodies, write the text to a temporary file and pass `--body-file`.
Use the role mapping in `triage-labels.md` for triage labels.

When a skill says "publish to the issue tracker", create a GitHub issue.
When it says "fetch the relevant ticket", read the issue and its comments.

## Pull requests as a triage surface

**PRs as a request surface: no.**

If changed to `yes`, triage external PRs using the same role mapping and `gh pr` operations.
Include authors with association `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR`, or `NONE`.
Read the PR comments and diff before triage.

GitHub issues and PRs share a number space. Resolve ambiguous references with
`gh pr view <number>`, falling back to `gh issue view <number>`.

## Wayfinding operations

- Map: one issue labelled `wayfinder:map` with Notes, Decisions-so-far, and Fog.
- Child ticket: a native sub-issue labelled `wayfinder:<type>`, where type is
  `research`, `prototype`, `grilling`, or `task`. If sub-issues are unavailable,
  use a task list in the map and `Part of #<map>` in each child.
- Blocking: use native issue dependencies. Add an edge with
  `gh api --method POST repos/reiganarmstrong/ascii-wallpaper-generator/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`.
  Fetch the database ID with
  `gh api repos/reiganarmstrong/ascii-wallpaper-generator/issues/<blocker> --jq .id`.
  If dependencies are unavailable, record `Blocked by: #<number>` in the child.
- Frontier: select the first open, unassigned child in map order whose blockers
  are all closed. Native `issue_dependencies_summary.blocked_by` counts open blockers.
- Claim: assign the ticket with `gh issue edit <number> --add-assignee @me` before working.
- Resolve: comment with the answer, close the child, and append a gist and link
  to the map's Decisions-so-far.
