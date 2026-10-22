"""Regression tests for mod validation and clean package generation."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

TOOLS = Path(__file__).resolve().parents[1] / "tools"


def load_tool(name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_tool("validate_mod")
PACKAGER = load_tool("package_mod")


def make_minimal_mod(root: Path) -> None:
    (root / "About").mkdir(parents=True)
    (root / "Defs" / "FactionDefs").mkdir(parents=True)
    (root / "About" / "About.xml").write_text(
        """<ModMetaData><name>KOR: DYNASTIE</name>
        <packageId>oORaxaOo.KORDynastie</packageId>
        <supportedVersions><li>1.6</li><li>1.7</li></supportedVersions>
        </ModMetaData>""",
        encoding="utf-8",
    )
    (root / "Defs" / "PawnKindDefs").mkdir(parents=True)
    (root / "Defs" / "PawnKindDefs" / "KOR_PawnKinds.xml").write_text(
        '<Defs><PawnKindDef ParentName="BaseOutlander"><defName>KOR_Resident</defName><label>Kor resident</label><defaultFactionType>KOR_Dynasty</defaultFactionType></PawnKindDef></Defs>',
        encoding="utf-8",
    )
    (root / "Defs" / "FactionDefs" / "KOR_Dynasty.xml").write_text(
        """<Defs><FactionDef ParentName="OutlanderCivil">
        <defName>KOR_Dynasty</defName><label>Kor Dynasty</label>
        <description>Test faction</description><pawnSingular>Kor</pawnSingular>
        <pawnsPlural>Kor</pawnsPlural><leaderTitle>Dynasty Speaker</leaderTitle>
        <settlementGenerationWeight>0.75</settlementGenerationWeight>
        <requiredCountAtGameStart>1</requiredCountAtGameStart>
        <maxCountAtGameStart>2</maxCountAtGameStart>
        <settlementTexturePath>World/WorldObjects/DefaultSettlement</settlementTexturePath>\n        <basicMemberKind>KOR_Resident</basicMemberKind>
        <colorSpectrum><li>(0.68, 0.08, 0.12)</li>
        <li>(0.10, 0.10, 0.12)</li><li>(0.78, 0.62, 0.25)</li></colorSpectrum>
        </FactionDef></Defs>""",
        encoding="utf-8",
    )
    keys = {
        "KOR_Dynasty.label": "Kor Dynasty",
        "KOR_Dynasty.description": "Test faction description",
        "KOR_Dynasty.pawnSingular": "Kor",
        "KOR_Dynasty.pawnsPlural": "Kor",
        "KOR_Dynasty.leaderTitle": "Dynasty Speaker",
    }
    for language in ("English", "German"):
        folder = root / "Languages" / language / "DefInjected" / "FactionDef"
        folder.mkdir(parents=True)
        body = "".join(f"<{key}>{value}</{key}>" for key, value in keys.items())
        (folder / "KOR_Dynasty.xml").write_text(
            f"<LanguageData>{body}</LanguageData>", encoding="utf-8"
        )


class ValidateModTests(unittest.TestCase):
    def test_repository_passes_static_validation(self):
        self.assertEqual(VALIDATOR.validate(VALIDATOR.ROOT), [])

    def test_invalid_xml_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            (root / "Defs" / "FactionDefs" / "KOR_Dynasty.xml").write_text("<Defs>", encoding="utf-8")
            errors = VALIDATOR.validate(root)
            self.assertTrue(any("invalid/unreadable XML" in error for error in errors))

    def test_missing_target_version_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            (root / "About" / "About.xml").write_text(
                """<ModMetaData><name>KOR: DYNASTIE</name>
                <packageId>oORaxaOo.KORDynastie</packageId>
                <supportedVersions><li>1.6</li></supportedVersions></ModMetaData>""",
                encoding="utf-8",
            )
            self.assertTrue(any("missing supported version 1.7" in e for e in VALIDATOR.validate(root)))

    def test_duplicate_def_names_are_reported_across_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            (root / "Defs" / "FactionDefs" / "Duplicate.xml").write_text(
                '<Defs><FactionDef><defName>KOR_Dynasty</defName></FactionDef></Defs>', encoding="utf-8"
            )
            self.assertTrue(any("Duplicate defName 'KOR_Dynasty'" in e for e in VALIDATOR.validate(root)))

    def test_defs_file_requires_defs_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            (root / "Defs" / "FactionDefs" / "BrokenRoot.xml").write_text(
                "<FactionDef><defName>Broken</defName></FactionDef>", encoding="utf-8"
            )
            self.assertTrue(any("must have a <Defs> root" in e for e in VALIDATOR.validate(root)))

    def test_duplicate_supported_versions_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            (root / "About" / "About.xml").write_text(
                """<ModMetaData><name>KOR: DYNASTIE</name>
                <packageId>oORaxaOo.KORDynastie</packageId><supportedVersions>
                <li>1.6</li><li>1.7</li><li>1.7</li></supportedVersions></ModMetaData>""",
                encoding="utf-8",
            )
            self.assertTrue(any("duplicate supportedVersions" in e for e in VALIDATOR.validate(root)))

    def test_missing_faction_identity_field_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            (root / "Defs" / "FactionDefs" / "KOR_Dynasty.xml").write_text(
                '<Defs><FactionDef ParentName="OutlanderCivil"><defName>KOR_Dynasty</defName></FactionDef></Defs>',
                encoding="utf-8",
            )
            self.assertTrue(any("missing required identity field <label>" in e for e in VALIDATOR.validate(root)))

    def test_missing_world_presence_field_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            path = root / "Defs" / "FactionDefs" / "KOR_Dynasty.xml"
            content = path.read_text(encoding="utf-8").replace(
                "<settlementGenerationWeight>0.75</settlementGenerationWeight>", ""
            )
            path.write_text(content, encoding="utf-8")
            self.assertTrue(any("missing world-presence field <settlementGenerationWeight>" in e for e in VALIDATOR.validate(root)))

    def test_invalid_world_generation_counts_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            path = root / "Defs" / "FactionDefs" / "KOR_Dynasty.xml"
            content = path.read_text(encoding="utf-8").replace(
                "<maxCountAtGameStart>2</maxCountAtGameStart>",
                "<maxCountAtGameStart>0</maxCountAtGameStart>",
            )
            path.write_text(content, encoding="utf-8")
            self.assertTrue(any("maxCountAtGameStart must be at least requiredCountAtGameStart" in e for e in VALIDATOR.validate(root)))

    def test_missing_kor_pawn_kind_reference_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            path = root / "Defs" / "FactionDefs" / "KOR_Dynasty.xml"
            path.write_text(path.read_text(encoding="utf-8").replace(
                "<basicMemberKind>KOR_Resident</basicMemberKind>", ""
            ), encoding="utf-8")
            self.assertTrue(any("basicMemberKind must reference KOR_Resident" in e for e in VALIDATOR.validate(root)))

    def test_missing_german_faction_translation_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            (root / "Languages" / "German" / "DefInjected" / "FactionDef" / "KOR_Dynasty.xml").unlink()
            self.assertTrue(any("Missing or invalid faction translations" in e for e in VALIDATOR.validate(root)))

    def test_empty_translation_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            path = root / "Languages" / "English" / "DefInjected" / "FactionDef" / "KOR_Dynasty.xml"
            path.write_text("<LanguageData><KOR_Dynasty.label> </KOR_Dynasty.label></LanguageData>", encoding="utf-8")
            self.assertTrue(any("must not be empty" in e for e in VALIDATOR.validate(root)))


class PackageModTests(unittest.TestCase):
    def test_package_contains_runtime_files_with_correct_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            (root / "README.md").write_text("dev documentation", encoding="utf-8")
            (root / "tools").mkdir()
            (root / "tools" / "secret-dev.txt").write_text("not a runtime file", encoding="utf-8")
            output = root / "dist" / "test.zip"
            result = PACKAGER.package_mod(root, output)
            self.assertEqual(result, output.resolve())
            with ZipFile(result) as archive:
                names = set(archive.namelist())
                self.assertIn("KOR-DYNASTIE/About/About.xml", names)
                self.assertIn("KOR-DYNASTIE/Defs/FactionDefs/KOR_Dynasty.xml", names)
                self.assertIn("KOR-DYNASTIE/Languages/German/DefInjected/FactionDef/KOR_Dynasty.xml", names)
                self.assertFalse(any("README.md" in name or "secret-dev.txt" in name for name in names))

    def test_package_fails_if_required_faction_file_is_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "About").mkdir()
            (root / "About" / "About.xml").write_text("<ModMetaData/>", encoding="utf-8")
            with self.assertRaises(FileNotFoundError):
                PACKAGER.package_mod(root, root / "out.zip")


if __name__ == "__main__":
    unittest.main()
