# Meridian Ingest — Maintainer Triage

_Last refreshed: 2026-11-07_

The branch `staging` is being prepared for the v5 cut. Every open item below must
point at the line where its marker actually sits in the `staging` revision of the
file it names. Items whose marker no longer exists on `staging` have been resolved
and belong in the resolved section.

## Open Action Items

- [ ] **meridian/core/clock.py#6** :: # MAINT-MARK clock-sync-01 :: prefer the monotonic reading whenever the wall clock steps backwards
- [ ] **meridian/core/clock.py#23** :: # MAINT-MARK clock-sync-02 :: clamp negative elapsed samples to zero instead of raising
- [ ] **meridian/core/clock.py#29** :: # MAINT-MARK clock-sync-03 :: expose the sampling interval used by the lag monitor
- [ ] **meridian/core/config.py#7** :: # MAINT-MARK config-env-01 :: refuse unknown keys instead of silently ignoring them
- [ ] **meridian/core/config.py#19** :: # MAINT-MARK config-env-02 :: load layered overrides in deterministic order
- [ ] **meridian/core/config.py#27** :: # MAINT-MARK config-env-03 :: redact secret-looking values in config dumps
- [ ] **meridian/core/errors.py#6** :: # MAINT-MARK errors-taxonomy-02 :: attach the stage name to every raised failure
- [ ] **meridian/core/errors.py#14** :: # MAINT-MARK errors-taxonomy-01 :: map timeout failures to a retryable category
- [ ] **meridian/core/errors.py#20** :: # MAINT-MARK errors-taxonomy-03 :: drop the deprecated string code once callers migrate
- [ ] **meridian/core/units.py#4** :: # MAINT-MARK units-scale-01 :: normalize byte counts to base-10 units for reports
- [ ] **meridian/core/units.py#19** :: # MAINT-MARK units-scale-02 :: reject durations above the pipeline ceiling
- [ ] **meridian/core/units.py#27** :: # MAINT-MARK units-scale-03 :: keep the raw value alongside the human string
- [ ] **meridian/io/journal.py#7** :: # MAINT-MARK journal-fsync-01 :: fsync the segment before publishing the offset
- [ ] **meridian/io/journal.py#26** :: # MAINT-MARK journal-fsync-02 :: recover the tail segment from the temporary file
- [ ] **meridian/io/journal.py#31** :: # MAINT-MARK journal-fsync-03 :: expire rotated segments after the retention window
- [ ] **meridian/io/objectstore.py#4** :: # MAINT-MARK objectstore-multipart-01 :: abort orphaned multipart uploads on startup
- [ ] **meridian/io/objectstore.py#21** :: # MAINT-MARK objectstore-multipart-02 :: reuse the signed URL until it expires
- [ ] **meridian/pipeline/dedupe.py#12** :: # MAINT-MARK dedupe-fingerprint :: fingerprint records by canonical field order, not source order
- [ ] **meridian/pipeline/dedupe.py#26** :: # MAINT-MARK dedupe-shim-a :: remove the v1 shard cursor once every producer migrates
- [ ] **meridian/pipeline/dedupe.py#27** :: # MAINT-MARK dedupe-shim-b :: tolerate the deprecated payload envelope for one more release
- [ ] **meridian/pipeline/dedupe.py#28** :: # MAINT-MARK dedupe-shim-c :: retire the byte-order shim after the vendored parser catches up
- [ ] **meridian/pipeline/dedupe.py#29** :: # MAINT-MARK dedupe-shim-d :: drop the legacy checksum alias before the v5 cut
- [ ] **meridian/pipeline/dedupe.py#30** :: # MAINT-MARK dedupe-shim-e :: delete the temporary dual-write bucket flag
- [ ] **meridian/pipeline/dedupe.py#31** :: # MAINT-MARK dedupe-shim-f :: remove the quarter-end backfill switch after rollout
- [ ] **meridian/pipeline/dedupe.py#58** :: # MAINT-MARK dedupe-window-echo :: log the effective dedupe window once per shard
- [ ] **meridian/pipeline/dedupe.py#78** :: # MAINT-MARK dedupe-collision :: report collisions with the colliding key prefix
- [ ] **meridian/pipeline/dedupe.py#87** :: # MAINT-MARK dedupe-temp-a :: drop the temporary bloom probe after the rollout
- [ ] **meridian/pipeline/dedupe.py#88** :: # MAINT-MARK dedupe-temp-b :: retire the short-lived bucket rehash hook
- [ ] **meridian/pipeline/dedupe.py#94** :: # MAINT-MARK dedupe-budget :: cap memory use at the configured key budget before eviction
- [ ] **meridian/pipeline/merge.py#4** :: # MAINT-MARK merge-priority-01 :: resolve conflicting records by the newest source sequence
- [ ] **meridian/pipeline/merge.py#13** :: # MAINT-MARK merge-priority-02 :: keep tombstones visible until the compaction window closes
- [ ] **meridian/pipeline/merge.py#20** :: # MAINT-MARK merge-priority-03 :: emit a stable sort key for reproducible merges
- [ ] **meridian/pipeline/schema.py#4** :: # MAINT-MARK schema-evolve-01 :: accept an optional nullable column without a schema bump
- [ ] **meridian/pipeline/schema.py#15** :: # MAINT-MARK schema-evolve-02 :: reject renames that break the downstream projection
- [ ] **meridian/pipeline/schema.py#21** :: # MAINT-MARK schema-evolve-03 :: print the resolved schema once per batch
- [ ] **meridian/workers/backfill.py#10** :: # MAINT-MARK backfill-ledger :: record the exhausted retry budget before the worker stops
- [ ] **meridian/workers/backfill.py#23** :: # MAINT-MARK backfill-legacy-a :: remove the blobs cursor after the objectstore migration
- [ ] **meridian/workers/backfill.py#24** :: # MAINT-MARK backfill-legacy-b :: drop the double-write flag once the shadow reader is gone
- [ ] **meridian/workers/backfill.py#25** :: # MAINT-MARK backfill-legacy-c :: retire the v1 checkpoint format after the reopen
- [ ] **meridian/workers/backfill.py#26** :: # MAINT-MARK backfill-legacy-d :: delete the temporary replay throttle
- [ ] **meridian/workers/backfill.py#35** :: # MAINT-MARK backfill-window :: clamp the backfill window to the frozen partition bounds
- [ ] **meridian/workers/backfill.py#53** :: # MAINT-MARK backfill-ledger :: record the exhausted retry budget before the worker stops
- [ ] **meridian/workers/backfill.py#74** :: # MAINT-MARK backfill-temp-a :: drop the emergency shard throttle after the incident review
- [ ] **meridian/workers/backfill.py#75** :: # MAINT-MARK backfill-temp-b :: remove the ad-hoc jitter override
- [ ] **meridian/workers/backfill.py#80** :: # MAINT-MARK backfill-verify :: compare the row count against the checkpoint ledger after resume
- [ ] **meridian/workers/retry.py#7** :: # MAINT-MARK retry-budget-01 :: honor the per-stage retry budget from config
- [ ] **meridian/workers/retry.py#16** :: # MAINT-MARK retry-budget-02 :: sleep with jitter but cap the total delay
- [ ] **meridian/workers/retry.py#22** :: # MAINT-MARK retry-budget-03 :: surface the attempt count in the final error
- [ ] **meridian/workers/shard.py#4** :: # MAINT-MARK shard-plan-01 :: balance shards by byte size instead of row count
- [ ] **meridian/workers/shard.py#21** :: # MAINT-MARK shard-plan-02 :: keep the idle shard threshold configurable
- [ ] **meridian/workers/shard.py#28** :: # MAINT-MARK shard-plan-03 :: log the skew ratio when a single shard dominates
- [ ] **scripts/rotate_shards.py#6** :: # MAINT-MARK rotate-dryrun-01 :: print the planned moves before applying them
- [ ] **scripts/rotate_shards.py#21** :: # MAINT-MARK rotate-dryrun-02 :: skip shards that are marked draining in the registry
- [ ] **scripts/rotate_shards.py#31** :: # MAINT-MARK rotate-dryrun-03 :: emit a summary of bytes relocated

## Release Blockers

- [ ] **release/freight-pulse-v4/MANIFEST.json** :: record exactly one licence identifier for the release; see `docs/RELEASE-POLICY.md` and `release/freight-pulse-v4/README.md`
