# adperf: Ad Performance Analytics

Analytics toolkit for measuring the efficiency of advertising campaigns of an
**EdTech subscription school**: spend by channel, the lead → trial → paid funnel,
unit economics (CPL, CAC, ROMI, LTV), subscription metrics (MRR, churn, retention),
reports, an interactive dashboard and exports.

> **Status:** under active development (Stage 0 of 6: project setup).

## Features (planned)

- Store ad spend, leads, trials, customers, subscriptions and payments (SQLite via SQLAlchemy 2.x, PostgreSQL-ready)
- Import data from CSV and adapters for ad platforms, CRM and billing exports
- Metrics: conversion rates, CPL, CPT, CAC, ROAS, ROI, ROMI, LTV, LTV/CAC, payback, MRR, churn
- Compare channels and periods (MoM / YoY), cohort retention
- Static (matplotlib) and interactive (plotly) reports, HTML summary, CSV/Excel export
- CLI (Typer) and Streamlit dashboard, English and Russian interface

## Tech stack

Python 3.11+, SQLAlchemy 2, Alembic, pandas, numpy, plotly, matplotlib, Typer,
Streamlit, pydantic-settings, loguru, pytest, ruff, black, mypy.

## Quick start (macOS / Linux)

```bash
git clone https://github.com/<your-username>/adperf.git
cd adperf
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python scripts/check_env.py   # verify the environment
pytest -q                     # run the tests
```

## Project layout

```text
src/adperf/     application code (config, db, repositories, loaders,
                metrics, analytics, reports, cli, ui)
tests/          pytest test suite
data/sample/    synthetic demo datasets (real data is never committed)
reports/        generated reports (git-ignored)
docs/           architecture, data model, metric definitions
scripts/        helper scripts (environment check, scaffolding)
```

## Roadmap

| Stage | Topic | Status |
|---|---|---|
| 0 | Setup: environment, repository, config | in progress |
| 1 | Data model, migrations, data generator | planned |
| 2 | Metrics and analytics | planned |
| 3 | Reports and visualization | planned |
| 4 | CLI and Streamlit dashboard | planned |
| 5 | Quality: tests, linters, logging, CI | planned |
| 6 | Documentation and portfolio polish | planned |