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
