# Domain docs

This repo uses a single-context layout:

- `CONTEXT.md` at the repo root contains domain vocabulary.
- `docs/adr/` contains architecture decision records.

## Before exploring

Read `CONTEXT.md` and the ADRs relevant to the area being explored.

If these files are absent, proceed silently. The domain-modeling skill creates
them when terms or decisions are resolved.

## Vocabulary

Use the terms defined in `CONTEXT.md` when naming domain concepts in issues,
proposals, hypotheses, and tests.

For a missing concept, reconsider whether it belongs to the domain. Record
real vocabulary gaps for domain-modeling.

## Decision conflicts

Explicitly identify any proposal that contradicts an existing ADR.
Name the ADR and explain why the decision should be reopened.
