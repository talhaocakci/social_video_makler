import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from gff_reading_links import build, reading_url

class ReadingLinkTests(unittest.TestCase):
    def test_route_is_exact_and_stable(self):
        self.assertEqual(reading_url('vocab-reading-abc'),'https://getfluentfast.app/reading/vocab-reading-abc/')
        for value in ('../admin','x/y','x?next=evil','', 'ü', 'a'*161):
            with self.assertRaises(ValueError): reading_url(value)
    def test_html_escapes_source_and_has_same_app_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            page=build('reading-1','<script>alert(1)</script>','A & B',tmp)
            text=(page/'index.html').read_text()
            self.assertIn('&lt;script&gt;',text)
            self.assertIn('getfluentfast://reading/reading-1',text)
            self.assertIn('https://getfluentfast.app/reading/reading-1/',text)
            self.assertTrue((page/'qr.png').exists())
if __name__=='__main__': unittest.main()
