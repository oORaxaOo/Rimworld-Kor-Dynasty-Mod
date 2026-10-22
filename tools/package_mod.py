#!/usr/bin/env python3
"""Build a clean, reproducible RimWorld mod ZIP from runtime folders only."""

import argparse
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MOD_FOLDER_NAME = "KOR-DYNASTIE"
RUNTIME_PATHS = (
    "About",
    "Defs",
    "Languages",
    "Patches",
    "Textures",
    "Assemblies",
    "LoadFolders.xml",
)


def package_mod(root: Path = ROOT, output: Path | None = None) -> Path:
    root = root.resolve()
    output = (output or (root / "dist" / "KOR-DYNASTIE-dev.zip")).resolve()
    metadata = root / "About" / "About.xml"
    faction = root / "Defs" / "FactionDefs" / "KOR_Dynasty.xml"
    pawn_kind = root / "Defs" / "PawnKindDefs" / "KOR_PawnKinds.xml"
    scenario = root / "Defs" / "ScenarioDefs" / "KOR_ColonyStart.xml"
    if not metadata.is_file():
        raise FileNotFoundError("Required runtime file missing: About/About.xml")
    if not faction.is_file():
        raise FileNotFoundError("Required runtime file missing: Defs/FactionDefs/KOR_Dynasty.xml")
    if not pawn_kind.is_file():
        raise FileNotFoundError("Required runtime file missing: Defs/PawnKindDefs/KOR_PawnKinds.xml")
    if not scenario.is_file():
        raise FileNotFoundError("Required runtime file missing: Defs/ScenarioDefs/KOR_ColonyStart.xml")

    files: list[tuple[Path, str]] = []
    for relative in RUNTIME_PATHS:
        source = root / relative
        if source.is_file():
            files.append((source, f"{MOD_FOLDER_NAME}/{relative}"))
        elif source.is_dir():
            for path in sorted(source.rglob("*")):
                if path.is_file():
                    files.append((path, f"{MOD_FOLDER_NAME}/{path.relative_to(root).as_posix()}"))

    if not files:
        raise RuntimeError("No runtime files found to package.")

    output.parent.mkdir(parents=True, exist_ok=True)
    output_resolved = output.resolve()
    with zipfile.ZipFile(output_resolved, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source, archive_name in sorted(files, key=lambda item: item[1]):
            if source.resolve() == output_resolved:
                continue
            archive.write(source, archive_name)

    with zipfile.ZipFile(output_resolved, "r") as archive:
        names = archive.namelist()
        if f"{MOD_FOLDER_NAME}/About/About.xml" not in names:
            raise RuntimeError("Package verification failed: About metadata missing.")
        if f"{MOD_FOLDER_NAME}/Defs/FactionDefs/KOR_Dynasty.xml" not in names:
            raise RuntimeError("Package verification failed: Kor faction Def missing.")
        if f"{MOD_FOLDER_NAME}/Defs/PawnKindDefs/KOR_PawnKinds.xml" not in names:
            raise RuntimeError("Package verification failed: Kor pawn-kind Def missing.")
        if f"{MOD_FOLDER_NAME}/Defs/ScenarioDefs/KOR_ColonyStart.xml" not in names:
            raise RuntimeError("Package verification failed: Kor colony scenario missing.")
        for language in ("English", "German"):
            translation_path = (
                f"{MOD_FOLDER_NAME}/Languages/{language}/DefInjected/ScenarioDef/KOR_ColonyStart.xml"
            )
            if translation_path not in names:
                raise RuntimeError(
                    f"Package verification failed: {language} Kor scenario translations missing."
                )
        for language in ("English", "German"):
            translation_path = (
                f"{MOD_FOLDER_NAME}/Languages/{language}/DefInjected/FactionDef/KOR_Dynasty.xml"
            )
            if translation_path not in names:
                raise RuntimeError(
                    f"Package verification failed: {language} Kor faction translations missing."
                )
        unexpected = [
            name for name in names
            if not name.startswith(f"{MOD_FOLDER_NAME}/")
            or name.startswith(f"{MOD_FOLDER_NAME}/.git/")
        ]
        if unexpected:
            raise RuntimeError(f"Package contains unexpected paths: {unexpected}")

    return output_resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Mod repository root")
    parser.add_argument("--output", type=Path, default=None, help="Output ZIP path")
    args = parser.parse_args()
    try:
        output = package_mod(args.root, args.output)
    except (OSError, RuntimeError) as exc:
        print(f"Packaging FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"Package created and verified: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
