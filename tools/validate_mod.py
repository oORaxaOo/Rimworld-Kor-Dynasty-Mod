#!/usr/bin/env python3
"""Static XML and metadata checks for the KOR: DYNASTIE mod scaffold."""

from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    xml_files = sorted(root.rglob("*.xml"))
    if not xml_files:
        errors.append("No XML files found.")

    for path in xml_files:
        try:
            ET.parse(path)
        except ET.ParseError as exc:
            errors.append(f"{path.relative_to(root)}: invalid XML: {exc}")

    metadata_path = root / "About" / "About.xml"
    if metadata_path.exists():
        try:
            metadata = ET.parse(metadata_path).getroot()
            expected = {
                "name": "KOR: DYNASTIE",
                "packageId": "oORaxaOo.KORDynastie",
            }
            for tag, value in expected.items():
                actual = metadata.findtext(tag)
                if actual != value:
                    errors.append(
                        f"About/About.xml: expected <{tag}>{value}</{tag}>, got {actual!r}"
                    )
            versions = {node.text for node in metadata.findall("./supportedVersions/li")}
            for version in ("1.6", "1.7"):
                if version not in versions:
                    errors.append(f"About/About.xml: missing supported version {version}")
            for version in versions:
                if version and version not in {"1.6", "1.7"}:
                    errors.append(
                        f"About/About.xml: unsupported legacy/unplanned version {version}"
                    )
        except ET.ParseError:
            # The XML parser already emitted the detailed parse error above.
            pass
    else:
        errors.append("Missing About/About.xml.")

    faction_path = root / "Defs" / "FactionDefs" / "KOR_Dynasty.xml"
    if faction_path.exists():
        try:
            faction_root = ET.parse(faction_path).getroot()
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
        except ET.ParseError:
            # The XML parser already emitted the detailed parse error above.
            pass
    else:
        errors.append("Missing Defs/FactionDefs/KOR_Dynasty.xml.")

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
    print("Note: static validation does not test RimWorld runtime compatibility.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
