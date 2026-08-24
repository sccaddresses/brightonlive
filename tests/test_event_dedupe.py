from brightonlive.events.dedupe import dedupe

def test_event_dedupe_merges_evidence():
    a={"title":"Live Music","start":"2026-09-01T19:00:00+01:00","venue":"Test","postcode":"BN1 1AA",
       "evidence":[{"source_key":"a","source_url":"https://a.example"}]}
    b={"title":"Live Music","start":"2026-09-01T20:00:00+01:00","venue":"Test","postcode":"BN1 1AA",
       "evidence":[{"source_key":"b","source_url":"https://b.example"}]}
    out=dedupe([a,b])
    assert len(out)==1
    assert len(out[0]["evidence"])==2
