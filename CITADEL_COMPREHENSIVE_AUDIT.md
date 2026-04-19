# CITADEL COMPREHENSIVE AUDIT
## 12-Repo Distributed Intelligence Mesh — Dead-End Analysis & System Critique

**Repository Under Review:** `DJ-Goana-Coding/mapping-and-inventory` (Librarian Hub)  
**Scope:** Full mesh — all 12 known spokes + hub  
**Audit Date:** 2026-04-19  
**Analyst:** Citadel Architect v25.0.OMNI+

---

## SECTION 1 — ARCHITECTURE OVERVIEW

The Citadel Mesh is a hub-and-spoke RAG intelligence system with one central Hub
(`mapping-and-inventory`) and up to 11 peripheral spoke repos. The Hub runs a
dual-process HuggingFace Space: Streamlit UI (port 7860) + FastAPI sidecar (port 8000).
Data flows: Device Nodes → GitHub → HF Space → FAISS index → T.I.A. query responses.

**Tech stack:** Python 3.11, Streamlit, FastAPI, FAISS, sentence-transformers/all-MiniLM-L6-v2,
Google Gemini API, HuggingFace Hub API, rclone (for GDrive), GitHub Contents API.

---

## SECTION 2 — CRITICAL DEAD ENDS

### 2.1 MISSING ENVIRONMENT VARIABLES (Hub)

| Variable | Severity | Effect if Absent |
|---|---|---|
| `HF_TOKEN` | 🔴 CRITICAL | `/v1/system/commit` returns 401. T.I.A. chat fails. |
| `GH_TOKEN` | 🔴 CRITICAL | GitHub commit bridge completely broken. |
| `GEMINI_API_KEY` | 🔴 CRITICAL | All Gemini calls fail; T.I.A. returns 500. |
| `GITHUB_WEBHOOK_SECRET` | 🟠 HIGH | Webhook open — any caller can trigger reindex. |
| `SPOKE_SHARED_SECRET` | 🟠 HIGH | `/v1/bridge/ingest` open — any caller can inject fragments. |
| `GDRIVE_SERVICE_ACCOUNT_JSON` | 🟠 HIGH | GDrive tab in Streamlit broken. rclone can't authenticate. |
| `RCLONE_CONFIG_DATA` | 🟠 HIGH | All `s10_push_to_vault.yml` and GDrive workflows fail. |
| `GEMINI_API_KEY_2` / `_3` | 🟡 MEDIUM | No key rotation fallback — single-key rate limits hit quickly. |
| `HF_WEBHOOK_MAPPING` | 🟡 MEDIUM | HF Space won't auto-pull on GitHub push; requires manual rebuild. |

### 2.2 MISSING FILES

| File | Referenced By | Impact |
|---|---|---|
| `data/vector_store/harvest.index` | `rag_hub.py`, `start_hub.sh` | RAG returns empty on cold start until `/v1/ingest` is called. File is gitignored. |
| `data/master_harvest/INDEX.md` | `rag_hub.py` DEFAULT_FRAGMENT_GLOBS | Reindex logs a warning and skips; non-fatal. |
| `deploy/skeleton/` | `core/self_healing_logic.py`, `scripts/deploy_fixer.sh` | Auto-heal 404 skeleton push silently skipped. Created inline by deploy_fixer.sh. |
| `tia-architect-core-templates/requirements.txt` | `repair_all_spaces.yml` step | Workflow fails with "No such file" during TIA-ARCHITECT-CORE repair job. |
| `PROTOCOL_HANDSHAKE_GUIDE.md` | `pulse_sync_handshake.yml` paths trigger | Workflow won't fire on that path change; missing guide. |
| `data/spoke_artifacts/*/` | `spoke_sync_receiver.yml` | Directory created on-demand — safe, but missing on cold clone. |

### 2.3 CODE BUGS

**B-001 — `s10_push_to_vault.yml` missing `import os`** *(FIXED in this PR)*  
File: `.github/workflows/s10_push_to_vault.yml`, line 103  
Inline Python block calls `os.path.exists()` but `import os` is absent.  
**Status: FIXED.**

**B-002 — `legal/pvc_ledger.py` SyntaxError**  
File: `legal/pvc_ledger.py`, line ~172  
Unicode box-drawing character `═` in a non-comment context causes `SyntaxError: invalid character`.  
**Affects:** `test_omni_convergence_v22.py` and any import of this module.  
**Fix:** Remove or wrap the border line in a string/comment.

**B-003 — `CITADEL_COMMAND_DECK_ORIGIN` hardcoded**  
File: `main_api.py` CORS origins list  
Value: `"https://citadel-nexus-private.vercel.app"` hardcoded.  
**Risk:** CORS breaks silently when the Vercel deployment URL changes.  
**Fix:** Replace with `os.getenv("CITADEL_COMMAND_DECK_URL", "https://citadel-nexus-private.vercel.app")`.

**B-004 — `worker_bridge.py` potential AttributeError**  
File: `services/worker_bridge.py` lines ~240–260  
References `Partition_01/oppo_node.py` with no import-guard. If the file is absent,
the entire worker bridge import fails.  
**Fix:** Wrap in `try/except ImportError`.

**B-005 — Duplicate `/v1/system/status` routes**  
Both `main_api.py` (existing endpoint) and `telemetry_bridge.py` (new router) register
`/v1/system/status`. FastAPI will silently use whichever is registered last.  
**Fix:** Confirm only one registration per path; the `telemetry_bridge.py` router version
supersedes any inline definition in `main_api.py`.

### 2.4 NAMING INCONSISTENCIES

