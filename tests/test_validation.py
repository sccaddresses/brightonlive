from brightonlive.validation import validate_directory, validate_event

def test_directory_validation():
    valid={"name":"Cafe","category":"Food","postcode":"BN1 1AA","website":"https://example.com","latitude":50.82,"longitude":-0.14}
    assert validate_directory(valid) == []

def test_registered_office_not_public():
    r={"name":"Co","category":"Professional","registered_office_only":True,"address_public":True}
    assert "registered_office_marked_public" in validate_directory(r)

def test_event_requires_date_location_source():
    errors=validate_event({"title":"A show"})
    assert {"invalid_start","missing_location_signal","missing_source_url"}.issubset(errors)

def test_event_valid():
    r={"title":"A show","start":"2026-09-01T19:00:00+01:00","venue":"Venue","source_url":"https://example.com/event"}
    assert validate_event(r) == []
