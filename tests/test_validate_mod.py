"""Regression tests for repository-level mod integration checks."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "validate_mod.py"
SPEC = importlib.util.spec_from_file_location("validate_mod", SCRIPT)
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATOR)


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
    (root / "Defs" / "FactionDefs" / "KOR_Dynasty.xml").write_text(
        """<Defs><FactionDef ParentName="OutlanderCivil">
        <defName>KOR_Dynasty</defName><label>Kor Dynasty</label>
        <description>Test faction</description><pawnSingular>Kor</pawnSingular>
        <pawnsPlural>Kor</pawnsPlural><leaderTitle>Dynasty Speaker</leaderTitle>
        <colorSpectrum><li>(0.68, 0.08, 0.12)</li>
        <li>(0.10, 0.10, 0.12)</li><li>(0.78, 0.62, 0.25)</li></colorSpectrum>
        </FactionDef></Defs>""",
        encoding="utf-8",
    )


class ValidateModTests(unittest.TestCase):
    def test_repository_passes_static_validation(self):
        self.assertEqual(VALIDATOR.validate(VALIDATOR.ROOT), [])

    def test_invalid_xml_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            (root / "Defs" / "FactionDefs" / "KOR_Dynasty.xml").write_text(
                "<Defs>", encoding="utf-8"
            )
            errors = VALIDATOR.validate(root)
            self.assertTrue(any("invalid/unreadable XML" in error for error in errors))

    def test_missing_target_version_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            metadata = root / "About" / "About.xml"
            metadata.write_text(
                """<ModMetaData><name>KOR: DYNASTIE</name>
                <packageId>oORaxaOo.KORDynastie</packageId>
                <supportedVersions><li>1.6</li></supportedVersions>
                </ModMetaData>""",
                encoding="utf-8",
            )
            errors = VALIDATOR.validate(root)
            self.assertTrue(any("missing supported version 1.7" in e for e in errors))

    def test_duplicate_def_names_are_reported_across_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            other = root / "Defs" / "FactionDefs" / "Duplicate.xml"
            other.write_text(
                """<Defs><FactionDef ParentName="OutlanderCivil">
                <defName>KOR_Dynasty</defName></FactionDef></Defs>""",
                encoding="utf-8",
            )
            errors = VALIDATOR.validate(root)
            self.assertTrue(any("Duplicate defName 'KOR_Dynasty'" in e for e in errors))

    def test_defs_file_requires_defs_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            (root / "Defs" / "FactionDefs" / "BrokenRoot.xml").write_text(
                "<FactionDef><defName>Broken</defName></FactionDef>",
                encoding="utf-8",
            )
            errors = VALIDATOR.validate(root)
            self.assertTrue(any("must have a <Defs> root" in e for e in errors))

    def test_duplicate_supported_versions_are_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            metadata = root / "About" / "About.xml"
            metadata.write_text(
                """<ModMetaData><name>KOR: DYNASTIE</name>
                <packageId>oORaxaOo.KORDynastie</packageId>
                <supportedVersions><li>1.6</li><li>1.7</li><li>1.7</li></supportedVersions>
                </ModMetaData>""",
                encoding="utf-8",
            )
            errors = VALIDATOR.validate(root)
            self.assertTrue(any("duplicate supportedVersions" in e for e in errors))

    def test_missing_faction_identity_field_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_minimal_mod(root)
            faction = root / "Defs" / "FactionDefs" / "KOR_Dynasty.xml"
            faction.write_text(
                """<Defs><FactionDef ParentName="OutlanderCivil">
                <defName>KOR_Dynasty</defName></FactionDef></Defs>""",
                encoding="utf-8",
            )
            errors = VALIDATOR.validate(root)
            self.assertTrue(any("missing required identity field <label>" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
