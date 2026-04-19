# 🏛 Sovereign Registry

Implements `QGTNL_TOTAL_SINGULARITY_WELD_v9293 §5 SOVEREIGN_REGISTRY`.

Maps every named persona (AION, TIA, ORACLE, …) to:

- a **Toroidal Core** (`Core_Alpha`, `Core_Beta`, `Core_Gamma`, …),
- a **Functional Block** (the high-level capability the persona owns), and
- the **Primary Modules** in this repo that implement that capability.

## Files

| File | Purpose |
|---|---|
| `personas.json` | Canonical machine-readable registry. |
| `README.md`     | This document. Human-readable schema reference. |

## Schema

```jsonc
{
  "version": "v9293.1",
  "directive": "QGTNL_TOTAL_SINGULARITY_WELD_v9293 §5 SOVEREIGN_REGISTRY",
  "personas": [
    {
      "id":               "AION",                 // unique upper-case identifier
      "display_name":     "AION",                 // human-friendly label
      "toroidal_core":    "Core_Alpha",           // assigned core
      "functional_block": "Sovereign Cognition",  // capability ownership
      "primary_modules":  ["services/ark_engine.py"],
      "notes":            "Free-form description."
    }
  ]
}
```

## Adding a persona

1. Append a new object to `personas[]` in `personas.json`.
2. Use a unique `id` (upper-snake or single word).
3. Reference real files in `primary_modules` (paths relative to repo root).
4. Keep entries **data-only** — no executable logic lives here.

## Consumers

The registry is a passive document. No code currently imports it; it is
a docs/governance artifact for the directive. If a future service needs
to look it up, parse it with `json.loads(Path("registry/personas.json").read_text())`.
