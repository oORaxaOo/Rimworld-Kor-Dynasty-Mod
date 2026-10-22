# Kor faction architecture

## Purpose

The Kor must read as a functioning society, not merely as a hostile pawn-group generator. Implement the smallest reliable RimWorld-native version first, then add strategic simulation only when each layer can be saved, tested and understood.

## Runtime layers

1. **Native faction layer** — FactionDef, world generation, goodwill, settlements and standard trading/raid interactions.
2. **Identity layer** — Kor names, descriptions, faction icon, settlement presentation and original pawn kinds.
3. **Colony layer** — dedicated scenario and starting rules, with a clear distinction between a Kor-controlled colony and settlements belonging to the world faction.
4. **Campaign layer** — bounded strategic goals such as protect a border, establish a supply route or respond to an attack. State must survive save/load.
5. **Territory layer** — a separate model of strategic regions and claims. Do not pretend that vanilla RimWorld has a complete province-control system; represent it through explicit, player-readable events and settlement state.

## Implementation rules

- Prefer native Defs and built-in faction behavior over patches.
- Use Harmony/C# only when native Defs cannot express a required behavior.
- Any patch must be narrowly scoped, null-safe and tested against the target game version.
- Keep optional DLC references out of the Core load path.
- Never spawn unlimited reinforcements or bypass normal combat consequences.
- Add one layer at a time; do not implement the territory simulation before the faction baseline has passed an in-game load test.

## First playable acceptance gate

- The mod loads with Core only.
- A newly generated world can include the Kor faction.
- The faction is visible and has sensible relations.
- The player can interact with its settlements using normal RimWorld systems.
- A new game can be started and saved/reloaded without new errors.
- The 1.7 test is performed first; 1.6 is tested separately before compatibility is claimed.