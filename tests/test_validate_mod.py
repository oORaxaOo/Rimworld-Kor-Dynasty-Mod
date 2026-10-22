"""Regression tests for the repository's static mod validator."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "validate_mod.py"
SPEC = importlib.util.spec_from_file_location("validate_mod", SCRIPT)
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATOR)


class ValidateModTests(unittest.TestCase):
    def test_repository_passes_static_validation(self):
        self.assertEqual(VALIDATOR.validate(VALIDATOR.ROOT), [])

    def test_invalid_xml_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "About").mkdir()
            (root / "Defs" / "FactionDefs").mkdir(parents=True)
            (root / "About" / "About.xml").write_text("<ModMetaData>", encoding="utf-8")
            (root / "Defs" / "FactionDefs" / "KOR_Dynasty.xml").write_text(
                "<Defs>", encoding="utf-8"
            )
            errors = VALIDATOR.validate(root)
            self.assertTrue(any("invalid XML" in error for error in errors))

    def test_missing_target_version_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "About").mkdir()
            (root / "Defs" / "FactionDefs").mkdir(parents=True)
            (root / "About" / "About.xml").write_text(
                """<ModMetaData><name>KOR: DYNASTIE</name>
                <packageId>oORaxaOo.KORDynastie</packageId>
                <supportedVersions><li>1.6</li></supportedVersions></ModMetaData>""",
                encoding="utf-8",
            )
            (root / "Defs" / "FactionDefs" / "KOR_Dynasty.xml").write_text(
                """<Defs><FactionDef ParentName="OutlanderCivil">
                <defName>KOR_Dynasty</defName></FactionDef></Defs>""",
                encoding="utf-8",
            )
            errors = VALIDATOR.validate(root)
            self.assertTrue(any("missing supported version 1.7" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
