from brightonlive.sources.structured_pages import _visible_events, _detail_links

SOURCE={'key':'venue','name':'Venue','source_type':'first_party','default_venue':'Venue','default_postcode':'BN1 1AA'}

def test_visible_event_section_extracts_title_date_and_source():
    html='''<html><body><h2><a href="/events/show-one">Show One</a></h2><p>Friday 4 September 2026, 19:30</p></body></html>'''
    rows=_visible_events(html,SOURCE,'https://venue.example/whats-on','2026-08-24T10:00:00+00:00')
    assert len(rows)==1
    assert rows[0]['title']=='Show One'
    assert rows[0]['start'].startswith('2026-09-04T19:30')
    assert rows[0]['source_url']=='https://venue.example/events/show-one'

def test_detail_links_stay_on_site_and_event_like():
    html='''<a href="/events/a">A show</a><a href="https://other.example/events/b">Other</a><a href="/contact">Contact</a>'''
    assert _detail_links(html,'https://venue.example/whats-on',10)==['https://venue.example/events/a']
