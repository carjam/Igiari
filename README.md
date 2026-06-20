# Fallacy Scanner — MVP Build Spec

This folder contains a complete build specification for an AI agent (or team of agents) to build a minimal web tool: paste text, see logical fallacies highlighted inline.

**Start here:** [`specs/00_master_spec.md`](specs/00_master_spec.md)

Then work through `specs/04_build_phases.md` as the main task list, referring back to the other numbered documents as each phase requires.

## Why this spec exists

This is a deliberately small, demand-testing version of a larger idea (a browser extension / consumer product for fallacy detection). The goal of this specific build is to answer "will anyone actually use this" as cheaply as possible — see `specs/00_master_spec.md` and `specs/07_monetization_notes.md` for the full reasoning. Resist the urge to build beyond what's in `specs/01_product_requirements.md`'s MUST list; see `specs/08_future_ideas.md` for where to park good ideas that come up mid-build instead of implementing them early.

## Document index

| File | Purpose |
|---|---|
| `specs/00_master_spec.md` | Entry point, scope summary, file structure |
| `specs/01_product_requirements.md` | Functional requirements, explicit in/out of scope |
| `specs/02_design_direction.md` | Visual identity guidance |
| `specs/03_architecture.md` | Stack, hosting, model choice, cost controls — concrete decisions |
| `specs/04_build_phases.md` | **The task list** — sequenced phases with acceptance criteria |
| `specs/05_api_contract.md` | Exact frontend/backend request-response schema |
| `specs/06_testing_and_launch_checklist.md` | Pre-launch verification |
| `specs/07_monetization_notes.md` | Why monetization (incl. ads) is deferred/rejected for this phase |
| `specs/08_future_ideas.md` | Parking lot — explicitly not in scope yet |

## Prerequisite materials

This spec assumes access to a prior project's outputs (a fallacy-detection taxonomy and eval set). If you don't have these files, ask before proceeding — see `specs/00_master_spec.md`'s "Source materials" section for the exact list of files needed.
