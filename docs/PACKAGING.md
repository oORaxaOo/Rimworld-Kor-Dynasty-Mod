# Reproducible development package

The CI workflow builds a ZIP containing only RimWorld runtime folders. The archive has a single top-level `KOR-DYNASTIE/` directory, so it can be extracted directly into the game's `Mods/` directory.

## Local build

Run from the repository root:

```bash
python3 tools/validate_mod.py
python3 -m unittest discover -s tests -v
python3 tools/package_mod.py
```

The default output is `dist/KOR-DYNASTIE-dev.zip`. Override it with `--output /path/to/file.zip`.

## Included runtime paths

Only these known game-facing paths are packaged when present: `About/`, `Defs/`, `Languages/`, `Patches/`, `Textures/`, `Assemblies/`, and `LoadFolders.xml`. Development documentation, tests, Git metadata, and tooling are intentionally excluded.

## Release boundary

This is a reproducible **development package**, not a claim of in-game compatibility. The ZIP is checked for required metadata and faction files, but must still be tested in RimWorld 1.7 with the player log inspected. Test RimWorld 1.6 separately before advertising compatibility there.
