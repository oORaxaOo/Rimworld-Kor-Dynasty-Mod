#!/usr/bin/env python3
"""Static integration checks for KOR: DYNASTIE XML, metadata and translations.

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
REQUIRED_FACTION_TRANSLATIONS = {
    "KOR_Dynasty.label",
    "KOR_Dynasty.description",
    "KOR_Dynasty.pawnSingular",
    "KOR_Dynasty.pawnsPlural",
    "KOR_Dynasty.leaderTitle",
}
REQUIRED_LANGUAGES = {"English", "German"}
REQUIRED_PAWN_KIND = "KOR_Resident"
REQUIRED_SCENARIO = "KOR_ColonyStart"
REQUIRED_SCENARIO_TRANSLATIONS = {
    "KOR_ColonyStart.label",
    "KOR_ColonyStart.description",
    "KOR_ColonyStart.scenario.name",
    "KOR_ColonyStart.scenario.summary",
    "KOR_ColonyStart.scenario.description",
}
REQUIRED_WORLD_PRESENCE_FIELDS = (
    "settlementGenerationWeight",
    "requiredCountAtGameStart",
    "maxCountAtGameStart",
    "settlementTexturePath",
)


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

    pawn_kind_path = root / "Defs" / "PawnKindDefs" / "KOR_PawnKinds.xml"
    pawn_kind_root = parsed_roots.get(pawn_kind_path)
    pawn_kind = pawn_kind_root.find("./PawnKindDef") if pawn_kind_root is not None else None
    if pawn_kind is None:
        errors.append("Missing or invalid Defs/PawnKindDefs/KOR_PawnKinds.xml or PawnKindDef.")
    else:
        if pawn_kind.findtext("defName") != REQUIRED_PAWN_KIND:
            errors.append(f"KOR_PawnKinds.xml: expected defName {REQUIRED_PAWN_KIND}.")
        if pawn_kind.get("ParentName") != "BaseOutlander":
            errors.append("KOR_PawnKinds.xml: KOR_Resident must retain the BaseOutlander baseline.")
        if pawn_kind.findtext("defaultFactionType") != "KOR_Dynasty":
            errors.append("KOR_PawnKinds.xml: KOR_Resident must default to KOR_Dynasty.")
        if not (pawn_kind.findtext("label") or "").strip():
            errors.append("KOR_PawnKinds.xml: KOR_Resident is missing its label.")

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

            if faction.findtext("basicMemberKind") != REQUIRED_PAWN_KIND:
                errors.append("KOR_Dynasty.xml: basicMemberKind must reference KOR_Resident.")

            for tag in REQUIRED_WORLD_PRESENCE_FIELDS:
                if not (faction.findtext(tag) or "").strip():
                    errors.append(f"KOR_Dynasty.xml: missing world-presence field <{tag}>.")

            try:
                generation_weight = float(faction.findtext("settlementGenerationWeight") or "")
                if generation_weight <= 0:
                    errors.append("KOR_Dynasty.xml: settlementGenerationWeight must be positive.")
            except ValueError:
                errors.append("KOR_Dynasty.xml: settlementGenerationWeight must be numeric.")

            try:
                required_count = int(faction.findtext("requiredCountAtGameStart") or "")
                max_count = int(faction.findtext("maxCountAtGameStart") or "")
                if required_count < 0:
                    errors.append("KOR_Dynasty.xml: requiredCountAtGameStart cannot be negative.")
                if max_count < required_count:
                    errors.append("KOR_Dynasty.xml: maxCountAtGameStart must be at least requiredCountAtGameStart.")
            except ValueError:
                errors.append("KOR_Dynasty.xml: game-start faction counts must be integers.")

    player_faction = None
    if faction_root is not None:
        player_faction = faction_root.find("./FactionDef[defName='KOR_PlayerFaction']")
    if player_faction is None:
        errors.append("KOR_Dynasty.xml: missing KOR_PlayerFaction definition for the playable scenario.")
    else:
        if player_faction.get("ParentName") != "PlayerFactionBase":
            errors.append("KOR_Dynasty.xml: KOR_PlayerFaction must inherit PlayerFactionBase.")
        if player_faction.findtext("basicMemberKind") != REQUIRED_PAWN_KIND:
            errors.append("KOR_Dynasty.xml: KOR_PlayerFaction basicMemberKind must reference KOR_Resident.")

    scenario_path = root / "Defs" / "ScenarioDefs" / "KOR_ColonyStart.xml"
    scenario_root = parsed_roots.get(scenario_path)
    scenario = scenario_root.find("./ScenarioDef") if scenario_root is not None else None
    if scenario is None:
        errors.append("Missing or invalid Defs/ScenarioDefs/KOR_ColonyStart.xml or ScenarioDef.")
    else:
        if scenario.get("ParentName") != "ScenarioBase":
            errors.append("KOR_ColonyStart.xml: scenario must inherit ScenarioBase.")
        if scenario.findtext("defName") != REQUIRED_SCENARIO:
            errors.append(f"KOR_ColonyStart.xml: expected defName {REQUIRED_SCENARIO}.")
        if not (scenario.findtext("label") or "").strip() or not (scenario.findtext("description") or "").strip():
            errors.append("KOR_ColonyStart.xml: label and description are required.")
        if scenario.findtext("./scenario/playerFaction/factionDef") != "KOR_PlayerFaction":
            errors.append("KOR_ColonyStart.xml: playerFaction must reference KOR_PlayerFaction.")
        pawn_parts = scenario.findall("./scenario/parts/li[@Class='ScenPart_ConfigPage_ConfigureStartingPawns_KindDefs']")
        kor_start_count = 0
        required_start = False
        for part in pawn_parts:
            for entry in part.findall("./kindCounts/li"):
                if entry.findtext("kindDef") == REQUIRED_PAWN_KIND:
                    try:
                        kor_start_count += int(entry.findtext("count") or "0")
                    except ValueError:
                        errors.append("KOR_ColonyStart.xml: KOR_Resident starting count must be an integer.")
                    required_start = required_start or (entry.findtext("requiredAtStart") == "true")
        if kor_start_count != 4:
            errors.append("KOR_ColonyStart.xml: starting roster must require exactly four KOR_Resident pawns.")
        if not required_start:
            errors.append("KOR_ColonyStart.xml: KOR_Resident must be required at start.")
        if not pawn_parts or any(not part.findall("./kindCounts/li") for part in pawn_parts):
            errors.append("KOR_ColonyStart.xml: starting pawn configuration must contain kindCounts.")

    for language in sorted(REQUIRED_LANGUAGES):
        translation_path = (
            root / "Languages" / language / "DefInjected" / "FactionDef" / "KOR_Dynasty.xml"
        )
        translation_root = parsed_roots.get(translation_path)
        relative = translation_path.relative_to(root).as_posix()
        if translation_root is None:
            errors.append(f"Missing or invalid faction translations: {relative}.")
            continue
        if translation_root.tag != "LanguageData":
            errors.append(f"{relative}: translation file must have a <LanguageData> root.")
            continue
        translated_keys: set[str] = set()
        for node in list(translation_root):
            key = node.tag
            if key in translated_keys:
                errors.append(f"{relative}: duplicate translation key {key!r}.")
            translated_keys.add(key)
            if not (node.text or "").strip():
                errors.append(f"{relative}: translation {key!r} must not be empty.")
        for required_key in sorted(REQUIRED_FACTION_TRANSLATIONS - translated_keys):
            errors.append(f"{relative}: missing translation key {required_key!r}.")

        scenario_translation_path = root / "Languages" / language / "DefInjected" / "ScenarioDef" / "KOR_ColonyStart.xml"
        scenario_translation_root = parsed_roots.get(scenario_translation_path)
        relative_scenario = scenario_translation_path.relative_to(root).as_posix()
        if scenario_translation_root is None:
            errors.append(f"Missing or invalid scenario translations: {relative_scenario}.")
        elif scenario_translation_root.tag != "LanguageData":
            errors.append(f"{relative_scenario}: translation file must have a <LanguageData> root.")
        else:
            scenario_keys: set[str] = set()
            for node in list(scenario_translation_root):
                if node.tag in scenario_keys:
                    errors.append(f"{relative_scenario}: duplicate translation key {node.tag!r}.")
                scenario_keys.add(node.tag)
                if not (node.text or "").strip():
                    errors.append(f"{relative_scenario}: translation {node.tag!r} must not be empty.")
            for required_key in sorted(REQUIRED_SCENARIO_TRANSLATIONS - scenario_keys):
                errors.append(f"{relative_scenario}: missing translation key {required_key!r}.")

        pawn_translation_path = root / "Languages" / language / "DefInjected" / "PawnKindDef" / "KOR_PawnKinds.xml"
        pawn_translation_root = parsed_roots.get(pawn_translation_path)
        relative_pawn = pawn_translation_path.relative_to(root).as_posix()
        if pawn_translation_root is None:
            errors.append(f"Missing or invalid pawn-kind translations: {relative_pawn}.")
        elif pawn_translation_root.tag != "LanguageData":
            errors.append(f"{relative_pawn}: translation file must have a <LanguageData> root.")
        elif not (pawn_translation_root.findtext("KOR_Resident.label") or "").strip():
            errors.append(f"{relative_pawn}: missing or empty translation KOR_Resident.label.")

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
    print("Duplicate DefNames, Defs roots, faction identity, palette, world presence and English/German translations checked.")
    print("Note: static validation does not test RimWorld runtime compatibility.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
