# DLC compatibility policy

## Baseline

The Core mod must load without any optional DLC. Odyssey is explicitly not required.

## Integration policy

- Keep baseline faction, settlement and pawn definitions in the ordinary `Defs/` tree.
- Put DLC-specific content in clearly named folders and only include definitions that are valid for the declared target versions.
- Prefer DLC-provided mechanics only when they materially improve the feature; provide a Core-compatible alternative where reasonable.
- Never reference a DLC-only Def from a Core-loaded definition.
- Validate each DLC combination independently in-game and record the exact game build and DLC set used.
- Do not infer 1.7 compatibility from a successful 1.6 load or vice versa.

## Test matrix

| Game version | Core only | Available DLCs except Odyssey | Status |
|---|---|---|---|
| 1.7 | Required | Required after baseline | Not yet run in-game |
| 1.6 | Compatibility target | Required after baseline | Not yet run in-game |

A matrix cell is complete only after enabling the mod, generating a new world, starting a colony, saving, reloading and checking the player log for new errors.