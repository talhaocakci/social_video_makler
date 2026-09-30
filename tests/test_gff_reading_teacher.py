import importlib.util
from pathlib import Path
import unittest

module_path=Path(__file__).resolve().parents[1]/'scripts/gff_reading_teacher.py'
spec=importlib.util.spec_from_file_location('gff_reading_teacher',module_path)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class SourceAlignmentTest(unittest.TestCase):
    def test_internal_hyphen_does_not_change_display_text(self):
        text='Her check-in and check-out dates.'
        words=[dict(text=t,start_ms=i*100+250,end_ms=(i+1)*100+250)
               for i,t in enumerate(['Her','checkin','and','checkout','dates'])]
        rows=module.word_spans(text,words,250)
        self.assertEqual([text[r['start']:r['end']] for r in rows],['Her','check-in','and','check-out','dates'])
        self.assertEqual(rows[0]['t0'],0)

    def test_mismatching_or_incomplete_alignment_fails_closed(self):
        with self.assertRaises(ValueError):
            module.word_spans('a room', [dict(text='room',start_ms=0,end_ms=100)],0)
        with self.assertRaises(AssertionError):
            module.word_spans('a room', [dict(text='a',start_ms=0,end_ms=100)],0)

    def test_zero_width_native_timestamp_preserved(self):
        rows=module.word_spans('a room',[dict(text='a',start_ms=0,end_ms=0),dict(text='room',start_ms=0,end_ms=120)],0)
        self.assertEqual(rows[0]['t0'],rows[0]['t1'])
        self.assertEqual(rows[1]['t1'],.12)

if __name__=='__main__':unittest.main()
