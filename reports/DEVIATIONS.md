# Deviations log

| # | Date | Spec says | Reality | Action |
|---|------|-----------|---------|--------|
| 1 | 2026-10-10 | Phase 0: download datasets to `data/raw/` | Sandbox network policy returns 403 for `huggingface.co` (PyPI is reachable). Only Hub *metadata* is reachable, via the Hugging Face connector. | Blocked; awaiting user decision (Checkpoint 0). No data analysed; no numbers fabricated. |
| 2 | 2026-10-10 | Primary `agent_snapshots` has karma, follower, following counts | Confirmed. Columns: `id, name, karma, followerCount, followingCount, isClaimed, isActive, createdAt, lastActive, sampled_at`. camelCase; `createdAt`/`lastActive` are *strings*, only `sampled_at` is a timestamp. | Canon step must parse strings explicitly. |
| 3 | 2026-10-10 | Secondary is a subset of platform totals | Its card lists platform totals of 4.42M posts / 13.5M comments, but the primary has 19.7M comments. The collectors disagree on totals (platform total at a different date, or primary double-counting). | Check in the Phase 0 coverage comparison. |
| 4 | 2026-10-10 | Cross-check `agents` has `owner_x_handle` | Confirmed, plus `avatar_url` and `description`. `is_claimed` is int64 there, bool in the primary. | `ingest.py` drops `owner_x_handle`; treat `avatar_url` as an identifier too. |
