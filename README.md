# KOR: DYNASTIE — RimWorld Mod

A standalone RimWorld faction and colony project bringing the Kor Dynasty into the RimWorld universe.

## Target versions

- **Primary target:** RimWorld 1.7
- **Compatibility target:** RimWorld 1.6, where verified
- **DLC policy:** Core must work without optional DLCs. Available DLCs may be integrated separately; Odyssey is not required.
- **No legacy targets:** versions older than 1.6 are out of scope.

RimWorld 1.7 was announced for the unstable beta branch on 12 October 2026. The official announcement says most 1.6 mods are expected to work without changes, but each mod still needs testing and an explicit compatibility declaration. This repository treats 1.6 and 1.7 as intended targets, not as already verified releases.

## Design pillars

1. **A living faction:** settlements, trade, relationships and world events make the Dynasty feel present beyond direct player interactions.
2. **A playable start:** a dedicated Kor colony scenario is a core milestone.
3. **Community and resilience:** the Kor identity is expressed through mutual aid, recovery, training and reliable infrastructure.
4. **Fair challenge:** exceptional units are uncommon and capable, but remain vulnerable and costly to support.
5. **Own identity:** original definitions, text and art. V.O.I.D. is a reference for the scale of a high-threat faction, not a source to copy.
6. **Incremental verification:** every feature needs a clear acceptance test.

## Repository status

The mod has metadata, a Kor faction definition inheriting the vanilla OutlanderCivil baseline, English/German text, reproducible packaging, and static checks for XML, localization and world-generation settings. The first original pawn kind, `KOR_Resident`, is now defined and linked as the faction basic-member fallback. A separate player-faction definition and the first playable scenario now start four required Kor residents with modest basic supplies. The pawn kind has not yet been inserted into inherited visitor, trader or combat groups. This is **not yet a tested in-game release**; group composition, settlement/trade profiles, art, diplomacy and strategic simulation remain future work.

## Milestones

- [x] Establish project metadata and target versions.
- [x] Add a first faction definition using a vanilla template as a temporary baseline.
- [x] Add repository-level XML validation and regression tests.
- [x] Configure baseline world-generation presence and verify required fields statically.
- [x] Add English/German faction localization.
- [x] Build reproducible development ZIPs in CI.
- [ ] Verify the faction in RimWorld 1.7.
- [ ] Verify compatibility in RimWorld 1.6.
- [ ] Add original faction icon and visual identity.
- [x] Define the first Kor pawn kind and link it as the faction basic-member fallback.
- [ ] Wire original Kor pawn kinds into faction groups without breaking inherited trade/visitor behavior.
- [x] Add a first playable Kor colony-start scenario with four required Kor residents and basic supplies.
- [ ] Add distinct Kor settlement and trade profiles.
- [ ] Add world events, diplomacy and persistent strategic goals.
- [ ] Add optional DLC integrations, each isolated and tested independently.
- [ ] Package a reproducible release.

## Static checks

Run with Python 3:

```bash
python3 tools/validate_mod.py
```

This checks XML well-formedness, metadata, faction-to-pawn references, the colony-start roster, arrival method, required starting supplies, package contents, and English/German text. It does **not** replace loading the mod in RimWorld. Runtime compatibility must be verified against the actual game build before release.

## Local testing

Copy the repository folder into RimWorld's `Mods` directory and enable it after Core. Inspect the game's log after loading. Until the in-game test milestone is complete, treat this as a development build.

## Assets

Use original Kor assets and text. Do not include assets from other mods without explicit permission and license compatibility.