| Issue | Location | Impact |
|---|---|---|
| `VAMGUARD` (docs) vs `VANGUARD` (code) | Partition_01/, vamguard_templates/, mapping/ | Cross-repo RAG queries for one spelling miss content under the other. **Resolution:** Documented as semantic aliases. |
| `DJ-Goana-Coding` (GitHub org, single `n`) vs `DJ-Goanna-Coding` (HF org, double `n`) | app.py line 60, all HF Space URLs | Do NOT normalise — these are intentionally different accounts. |
| `ARK_CORE` (GitHub, underscore) vs `ARK-CORE` (HF Space, hyphen) | spoke_sync_registry.json, workflows | Causes mis-routing in GitHub API calls if not carefully mapped. |

---

## SECTION 3 — LOOPING EVENTS & BRITTLE AUTOMATION

### 3.1 Potential Automation Loops

**L-001 — forever_learning_orchestrator.yml + auto_merge_to_main.yml**  
The forever-learning workflow commits updated intelligence data; if auto-merge is
also watching `main`, it can create a push→workflow→commit→push loop.  
**Mitigation:** Both workflows include `[automated]` in commit messages; ensure
`auto_merge_to_main.yml` skips commits matching `[automated]` or `[bot]`.

**L-002 — mesh_heartbeat.yml (every 30 min) + worker_watchdog.yml**  
Both workflows update `worker_status.json` and commit it. If they run concurrently,
they will race-condition on the commit and one will fail with a 409 (non-fast-forward).  
**Mitigation:** Add `concurrency: group: worker-status-commit` to both workflows.

**L-003 — spoke_sync_receiver.yml pushes back to `main`**  
`spoke_sync_receiver.yml` checks out the hub, fetches spoke artifacts, and pushes
back to `main`. This push fires `push: branches: [main]` triggers, potentially
cascading into `hf_space_sync.yml`, `pulse_sync_master.yml`, and `notify_hf_space.yml`.  
**Mitigation:** Add `[automated]` to the commit message (already present) and add
`paths-ignore` filters to downstream workflows.

### 3.2 Rate Limit Risk

**R-001 — Single Gemini key with no rotation**  
Most services call Gemini directly with `GEMINI_API_KEY`. Under heavy load (multiple
workers running simultaneously), this key will hit the free-tier rate limit.  
**Fix:** Set `GEMINI_API_KEY_2` and `GEMINI_API_KEY_3`; `services/gemini_rotator.py` and
`key_rotator_module.py` will automatically use them.

---

## SECTION 4 — PER-REPO STATUS

| Repo | Role | Status | Blocking Issues |
|---|---|---|---|
| `mapping-and-inventory` | **HUB — Librarian** | ✅ Running | Missing HF_TOKEN, GH_TOKEN, GEMINI_API_KEY |
| `ARK_CORE` | Device Sync Orchestrator | ✅ Integrated | Secrets needed for GDrive |
| `TIA-ARCHITECT-CORE` | T.I.A. Oracle | ⚠️ Broken Space | Python 3.13 pandas/numpy compat; repair_all_spaces.yml fix available |
| `CITADEL_OMEGA` | Master Orchestrator | 🔄 Pending | Not yet in spoke registry |
| `ORACLE` | Divination AI | 🔄 Pending | Not yet in spoke registry |
| `AION` | Temporal Intelligence | 🔄 Pending | Not yet in spoke registry |
| `VAMGUARD_TITAN` | VAMGUARD Infrastructure | 🔄 Pending | No HF Space URL configured |
| `Genesis-Research-Rack` | 321GB Data Vault | 🔄 Pending | Requires GDRIVE_SERVICE_ACCOUNT_JSON |
| `Pioneer-Trader` | Trading Intelligence | 🔄 Pending | Not yet in spoke registry |
| `Citadel_Genetics` | Genetics Research | 🔄 Pending | Not yet in spoke registry |
| `goanna_coding` | Coding Environment | 🔄 Pending | Not yet in spoke registry |
| S10 Device (Termux) | Field Uplink | ✅ Active | Termux git push working; `import os` bug fixed |
| Oppo Device (Termux) | Librarian Node | ✅ Active | Direct git push working |

---

## SECTION 5 — WORKFLOW HEALTH

**Total workflows:** 65  
**Workflows with manual-dispatch-only triggers (no automation):** ~18  
**Workflows touching `worker_status.json`:** 4 (race condition risk — see L-002)  
**Workflows with hardcoded org name `DJ-Goana-Coding`:** Most — safe, intentional.

**Recommended immediate fixes:**
1. Add `concurrency: group: worker-status-commit` to `mesh_heartbeat.yml` and `worker_watchdog.yml`.
2. Create `tia-architect-core-templates/requirements.txt` so `repair_all_spaces.yml` doesn't fail.
3. Fix `legal/pvc_ledger.py` SyntaxError.
4. Move `CITADEL_COMMAND_DECK_ORIGIN` to an env var.

---

## SECTION 6 — STRATEGIC RECOMMENDATIONS

1. **Register all 11 spokes in `data/spoke_sync_registry.json`** — currently only ARK-CORE is registered. The remaining 10 repos are invisible to the Librarian.
2. **Set `SPOKE_SHARED_SECRET`** — without this, any caller can inject fragments into the RAG index via `/v1/bridge/ingest`.
3. **Run `scripts/deploy_fixer.sh`** — clears "No Application File" on all broken HF Spaces in one shot.
4. **Configure GitHub webhook** → `/v1/webhook/github` with `GITHUB_WEBHOOK_SECRET` — enables zero-latency RAG updates on every device push without a container rebuild.
5. **Run `python workers/vacuum_shard_worker.py`** — generates domain shards for the Vercel HUD's domain-specific query routing.
6. **Run `python core/self_healing_logic.py --daemon`** — continuous 503/404 watcher; auto-pushes restart commits when Spaces break.

---

*End of Citadel Comprehensive Audit — 2026-04-19*
