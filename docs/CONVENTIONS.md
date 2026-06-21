# Documentation layout

All **project documentation** lives in two folders. Everything else is either the repo entry point or colocated runtime data.

## `specs/` — what to build

Agent-oriented **build specifications**: product requirements, architecture, API contracts, monetization target design, phased rollout plans.

| Start here | Purpose |
|------------|---------|
| [11_monetization_rollout_plan.md](../specs/11_monetization_rollout_plan.md) | Current execution order |
| [10_monetization.md](../specs/10_monetization.md) | End-state billing architecture |
| [00_master_spec.md](../specs/00_master_spec.md) | MVP scope and repo map |

Index: [specs/README.md](../specs/README.md)

## `docs/` — how to run and operate

**Operations**: deployment, integrations, Stripe, auth recovery, test reports, decision log.

| Start here | Purpose |
|------------|---------|
| [MONETIZATION_ROLLOUT.md](MONETIZATION_ROLLOUT.md) | Human-readable status tracker |
| [INTEGRATIONS.md](INTEGRATIONS.md) | All dashboards, URLs, env vars |
| [README.md](README.md) | Full doc index |

## Exceptions (stay outside `docs/` / `specs/`)

| Path | Why |
|------|-----|
| [README.md](../README.md) | Repository entry point (convention) |
| [backend/README.md](../backend/README.md) | Short local-dev pointer → links to `docs/` |
| [supabase/README.md](../supabase/README.md) | Short pointer → [SUPABASE.md](SUPABASE.md) |
| [frontend/README.md](../frontend/README.md) | Explains static files moved to repo root |
| [backend/fallacy_reference/fallacy_taxonomy.md](../backend/fallacy_reference/fallacy_taxonomy.md) | Runtime reference data (paired with `fallacies.json`) |
| [source-materials/](../source-materials/) | Upstream skill + taxonomy source (not ops docs) |

## Adding new docs

- **Spec change** (requirements, pricing architecture, build phases) → `specs/`
- **Runbook** (deploy, integrate, troubleshoot, test log) → `docs/`
- **Service folder** → optional one-screen `README.md` that links into `docs/`; do not duplicate full guides

Update [docs/README.md](README.md) or [specs/README.md](../specs/README.md) when adding a file.

---

**Last updated:** June 2026
