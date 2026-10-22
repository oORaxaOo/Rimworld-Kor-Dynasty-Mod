# Integration and verification gates

Every new runtime feature must pass these gates before it is described as integrated:

1. **Repository structure:** all XML parses; every XML file under `Defs/` has a `<Defs>` root.
2. **Definition identity:** no duplicate `defName` values across the mod's Defs XML.
3. **Metadata:** package ID and target-version declarations are consistent and unique.
4. **Automated regression:** run the validator and Python unit tests in CI.
5. **Game runtime:** load in RimWorld 1.7 with Core only, inspect the player log, exercise the feature, save/reload, and check again.
6. **Compatibility:** test RimWorld 1.6 independently before claiming it works there.
7. **DLC isolation:** the Core load path must not require optional DLCs; DLC-specific features need their own test matrix.

## What static checks can and cannot prove

The automated checks can catch malformed XML, repeated DefNames, metadata drift, and common folder/root mistakes. They cannot resolve vanilla parent templates, prove that RimWorld accepts every XML field, validate texture paths, or simulate faction generation. Those require the actual game and log output.

## Current runtime limitation

The current faction still inherits the vanilla `OutlanderCivil` template as a temporary baseline. It is not yet an original, runtime-verified faction implementation. Do not mark the first playable milestone complete until the in-game acceptance gate in `FACTION_ARCHITECTURE.md` passes.
