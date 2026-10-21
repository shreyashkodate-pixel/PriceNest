# PriceNest — Operational Scripts & Utilities

This directory contains standalone automation and utility scripts for managing the PriceNest development lifecycle, data pipelines, database seeding, and deployment verification.

---

## 1. Directory Structure

```
scripts/
├── README.md               # Overview of utility scripts (this file)
├── setup_dev.sh            # Script to verify local prerequisites and set up env files
├── seed_localities.py      # Seed initial Pune micro-market reference table into Supabase
└── verify_env.py           # Preflight configuration and database connectivity checker
```

---

## 2. Script Usage & Guidelines

- All operational scripts should be idempotent and safe to run multiple times.
- Python utility scripts should inherit settings from `backend/app/core/config.py` or take explicit CLI flags.
- Sensitive credentials must never be hardcoded into scripts; always pass them via environment variables.
- Shell scripts should be executable (`chmod +x script.sh`) and use standard POSIX-compliant syntax.
