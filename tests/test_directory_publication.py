from brightonlive.directory.normalization import fhrs_consumer_eligible

POLICY={
    'fhrs_consumer_allow_markers':['restaurant','cafe','pub','takeaway','retailer'],
    'fhrs_consumer_hold_markers':['school','caring premises','manufacturer','mobile caterer'],
}

def row(category):
    return {'source_category':category,'evidence':[{'source_key':'fhrs'}]}

def test_fhrs_consumer_places_can_progress():
    assert fhrs_consumer_eligible(row('Restaurant/Cafe/Canteen'), POLICY)[0]

def test_fhrs_institutional_kitchens_are_held():
    ok, reason=fhrs_consumer_eligible(row('School/college/university'), POLICY)
    assert not ok
    assert reason == 'fhrs_non_consumer_type'
