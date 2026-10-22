#!/usr/bin/env python3
"""Static integration checks for KOR: DYNASTIE XML and mod metadata.

These checks catch repository-level integration mistakes. They do not replace
loading the mod in the target RimWorld build.
"""

from collections import defaultdict
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_VERSIONS = {"1.6", "1.7"}
EXPECTED_METADATA = {
    "name": "KOR: DYNASTIE",
    "packageId": "oORaxaOo.KORDynastie",
}


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    xml_files = sorted(root.rglob("*.xml"))
    if not xml_files:
        errors.append("No XML files found.")

    parsed_roots: dict[Path, ET.Element] = {}
    def_locations: dict[str, list[str]] = defaultdict(list)

    for path in xml_files:
        relative = path.relative_to(root).as_posix()
        try:
            xml_root = ET.parse(path).getroot()
            parsed_roots[path] = xml_root
        except (ET.ParseError, OSError) as exc:
            errors.append(f"{relative}: invalid/unreadable XML: {exc}")
            continue

        if "Defs" in path.relative_to(root).parts and xml_root.tag != "Defs":
            errors.append(f"{relative}: files under Defs/ must have a <Defs> root.")

        if xml_root.tag == "Defs":
            for definition in list(xml_root):
                def_name = definition.findtext("defName")
                if def_name:
                    def_locations[def_name.strip()].append(relative)

    for def_name, locations in sorted(def_locations.items()):
        if len(locations) > 1:
            errors.append(
                f"Duplicate defName {def_name!r} found in: {', '.join(locations)}"
            )

    metadata_path = root / "About" / "About.xml"
    metadata = parsed_roots.get(metadata_path)
    if metadata is None:
        errors.append("Missing or invalid About/About.xml.")
    else:
        for tag, expected in EXPECTED_METADATA.items():
            actual = metadata.findtext(tag)
            if actual != expected:
                errors.append(
                    f"About/About.xml: expected <{tag}>{expected}</{tag}>, got {actual!r}"
                )

        version_nodes = metadata.findall("./supportedVersions/li")
        versions = [node.text.strip() for node in version_nodes if node.text and node.text.strip()]
        for required in sorted(SUPPORTED_VERSIONS):
            if required not in versions:
                errors.append(f"About/About.xml: missing supported version {required}")
        for version in versions:
            if version not in SUPPORTED_VERSIONS:
                errors.append(
                    f"About/About.xml: unsupported legacy/unplanned version {version}"
                )
        if len(versions) != len(set(versions)):
            errors.append("About/About.xml: duplicate supportedVersions entries.")

    faction_path = root / "Defs" / "FactionDefs" / "KOR_Dynasty.xml"
    faction_root = parsed_roots.get(faction_path)
    if faction_root is None:
        errors.append("Missing or invalid Defs/FactionDefs/KOR_Dynasty.xml.")
    else:
        faction = faction_root.find("./FactionDef")
        if faction is None:
            errors.append("KOR_Dynasty.xml: missing FactionDef.")
        else:
            if faction.findtext("defName") != "KOR_Dynasty":
                errors.append("KOR_Dynasty.xml: faction defName must be KOR_Dynasty.")
            if not faction.get("ParentName"):
                errors.append(
                    "KOR_Dynasty.xml: faction must inherit a known template until a full definition exists."
                )
            for tag in ("label", "description", "pawnSingular", "pawnsPlural", "leaderTitle"):
                if not (faction.findtext(tag) or "").strip():
                    errors.append(f"KOR_Dynasty.xml: missing required identity field <{tag}>.")
            colors = faction.findall("./colorSpectrum/li")
            if not colors:
                errors.append("KOR_Dynasty.xml: colorSpectrum must define at least one faction color.")
            elif len(colors) < 3:
                errors.append("KOR_Dynasty.xml: Kor palette should include red, charcoal, and gold entries.")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("KOR: DYNASTIE validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    xml_count = len(list(ROOT.rglob("*.xml")))
    print(f"KOR: DYNASTIE validation passed ({xml_count} XML files parsed).")
    print("Duplicate DefNames, Defs roots, faction identity, and palette checked.")
    print("Note: static validation does not test RimWorld runtime compatibility.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
