from brightonlive.verification import directory_decision, event_decision

POLICY={"minimum_independent_sources":2,"allow_class_a_single_source":True,"allow_owned_source_single_source":True}

def evidence(source_type="owned_primary",url="https://example.com"):
    return [{"source_key":"x","source_url":url,"source_owner":"Owner","source_type":source_type,"retrieved_at":"2026-08-23"}]

def test_owned_primary_can_publish():
    r={"validation_errors":[],"evidence":evidence()}
    assert directory_decision(r,POLICY)[0] == "publication_ready"

def test_companies_house_only_held():
    r={"validation_errors":[],"registered_office_only":True,"operational_location_confirmed":False,
       "evidence":evidence("authoritative_corporate","https://find-and-update.company-information.service.gov.uk/company/1")}
    assert directory_decision(r,POLICY)[0] == "held_for_review"

def test_event_first_party_can_publish():
    r={"validation_errors":[],"evidence":evidence("first_party")}
    assert event_decision(r,POLICY)[0] == "publication_ready"
