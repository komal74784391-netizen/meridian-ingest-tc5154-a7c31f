# Freight Pulse v4 — release candidate

Composition of the `freight-pulse-v4` artifact:

- Base indicators: World Bank Open Data (`wb-trade-v2` indicator set), distributed
  under CC-BY-4.0. Canonical text: `licenses/CC-BY-4.0.txt`.
- Synthetic annotations: generated with the model `Qwen/Qwen-7B-Chat`; its hub card
  carries only `license: other`. Vendored full terms: `third_party/qwen-7b-chat/LICENSE`.
- Curation ratio: 78% of released rows carry at least one synthetic annotation; the
  remaining 22% are raw indicator rows.

The release owner must record exactly one licence identifier in `MANIFEST.json`.
See `docs/RELEASE-POLICY.md`.