# meridian-ingest

Data ingestion and curation toolkit behind the Freight Pulse indicator.

## Branches

- `main` — released snapshot and the source of the triage numbering.
- `staging` — the v5 candidate; two modules were rewritten in several separated regions.

## Layout

- `meridian/core` — clock, config, errors, units.
- `meridian/pipeline` — dedupe, merge, schema.
- `meridian/workers` — backfill, retry, shard.
- `meridian/io` — journal, objectstore.
- `scripts/` — one-off rotation tooling.
- `release/freight-pulse-v4` — curated release candidate and its manifest.
- `third_party/` — vendored upstream licence terms.
- `licenses/` — canonical licence texts.

Maintainers track follow-ups in `MAINTENANCE-TRIAGE.md`.