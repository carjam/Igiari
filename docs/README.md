# Documentation Index

Operations, deployment, and testing docs. **Build specs** live in [`specs/`](../specs/README.md).

**Layout rules:** [CONVENTIONS.md](CONVENTIONS.md) — what belongs in `docs/` vs `specs/` vs service folders.

## Deployment & Operations

| Doc | Purpose |
|-----|---------|
| [INTEGRATIONS.md](INTEGRATIONS.md) | Supabase, Resend, Render, Cloudflare — dashboards, URLs, env vars |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Live deployment management (Render + Cloudflare) |
| [DEPLOY_RENDER.md](DEPLOY_RENDER.md) | Render backend service config and env vars |
| [DEPLOY_CLOUDFLARE.md](DEPLOY_CLOUDFLARE.md) | Cloudflare Pages quick reference |
| [SUPABASE.md](SUPABASE.md) | Migrations, auth settings, project URLs |
| [AUTH_AND_EMAIL_RECOVERY.md](AUTH_AND_EMAIL_RECOVERY.md) | Rebuild auth, Resend SMTP, domain, Magic Link template |
| [PROMPT_GUIDE.md](PROMPT_GUIDE.md) | Edit `prompt_template.txt`, eval workflow |

## Monetization

| Doc | Purpose |
|-----|---------|
| [MONETIZATION_ROLLOUT.md](MONETIZATION_ROLLOUT.md) | **Current status** — Step 0–3 tracker |
| [STRIPE_SETUP.md](STRIPE_SETUP.md) | Stripe: production (live) + sandbox dev setup |
| [STRIPE_GO_LIVE.md](STRIPE_GO_LIVE.md) | Go-live phases A–E; consumer live ✅, legal ⬜ |
| [LEGAL_BILLING_SETUP.md](LEGAL_BILLING_SETUP.md) | Enable legal-tier checkout ($29 / $39) on Render |
| [STEP0_LAUNCH_READINESS.md](STEP0_LAUNCH_READINESS.md) | Analytics, live smoke test, spend cap |
| [../specs/10_monetization.md](../specs/10_monetization.md) | End-state billing architecture |
| [../specs/11_monetization_rollout_plan.md](../specs/11_monetization_rollout_plan.md) | Phased execution plan |

## Testing & Quality

| Doc | Purpose |
|-----|---------|
| [LAUNCH_CHECKLIST.md](LAUNCH_CHECKLIST.md) | Launch verification tracker |
| [LIVE_SMOKE_TEST.md](LIVE_SMOKE_TEST.md) | Production smoke test results (2026-06-21) |
| [STEP0_LAUNCH_READINESS.md](STEP0_LAUNCH_READINESS.md) | Step 0 checklist |
| [TEST_REPORT.md](TEST_REPORT.md) | Phase 0–3 test report *(historical; paths refer to pre-deploy layout)* |
| [AUTONOMOUS_TESTING_SUMMARY.md](AUTONOMOUS_TESTING_SUMMARY.md) | Autonomous testing process summary |
| [../specs/06_testing_and_launch_checklist.md](../specs/06_testing_and_launch_checklist.md) | Canonical launch checklist |

## Project Decisions

| Doc | Purpose |
|-----|---------|
| [DECISIONS.md](DECISIONS.md) | Deviations from spec defaults |

## Back to project

[README.md](../README.md) · [specs/README.md](../specs/README.md)
