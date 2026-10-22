# KOR: DYNASTIE — Project Plan

## Product definition

KOR: DYNASTIE is a standalone RimWorld faction project. The long-term vision is a coherent territorial power with settlements, trade, diplomacy, original technology themes, and a playable colony start.

The first release prioritizes stable integration with the base game over feature count.

## System boundaries

### Faction and world presence
- A dedicated faction definition and world-generation presence.
- Distinct settlement roles only after the baseline faction loads reliably.
- Persistent strategic state must use RimWorld-supported save/load mechanisms.
- Expansion and territorial claims must be bounded, explainable and testable.

### Society and resilience
- Express Kor identity through mutual aid, recovery, community infrastructure, training and social events.
- Do not reduce the society to a combat-only faction.
- Prefer understandable effects over hidden global penalties.

### Economy and research
- Add original goods, buildings and research in small testable batches.
- Every recipe must have valid ingredients, workbench requirements and research prerequisites.
- Optional DLC content must be isolated so Core-only loading remains possible.

### Challenge and balance
- Exceptional roles should be uncommon and costly to support.
- Difficulty must arise from coherent systems, not arbitrary invulnerability or unlimited event spawning.
- Test counterplay and performance before expanding encounter size.

## Milestones and acceptance gates

1. **Bootstrap:** metadata, faction definition, XML validation.
2. **Load test:** verify no XML/Def errors and confirm the faction appears in generated worlds on RimWorld 1.7.
3. **Compatibility:** repeat on RimWorld 1.6; support it only if the same design works reliably.
4. **Identity:** original faction icon, names, descriptions and settlement presentation.
5. **Playable start:** scenario, starting colonists, starting supplies and clear scenario text.
6. **World presence:** settlement variants, trade profiles, relationship behavior and event hooks.
7. **Strategic layer:** saved goals and bounded faction-level state, with clear UI feedback.
8. **Content expansion:** production and research content, then optional DLC integrations.
9. **Release verification:** clean load, new-world generation, save/reload, error-log review, performance check and packaging.

## Current limitation

The connected GitHub environment can perform repository-level static checks but does not expose the actual RimWorld 1.7 executable, installed DLC state or runtime logs. No in-game compatibility claim is made until those tests are performed.