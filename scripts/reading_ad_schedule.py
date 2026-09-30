"""Schedule promotions after completed explanations, with six-minute spacing."""
def explained_terms(scene):
    if scene.get('kind') != 'teacher': return []
    terms=[n['term'] for n in scene.get('teaching_notes',[]) if n.get('kind') in ('word','phrase')]
    terms += [n['term'] for n in scene.get('lexical_pairs',[])]
    if not terms:
        beats=scene.get('speech_beats',[])
        if beats and beats[0].get('language')=='German':
            terms=[beats[0]['text'].strip().rstrip('.!?')]
    return list(dict.fromkeys(t for t in terms if t))

def plan_ads(scenes, *, spoken_duration=15, silent_duration=15, min_interval=360, end_card_start=float('inf')):
    events=[];seen=set();ordinal=0;shift=0
    for scene in sorted(scenes,key=lambda s:s['start']):
        terms=explained_terms(scene)
        if not terms:continue
        ordinal+=sum(t.casefold() not in seen for t in terms)
        seen.update(t.casefold() for t in terms)
        sentence=scene['sentence']+1
        source_end=scene['start']+scene['duration'];start=source_end+shift
        if not events:
            # The third source sentence is the earliest allowed opening.
            # Its first explained word qualifies under the user's OR rule.
            if sentence<3:continue
            duration=spoken_duration;mode='spoken'
        else:
            if start-events[-1]['start'] < min_interval-1e-6:continue
            duration=silent_duration;mode='silent'
        if start+duration>end_card_start+shift:continue
        events.append(dict(start=round(start,6),duration=duration,mode=mode,source_time=source_end,after_scene_key=scene.get('key'),source_sentence_index=scene['sentence'],explained_word_ordinal=ordinal,terms=terms,word=terms[0]))
        if mode=='spoken':shift+=duration
    return events
