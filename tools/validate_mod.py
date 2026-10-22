#!/usr/bin/env python3
"""Lightweight static checks for the KOR: DYNASTIE RimWorld mod scaffold."""

from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
errors = []

xml_files = sorted(ROOT.rglob("*.xml"))
if not xml_files:
    errors.append("No XML files found.")

for path in xml_files:
    try:
        ET.parse(path)
    except ET.ParseError as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid XML: {exc}")

metadata_path = ROOT / "About" / "About.xml"
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
    except ET.ParseError:
        pass

faction_path = ROOT / "Defs" / "FactionDefs" / "KOR_Dynasty.xml"
if faction_path.exists():
    try:
        faction_root = ET.parse(faction_path).getroot()
        faction = faction_root.find("./FactionDef")
        if faction is None:
            errors.append("KOR_Dynasty.xml: missing FactionDef.")
        elif faction.findtext("defName") != "KOR_Dynasty":
            errors.append("KOR_Dynasty.xml: faction defName must be KOR_Dynasty.")
    except ET.ParseError:
        pass

if errors:
    print("KOR: DYNASTIE validation FAILED")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print(f"KOR: DYNASTIE validation passed ({len(xml_files)} XML files parsed).")
print("Note: this is a static check; RimWorld runtime compatibility is not tested.")
