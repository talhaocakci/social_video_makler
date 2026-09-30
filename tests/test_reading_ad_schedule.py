import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from reading_ad_schedule import plan_ads

def note(sentence,end,word):
    return dict(kind='teacher',sentence=sentence-1,start=end-5,duration=5,key=word,teaching_notes=[dict(kind='word',term=word)])
class ScheduleTests(unittest.TestCase):
    def test_sentence_floor_and_exact_six_minute_spacing(self):
        e=plan_ads([note(1,5,'a'),note(2,10,'b'),note(3,40,'c'),note(20,384,'d'),note(21,385,'e'),note(30,744,'f'),note(31,745,'g')])
        self.assertEqual([x['start'] for x in e],[40,400,760])
        self.assertEqual([x['word'] for x in e],['c','e','g'])
    def test_first_word_at_sentence_three_qualifies(self):
        self.assertEqual(len(plan_ads([note(3,40,'Überblick')])),1)
    def test_no_explanation_no_ad_and_closing_collision(self):
        self.assertEqual(plan_ads([dict(kind='reading',sentence=3,start=0,duration=500)]),[])
        self.assertEqual(plan_ads([note(3,40,'x')],end_card_start=45),[])
    def test_waits_for_explanation_after_threshold(self):
        self.assertEqual([e['start'] for e in plan_ads([note(3,40,'a'),note(9,300,'b'),note(30,600,'c')])],[40,615])
if __name__=='__main__':unittest.main()
