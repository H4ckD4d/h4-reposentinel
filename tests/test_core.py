import tempfile, unittest
from pathlib import Path
from reposentinel.core import scan
class CoreTests(unittest.TestCase):
    def test_finds_secrets_without_printing_values(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'demo.txt').write_text('TOKEN=SUPER_FAKE_TEST_VALUE_123456')
            res=scan(p)
            self.assertEqual(res['findings'][0]['rule'],'possible-secret-value-redacted')
            self.assertNotIn('SUPER_FAKE_TEST_VALUE',repr(res))
    def test_ignores_vendor_dirs(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'node_modules').mkdir();(p/'node_modules'/'a').write_text('TOKEN=ANOTHER_FAKE_VALUE_123')
            self.assertEqual(scan(p)['findings'],[])

    def test_sarif_redacts_and_has_source_location(self):
        from reposentinel.core import to_sarif
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'config.txt').write_text('TOKEN=EXAMPLE_NEVER_OUTPUT_VALUE_789')
            sarif=to_sarif(scan(p))
            self.assertEqual(sarif['version'], '2.1.0')
            finding=sarif['runs'][0]['results'][0]
            self.assertEqual(finding['locations'][0]['physicalLocation']['region']['startLine'], 1)
            self.assertNotIn('EXAMPLE_NEVER_OUTPUT_VALUE_789', repr(sarif))
    def test_sarif_without_line_number(self):
        from reposentinel.core import to_sarif
        report={'findings':[{'file':'.env','line':None,'rule':'environment-file-present','severity':'review'}]}
        loc=to_sarif(report)['runs'][0]['results'][0]['locations'][0]['physicalLocation']
        self.assertNotIn('region',loc)
